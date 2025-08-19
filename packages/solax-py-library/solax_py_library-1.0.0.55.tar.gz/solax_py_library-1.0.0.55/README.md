### solax common module

#### install

```shell
pip install solax_py_library
```

#### struction

module:
- api: provide the api
- core: core code
- errors: define errors
- test: unit tests
- types: modle define

#### module

This package provide some general modules to help us can focus on the real project coding.It`s our own package,we can add more and more general modules.

- upload: The module define the upload tool.It support the way by Ftp.


#### quick start

```python
await upload(
    upload_type=UploadType.FTP,
    configuration=ftp_config,
    upload_data=UploadData(
        upload_type=UploadType.FTP,
        data=dict(
            file_type=FTPFileType.CSV,
            file_name="new_file.csv",
            data=[
                {
                    "EMS1000序列号": "XMG11A011L",
                    "EMS1000本地时间": "2025-02-11 15:39:10",
                    "EMS1000版本号": "V007.11.1",
                    "电站所在国家和地区": None,
                    "电站所在当前时区": None,
                    "电站系统类型": None,
                }
            ],
        ),
    ),
)
```
