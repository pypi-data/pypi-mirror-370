"""three types of congestions"""

# Requirements

import numpy as np
import pandas as pd

from tqdm import tqdm

import geopy.distance
import geopandas as gpd
import movingpandas as mpd
from shapely.ops import unary_union

import time as tm
from datetime import datetime, timedelta, time

import os
import math


class get_Safety():

    def find_direction(self, data, road_direction): # Get direction of pedestrian
        #geometry = gpd.GeoSeries(data["geometry"])
        data = gpd.GeoDataFrame(data, geometry = "geometry", crs = "EPSG:4326")
        data["dtct_dt"] = pd.to_datetime(data["dtct_dt"])
        data['time_without_ms'] = data['dtct_dt'].apply(lambda dt: dt.replace(microsecond=0))
        data = data.drop(columns=["dtct_dt"])

        dist_data = data["distance"][1:]
        dist_data.reset_index(inplace=True, drop=True)
        dist_data = pd.DataFrame(dist_data, columns=["distance"])

        new = pd.concat([dist_data, pd.DataFrame([0], columns=["distance"])], axis=0)

        #new.reset_index(drop=True, inplace=True)
        #new.set_index(pd.DatetimeIndex(data["time_without_ms"]), inplace=True)
        #data["new_distance"] = new["distance"]

        # 순서대로 직접 할당 (인덱스 정렬 없이)
        data = data.reset_index(drop=True).copy()
        data["new_distance"] = new["distance"].values

        ID = data["traj_id"].unique()
        moving_direction = [] # 0: forward, 1: backward

        for ids in ID:
            new_df = data.loc[data["traj_id"] == ids]
            indx_len = len(new_df)
            if indx_len > 0:
                for d in new_df["direction"]:
                    if road_direction == 0: # 0: height > width, 1: width > height
                        moving_direction.append(0) if 90 <= d <= 270 else moving_direction.append(1) # 0: down, 1: up
                    else:
                        moving_direction.append(0) if 0 <= d <= 180 else moving_direction.append(1) # 0: right, 1: left

        moving_direction = pd.DataFrame(moving_direction, columns = ["moving_direction"])
        data.reset_index(drop = True, inplace = True)
        df = pd.concat([data, moving_direction], axis = 1)
        df.set_index(pd.DatetimeIndex(df["time_without_ms"]), drop = True, inplace = True)

        return df

    def __init__(self, data, road_direction, road_sta):
        # Units =  road: meters, time: seconds
        # type_code 1 = pedestrian, 2 = vehicle, 200 = pm

        data_ = self.find_direction(data, road_direction)
        # pedestrian
        self.ped = data_.loc[data_["obj_cd"] == "M0101"]
        # vehicle
        self.vehicle = data_.loc[data_["obj_cd"].isin(["M0301", "M0302", "M0303", "M0304", "M0305", "M0306", "M0307", "M0308", "M0309"])]
        # PM (width & length by types)
        self.pm = data_.loc[data_["obj_cd"].isin(["M0201", "M0202", "M0203", "M0204", "M0205", "M0206"])]

        # total road(polygon) area
        self.road_sta = road_sta

    def separate_time_optimized(self, interval):
        """processing time only exists"""
        #print("time separation processing...")

        def process_group(df, label):
            df = df.copy()
            df['time_bucket'] = df.index.floor(f'{interval}s')
            grouped = df.groupby('time_bucket')
            return grouped

        self.ped['time_without_ms'] = pd.to_datetime(self.ped['time_without_ms'])
        self.vehicle['time_without_ms'] = pd.to_datetime(self.vehicle['time_without_ms'])
        self.pm['time_without_ms'] = pd.to_datetime(self.pm['time_without_ms'])

        self.ped.set_index('time_without_ms', inplace=True)
        self.vehicle.set_index('time_without_ms', inplace=True)
        self.pm.set_index('time_without_ms', inplace=True)

        ped_grouped = process_group(self.ped.copy(), 'ped')
        veh_grouped = process_group(self.vehicle.copy(), 'veh')
        pm_grouped = process_group(self.pm.copy(), 'pm')

        #self.times = ped_grouped.groups.keys()
        ped_times = set(ped_grouped.groups.keys())
        veh_times = set(veh_grouped.groups.keys())
        pm_times  = set(pm_grouped.groups.keys())

        self.times = sorted(ped_times | veh_times | pm_times)


        self.pedestrians = [ped_grouped.get_group(t) if t in ped_grouped.groups else pd.DataFrame(columns=self.ped.columns, index=[t]) for t in self.times]
        self.vehicles = [veh_grouped.get_group(t) if t in veh_grouped.groups else pd.DataFrame(columns=self.vehicle.columns, index=[t]) for t in self.times]
        self.pms = [pm_grouped.get_group(t) if t in pm_grouped.groups else pd.DataFrame(columns=self.pm.columns, index=[t]) for t in self.times]

    def separate_time_optimized_inclusive(self, interval):
        """
        processing time includes data doesn't exists.
        empty dataframe is appended if data doesn't exists.
        """
        #print("time separation processing...")

        # create whole time of a day
        date = self.ped['time_without_ms'].iloc[0].strftime('%Y-%m-%d')
        full_index = pd.date_range(start=f'{date} 00:00:00', end=f'{date} 23:59:59', freq=f'{interval}s')

        # parsing time and index setup
        self.ped['time_without_ms'] = pd.to_datetime(self.ped['time_without_ms'])
        self.vehicle['time_without_ms'] = pd.to_datetime(self.vehicle['time_without_ms'])
        self.pm['time_without_ms'] = pd.to_datetime(self.pm['time_without_ms'])

        self.ped.set_index('time_without_ms', inplace=True)
        self.vehicle.set_index('time_without_ms', inplace=True)
        self.pm.set_index('time_without_ms', inplace=True)

        # time bucket for empty dataframes
        self.ped['time_bucket'] = self.ped.index.floor(f'{interval}s')
        self.vehicle['time_bucket'] = self.vehicle.index.floor(f'{interval}s')
        self.pm['time_bucket'] = self.pm.index.floor(f'{interval}s')

        # group by time bucket
        ped_grouped = self.ped.groupby('time_bucket')
        veh_grouped = self.vehicle.groupby('time_bucket')
        pm_grouped = self.pm.groupby('time_bucket')

        # save columns without time bucket
        ped_cols = self.ped.drop(columns='time_bucket').columns
        veh_cols = self.vehicle.drop(columns='time_bucket').columns
        pm_cols = self.pm.drop(columns='time_bucket').columns

        # fill time by seconds
        self.times = full_index

        self.pedestrians = [ped_grouped.get_group(t).drop(columns='time_bucket') if t in ped_grouped.groups else pd.DataFrame(columns=ped_cols, index=[t]) for t in full_index]
        self.vehicles = [veh_grouped.get_group(t).drop(columns='time_bucket') if t in veh_grouped.groups else pd.DataFrame(columns=veh_cols, index=[t]) for t in full_index]
        self.pms = [pm_grouped.get_group(t).drop(columns='time_bucket') if t in pm_grouped.groups else pd.DataFrame(columns=pm_cols, index=[t]) for t in full_index]

    # --- 1. TTC based buffer calculation ---

    def STA(self, seconds_interval): # Basic Spatio-Temporal Area of CCTV coverage area
        spatio_temporal_area = (self.length * self.width) * seconds_interval
        return spatio_temporal_area

    def TTC(self, data, trajec_id, type_code):

        D = data["new_distance"][0]
        #print(D)
        v = data["speed"][0]
        a = data["acceleration"][0]
        type_code = type_code

        if v == 0:
            ttc = float("inf")
        elif a == 0:
            ttc = D / v if v != 0 else float("inf")
        else:
            discriminant = ((2*a)*D) + v**2
            ttc = (-v + np.sqrt(discriminant)) / a if discriminant >= 0 else float("inf")

        #real_distance = data["speed"].iloc[0] * ttc if ttc != float("inf") else float("inf")
        ttc = 0 if ttc == -0.0 else ttc

        dic = {}
        dic["id"] = [int(trajec_id)]
        dic["obj_cd"] = [type_code]
        dic["new_distance"] = [D]
        dic["velocity"] = [v]
        dic["acceleration"] = [a]
        dic["TTC"] = [ttc]

        return ttc, dic


    def buffer_area(self, ttc, object_length, object_width): # Area which is occupied by vehicles or pedestrian

        width = object_width
        length = object_length

        v = width * length
        if ttc == float("inf"):
            total_v = v
        elif ttc < 0.1:
            total_v = v
        else:
            total_v = ((1/ttc) * v) + v

        return total_v


    def calculates(self, objects, length, width):

        traj_id = objects["traj_id"].unique()
        result = []

        # 카테고리 집합 정리
        PASSENGER = {"M0301", "M0302", "M0309"}                  # 승용/SUV/기타
        AMBULANCE_VAN = {"M0307", "M0308"}                       # 구급차/밴
        HEAVY = {"M0303", "M0304", "M0305", "M0306"}             # 트럭/버스/중장비/소방 등

        for tid in traj_id:
            df = objects.loc[objects["traj_id"] == tid]
            df.reset_index(drop=True, inplace=True)

            type_code = df["obj_cd"][0]
            if type_code == "M0101": # 보행자
                length, width = 0.417 + 0.08,  0.233 + 0.08
                ttc = self.TTC(df, tid, type_code)   
                total_area = self.buffer_area(ttc[0], length, width)         
            elif type_code == "M0201": # M0201: motorcycle, M0202: bicycle, M0203: autoelectric kickboard
                length, width = 1.2 + 0.66, 0.6 + 0.66
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)
            elif type_code == "M0202":
                length, width = 2.3 + 1.0, 0.8 + 1.0
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)
            elif type_code == "M0203":
                length, width = 1.9 + 0.8, 0.7 + 0.8
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)
            elif type_code == "M0206": # PM 기타
                length, width = 1.2 + 0.66, 0.6 + 0.66
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)
            elif type_code in PASSENGER: # 승용차, SUV, 자동차 기타
                length, width = 4.7 + 1.0, 1.7 + 1.0 # 일반 승용차 기준
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)
            elif type_code in AMBULANCE_VAN: # 구급차, 밴
                length, width = 6.19 + 1.0, 2.03 + 1.0 # 중형(15인승) 구급차 기준
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)                
            elif type_code in HEAVY: # 트럭, 버스, 중장비, 소방차
                length, width = 8.0 + 1.0, 2.5 + 1.0 # 중형 소방 펌프차 기준
                ttc = self.TTC(df, tid, type_code)
                total_area = self.buffer_area(ttc[0], length, width)                
            else:
                continue

            result.append({"id":df["traj_id"].values[0], "type":df["obj_cd"].values[0], "geometry":df["geometry"].values[0], "buffer_area":total_area})

        df = pd.DataFrame(result)

        return df

    # --- 2. Count ped-ped safety ---

    def is_na(self, df):
        """ 데이터프레임이 NaN 값으로만 구성되어 있는지 확인해서 True or False로 반환 """
        return df.empty or df.isna().all().all()

    def count_danger(self, df, personal_border = 1.2): # intimate space: 0.45m, personal space: 1.2m, social space: 3.6m

        forward = []
        backward = []
        cross_a_line = []
        for i, d in enumerate(df["moving_direction"]):
            point = df["geometry"].iloc[i]
            if d == 0:
                forward.append([point.y, point.x])  # (latitude, longitude)
            else:
                backward.append([point.y, point.x])


        for f in forward:
            for b in backward:
                dist = geopy.distance.geodesic(f, b).m
                if dist <= personal_border:
                    cross_a_line.append(1)
                else:
                    continue
        return forward, backward, cross_a_line


    def get_ped_ped_safety(self):
        ped_safety_count = []

        for df in tqdm(self.pedestrians, total=len(self.pedestrians), desc='iterate ped_ped collision'):
          try:
            if not self.is_na(df):
                #print("not empty")
                count = self.count_danger(df)
                ped_safety_count.append({"forward":len(count[0]), "backward":len(count[1]), "pp_colisions":len(count[2])})
            else:
                #print("empty")
                ped_safety_count.append({"forward":0, "backward":0, "pp_colisions":0})
          except Exception as e:
            print(f"[Error] ped_ped_safety at {df.index}: {e}")
            ped_safety_count.append({
                "forward": 0,
                "backward": 0,
                "pp_colisions": 0
            })


        ped_safety_count_ = pd.DataFrame(ped_safety_count)
        time_ = pd.DataFrame({"time": self.times})
        final_df = pd.concat([time_, ped_safety_count_], axis = 1)

        return final_df

    # --- 3. Count ped-veh safety & calculate Road Congestion ---

    def calculate_buffer_geometry(self, df):
        # GeoDataFrame
        geo_pd = gpd.GeoDataFrame(df, geometry='geometry', crs = "EPSG:4326")
        geo_pd = geo_pd.to_crs("EPSG:5179")  # Korea 2000 / Unified CS

        # transfer buffer area into radius
        geo_pd['buffer_radius'] = geo_pd['buffer_area'].apply(lambda x: math.sqrt(x / math.pi))

        # buffer geometry
        geo_pd['buffered_geometry'] = geo_pd['geometry'].buffer(geo_pd['buffer_radius'])

        # setting geometry
        geo_pd.set_geometry('buffered_geometry', inplace=True)

        # create spatial index
        geo_pd.sindex
        return geo_pd


    def get_ped_veh_safety(self):
      results = []
      #print(f"ped : {len(self.pedestrians)}, veh : {len(self.vehicles)}, pm : {len(self.pms)}")
      for p, v, pm, t in tqdm(zip(self.pedestrians, self.vehicles, self.pms, self.times), total=len(self.pedestrians), desc='iterate all buffers'):

          # PSTA, VSTA, PMSTA calculation
          Psta = self.calculates(p, None, None) if not self.is_na(p) else pd.DataFrame()
          Vsta = self.calculates(v, None, None) if not self.is_na(v) else pd.DataFrame()
          PMsta = self.calculates(pm, None, None) if not self.is_na(pm) else pd.DataFrame()

          # STA = full road(polygon) area
          sta = self.road_sta

          # buffer area sum
          psta_area = Psta['buffer_area'].sum() if not Psta.empty else 0
          vsta_area = Vsta['buffer_area'].sum() if not Vsta.empty else 0
          pmsta_area = PMsta['buffer_area'].sum() if not PMsta.empty else 0

          rc_area = psta_area + vsta_area + pmsta_area

          # congestions calculation
          road_congestion = rc_area / sta if sta > 0 else 0
          pm_congestion = pmsta_area / (sta - (psta_area + vsta_area)) if (sta - (psta_area + vsta_area)) > 0 else 0

          # count collisions
          ped_veh_collision = 0
          ped_pm_collision = 0

          if not Psta.empty:
              gdf_ped = self.calculate_buffer_geometry(Psta)
              
              if not Vsta.empty:
                  gdf_veh = self.calculate_buffer_geometry(Vsta)
                  inter_veh = gpd.sjoin(gdf_ped, gdf_veh, how="inner", predicate='intersects')
                  ped_veh_collision = inter_veh.shape[0]

              if not PMsta.empty:
                  gdf_pm = self.calculate_buffer_geometry(PMsta)
                  inter_pm = gpd.sjoin(gdf_ped, gdf_pm, how="inner", predicate='intersects')
                  ped_pm_collision = inter_pm.shape[0]



          ped_veh_pm_collision = ped_veh_collision + ped_pm_collision
          sta_pv = sta-(psta_area+vsta_area)
          if sta_pv <= 0:
            sta_pv = pmsta_area

          #print(f"pmsta : {pmsta_area}")
          results.append({
              "time": t,
              "Road_congestion": min(road_congestion, 1),
              "PM_congestion": min(pm_congestion, 1),
              "ped_veh_collision": ped_veh_collision,
              "ped_pm_collision": ped_pm_collision,
              "ped_veh_pm_collision": ped_veh_pm_collision,
              "Psta": psta_area,
              "Vsta": vsta_area,
              "PMsta": pmsta_area,
              "RCarea": rc_area,
              "STA-PV": sta_pv
          })

      return pd.DataFrame(results)


    def get_full_safety(self, interval):

        self.separate_time_optimized(interval)
        #self.separate_time_optimized_inclusive(interval)

        ped_ped = self.get_ped_ped_safety()
        ped_veh = self.get_ped_veh_safety()
        ped_ped = ped_ped.rename(columns={"pp_colisions": "ped_ped_collision"})
        #print(ped_ped.columns)
        #print(ped_veh.columns)
        # ped_ped가 비어 있거나 컬럼이 없을 경우, 기본값 생성
        if ped_ped.empty or "ped_ped_collision" not in ped_ped.columns:
            print("[Info] ped_ped is empty or missing 'ped_ped_collision'. Filling with zeros.")
            
            # ped_veh에 있는 time 기준으로 더미 DataFrame 생성
            ped_ped = pd.DataFrame({
                "time": ped_veh["time"],
                "ped_ped_collision": 0
            })
        full_df = pd.merge(ped_veh, ped_ped[["time", "ped_ped_collision"]], on="time", how="left")
        return full_df


