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
    AccountNotValidatedError,
    ApiError,
    ValidateAccountInfoError,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("tests/debug.log",mode='w'),
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

    valid_account = False
    try:
        valid_account = await mywatertoronto.async_validate_account()
    except ( ValidateAccountInfoError, ApiError ) as err:
        logging.debug(f"Error validating account with MyWaterToronto API: {err}")

    if valid_account:
        account_details = None
        try:
            account_details = await mywatertoronto.async_get_account_details()
        except ( AccountDetailsError, AccountNotValidatedError, ApiError ) as err:
            logging.debug(f"Error getting account details from MyWaterToronto API: {err}")

        if account_details is not None:
            consumption_data = None

            try:
                consumption_data = await mywatertoronto.async_get_consumption()
            except ( ApiError ) as err:
                logging.debug(f"Error getting water consumption data from MyWaterToronto API: {err}")

            if consumption_data is not None:
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