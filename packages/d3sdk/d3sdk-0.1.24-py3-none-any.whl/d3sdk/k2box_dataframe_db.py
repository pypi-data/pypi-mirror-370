import logging
import re
from datetime import datetime
from typing import Union, List

from k2magic.dataframe_db_exception import DataFrameDBException
from k2magic.dialect import k2a_requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import URL, make_url, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from d3sdk.model.business_model_define import InstanceMeasurement


class K2boxDataFrameDB:
    """
    基于K2DataFrameDB，提供根据业务信息如报警组访问K2Assets Repo数据的能力
    :param k2a_url: k2a地址
    :param debug: 调试模式可输出更多日志信息
    """

    def __init__(self, k2a_url: Union[str, URL], debug: bool = False,):
        self.debug = debug

        # 日志配置（与父类初始化可能存在重复，但问题不大）
        self.logger = logging.getLogger(self.__class__.__name__)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        # pg连接配置
        pg_url_obj = self._disclose_pg_url(k2a_url)
        self.engine = create_engine(pg_url_obj, echo=debug)
        # self.k2DataFrameDB = K2DataFrameDB(k2a_url, schema=schema, db_port=db_port, debug=debug, rest=rest)

    def getInstanceMeasurements(self, devices: list = None, schemas: list = None) -> List[InstanceMeasurement]:
        """
        -- 查看量测实例列表
        """
        device_list = ",".join(f"'{device}'" for device in devices)
        schema_list = ",".join(f"'{schema}'" for schema in schemas)

        # 构建 SQL 查询字符串
        sql = f"""
        SELECT 
            M.*,
            C.c_name_cn schema_column_name,
            C.c_unit unit,
            C.c_lower_bound lower_bound,
            C.c_upper_bound upper_bound,
            C.c_type TYPE 
        FROM
            (
                SELECT 
                    M.c_device_id AS device_code,
                    M.c_schema SCHEMA,
                    M.c_repo repo_code,
                    r.c_label repo_name,
                    UNNEST ( string_to_array( M.c_columns, ',' ) ) AS schema_column,
                    UNNEST ( string_to_array( M.c_data_columns, ',' ) ) AS repo_column 
                FROM
                    t_schema_mapping M LEFT JOIN t_repo r ON r.c_name = M.c_repo 
                WHERE 1 = 1
                    AND M.c_schema IN ({schema_list})
                    AND ( M.c_device_id IN ({device_list}) OR M.c_device_id = '*' ) 
            )
            M LEFT JOIN t_column C ON M.SCHEMA = C.c_schema 
            AND M.schema_column = C.c_name_en
        """

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                records = []
                for row in result.fetchall():
                    record = InstanceMeasurement(
                        deviceCode=row[0],
                        schema=row[1],
                        repoCode=row[2],
                        repoName=row[3],
                        schemaColumn=row[4],
                        repoColumn=row[5],
                        schemaColumnName=row[6],
                        unit=row[7],
                        lowerBound=row[8],
                        upperBound=row[9],
                        type=row[10],
                        measurement=None,
                        measurementGroupCode=None,
                        measurementGroupName=None,
                        deviceTypeCode=None,
                        measurementName=None
                    )
                    records.append(record)
                return records
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                "Failed to query records due to a database error.",
                original_exception=e
            )

    def _disclose_pg_url(self, k2a_url: Union[str, URL]) -> URL:
        """
        访问k2a的env接口，获取pg数据库的连接信息
        """
        k2a_url_obj = make_url(k2a_url)
        protocol = k2a_url_obj.query.get('protocol', 'https')  # k2assets http protocol
        auth = HTTPBasicAuth(k2a_url_obj.username, k2a_url_obj.password)
        api_url = f"{protocol}://{k2a_url_obj.host}:{k2a_url_obj.port}/api/env/k2box.postgresql"
        resp = k2a_requests.get(api_url, auth=auth)

        envs = resp['body']['values']
        pg_host = k2a_url_obj.host
        pg_port = re.search(r':(\d+)/', envs['k2box.postgresql.url']).group(1)   # 从 jdbc:postgresql://k2a-repos:5432/repos?xxx 中提取端口号
        pg_password = envs['k2box.postgresql.password']
        pg_user = envs['k2box.postgresql.username']
        pg_url_obj = make_url(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/k2box_server')
        self.logger.debug(f'postgres url: {pg_url_obj}')
        return pg_url_obj