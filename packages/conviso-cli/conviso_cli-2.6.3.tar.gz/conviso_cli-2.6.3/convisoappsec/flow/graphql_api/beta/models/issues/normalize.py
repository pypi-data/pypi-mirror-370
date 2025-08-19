class Normalize:

    @staticmethod
    def normalize_severity(severity):
        """
        The function normalizes severity by validating and returning a standardized severity level.
        """

        validate_severity = ["LOW", "MEDIUM", "HIGH", "CRITICAL", "NOTIFICATION"]
        if severity.upper() in validate_severity:
            return severity.upper()
        else:
            return validate_severity[0]
