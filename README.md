# 🌤️ Python Wrapper for MyWaterToronto REST API

![Latest PyPI version](https://img.shields.io/pypi/v/pymywatertoronto) ![Supported Python](https://img.shields.io/pypi/pyversions/pymywatertoronto)

This module communicates with the City of Toronto [MyWaterToronto](https://www.toronto.ca/services-payments/water-environment/how-to-use-less-water/mywatertoronto/) service.

The module is primarily written for the purpose of being used in Home Assistant for the Custom Integration called [`mywatertoronto`](https://github.com/davecpearce/hacs-mywatertoronto) .

This API will read the account information and obtain a list of address(es) and meter(s).

Consumption data incude

Unfortunately, the City of Toronto only appears to be pulling meter data every 1-2 days.

## Install

`pymywatertoronto` is available on PyPi:

```bash
pip install pymywatertoronto
```

## Consumption Buckets

This library will provide the following consumption buckets

- `Total usage`
- `Today usage`
- `Week-to-date usage`
- `Month-to-date usage`
- `Year-to-date usage`

## Usage

This library is primarily designed to be used in Home Assistant.

The main interface for the library is the `pymywatertoronto.MyWaterToronto`. This interface takes 6 options:

- `session`: (required) An existing _aiohttp.ClientSession_.
- `account_number`: (required) Enter your Account No. found on the utility bill.
- `client_number`: (required) Enter your Client No. found on the utility bill.
- `last_name`: (required) Enter your Last Name - must match the first last name on the utility bill.
- `postal_code`: (required) Enter your Postal Code - must match the postal code on the utility bill.
- `last_payment_method`: (required) use the enumerations from _const.LastPaymentMethod_.

Copy the _tests/template.env_ to _tests/.env_ file and update the account information with your your City of Toronto account information:

```python
ACCOUNT_NUMBER="000000000"
CLIENT_NUMBER="000000000-00"
LAST_NAME="lastname"
POSTAL_CODE="A1A 1A1"
LAST_PAYMENT_METHOD="4"
```

Use the enumerations from _const.LastPaymentMethod_.

Run the test file:
python tests/test_mywatertoronto.py [-h or --dump]

--dump paramater will create two files containing data that is leveraged in the Home Assistant integration:

- data_account_details.json
- data_consumption.json
