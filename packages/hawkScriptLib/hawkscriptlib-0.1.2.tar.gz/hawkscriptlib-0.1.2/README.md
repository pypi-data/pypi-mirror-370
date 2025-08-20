# My myHawkScriptLib Library

This is a sample Python library that demonstrates how to create and publish your own library to PyPI.

## Installation

```bash
pip install myHawkScriptLib
```

## Usage

```python
from  hawkScriptLib import myHawkGUI_PLC_API
with myHawkGUI_PLC_API() as client:
    if client.client_socket:
        #读取PLC 地址 250 和 251 上的值
        print(client.read_value(250,2))   #  100，101   （成功：假如250 251 寄存器值里面的值分别是 100，101）；err  (失败)
        #写入PLC 地址 250 和 251 分别为200，201
        print(client.write_value(250, [200,201])) # 200，201   （成功）； err  （失败）

```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)