class Get_Congestion():
  def __init__(self, df, road_direction, road_sta, interval):
    self.df = df
    self.road_direction = road_direction
    self.road_sta = road_sta
    self.interval = interval

    self.gs = get_Safety(self.df, self.road_direction, self.road_sta)

  def trapezoidal_rule(self, y, x):
    return np.trapezoid(y, x)


  # calculate congestions by time range you want. set time interval by seconds (e.g. 1min = 60)
  def integral_function(self, df, road_sta, time_interval):
    hourly_integrals = {}
    hourly_RC_ratio = {}
    hourly_PM_ratio = {}

    time_seconds = list(range(len(df)))
    time_range = math.ceil(len(time_seconds)/time_interval)

    hour_sta = road_sta * time_interval

    for t in range(time_range):
      start_idx = t * time_interval
      end_idx = min((t + 1) * time_interval, len(df))

      # extract sec data
      times = np.array(time_seconds[start_idx:end_idx])
      RC_values = np.array(df['RCarea'].values[start_idx:end_idx])
      pm_values = np.array(df['PMsta'].values[start_idx:end_idx])
      pmsta_values = np.array(df['STA-PV'].values[start_idx:end_idx])

      integral_rc = self.trapezoidal_rule(RC_values, times)
      hourly_integrals[df['time'].iloc[start_idx]] = integral_rc

      integral_pm = self.trapezoidal_rule(pm_values, times)
      hourly_integrals[df['time'].iloc[start_idx]] = integral_pm

      integral_pmsta = self.trapezoidal_rule(pmsta_values, times)
      hourly_integrals[df['time'].iloc[start_idx]] = integral_pmsta

      #rc_ratio = round(integral_rc/hour_sta, 4)
      rc_ratio = round(integral_rc / hour_sta, 4) if hour_sta and not np.isnan(hour_sta) else 0
      #pm_ratio = round(integral_pm/integral_pmsta, 4)
      pm_ratio = round(integral_pm / integral_pmsta, 4) if integral_pmsta and not np.isnan(integral_pmsta) else 0


      hourly_RC_ratio[df['time'].iloc[start_idx]] = float(rc_ratio) if rc_ratio <= 1 else 1
      hourly_PM_ratio[df['time'].iloc[start_idx]] = float(pm_ratio) if rc_ratio <= 1 else 1

    return hourly_integrals, hourly_RC_ratio, hourly_PM_ratio


  def Congestion_adjust(self, congestion, pp_safety, pv_safety, weight):

      safety = max([pp_safety, pv_safety])
      adj_con = float(congestion * np.exp(weight * safety))
      adj_con = round(adj_con, 4)

      if adj_con > 1:
          adj_con = 1

      return adj_con

  def safety_median(self, df, time_interval):
      ped_ped = {} # ped to ped collision
      ped_veh = {} # ped to vehi & ped to pm collision

      if "ped_ped_collision" not in df.columns:
          df["ped_ped_collision"] = 0
      if "ped_veh_pm_collision" not in df.columns:
          df["ped_veh_pm_collision"] = 0

      time_seconds = list(range(len(df)))
      time_range = math.ceil(len(time_seconds)/time_interval)

      for t in range(time_range):
          start_idx = t * time_interval
          end_idx = min((t + 1) * time_interval, len(df))

          times = df['time'].iloc[start_idx]

          pp_values = df['ped_ped_collision'].values[start_idx:end_idx]
          pv_values = df['ped_veh_pm_collision'].values[start_idx:end_idx]

          ped_ped[times] = np.max(pp_values)
          ped_veh[times] = np.max(pv_values)

      return ped_ped, ped_veh

  def get_full_congestion(self, weight=0.01):
      # calculate road and pm congestion by 1 sec
      result = self.gs.get_full_safety(1)

      if len(result) < self.interval:
        print(f"[Warning] Length of Data {len(result)} sec < time_interval {self.interval} sec, automatically adjusts interval into {len(result)}.")
        self.interval = len(result)

      integral_ = self.integral_function(result, self.road_sta, self.interval)
      rc_integrated = pd.DataFrame([integral_[1]], index=[self.road_direction]).transpose().reset_index()
      pm_integrated = pd.DataFrame([integral_[2]], index=[self.road_direction]).transpose().reset_index()

      rc_integrated.columns = ['hour', 'RC_ratio_integrated']
      pm_integrated.columns = ['hour', 'PM_congestion_integrated']

      merged = rc_integrated.merge(pm_integrated, on='hour', how='outer')

      # adjust road congestion by collisions
      pp_dict, pv_dict = self.safety_median(result, time_interval=self.interval)
      safety_df = pd.DataFrame({
          "hour": list(pp_dict.keys()),
          "ped_ped_max": list(pp_dict.values()),
          "ped_veh_max": list(pv_dict.values())
      })
      #print(safety_df)
      merged['hour'] = pd.to_datetime(merged['hour'])
      safety_df['hour'] = pd.to_datetime(safety_df['hour'])
      merged = merged.merge(safety_df, on="hour", how="left")

      # calcul pedestrian congestion
      merged["pedestrian_congestion"] = merged.apply(
          lambda row: self.Congestion_adjust(
              congestion=row["RC_ratio_integrated"],
              pp_safety=row["ped_ped_max"],
              pv_safety=row["ped_veh_max"],
              weight=weight
          ), axis=1
      )

      # extract columns which are needed
      final_df = merged[["hour", "RC_ratio_integrated", "PM_congestion_integrated", "pedestrian_congestion"]]
      final_df = final_df.rename(columns={"hour": "time", "RC_ratio_integrated":"Road_Congestion", "PM_congestion_integrated":"PM_Congestion", "pedestrian_congestion":"Pedestrian_Congestion"})

      return final_df

