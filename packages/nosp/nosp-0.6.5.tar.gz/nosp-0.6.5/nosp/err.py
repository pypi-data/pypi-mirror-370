class CustomException(Exception):
    def __init__(self, status, msg=None, data=None):
        self.status = status
        self.msg = msg
        self.data = data
