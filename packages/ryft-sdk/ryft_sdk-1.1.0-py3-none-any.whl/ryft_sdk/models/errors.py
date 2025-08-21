class RyftError(Exception):
    def __init__(self, status, response):
        self.requestId = response.get("requestId")
        self.code = response.get("code")
        self.status = status
        self.message = "Unknown error"
        self.errors = response.get("errors", [])

        if self.errors:
            self.message = self.errors[0].get("message", "Unknown error")

        super().__init__(self.message)
        self.__class__.__name__ = "RyftError"
