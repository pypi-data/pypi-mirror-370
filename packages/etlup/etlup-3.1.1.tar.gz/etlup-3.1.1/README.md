# etlup

[![PyPI - Version](https://img.shields.io/pypi/v/etlup.svg)](https://pypi.org/project/etlup)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/etlup.svg)](https://pypi.org/project/etlup)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install etlup
```


## Example

```
from etlup import ETLup

etl_up = ETLup(api_key=None, timezone='US/Eastern')

#list of dictionaries 
for t in tests:
    etl_up.add_constr(t)

etl_up.to_file("/home/hayden/Desktop/ETLdbTest/etlappdump/my_special_output_3.json")
```


## License

`etlup` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
