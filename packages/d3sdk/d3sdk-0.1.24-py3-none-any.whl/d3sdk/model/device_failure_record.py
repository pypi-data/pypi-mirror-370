from typing import List

class DiagnosticModule:
    def __init__(self, diagnosticModuleCode, diagnosticModuleName, diagnosticModuleTypeCode, diagnosticModuleTypeName, typeOfDiagnosticModuleType):
        self.diagnosticModuleCode = diagnosticModuleCode
        self.diagnosticModuleName = diagnosticModuleName
        self.diagnosticModuleTypeCode = diagnosticModuleTypeCode
        self.diagnosticModuleTypeName = diagnosticModuleTypeName
        self.typeOfDiagnosticModuleType = typeOfDiagnosticModuleType

    def __repr__(self):
        return f"DiagnosticModule(diagnosticModuleCode={self.diagnosticModuleCode}, diagnosticModuleName={self.diagnosticModuleName}, diagnosticModuleTypeCode={self.diagnosticModuleTypeCode}, diagnosticModuleTypeName={self.diagnosticModuleTypeName}, typeOfDiagnosticModuleType={self.typeOfDiagnosticModuleType})"
    
    def to_dict(self):
        return {
            'diagnosticModuleCode': self.diagnosticModuleCode,
            'diagnosticModuleName': self.diagnosticModuleName,
            'diagnosticModuleTypeCode': self.diagnosticModuleTypeCode,
            'diagnosticModuleTypeName': self.diagnosticModuleTypeName,
            'typeOfDiagnosticModuleType': self.typeOfDiagnosticModuleType
        }

class DeviceFailureRecord:
    def __init__(self, alarmGroupCode, alarmGroupName, alarmType, alarmCode, description, alarmNumber, level, status, keywords, earliestAlarmTime, latestAlarmTime, deviceCode, deviceName, diagnosticModules:List[DiagnosticModule]):
        self.alarmGroupCode = alarmGroupCode
        self.alarmGroupName = alarmGroupName
        self.alarmType = alarmType
        self.alarmCode = alarmCode
        self.description = description
        self.alarmNumber = alarmNumber
        self.level = level
        self.status = status
        self.keywords = keywords
        self.earliestAlarmTime = earliestAlarmTime
        self.latestAlarmTime = latestAlarmTime
        self.deviceCode = deviceCode
        self.deviceName = deviceName
        self.diagnosticModules = diagnosticModules

    def __repr__(self):
        return (f"DeviceFailureRecord(alarmGroupCode={self.alarmGroupCode}, "
                f"alarmGroupName={self.alarmGroupName}, "
                f"alarmType={self.alarmType}, "
                f"alarmCode={self.alarmCode}, "
                f"description={self.description}, "
                f"alarmNumber={self.alarmNumber}, "
                f"level={self.level}, "
                f"status={self.status}, "
                f"keywords={self.keywords}, "
                f"earliestAlarmTime={self.earliestAlarmTime}, "
                f"latestAlarmTime={self.latestAlarmTime}, "
                f"deviceCode={self.deviceCode}, "
                f"diagnosticModules={self.diagnosticModules!r})")

    def to_dict(self):
        return {
            'alarmGroupCode': self.alarmGroupCode,
            'alarmGroupName': self.alarmGroupName,
            'alarmType': self.alarmType,
            'alarmCode': self.alarmCode,
            'description': self.description,
            'alarmNumber': self.alarmNumber,
            'level': self.level,
            'status': self.status,
            'keywords': self.keywords,
            'earliestAlarmTime': self.earliestAlarmTime,
            'latestAlarmTime': self.latestAlarmTime,
            'deviceCode': self.deviceCode,
            'deviceName': self.deviceName,
            'diagnosticModules': [diagnosticModule.to_dict() for diagnosticModule in self.diagnosticModules]
        }

class DeviceSymptom:
    def __init__(self, code, name, description, diagnosticModules:List[DiagnosticModule]):
        self.code = code
        self.name = name
        self.description = description
        self.diagnosticModules = diagnosticModules
    def __repr__(self):
        return f"DeviceSymptom(code={self.code}, name={self.name}, description={self.description}, diagnosticModules={self.diagnosticModules!r})"
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'diagnosticModules': [diagnosticModule.to_dict() for diagnosticModule in self.diagnosticModules]
        }

class DeviceFailure:
    def __init__(self, code, name, description, diagnosticModules:List[DiagnosticModule]):
        self.code = code
        self.name = name
        self.description = description
        self.diagnosticModules = diagnosticModules
    def __repr__(self):
        return f"DeviceFailure(code={self.code}, name={self.name}, description={self.description}, diagnosticModules={self.diagnosticModules!r})"
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'diagnosticModules': [diagnosticModule.to_dict() for diagnosticModule in self.diagnosticModules]
        }

class AlarmType:
    def __init__(self, code, name, description, keywords, type):
        self.code = code
        self.name = name
        self.description = description
        self.keywords = keywords
        self.type = type
    def __repr__(self):
        return f"AlarmType(code={self.code}, name={self.name}, description={self.description}, keywords={self.keywords}, type={self.type})"
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'keywords': self.keywords,
            'type': self.type
        }
