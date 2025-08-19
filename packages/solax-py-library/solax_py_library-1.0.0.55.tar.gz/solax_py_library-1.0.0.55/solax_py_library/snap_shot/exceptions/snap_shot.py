from solax_py_library.exception import SolaxBaseError


class SnapshotError(SolaxBaseError):
    ...


class SnapshotTimeoutError(SnapshotError):
    ...
