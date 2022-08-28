# 🌤️ Python Wrapper for MyWaterToronto REST API

![Latest PyPI version](https://img.shields.io/pypi/v/pymywatertoronto) ![Supported Python](https://img.shields.io/pypi/pyversions/pymywatertoronto)


This module communicates with the City of Toronto [MyWaterToronto](https://www.toronto.ca/services-payments/water-environment/how-to-use-less-water/mywatertoronto/) service.

The module is primarily written for the purpose of being used in Home Assistant for the Custom Integration called [`mywatertoronto`](https://github.com/davecpearce/hacs-mywatertoronto) .

This API will read the account information and obtain a list of address(es) and meter(s).  

Consumption data incude

Unfortunately, the City of Toronto only appears to be pulling meter data every 1-2 days.  

## Install

`pymywatertoronto` is avaible on PyPi:

```bash
pip install pymywatertoronto
```

## Consumption Buckets

This library will provide the following consumption buckets
* `Total usage`
* `Today usage`
* `Week-to-date usage`
* `Month-to-date usage`
* `Year-to-date usage`

## Usage

This library is primarily designed to be used in Home Assistant.

The main interface for the library is the `pymywatertoronto.MyWaterToronto`. This interface takes 6 options:

* `session`: (required) An existing *aiohttp.ClientSession*. 
* `account_number`: (required) Enter your Account No. found on the utility bill.
* `client_number`: (required) Enter your Client No. found on the utility bill.
* `last_name`: (required) Enter your Last Name - must match the first last name on the utility bill.
* `postal_code`: (required) Enter your Postal Code - must match the postal code on the utility bill.
* `last_payment_method`: (required) use the enumerations from *const.LastPaymentMethod*.

```python
import asyncio

from datetime import timedelta
from aiohttp import ClientSession
import logging

from pymywatertoronto.mywatertoronto import (
    MyWaterToronto, 
)
from pymywatertoronto.const import (
    KEY_ADDRESS,
    KEY_METER_FIRST_READ_DATE,
    KEY_METER_LIST,
    KEY_METER_NUMBER,
    KEY_PREMISE_ID,
    KEY_PREMISE_LIST, 
)
from pymywatertoronto.enums import (
    ConsumptionBuckets,
    LastPaymentMethod, 
)
from pymywatertoronto.errors import (
    AccountDetailsError,
    ApiError,
    ValidateAccountInfoError,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log",mode='w'),
        logging.StreamHandler()
    ]
)

# Update this section with your City of Toronto Utility account information
account_number="000000000"
client_number="000000000-00"
last_name="lastname"
postal_code="X1X 1X1"
last_payment_method=LastPaymentMethod.BANK_PAYMENT

async def main():
    session = ClientSession()

    mywatertoronto = MyWaterToronto(session,
                                    account_number, 
                                    client_number, 
                                    last_name, 
                                    postal_code, 
                                    last_payment_method )

    try:
        await mywatertoronto.async_validate_account()
    except ( ValidateAccountInfoError, ApiError ) as err:
        logging.debug(f"Error validating account with MyWaterToronto API: {err}")

    try:
        account_details = await mywatertoronto.async_get_account_details()
    except ( AccountDetailsError, ApiError ) as err:
        logging.debug(f"Error getting account details from MyWaterToronto API: {err}")

    try:
        consumption_data = await mywatertoronto.async_get_consumption()
    except ( ApiError ) as err:
        logging.debug(f"Error getting water consumption data from MyWaterToronto API: {err}")

    for premise in account_details[KEY_PREMISE_LIST]:
        premise_id = premise[KEY_PREMISE_ID]
        premise_address = premise[KEY_ADDRESS]
        logging.debug('Premise Address: %s', premise_address)  # noqa: WPS323

        meter_list = premise[KEY_METER_LIST]
        for meter in meter_list:
            meter_number = meter[KEY_METER_NUMBER]
            meter_name = f"{premise_address} {meter_number}"
            logging.debug('Meter Name: %s', meter_name)  # noqa: WPS323

            data = consumption_data[KEY_PREMISE_LIST][premise_id][KEY_METER_LIST][meter_number]
            firstReadDate = data[KEY_METER_FIRST_READ_DATE]
            logging.debug('First Read Date: %s', firstReadDate)  # noqa: WPS323

            for bucket in ConsumptionBuckets:
                consumption = data['consumption_data'][bucket.value]['consumption']
                unit = data['consumption_data'][bucket.value]['unit_of_measure']
                logging.debug('%s: %s %s', bucket.value, consumption, unit)  # noqa: WPS323

    await session.close()

asyncio.run(main())
```