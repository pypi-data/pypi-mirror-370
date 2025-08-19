class SolaxBaseError(Exception):
    code = 0x1000
    message = "upload error"

    def __init__(self, *args, message=None):
        super().__init__(*args)
        self.message = message or self.message

    def __str__(self):
        return self.message
