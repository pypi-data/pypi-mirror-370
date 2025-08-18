class MTeamException(Exception):
    """基础异常类"""
    pass

class APIError(MTeamException):
    """API 调用错误"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message) 