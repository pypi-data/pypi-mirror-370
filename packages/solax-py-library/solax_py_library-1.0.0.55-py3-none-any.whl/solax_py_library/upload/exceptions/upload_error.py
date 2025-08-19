from solax_py_library.exception import SolaxBaseError


class ConnectError(SolaxBaseError):
    code = 0x1001
    message = "connect error"


class LoginError(SolaxBaseError):
    code = 0x1002
    message = "authentication error"


class SendDataError(SolaxBaseError):
    code = 0x1003
    message = "send data error"


class ConfigurationError(SolaxBaseError):
    code = 0x1004
    message = "server configuration error"