class Processing_congestions():
  #def __init__(self, df, road_df, interval, ian_road_info):
  def __init__(self, df, interval, ian_road_info):
    self.df = df
    #self.road_df = road_df
    self.interval = interval
    self.ian_road_info = ian_road_info

  def direction(self, polygon):
    minx, miny, maxx, maxy = polygon.bounds
    height = maxy - miny
    width = maxx - minx
    if height > width:
      return 0 # road height > road width
    else:
      return 1 # road width > road height

  def level(self, x):
    if x <= 0.2:
      return 0
    elif x <= 0.4:
      return 1
    elif x <= 0.6:
      return 2
    elif x <= 0.8:
      return 3
    else:
      return 4

  def calcul_level(self, df, column):
      """
      lv. 0 excellent = 0 ~ 0.2
      lv. 1 good = 0.2 ~ 0.4
      lv. 2 normal = 0.4 ~ 0.6
      lv. 3 little crowded = 0.6 ~ 0.8
      lv. 4 very crowded = 0.8 ~
      """
      df["congestion_level"] = df[column].apply(self.level)
      return df

  def call(self):

    cctv_id = self.df["snr_id"].unique()
    # ccvt_id_sub = cctv_id[:3] # for tests
    results = pd.DataFrame()

    #self.ian_road_info["road_area"] = self.ian_road_info["geometry"].apply(lambda x: x.area)
    self.ian_road_info = self.ian_road_info.copy()
    self.ian_road_info["road_direction"] = self.ian_road_info["geometry"].apply(lambda x: self.direction(x))

    for id in cctv_id:
      print(f"start CCTV {id}")
      df_sub = self.df.loc[self.df["snr_id"] == id].copy()
      road_df_sub = self.ian_road_info.loc[self.ian_road_info["CCTV_ID"] == id].copy()

      # remove NaN coord
      df_sub = df_sub.dropna(subset=["geometry"])
      if df_sub.empty:
          print(f"  → skipped {id} due to empty or NaN coordinates.")
          continue
      if road_df_sub.empty:
          print(f"  → skipped {id} because road data doesn't exist.")
          continue

      ped = df_sub.loc[df_sub["obj_cd"]=="M0101"]
      veh = df_sub.loc[df_sub["obj_cd"].isin(["M0301", "M0302", "M0303", "M0304", "M0305", "M0306", "M0307", "M0308", "M0309"])]
      pm = df_sub.loc[df_sub["obj_cd"].isin(["M0201", "M0202", "M0203", "M0204", "M0205", "M0206"])]
      print(f"ped count : {len(ped)}, veh count : {len(veh)}, pm count : {len(pm)}")
      road_stas=road_df_sub["area"].values
      gc = Get_Congestion(
          df=df_sub,
          road_direction=road_df_sub["road_direction"].values[0],
          road_sta=sum(road_stas),
          interval=self.interval
      )
      result = gc.get_full_congestion()

      # add CCTV ID(snr_id)
      result_df = result.copy()
      result_df["CCTV_ID"] = id

      results = pd.concat([results, result_df], axis=0)
      print(f"  → finished {id}\n")

    if results.empty or "time" not in results.columns:
        logging.warning("No data or missing 'time' column. Skipping congestion processing.")
        return None, None, None

    results["time"] = pd.to_datetime(results["time"])
    results.sort_values(by="time", inplace=True)

    # add congestion level
    road_cong = results[["CCTV_ID", "time", "Road_Congestion"]].copy()
    road_cong = self.calcul_level(road_cong, "Road_Congestion")
    road_cong = road_cong.reset_index(drop=True)
    road_cong_1 = pd.merge(road_cong, self.ian_road_info[["CCTV_ID", "ufid"]], on='CCTV_ID', how='inner')

    ped_cong = results[["CCTV_ID", "time", "Pedestrian_Congestion"]].copy()
    ped_cong = self.calcul_level(ped_cong, "Pedestrian_Congestion")
    ped_cong = ped_cong.reset_index(drop=True)
    ped_cong_1 = pd.merge(ped_cong, self.ian_road_info[["CCTV_ID", "ufid"]], on='CCTV_ID', how='inner')

    pm_cong = results[["CCTV_ID", "time", "PM_Congestion"]].copy()
    pm_cong = self.calcul_level(pm_cong, "PM_Congestion")
    pm_cong = pm_cong.reset_index(drop=True)
    pm_cong_1 = pd.merge(pm_cong, self.ian_road_info[["CCTV_ID", "ufid"]], on='CCTV_ID', how='inner')

    return road_cong_1, ped_cong_1, pm_cong_1
