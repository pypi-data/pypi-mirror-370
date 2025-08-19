class KError(Exception):
    def __init__(self, msg=None):
        self.msg = msg

    def __str__(self):
        _msg = f"{self.msg}\n"
        return _msg


