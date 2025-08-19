import logging
import re
import pdb
from datetime import datetime
from typing import Union, List

from k2magic.dataframe_db_exception import DataFrameDBException
from k2magic.dialect import k2a_requests
from requests.auth import HTTPBasicAuth
from sqlalchemy import URL, make_url, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from d3sdk.model.device_failure_record import DeviceFailureRecord, DiagnosticModule, DeviceSymptom, DeviceFailure, AlarmType
from d3sdk.model.alarm_group_detail import AlarmDetail, Suggestion, Cause
from d3sdk.model.business_model_define import DeviceMeasurementGroup, InstanceMeasurement, AlarmInstancePointsConfig, AlarmInstancePointsStatistic
from d3sdk.k2box_dataframe_db import K2boxDataFrameDB
from d3sdk.util.business_util import get_between


class D3DataFrameDB:
    """
    基于K2DataFrameDB，提供根据业务信息如报警组访问K2Assets Repo数据的能力
    :param k2a_url: k2a地址
    :param debug: 调试模式可输出更多日志信息
    """
    def __init__(self, k2a_url: Union[str, URL], debug: bool = False,):
        self.debug = debug
        self.k2a_url = k2a_url

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

    def getDeviceFailureRecords(self, 
                                earliestAlarmTimeBegin: Union[str, int, datetime] = None, earliestAlarmTimeEnd: Union[str, int, datetime] = None,
                                latestAlarmTimeBegin: Union[str, int, datetime] = None, latestAlarmTimeEnd: Union[str, int, datetime] = None,
                                alarmTimeBegin: Union[str, int, datetime] = None, alarmTimeEnd: Union[str, int, datetime] = None,
                                devices: list = None, 
                                alarmTypes: list = None, 
                                alarmCodes: list = None,
                                description: str = None,
                                diagnosticModuleTypeNames: list = None,
                                alarmLevels: list = None,
                                alarmStatus: list = None,
                                limit: int = 100, desc: bool = None) -> List[DeviceFailureRecord]:
        """
        -- 1.1 报警组列表查询（包括报警信息、相关诊断模块列表）
        -- 查询获取报警组关联的报警类型、报警描述、报警数、严重程度、报警位置等业务信息
        -- 根据时间范围和设备信息、报警位置等信息查询获取符合要求的报警组编号
        -- 查询参数可选为：机组编码、诊断模块实例名称、报警组状态、报警等级、报警类型、最早报警时间范围、最新报警时间范围、报警描述、报警等级、报警状态、报警编码
        """
        # 将时间参数转换为 datetime 对象
        if isinstance(earliestAlarmTimeBegin, str):
            earliestAlarmTimeBegin = datetime.strptime(earliestAlarmTimeBegin, "%Y-%m-%d %H:%M:%S")
        if isinstance(earliestAlarmTimeEnd, str):
            earliestAlarmTimeEnd = datetime.strptime(earliestAlarmTimeEnd, "%Y-%m-%d %H:%M:%S")
        if isinstance(latestAlarmTimeBegin, str):
            latestAlarmTimeBegin = datetime.strptime(latestAlarmTimeBegin, "%Y-%m-%d %H:%M:%S")
        if isinstance(latestAlarmTimeEnd, str):
            latestAlarmTimeEnd = datetime.strptime(latestAlarmTimeEnd, "%Y-%m-%d %H:%M:%S")
        if isinstance(alarmTimeBegin, str):
            alarmTimeBegin = datetime.strptime(alarmTimeBegin, "%Y-%m-%d %H:%M:%S")
        if isinstance(alarmTimeEnd, str):
            alarmTimeEnd = datetime.strptime(alarmTimeEnd, "%Y-%m-%d %H:%M:%S")

        # 构建 SQL 查询字符串
        sql = """
        SELECT
            ag.dfem_code,	-- 报警组编码（唯一标识）
            ag.display_name, -- 报警组名称
            CASE 
                WHEN ag.dfem_bjlx ILIKE '%symptom%' THEN 'symptom'
                WHEN ag.dfem_bjlx ILIKE '%failure%' THEN 'failure'
                ELSE ag.dfem_bjlx
            END as dfem_bjlx,	-- 报警类型
            ag.dfem_sxmsbh,	-- 报警编码
            ag.description,	--报警描述
            ag.dfem_bjs,	-- 报警数
            ag.dfem_bjdj,	--报警等级
            ag.dfem_zt,	-- 报警状态
            ag.dfem_gjz,	--关键字
            to_char(ag.dfem_zzbjsj, 'YYYY-MM-DD HH24:MI:SS') dfem_zzbjsj, -- 最早报警时间
            to_char(ag.dfem_zxbjsj, 'YYYY-MM-DD HH24:MI:SS') dfem_zxbjsj,	-- 最新报警时间
            ai.name AS device_code, -- 机组编码
            ai.display_name AS device_name, -- 机组名称
            w.fm_id AS fm_id, -- 诊断模块ID
            w.fm_code fm_code, -- 诊断模块Code
            w.fm_name AS fm_name, -- 诊断模块名称
            w.fm_parent_code fm_parent_code,-- 诊断模块父级Code
            fmt.id fmt_id,-- 诊断模块类型ID
            fmt.dfem_code fmt_code, -- 诊断模块类型Code
            fmt.display_name AS fmt_name, -- 诊断模块类型名称
            fmt.type fmt_type -- 诊断模块类型Type 0电站 1机组 2部件部套
        FROM
            dfem_alarm_group ag
            LEFT JOIN dfem_sign s ON s.dfem_code = ag.dfem_sxmsbh AND ag.dfem_bjlx ILIKE '%symptom%'
            LEFT JOIN dfem_failure_mode f ON f.dfem_code = ag.dfem_sxmsbh AND ag.dfem_bjlx ILIKE '%failure%'
            LEFT JOIN dfem_rt_fm_sg fs ON fs.entity_type2_id = s.ID AND ag.dfem_bjlx ILIKE '%symptom%'
            LEFT JOIN dfem_rt_fmt_fm ff ON ff.entity_type2_id = f.ID AND ag.dfem_bjlx ILIKE '%failure%'
            LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = COALESCE(ff.entity_type1_id, fs.entity_type1_id)
            LEFT JOIN asset_instances ai ON ai.ID = CAST ( ag.dfem_sbbh AS NUMERIC )
            LEFT JOIN (
                SELECT
                    ai.id AS device_id,
                    fm.id AS fm_id,
                    fm.dfem_gnmkbh AS fm_code,
                    fm.display_name AS fm_name,
                    fm.parent_code AS fm_parent_code,
                    fmt.id AS fmt_id
                FROM asset_instances ai
                LEFT JOIN dfem_rt_ai_fm af ON ai.id = af.entity_type1_id
                LEFT JOIN dfem_functional_module fm ON fm.id = af.entity_type2_id
                LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.id
                LEFT JOIN dfem_functional_module_type fmt ON fmt.id = fmt1.entity_type1_id
            ) w ON w.device_id = ai.ID AND w.fmt_id = fmt.id 
        WHERE 1=1
        """

        # 动态添加时间范围条件
        if earliestAlarmTimeBegin and earliestAlarmTimeEnd:
            sql += f" and ag.dfem_zzbjsj BETWEEN '{earliestAlarmTimeBegin.strftime('%Y-%m-%d %H:%M:%S')}' AND '{earliestAlarmTimeEnd.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        if latestAlarmTimeBegin and latestAlarmTimeEnd:
            sql += f" and ag.dfem_zxbjsj BETWEEN '{latestAlarmTimeBegin.strftime('%Y-%m-%d %H:%M:%S')}' AND '{latestAlarmTimeEnd.strftime('%Y-%m-%d %H:%M:%S')}'"

        if alarmTimeBegin and alarmTimeEnd:
            sql += f" and NOT (ag.dfem_zzbjsj > '{alarmTimeEnd.strftime('%Y-%m-%d %H:%M:%S')}' or ag.dfem_zxbjsj < '{alarmTimeBegin.strftime('%Y-%m-%d %H:%M:%S')}')"

        # 添加机组列表条件
        if devices:
            device_list = ",".join(f"'{device}'" for device in devices)
            sql += f" and ai.name in ({device_list})"

        # 添加诊断模块类型名称列表条件
        if diagnosticModuleTypeNames:
            fmt_names_list = ",".join(f"'{fmtName}'" for fmtName in diagnosticModuleTypeNames)
            sql += f" and fmt.display_name in ({fmt_names_list})"

        # 添加报警类型列表条件
        if alarmTypes:
            alarm_types_list = ",".join(f"'alarm_type_{alarmType}'" for alarmType in alarmTypes)
            sql += f" and ag.dfem_bjlx in ({alarm_types_list})"
        
        # 添加报警编码列表条件
        if alarmCodes:
            alarm_codes_list = ",".join(f"'{alarmCode}'" for alarmCode in alarmCodes)
            sql += f" and ag.dfem_sxmsbh in ({alarm_codes_list})"

        # 添加报警描述条件
        if description:
            sql += f" and (ag.description LIKE CONCAT('%', '{description}', '%') OR ag.display_name LIKE CONCAT('%', '{description}', '%'))"

        # 添加报警等级列表条件
        if alarmLevels:
            alarm_levels_list = ",".join(f"'{alarmLevel}'" for alarmLevel in alarmLevels)
            sql += f" and ag.dfem_bjdj in ({alarm_levels_list})"

        # 添加报警状态列表条件
        if alarmStatus:
            status_list = ",".join(f"'{status}'" for status in alarmStatus)
            sql += f" and ag.dfem_zt in ({status_list})"

        # 添加排序条件
        sql += f" ORDER BY ag.dfem_zxbjsj {'desc' if desc else 'asc'}"

        # 添加 LIMIT 条件
        sql += f" LIMIT {limit}"

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                alarm_map = {}
                for row in result.fetchall():
                    type = row[20]
                    typeName = ''
                    if type == 0:
                        typeName = '电站'
                    elif type == 1:
                        typeName = '机组'
                    elif type == 2:
                        typeName = '部件部套'
                    else:
                        typeName = '未知类型'
                    
                    fm = DiagnosticModule(row[14], row[15], row[18], row[19], typeName)

                    if row[0] not in alarm_map:
                        alarm_map[row[0]] = DeviceFailureRecord(
                            alarmGroupCode=row[0],
                            alarmGroupName=row[1],
                            alarmType=row[2],
                            alarmCode=row[3],
                            description=row[4],
                            alarmNumber=row[5],
                            level=row[6],
                            status=row[7],
                            keywords=row[8],
                            earliestAlarmTime=row[9],
                            latestAlarmTime=row[10],
                            deviceCode=row[11],
                            deviceName=row[12],
                            diagnosticModules=[fm],
                        )
                    else:
                        alarm_map[row[0]].diagnosticModules.append(fm)
                return alarm_map.values()
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )

    def getAlarmDetail(self, alarmGroupCode: str) -> AlarmDetail:
        """
        -- 1.2 根据报警组编号查询获取报警组关联的业务对象实例，如征兆、失效、原因、建议编码等
        """

        sql = f"""
        SELECT 
            ag.dfem_sxmsbh, -- 报警编码
            CASE 
                WHEN ag.dfem_bjlx ILIKE '%symptom%' THEN 'symptom'
                WHEN ag.dfem_bjlx ILIKE '%failure%' THEN 'failure'
                ELSE ag.dfem_bjlx
            END as dfem_bjlx, -- 报警类型
            cause.dfem_sxyybh cause_code, -- 原因编码 （报警:原因 1:n）
            cause.display_name cause_display_name, -- 原因名称
            cause.description cause_description,	-- 原因描述
            step.dfem_csbh step_code, -- 建议编号（原因:建议 1:n）
            step.display_name step_display_name, 	-- 建议名称
            step.description step_description -- 建议描述
        FROM
            dfem_alarm_group ag
            -- 征兆类型报警组
            LEFT JOIN dfem_sign s ON s.dfem_code = ag.dfem_sxmsbh AND ag.dfem_bjlx ILIKE '%symptom%'
            -- 失效类型报警组
            LEFT JOIN dfem_failure_mode f ON f.dfem_code = ag.dfem_sxmsbh AND ag.dfem_bjlx ILIKE '%failure%'
            -- 征兆和原因的关联
            LEFT JOIN dfem_rt_si_fc sf ON sf.entity_type1_id = s.ID AND ag.dfem_bjlx ILIKE '%symptom%'
            -- 失效和原因的关联
            LEFT JOIN dfem_rt_fm_fc ff ON ff.entity_type1_id = f.ID AND ag.dfem_bjlx ILIKE '%failure%'
          -- 原因
            LEFT JOIN dfem_failurecause cause ON cause.ID = sf.entity_type2_id or cause.ID = ff.entity_type2_id
            LEFT JOIN dfem_rt_fc_st fs on fs.entity_type1_id = cause.id
            LEFT JOIN dfem_step step on step.id = fs.entity_type2_id
        WHERE ag.dfem_code = '{alarmGroupCode}'
        ORDER BY ag.dfem_sxmsbh, cause_code, step_code
        """

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                alarmDetail = None
                cause_map = {}
                for row in result.fetchall():
                    alarm_code = row[0]
                    alarm_type = row[1]
                    cause_code = row[2]
                    cause_display_name = row[3]
                    cause_description = row[4]
                    step_code = row[5]  
                    step_display_name = row[6]
                    step_description = row[7]

                    if alarmDetail is None:
                        alarmDetail = AlarmDetail(alarm_code, alarm_type, [])

                    if cause_code not in cause_map:
                        suggestion = Suggestion(step_code, step_display_name, step_description)
                        cause_map[cause_code] = Cause(cause_code, cause_display_name, cause_description, [suggestion])
                    else:
                        cause_map[cause_code].suggestions.append(Suggestion(step_code, step_display_name, step_description))

                alarmDetail.causes = cause_map.values()
                return alarmDetail
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
        
    def getSymptomCauses(self, symptomCode: str) -> List[Cause]:
        """
        -- 查询某个征兆的原因及其建议
        """

        sql = f"""
        SELECT
            cause.dfem_sxyybh cause_code, -- 原因编码 （报警:原因 1:n）
            cause.display_name cause_display_name, -- 原因名称
            cause.description cause_description,	-- 原因描述
            cause.dfem_gjz cause_keywords,
            step.dfem_csbh step_code, -- 建议编号（原因:建议 1:n）
            step.display_name step_display_name, 	-- 建议名称
            step.description step_description, -- 建议描述
            step.dfem_gjz step_keywords
        FROM
            dfem_sign s
            LEFT JOIN dfem_rt_si_fc sf ON sf.entity_type1_id = s.ID 
            LEFT JOIN dfem_failurecause cause ON sf.entity_type2_id = cause.ID
            LEFT JOIN dfem_rt_fc_st fs on fs.entity_type1_id = cause.id
            LEFT JOIN dfem_step step on fs.entity_type2_id = step.id
        WHERE s.dfem_code = '{symptomCode}'
        """

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                causes = {}
                for row in result.fetchall():
                    cause_code = row[0]
                    suggestion_code = row[4]
                    suggestion = Suggestion(suggestion_code, row[5], row[6])

                    if cause_code not in causes:
                        causes[cause_code] = Cause(
                            cause_code,
                            row[1],
                            row[2],
                            [suggestion]
                        )
                    else:
                        causes[cause_code].suggestions.append(suggestion)

                return list(causes.values())
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
        
    
    def getFailureCauses(self, failureCode: str) -> List[Cause]:
        """
        -- 查询某个失效的原因及其建议
        """

        sql = f"""
        SELECT
            cause.dfem_sxyybh cause_code, -- 原因编码 （报警:原因 1:n）
            cause.display_name cause_display_name, -- 原因名称
            cause.description cause_description,	-- 原因描述
            cause.dfem_gjz cause_keywords,
            step.dfem_csbh step_code, -- 建议编号（原因:建议 1:n）
            step.display_name step_display_name, 	-- 建议名称
            step.description step_description, -- 建议描述
            step.dfem_gjz step_keywords
        FROM
            dfem_failure_mode f
            LEFT JOIN dfem_rt_fm_fc ff ON ff.entity_type1_id = f.ID 
            LEFT JOIN dfem_failurecause cause ON ff.entity_type2_id = cause.ID
            LEFT JOIN dfem_rt_fc_st fs on fs.entity_type1_id = cause.id
            LEFT JOIN dfem_step step on fs.entity_type2_id = step.id
        WHERE f.dfem_code = '{failureCode}'
        """

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                causes = {}
                for row in result.fetchall():
                    cause_code = row[0]
                    suggestion_code = row[4]
                    suggestion = Suggestion(suggestion_code, row[5], row[6])

                    if cause_code not in causes:
                        causes[cause_code] = Cause(
                            cause_code,
                            row[1],
                            row[2],
                            [suggestion]
                        )
                    else:
                        causes[cause_code].suggestions.append(suggestion)

                return list(causes.values())
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
        
    def getDeviceMeasurementGroups(self, devices: list = None) -> List[DeviceMeasurementGroup]:
        """
        -- 查看机组的数据分组
        """

        # 构建 SQL 查询字符串
        sql = """
        SELECT
            ai.NAME device_code,
            ai.display_name device_name,
            mg.NAME measurement_group_code,
            aty.NAME device_type_code,
            mg.display_name measurement_group_name,
            concat(aty.NAME, '_', mg.NAME) schema
        FROM
            asset_instances ai
            LEFT JOIN asset_types aty ON ai.asset_type_id = aty.ID 
            LEFT JOIN asset_type_measurement_groups mg ON mg._asset_type_id = aty.ID 
        """
        # 添加机组列表条件
        if devices:
            device_list = ",".join(f"'{device}'" for device in devices)
            sql += f" WHERE ai.name in ({device_list})"
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                records = []
                for row in result.fetchall():
                    record = DeviceMeasurementGroup(
                            deviceCode=row[0],
                            deviceName=row[1],
                            measurementGroupCode=row[2],
                            deviceTypeCode=row[3],
                            measurementGroupName=row[4],
                            schema=row[5]
                        )
                    records.append(record)
                return records
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )

    def getInstanceMeasurements(self, devices: list = None) -> List[InstanceMeasurement]:
        deviceMeasurementGroups = self.getDeviceMeasurementGroups(devices=devices)
        if not deviceMeasurementGroups:
            return []
        k2boxDB = K2boxDataFrameDB(k2a_url=self.k2a_url, debug=self.debug)
        
        devices = list({deviceMeasurementGroup.deviceCode for deviceMeasurementGroup in deviceMeasurementGroups})
        schemas = list({deviceMeasurementGroup.schema for deviceMeasurementGroup in deviceMeasurementGroups})
        instanceMeasurements = k2boxDB.getInstanceMeasurements(devices=devices, schemas=schemas)
        if not deviceMeasurementGroups:
            return []
        schemaDevices = {}
        for deviceMeasurementGroup in deviceMeasurementGroups:
            schema = deviceMeasurementGroup.schema
            if schema not in schemaDevices:
                schemaDevices[schema] = []
            schemaDevices[schema].append(deviceMeasurementGroup.deviceCode)

        wildcardInstanceMeasurements = [
            item for item in instanceMeasurements if item.deviceCode == "*"
        ]
        if wildcardInstanceMeasurements:
            # 按 schema 分组 wildcardInstanceMeasurements
            wildcardSchemaDevices = {}
            for wildcardInstanceMeasurement in wildcardInstanceMeasurements:
                schema = wildcardInstanceMeasurement.schema
                if schema not in wildcardSchemaDevices:
                    wildcardSchemaDevices[schema] = []
                wildcardSchemaDevices[schema].append(wildcardInstanceMeasurement)
            
            # 将 device_code 为 "*" 的转换成实际的 device_code
            for schema, instances in wildcardSchemaDevices.items():
                for device in schemaDevices.get(schema, []):
                    for instanceMeasurement in instances:
                        temp  = InstanceMeasurement(
                            deviceCode=device,
                            schema=instanceMeasurement.schema,
                            repoCode=instanceMeasurement.repoCode,
                            repoName=instanceMeasurement.repoName,
                            schemaColumn=instanceMeasurement.schemaColumn,
                            repoColumn=instanceMeasurement.repoColumn,
                            schemaColumnName=instanceMeasurement.schemaColumnName,
                            unit=instanceMeasurement.unit,
                            lowerBound=instanceMeasurement.lowerBound,
                            upperBound=instanceMeasurement.upperBound,
                            type=instanceMeasurement.type,
                            measurement=None,
                            measurementGroupCode=None,
                            measurementGroupName=None,
                            deviceTypeCode=None,
                            measurementName=None
                        )
                        instanceMeasurements.append(temp)
            # 移除 device_code 为 "*" 的实例测量
            instanceMeasurements = [
                im for im in instanceMeasurements if im.deviceCode() != "*"
        ]
        # 填充 group_code 和 group_name
        for instanceMeasurement in instanceMeasurements:
            for deviceMeasurementGroup in deviceMeasurementGroups:
                if (instanceMeasurement.deviceCode == deviceMeasurementGroup.deviceCode and instanceMeasurement.schema == deviceMeasurementGroup.schema):
                    instanceMeasurement.measurementGroupCode = deviceMeasurementGroup.measurementGroupCode
                    instanceMeasurement.measurementGroupName = deviceMeasurementGroup.measurementGroupName
                    instanceMeasurement.measurement = f"{deviceMeasurementGroup.measurementGroupCode}.{instanceMeasurement.schemaColumn}"
                    instanceMeasurement.measurementName = instanceMeasurement.schemaColumnName
                    instanceMeasurement.deviceTypeCode = deviceMeasurementGroup.deviceTypeCode
                    break
        return instanceMeasurements

    def getInstanceMeasurementsFilter(self, device: str = None, alarms: list = None) -> List[InstanceMeasurement]:
        returnInstanceMeasurements = []
        # 获取机组测诊断依据测点列表
        # 构建 SQL 查询字符串
        sql = f"""
        SELECT 
            C.device_code,
            T.name device_type,
            C.events,
            C.related
        FROM
            dfem_alarm_type_points
            C LEFT JOIN asset_instances ai ON ai.NAME = C.device_code
            LEFT JOIN asset_types T ON ai.asset_type_id = T.ID 
        WHERE
            C.device_code = '{device}' 
        ORDER BY
            C.VERSION ASC
        """
        alarmInstancePointsConfigs = []
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                for row in result.fetchall():
                    record = AlarmInstancePointsConfig(
                            deviceCode=row[0],
                            deviceType=row[1],
                            events=row[2],
                            related=row[3]
                        )
                    alarmInstancePointsConfigs.append(record)
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
        
        if not alarmInstancePointsConfigs:
            return returnInstanceMeasurements
        # 解析出来的测点组
        pointGroupPoints = {}
        alarmCodeSinglePoints = {}
        alarmCodeGroups = {}
        
        for alarmInstancePointsConfig in alarmInstancePointsConfigs:
            eventsStr = alarmInstancePointsConfig.events
            relatedStr = alarmInstancePointsConfig.related
            relatedList = [r.strip() for r in relatedStr.split(',')]
            # eventsStr split by ','
            events = [e.strip() for e in eventsStr.split(',')]
            # 如果events的长度等于1 并且元素以'GP'开头，则认为是一个测点组
            if len(events) == 1 and events[0].startswith('GP'):
                pointGroupCode = events[0]
                if pointGroupCode not in pointGroupPoints:
                    pointGroupPoints[pointGroupCode] = []
                # relatedList过滤出以'!'开头，并截取related.substring(1)，这样的测点是忽略测点
                ignorePoints = [r[1:] for r in relatedList if r.startswith('!')]
                # relatedList过滤出不以'!'开头，并且related中不包括'~'的related，这样的测点是单测点
                singlePoints = [r for r in relatedList if not r.startswith('!') and '~' not in r]
                pointGroupPoints[pointGroupCode].extend(singlePoints)
                # relatedList过滤出不以'!'开头，并且related中包括'~'的related，这样的测点是范围测点
                scopePoints = [r for r in relatedList if '~' in r]
                if scopePoints:
                    for scopePoint in scopePoints:
                        scopePoint = scopePoint.split('~')
                        startPoint = scopePoint[0]
                        endPoint = scopePoint[1]
                        betweenPoints = get_between(startPoint, endPoint)
                        singlePoints.extend(betweenPoints)
                # pointGroups排除ignorePoints中的测点
                if ignorePoints:
                    pointGroupPoints[pointGroupCode] = [p for p in singlePoints if p not in ignorePoints]
            else:
                alarmCodes = []
                # events就是alarmCodes
                # events过滤出以'!'开头，并截取event.substring(1)，这样的alarmCode是忽略alarmCode
                ignoreAlarmCodes = [a[1:] for a in events if a.startswith('!')]
                # events过滤出不以'!'开头，并且event中不包括'~'的event，这样的alarmCode是单alarmCode
                singleAlarmCodes = [a for a in events if not a.startswith('!') and '~' not in a]
                alarmCodes.extend(singleAlarmCodes)
                # events过滤出不以'!'开头，并且event中包括'~'的event，这样的alarmCode是范围alarmCode
                scopeAlarmCodes = [a for a in events if '~' in a]
                if scopeAlarmCodes:
                    for scopeAlarmCode in scopeAlarmCodes:
                        scopeAlarmCode = scopeAlarmCode.split('~')
                        startAlarmCode = scopeAlarmCode[0]
                        endAlarmCode = scopeAlarmCode[1]
                        betweenAlarmCodes = get_between(startAlarmCode, endAlarmCode)
                        alarmCodes.extend(betweenAlarmCodes)
                # alarmCodes排除ignoreAlarmCodes中的alarmCode
                if ignoreAlarmCodes:
                    alarmCodes = [a for a in alarmCodes if a not in ignoreAlarmCodes]

                # relatedList过滤出以'!'开头但不以'!GP'开头，并截取related.substring(1)，这样的测点是忽略测点
                ignorePoints = [r[1:] for r in relatedList if r.startswith('!') and not r.startswith('!GP')]
                # relatedList过滤出不以'!'开头，且不以'!GP开头，且不已'GP'开头，且不包括'~'的related，并截取related.substring(1)，这样的测点是单测点
                singlePoints = [r for r in relatedList if not r.startswith('!') and not r.startswith('GP') and '~' not in r]
                # relatedList过滤出包括'~'，但是不以'GP'开头的related，这样的测点是范围测点
                scopePoints = [r for r in relatedList if '~' in r and not r.startswith('GP')]
                if scopePoints:
                    for scopePoint in scopePoints:
                        scopePoint = scopePoint.split('~')
                        startPoint = scopePoint[0]
                        endPoint = scopePoint[1]
                        betweenPoints = get_between(startPoint, endPoint)
                        singlePoints.extend(betweenPoints)
                # singlePoints排除ignorePoints中的测点
                if ignorePoints:
                    singlePoints = [p for p in singlePoints if p not in ignorePoints]
                for alarmCode in alarmCodes:
                    if alarmCode not in alarmCodeSinglePoints:
                        alarmCodeSinglePoints[alarmCode] = []
                    alarmCodeSinglePoints[alarmCode].extend(singlePoints)
                
                # relatedList过滤出以'!GP'开头，并截取related.substring(1)，这样的是忽略测点组
                ignorePointGroups = [r[1:] for r in relatedList if r.startswith('!GP')]
                # relatedList过滤出以'GP'开头，但是不包括'~'的related，这样的是单测点组
                singlePointGroups = [r for r in relatedList if r.startswith('GP') and '~' not in r]
                # relatedList过滤出包括'~'，且以'GP'开头的related，这样的范围测点组
                scopePointGroups = [r for r in relatedList if '~' in r and r.startswith('GP')]
                if scopePointGroups:
                    for scopePointGroup in scopePointGroups:
                        scopePointGroup = scopePointGroup.split('~')
                        startPointGroup = scopePointGroup[0]
                        endPointGroup = scopePointGroup[1]
                        betweenPointGroups = get_between(startPointGroup, endPointGroup)
                        singlePointGroups.extend(betweenPointGroups)

                if ignorePointGroups:
                    singlePointGroups = [p for p in singlePointGroups if p not in ignorePointGroups]
                
                for alarmCode in alarmCodes:
                    if alarmCode not in alarmCodeGroups:
                        alarmCodeGroups[alarmCode] = []
                    alarmCodeGroups[alarmCode].extend(singlePointGroups)
        # 获取alarmCodeSinglePoints和alarmCodeGroups中的alarmCode列表
        alarmCodes = list(alarmCodeSinglePoints.keys())
        alarmCodes.extend(list(alarmCodeGroups.keys()))
        # alarmCodes去重
        alarmCodes = list(set(alarmCodes))
        alarmInstancePointsStatistics = []
        for alarmCode in alarmCodes:
            points = []
            if alarmCode in alarmCodeSinglePoints:
                points.extend(alarmCodeSinglePoints[alarmCode])
            if alarmCode in alarmCodeGroups:
                pointGroups = alarmCodeGroups[alarmCode]
                for pointGroup in pointGroups:
                    if pointGroup in pointGroupPoints:
                        points.extend(pointGroupPoints[pointGroup])
                    else:
                        print(f"Error: {device},测点组{pointGroup} 未定义测点")
            alarmInstancePointsStatistics.append(AlarmInstancePointsStatistic(deviceCode=device, alarmCode=alarmCode, measurements=points))
        if alarmInstancePointsStatistics:
            # alarmInstancePointsStatistics通过参数alarms过滤出所有的measurement
            measurements = []
            for alarm in alarms:
                for alarmInstancePointsStatistic in alarmInstancePointsStatistics:
                    if alarm == alarmInstancePointsStatistic.alarmCode:
                        measurements.extend(alarmInstancePointsStatistic.measurements)
            if measurements:
                instanceMeasurements = self.getInstanceMeasurements(devices=[device])
                returnInstanceMeasurements = [instanceMeasurement for instanceMeasurement in instanceMeasurements if instanceMeasurement.measurement in measurements]
                
        return returnInstanceMeasurements

    def getDeviceSymptomInfo(self, device: str, symptomCode: str) -> List[DeviceSymptom]:
        """
        -- 查询机组征兆的信息（描述、关键字和诊断模块）
        """

        sql = f"""
        SELECT
            ai.NAME device_code, -- 机组编码
            symptom.dfem_code symptom_code,	-- 征兆编码
            symptom.display_name symptom_display_code, -- 征兆名称
            symptom.description symptom_description,	-- 征兆描述
            symptom.dfem_gjz keywords, -- 关键字
            fm.dfem_gnmkbh fm_code, -- 诊断模块实例编码（征兆:诊断模块实例 1:n）
            fm.display_name fm_name, -- 诊断模块实例名称
            fmt.dfem_code fmt_code,
            fmt.display_name fmt_name,
            fmt.type fmt_type
        FROM
            asset_instances ai
            LEFT JOIN dfem_rt_ai_fm af ON af.entity_type1_id = ai.ID 
            LEFT JOIN dfem_functional_module fm ON fm.ID = af.entity_type2_id
            LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.ID 
            LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = fmt1.entity_type1_id
            LEFT JOIN dfem_rt_fm_sg fs ON fs.entity_type1_id = fmt.ID 
            LEFT JOIN dfem_sign symptom ON symptom.ID = fs.entity_type2_id
        WHERE symptom.dfem_code is not null
            and ai.NAME = '{device}'
            and symptom.dfem_code = '{symptomCode}' 
            order by ai.NAME, symptom.dfem_code
        """

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                symptom = None
                for row in result.fetchall():
                    type = row[9]
                    typeName = ''
                    if type == 0:
                        typeName = '电站'
                    elif type == 1:
                        typeName = '机组'
                    elif type == 2:
                        typeName = '部件部套'
                    else:
                        typeName = '未知类型'
                    
                    if symptom is None:
                        diagnosticModule = DiagnosticModule(row[5], row[6], row[7], row[8], typeName)
                        symptom = DeviceSymptom(code=row[1], name=row[2], description=row[3], diagnosticModules=[diagnosticModule])
                    else:
                        symptom.diagnosticModules.append(DiagnosticModule(row[5], row[6], row[7], row[8], typeName))
                return symptom
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
    
        
    def getDeviceFailureInfo(self, device: str, failureCode: str) -> List[DeviceFailure]:
        """
        -- 查询机组失效的信息（描述、关键字和诊断模块）
        """

        sql = f"""
        SELECT
            ai.NAME device_code, -- 机组编码
            failure.dfem_code symptom_code,	-- 失效编码
            failure.display_name symptom_display_code, -- 失效名称
            failure.description symptom_description,	-- 失效描述
            failure.dfem_gjz keywords, -- 关键字
            fm.dfem_gnmkbh fm_code, -- 诊断模块实例编码（征兆:诊断模块实例 1:n）
            fm.display_name fm_name, -- 诊断模块实例名称
            fmt.dfem_code fmt_code,
            fmt.display_name fmt_name,
            fmt.type fmt_type
        FROM
            asset_instances ai
            LEFT JOIN dfem_rt_ai_fm af ON af.entity_type1_id = ai.ID 
            LEFT JOIN dfem_functional_module fm ON fm.ID = af.entity_type2_id
            LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.ID 
            LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = fmt1.entity_type1_id
            LEFT JOIN dfem_rt_fmt_fm ff ON ff.entity_type1_id = fmt.ID 
            LEFT JOIN dfem_failure_mode failure ON failure.ID = ff.entity_type2_id
        WHERE failure.dfem_code is not null
            and ai.NAME = '{device}'
            and failure.dfem_code = '{failureCode}' 
            order by ai.NAME, failure.dfem_code
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                failure = None
                for row in result.fetchall():
                    type = row[9]
                    typeName = ''
                    if type == 0:
                        typeName = '电站'
                    elif type == 1:
                        typeName = '机组'
                    elif type == 2:
                        typeName = '部件部套'
                    else:
                        typeName = '未知类型'
                    
                    if failure is None:
                        diagnosticModule = DiagnosticModule(row[5], row[6], row[7], row[8], typeName)
                        failure = DeviceFailure(code=row[1], name=row[2], description=row[3], diagnosticModules=[diagnosticModule])
                    else:
                        failure.diagnosticModules.append(DiagnosticModule(row[5], row[6], row[7], row[8], typeName))
                return failure
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )


    def getDeviceSymptoms(self, device: str, symptomDescription: str, diagnosticModuleName: str, keywords: str) -> List[DeviceSymptom]:
        """
        -- 根据机组和征兆描述、关键字、部位等限制条件反查符合条件的征兆编码
        """

        sql = f"""
        SELECT
            ai.NAME device_code, -- 机组编码
            symptom.dfem_code symptom_code,	-- 征兆编码
            symptom.display_name symptom_display_code, -- 征兆名称
            symptom.description symptom_description,	-- 征兆描述
            symptom.dfem_gjz keywords,
            fm.dfem_gnmkbh fm_code, -- 诊断模块实例编码（征兆:诊断模块实例 1:n）
            fm.display_name fm_name, -- 诊断模块实例名称
            fmt.dfem_code fmt_code,
            fmt.display_name fmt_name,
            fmt.type fmt_type
        FROM
            asset_instances ai
            LEFT JOIN dfem_rt_ai_fm af ON af.entity_type1_id = ai.ID 
            LEFT JOIN dfem_functional_module fm ON fm.ID = af.entity_type2_id
            LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.ID 
            LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = fmt1.entity_type1_id
            LEFT JOIN dfem_rt_fm_sg fs ON fs.entity_type1_id = fmt.ID 
            LEFT JOIN dfem_sign symptom ON symptom.ID = fs.entity_type2_id
        WHERE symptom.dfem_code is not null
            and ai.name = '{device}'
        """
        
        if symptomDescription:
            sql += f" and (symptom.display_name like '%{symptomDescription}%' or symptom.description like '%{symptomDescription}%')"
        if diagnosticModuleName:
            sql += f" and (fmt.display_name = '{diagnosticModuleName}' or fm.display_name = '{diagnosticModuleName}')"
        if keywords:
            sql += f" and symptom.dfem_gjz like '%{keywords}%'"
        sql += " order by symptom.dfem_code"

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                symptom_map = {}
                for row in result.fetchall():
                    type = row[9]
                    typeName = ''
                    if type == 0:
                        typeName = '电站'
                    elif type == 1:
                        typeName = '机组'
                    elif type == 2:
                        typeName = '部件部套'
                    else:
                        typeName = '未知类型'

                    if row[1] not in symptom_map:
                        diagnosticModule = DiagnosticModule(row[5], row[6], row[7], row[8], typeName)
                        symptom_map[row[1]] = DeviceSymptom(code=row[1], name=row[2], description=row[3], diagnosticModules=[diagnosticModule])
                    else:
                        symptom_map[row[1]].diagnosticModules.append(DiagnosticModule(row[5], row[6], row[7], row[8], typeName))
                return symptom_map.values()
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
        

    def getDeviceFailures(self, device: str, failureDescription: str, diagnosticModuleName: str, keywords: str) -> List[DeviceFailure]:
        """
        -- 根据机组和失效描述、关键字、部位等限制条件反查符合条件的失效编码
        """

        sql = f"""
        SELECT
            ai.NAME device_code, -- 机组编码
            failure.dfem_code symptom_code,	-- 失效编码
            failure.display_name symptom_display_code, -- 失效名称
            failure.description symptom_description,	-- 失效描述
            failure.dfem_gjz keywords,
            fm.dfem_gnmkbh fm_code, -- 诊断模块实例编码（征兆:诊断模块实例 1:n）
            fm.display_name fm_name, -- 诊断模块实例名称
            fmt.dfem_code fmt_code,
            fmt.display_name fmt_name,
            fmt.type fmt_type
        FROM
            asset_instances ai
            LEFT JOIN dfem_rt_ai_fm af ON af.entity_type1_id = ai.ID 
            LEFT JOIN dfem_functional_module fm ON fm.ID = af.entity_type2_id
            LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.ID 
            LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = fmt1.entity_type1_id
            LEFT JOIN dfem_rt_fmt_fm ff ON ff.entity_type1_id = fmt.ID 
            LEFT JOIN dfem_failure_mode failure ON failure.ID = ff.entity_type2_id
        WHERE failure.dfem_code is not null
            and ai.name = '{device}'
        """
        
        if failureDescription:
            sql += f" and (failure.display_name like '%{failureDescription}%' or failure.description like '%{failureDescription}%')"
        if diagnosticModuleName:
            sql += f" and (fmt.display_name = '{diagnosticModuleName}' or fm.display_name = '{diagnosticModuleName}')"
        if keywords:
            sql += f" and failure.dfem_gjz like '%{keywords}%'"
        sql += " order by failure.dfem_code"


        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                failure_map = {}
                # 将result.fetchall()中的数据转换为List<DeviceFailure>对象
                for row in result.fetchall():
                    type = row[9]
                    typeName = ''
                    if type == 0:
                        typeName = '电站'
                    elif type == 1:
                        typeName = '机组'
                    elif type == 2:
                        typeName = '部件部套'
                    else:
                        typeName = '未知类型'
                    
                    diagnosticModule = DiagnosticModule(row[5], row[6], row[7], row[8], typeName)
                    if row[1] not in failure_map:
                        failure_map[row[1]] = DeviceFailure(code=row[1], name=row[2], description=row[3], diagnosticModules=[diagnosticModule])
                    else:
                        failure_map[row[1]].diagnosticModules.append(diagnosticModule)
                        
                return failure_map.values()
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
                original_exception=e
            )
        
    # 根据设备、部位编码反查所关联的征兆、失效
    def getDeviceSymptomsAndFailures(self, device: str, diagnosticModuleName: str) -> List[AlarmType]:
        """
        -- 根据设备、部位编码反查所关联的征兆、失效
        """
        sql = f"""
        SELECT
            ai.NAME device_code,
            failure.dfem_code code,
            failure.display_name display_code,
            failure.description description,
            failure.dfem_gjz keywords,
            'failure' alarm_type
        FROM
            asset_instances ai
            LEFT JOIN dfem_rt_ai_fm af ON af.entity_type1_id = ai.ID
            LEFT JOIN dfem_functional_module fm ON fm.ID = af.entity_type2_id
            LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.ID
            LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = fmt1.entity_type1_id
            LEFT JOIN dfem_rt_fmt_fm ff ON ff.entity_type1_id = fmt.ID
            LEFT JOIN dfem_failure_mode failure ON failure.ID = ff.entity_type2_id
        WHERE failure.dfem_code is not null
                and ai.name = '{device}'
        and (fmt.display_name = '{diagnosticModuleName}' or fm.display_name = '{diagnosticModuleName}')
                        
        union
                        
        SELECT
                ai.NAME device_code,
                symptom.dfem_code code,
                symptom.display_name display_code,
                symptom.description description,
                symptom.dfem_gjz keywords,
                'symptom' alarm_type
        FROM
                asset_instances ai
                LEFT JOIN dfem_rt_ai_fm af ON af.entity_type1_id = ai.ID 
                LEFT JOIN dfem_functional_module fm ON fm.ID = af.entity_type2_id
                LEFT JOIN dfem_rt_fmt_fm1 fmt1 ON fmt1.entity_type2_id = fm.ID 
                LEFT JOIN dfem_functional_module_type fmt ON fmt.ID = fmt1.entity_type1_id
                LEFT JOIN dfem_rt_fm_sg fs ON fs.entity_type1_id = fmt.ID 
                LEFT JOIN dfem_sign symptom ON symptom.ID = fs.entity_type2_id
        WHERE symptom.dfem_code is not null
                and ai.name = '{device}'
        and (fmt.display_name = '{diagnosticModuleName}' or fm.display_name = '{diagnosticModuleName}')
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                alarmTypeMap = {}   
                for row in result.fetchall():
                    if row[1] + row[5] not in alarmTypeMap:
                        alarmTypeMap[row[1] + row[5]] = AlarmType(row[1], row[2], row[3], row[4], row[5])
                    else:
                        alarmTypeMap[row[1] + row[5]].keywords.append(row[4])
                return alarmTypeMap.values()
        except SQLAlchemyError as e:
            raise DataFrameDBException(
                f"Failed to query records due to a database error. SQL: {sql}",
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
        pg_url_obj = make_url(f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/default')
        self.logger.debug(f'postgres url: {pg_url_obj}')
        return pg_url_obj
