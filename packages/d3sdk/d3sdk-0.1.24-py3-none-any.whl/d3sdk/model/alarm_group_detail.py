from typing import List

class Cause:
    def __init__(self, code: str, displayName: str, description: str, suggestions: List['Suggestion']):
        self.code = code
        self.displayName = displayName
        self.description = description
        self.suggestions = suggestions

    def __repr__(self):
        return (f"Cause(code={self.code!r}, "
                f"display_name={self.displayName!r}, "
                f"description={self.description!r}, "
                f"suggestions={self.suggestions!r})")
    
    def to_dict(self):
        return {
            'code': self.code,
            'displayName': self.displayName,
            'description': self.description,
            'suggestions': [suggestion.to_dict() for suggestion in self.suggestions]
        }


class Suggestion:
    def __init__(self, code: str, displayName: str, description: str):
        self.code = code
        self.displayName = displayName
        self.description = description

    def __repr__(self):
        return (f"Suggestion(code={self.code!r}, "
                f"displayName={self.displayName!r}, "
                f"description={self.description!r})")
    
    def to_dict(self):
        return {
            'code': self.code,
            'displayName': self.displayName,
            'description': self.description
        }

class AlarmDetail:
    """
    报警的原因建议
    """
    def __init__(self, alarmCode: str, alarmType: str, causes: List[Cause]):
        self.alarmCode = alarmCode
        self.alarmType = alarmType
        self.causes = causes

    def __repr__(self):
        return (f"AlarmDetail(alarmCode={self.alarmCode!r}, "
                f"alarmType={self.alarmType!r}, "
                f"causes={self.causes!r})")
    
    def to_dict(self):
        return {
            'alarmCode': self.alarmCode,
            'alarmType': self.alarmType,
            'causes': [cause.to_dict() for cause in self.causes]
        }
