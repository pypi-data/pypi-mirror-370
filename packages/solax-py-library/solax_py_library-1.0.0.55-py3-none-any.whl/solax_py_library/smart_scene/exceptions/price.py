from solax_py_library.exception import SolaxBaseError


class ElectricityPriceFailure(SolaxBaseError):
    message = "cloud__electricity_price_failure"
