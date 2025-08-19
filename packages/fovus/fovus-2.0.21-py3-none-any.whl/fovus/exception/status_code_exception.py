class StatusException(Exception):
    def __init__(self, status_code, source, message=""):
        self.status_code = status_code
        self.source = source
        self.message = message

    def __str__(self):
        # \033[91m \033[0m - print message in red color
        return f"\033[91m{str(self.status_code)} from {self.source}. {self.message}\033[0m"
