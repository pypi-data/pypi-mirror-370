import csv
import tempfile
from typing import Any, Union, List, Dict

from solax_py_library.upload.core.data_adapter.base import BaseDataAdapter


class CSVDataAdapter(BaseDataAdapter):
    @classmethod
    def parse_data(cls, data: Union[List[List[Any]], List[Dict[str, Any]]]):
        with tempfile.NamedTemporaryFile(
            delete=False, mode="w", newline="", encoding="utf-8-sig"
        ) as temp_file:
            if isinstance(data[0], list):
                writer = csv.writer(temp_file)
                writer.writerows(data)
            else:
                headers = list(data[0].keys())
                writer = csv.DictWriter(temp_file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)

            temp_file_path = temp_file.name
            temp_file.seek(0)

        return temp_file_path
