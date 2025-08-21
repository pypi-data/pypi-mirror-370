# ewha_trajdb_manager.py

"""
Import trajectories to process CCTV DataFrames

Code writer : Jiyoon Lee
E-mail : jiyoon821@ewha.ac.kr

Last update : 2025. 08. 21.

"""
import sys
import logging
from typing import Dict
from tqdm import tqdm

# 서드파티 라이브러리
import pandas as pd
import geopandas as gpd
import psycopg2
from psycopg2.extras import execute_values
from shapely import wkb
import movingpandas as mpd

class DBManager_dynamicP:
    """
    A manager for connecting to a PostgreSQL database, importing data,
    processing trajectory attributes, and grouping data by CCTV ID.
    """

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str, schema: str):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.schema = schema

        try:
            self.conn = psycopg2.connect(
                host = self.host,
                port = self.port,
                dbname = self.dbname,
                user = self.user,
                password = self.password
            )
            self.cur = self.conn.cursor()
            logging.info("Database connection established successfully.")
            schema_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.schema}';"
            self.cur.execute(schema_query)
            rows = self.cur.fetchall()
            logging.info(f"Tables in {self.schema} schema: {rows}")

        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            raise

    def close(self):
        """Closes the database connection safely."""
        if hasattr(self, "cur") and self.cur:
            self.cur.close()
        if hasattr(self, "conn") and self.conn:
            self.conn.close()
        logging.info("Database connection closed.")

    def upload_dataframe_to_postgres(self, df, table_name, schema, mode='insert', conflict_columns=None, update_columns=None):
        columns = ', '.join(df.columns)
        values = [tuple(x) for x in df.to_numpy()]
        placeholders = '%s'

        base_query = f"INSERT INTO {schema}.{table_name} ({columns}) VALUES {placeholders}"

        # Mode handling
        if mode == 'replace':
            if not conflict_columns or not update_columns:
                raise ValueError("For 'replace' mode, conflict_columns and update_columns must be provided.")
            conflict_cols = ', '.join(conflict_columns)
            update_set = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            base_query += f" ON CONFLICT ({conflict_cols}) DO UPDATE SET {update_set}"
        elif mode == 'insert' or mode == 'append':
            pass  # 기본 insert 동작
        else:
            raise ValueError("Mode must be one of ['insert', 'append', 'replace']")

        try:
            with self.conn.cursor() as cur:
                execute_values(cur, base_query, values)
                self.conn.commit()
                print(f"✅ {mode.upper()} success: {len(df)} rows into {schema}.{table_name}")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Failed to {mode} data: {e}")

    def clear_table(self, schema, table_name):
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"DELETE FROM {schema}.{table_name};")
                self.conn.commit()
                print(f"✅ All rows deleted from {schema}.{table_name}")
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Failed to delete rows: {e}")

    def import_data(self, table: str, schema: str, time_column=None, start_time=None, end_time=None) -> pd.DataFrame:

        try:
            where_clause = ""
            if time_column and start_time and end_time:
                where_clause = f"WHERE {time_column} BETWEEN %s AND %s ORDER BY {time_column} ASC"
                params = (start_time, end_time)
            else:
                params = ()
            
            count_query = f"SELECT COUNT(*) FROM {schema}.{table} {where_clause.split('ORDER')[0] if 'WHERE' in where_clause else ''};"
            self.cur.execute(count_query, params if where_clause else None)
            total_rows = self.cur.fetchone()[0]
            logging.info(f"Fetching {total_rows} rows from {table}.")

            named_cursor = self.conn.cursor(name=f"server_cursor_{table}")
            named_cursor.itersize = 1000
            table_query = f"SELECT * FROM {schema}.{table} {where_clause};"
            named_cursor.execute(table_query, params)

            first_row = next(named_cursor)
            col_names = [desc[0] for desc in named_cursor.description]
            rows = [first_row]

            for _, row in enumerate(tqdm(named_cursor, total=total_rows, desc="Fetching rows", ncols=100,
                                        file=sys.stdout, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed} elapsed]")):
                rows.append(row)

            df = pd.DataFrame(rows, columns=col_names)
            named_cursor.close()
            return df

        except Exception as e:
            logging.error(f"Error during data import: {e}")
            raise


    def add_attribute(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        """
        Adds trajectory attributes (acceleration, speed, etc.) to the data.

        Args:
            df (pd.DataFrame): DataFrame containing at least lon, lat, and dtct_dt columns.

        Returns:
            gpd.GeoDataFrame: GeoDataFrame with trajectory attributes.
        """
        df["geometry"] = df["geom"].apply(lambda x: wkb.loads(bytes.fromhex(x)))
        gdf = gpd.GeoDataFrame(df, geometry = "geometry")
        gdf["dtct_dt"] = pd.to_datetime(gdf["dtct_dt"]).apply(lambda dt: dt.replace(microsecond=0))
        gdf["dtct_dt"] = gdf["dtct_dt"].dt.tz_localize(None)
        gdf = gdf.set_index(pd.DatetimeIndex(gdf["dtct_dt"]))
        gdf = gdf.set_crs("epsg:4326")

        traj_collection = mpd.TrajectoryCollection(gdf, "obj_id")
        traj_collection.add_acceleration()
        traj_collection.add_angular_difference()
        traj_collection.add_direction()
        traj_collection.add_speed()
        traj_collection.add_distance()
        traj_collection.add_traj_id(overwrite=False)

        return traj_collection.to_point_gdf()

    def dataframe_groups(self, table_name: str, schema: str, time_column=None, start_time=None, end_time=None) -> Dict[str, gpd.GeoDataFrame]:
        """
        Imports data and groups it by CCTV ID after processing trajectory attributes.

        Args:
            table_name (str): Table name to import and process.

        Returns:
            Dict[str, gpd.GeoDataFrame]: Dictionary mapping CCTV IDs to processed GeoDataFrames.
        """        
        df = self.import_data(table_name, schema, time_column, start_time, end_time)
        self.close()

        df_group = {}
        cctv_ids = df["snr_id"].unique()

        logging.info(f"Processing {len(cctv_ids)} CCTV IDs.")

        for cctv_id in tqdm(cctv_ids, total = len(cctv_ids),
                            desc = "CCTV Preprocessing",
                            ncols = 100,
                            bar_format = "{l_bar}{bar} | {n_fmt}/{total_fmt} [{elapsed} elapsed]"):
            #df_by_cctv = self.add_attribute(df.loc[df["snr_id"] == cctv_id])
            #df_group[cctv_id] = df_by_cctv
            try:
                df_cctv = df.loc[df["snr_id"] == cctv_id].copy()

                if df_cctv.empty:
                    logging.warning(f"[Skip] CCTV {cctv_id}: no data.")
                    continue

                df_by_cctv = self.add_attribute(df_cctv)

                if df_by_cctv.empty:
                    logging.warning(f"[Skip] CCTV {cctv_id}: no result after attribute extraction.")
                    continue

                df_group[cctv_id] = df_by_cctv

            except Exception as e:
                logging.warning(f"[Error] CCTV {cctv_id}: {e}")
                continue            

        logging.info("Data processing completed. Returning CCTV data groups.")
        logging.info("Output data format : dictionary. e.g. {cctv id : dataframe}")
        
        return df_group
