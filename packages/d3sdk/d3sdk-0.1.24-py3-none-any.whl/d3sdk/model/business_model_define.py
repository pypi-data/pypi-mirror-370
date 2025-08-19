from typing import List

class DeviceMeasurementGroup:
    def __init__(self, deviceCode, deviceName, measurementGroupCode, measurementGroupName, deviceTypeCode, schema):
        self.deviceCode = deviceCode
        self.deviceName = deviceName
        self.measurementGroupCode = measurementGroupCode
        self.measurementGroupName = measurementGroupName
        self.deviceTypeCode = deviceTypeCode
        self.schema = schema

    def __repr__(self):
        return f"DeviceMeasurementGroup(deviceCode={self.deviceCode}, deviceTypeCode={self.deviceTypeCode}, measurementGroupCode={self.measurementGroupCode}, schema={self.schema})"
    
    def to_dict(self):
        return {
            'deviceCode': self.deviceCode,
            'deviceName': self.deviceName,
            'measurementGroupCode': self.measurementGroupCode,
            'measurementGroupName': self.measurementGroupName,
            'deviceTypeCode': self.deviceTypeCode,
            'schema': self.schema
        }


class InstanceMeasurement:
    def __init__(self, deviceCode, deviceTypeCode, schema, schemaColumn, schemaColumnName, repoCode, repoName, 
                 repoColumn, unit, lowerBound, upperBound, type, measurementGroupCode, measurementGroupName, measurement, measurementName):
        self.deviceCode = deviceCode
        self.deviceTypeCode = deviceTypeCode
        self.schema = schema
        self.schemaColumn = schemaColumn
        self.schemaColumnName = schemaColumnName
        self.repoCode = repoCode
        self.repoName = repoName
        self.repoColumn = repoColumn
        self.unit = unit
        self.lowerBound = lowerBound
        self.upperBound = upperBound
        self.type = type
        self.measurement = measurement
        self.measurementGroupCode = measurementGroupCode
        self.measurementGroupName = measurementGroupName
        self.measurementName = measurementName
    def __repr__(self):
        return f"InstanceMeasurement(deviceCode={self.deviceCode}, measurement={self.measurement}, repoCode={self.repoCode}, repoColumn={self.repoColumn})"
    
    def to_dict(self):
        return {
            'deviceCode': self.deviceCode,
            'deviceTypeCode': self.deviceTypeCode,
            'schema': self.schema,
            'schemaColumn': self.schemaColumn,
            'schemaColumnName': self.schemaColumnName,
            'repoCode': self.repoCode,
            'repoName': self.repoName,
            'repoColumn': self.repoColumn,
            'unit': self.unit,
            'lowerBound': self.lowerBound,
            'upperBound': self.upperBound,
            'type': self.type,
            'measurementGroupCode': self.measurementGroupCode,
            'measurementGroupName': self.measurementGroupName,
            'measurement': self.measurement,
            'measurementName': self.measurementName
        }
    
class AlarmInstancePointsConfig:
    def __init__(self, deviceCode, deviceType, events, related):
        self.deviceCode = deviceCode
        self.deviceType = deviceType
        self.events = events
        self.related = related

    def __repr__(self):
        return f"AlarmInstancePointsConfig(deviceCode={self.deviceCode}, events={self.events}, related={self.related})"
    
    def to_dict(self):
        return {
            'deviceCode': self.deviceCode,
            'deviceType': self.deviceType,
            'events': self.events,
            'related': self.related
        }

class AlarmInstancePointsStatistic:
    def __init__(self, deviceCode, alarmCode, measurements:List[str]):
        self.deviceCode = deviceCode
        self.alarmCode = alarmCode
        self.measurements = measurements

    def __repr__(self):
        return f"AlarmInstancePointsStatistic(deviceCode={self.deviceCode}, alarmCode={self.alarmCode}, measurements={self.measurements})"
    
    def to_dict(self):
        return {
            'deviceCode': self.deviceCode,
            'alarmCode': self.alarmCode,
            'measurements': self.measurements
        }
    
