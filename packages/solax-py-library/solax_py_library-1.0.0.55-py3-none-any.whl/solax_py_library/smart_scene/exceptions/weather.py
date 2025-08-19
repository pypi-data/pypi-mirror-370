from solax_py_library.exception import SolaxBaseError


class WeatherFailure(SolaxBaseError):
    message = "cloud__weather_failure"
