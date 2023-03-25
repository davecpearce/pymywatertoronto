""" Python test file for pymywatertoronto. """

import argparse
import asyncio
import json
import logging
import os
from aiohttp import ClientSession
from dotenv import load_dotenv
from os.path import dirname, join

from pymywatertoronto.const import (
    KEY_ADDRESS,
    KEY_METER_FIRST_READ_DATE,
    KEY_METER_LIST,
    KEY_METER_NUMBER,
    KEY_PREMISE_ID,
    KEY_PREMISE_LIST,
)
from pymywatertoronto.enums import ConsumptionBuckets, LastPaymentMethod
from pymywatertoronto.errors import (
    AccountDetailsError,
    AccountNotValidatedError,
    ApiError,
    ValidateAccountInfoError,
)
from pymywatertoronto.mywatertoronto import MyWaterToronto

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("tests/debug.log", mode="w"),
        logging.StreamHandler(),
    ],
)

# Load the account information
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

ACCOUNT_NUMBER = os.environ.get("ACCOUNT_NUMBER")
CLIENT_NUMBER = os.environ.get("CLIENT_NUMBER")
LAST_NAME = os.environ.get("LAST_NAME")
POSTAL_CODE = os.environ.get("POSTAL_CODE")
LAST_PAYMENT_METHOD = os.environ.get("LAST_PAYMENT_METHOD")


async def main(dump_data: bool = False):
    """Main function for testing"""
    session = ClientSession()

    mywatertoronto = MyWaterToronto(
        session,
        ACCOUNT_NUMBER,
        CLIENT_NUMBER,
        LAST_NAME,
        POSTAL_CODE,
        LastPaymentMethod(LAST_PAYMENT_METHOD),
    )

    try:
        await mywatertoronto.async_validate_account()
    except (ValidateAccountInfoError, ApiError) as err:
        logging.debug(
            "Error validating account with MyWaterToronto API: %s", err
        )  # noqa: E501
    else:
        try:
            account_details = await mywatertoronto.async_get_account_details()
        except (
            AccountDetailsError,
            AccountNotValidatedError,
            ApiError,
        ) as err:  # noqa: E501
            logging.debug(
                "Error getting account details from MyWaterToronto API: %s",
                err,  # noqa: E501
            )
        else:
            if dump_data:
                with open(
                    "data_account_details.json", "w", encoding="UTF-8"
                ) as dumpfile:
                    json.dump(account_details, dumpfile, indent=4)
            try:
                consumption_data = await mywatertoronto.async_get_consumption(
                    buckets=None
                )
            except (ApiError) as err:
                logging.debug(
                    "Error getting water consumption data from MyWaterToronto API: %s",  # noqa: E501
                    err,
                )  # pylint: disable=line-too-long
            else:
                with open(
                    "data_consumption.json", "w", encoding="UTF-8"
                ) as dumpfile:  # noqa: E501
                    json.dump(consumption_data, dumpfile, indent=4)

                for premise in account_details[KEY_PREMISE_LIST]:
                    premise_id = premise[KEY_PREMISE_ID]
                    premise_address = premise[KEY_ADDRESS]
                    logging.debug("Premise Address: %s", premise_address)

                    meter_list = premise[KEY_METER_LIST]
                    for meter in meter_list:
                        meter_number = meter[KEY_METER_NUMBER]
                        meter_name = f"{premise_address} {meter_number}"
                        logging.debug("Meter Name: %s", meter_name)

                        data = consumption_data[KEY_PREMISE_LIST][premise_id][
                            KEY_METER_LIST
                        ][meter_number]
                        first_read_date = data[KEY_METER_FIRST_READ_DATE]
                        logging.debug("First Read Date: %s", first_read_date)

                        c_data = data["consumption_data"]
                        for bucket in ConsumptionBuckets:
                            if bucket.value in c_data:
                                b_data = c_data[bucket.value]
                                consumption = b_data["consumption"]
                                unit = b_data["unit_of_measure"]

                                logging.debug(
                                    "%s: %s %s", bucket.value, consumption, unit
                                )

    await session.close()


parser = argparse.ArgumentParser("test")
parser.add_argument(
    "-d", action="store_true", help="Dumps data into json file"
)  # noqa: E501
args = parser.parse_args()
print(args.d)

asyncio.run(main(args.d))
