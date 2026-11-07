class ServiceError(Exception):
    def __init__(self, status_code: int, message: str, display_ui: bool = False):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.display_ui = display_ui
