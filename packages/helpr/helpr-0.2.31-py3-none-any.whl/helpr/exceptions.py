class AppException(Exception):
    def __init__(self, message, error_code=0, http_code=400):
        self.message = message
        self.error_code = error_code
        self.http_code = http_code
        super().__init__(self.message)