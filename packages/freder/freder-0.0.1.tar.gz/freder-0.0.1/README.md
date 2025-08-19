# FRED API Usage facilitator

![main workflow](https://img.shields.io/github/actions/workflow/status/haydenkuk/fred/main.yaml?logo=github)
![GitHub licence](https://img.shields.io/pypi/l/fred?logo=github)
![GitHub downloads](https://img.shields.io/github/downloads-pre/haydenkuk/fred/latest/total?logo=github)
![documentation](https://img.shields.io/readthedocs/fred?logo=readthedocs)
![PyPi download](https://img.shields.io/pypi/dm/fred?logo=pypi)
![PyPi version](https://img.shields.io/pypi/v/fred?logo=pypi)
![python version](https://img.shields.io/pypi/pyversions/fred?style=pypi)


FRED API
(https://fred.stlouisfed.org/docs/api/fred/)

Features
- All API endpoints included according to the fred docs(https://fred.stlouisfed.org/docs/api/fred/)

1. Installation
```sh
pip install fred
```
Requires Python 3.9+

2. Usage

1-1) Authentication: using dotenv
 - Created a file named ".env"
 - Add "FRED_APIKEY='YOURAPIKEY'" in the file
1-2) Authentication: using "set_apikey"
```python
import freder

freder.set_apikey('yourapikey')
```

2) apicalls
```python
import freder

result = freder.get_category(0)
print(result)
```
All API endpoints are included in this package,
Please refer to https://fred.stlouisfed.org/docs/api/fred/
For more API endpoints

Also, Please pay attention to docstrings of each fred functions in this package. I included fred's explanation of each input variable to facilitate the process.