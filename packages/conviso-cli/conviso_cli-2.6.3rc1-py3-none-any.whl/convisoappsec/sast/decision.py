from enum import IntEnum
import json

class Severity(IntEnum):
    # Sastbox [:undefined, :info, :low, :medium, :high, :critical]
    UNDEFINED = 0
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5
    
    @classmethod
    def has_value(cls, value):
        return value in cls._member_names_



class Decision:


    def __init__(self, report):
        self.report = open(report)
        self.json = json.load(self.report)
        self.issues = self.json.get('issues')
        self.sev = self.issues

    def block_from_severity(self, severity, threshold=1):
        if not severity:
            return False
        severity = Severity[severity]
        self.sev = [issue for issue in self.issues if Severity[issue.get('severity').upper()] >= severity]
        return len(self.sev) >= threshold

    def block_from_findings(self, threshold):
        if not threshold:
            return False
        return len(self.issues) >= threshold
    
    def filtered_issues(self):
        return self.sev




