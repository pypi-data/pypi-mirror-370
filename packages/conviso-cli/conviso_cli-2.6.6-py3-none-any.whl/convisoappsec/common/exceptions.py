class CommonException(RuntimeError):
    pass

class ExecutionFailureException(CommonException):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_code = kwargs['exit_code']
