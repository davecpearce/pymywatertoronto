"""Constants for MyWaterToronto library."""
from __future__ import annotations

API_BASE_URL = "https://secure.toronto.ca/cc_api/svcaccount_v1/WaterAccount"
API_VALIDATE_URL = "{}{}".format(API_BASE_URL, "/validate")
API_ACCOUNTDETAILS_URL = "{}{}".format(API_BASE_URL, "/accountdetails")  # noqa: E501
API_CONSUMPTION_URL = "{}{}".format(API_BASE_URL, "/consumption")  # noqa: E501

HTTP_MOVED_TEMPORARILY: int = 302
HTTP_HEADERS: dict[str, str] = {"content-type": "application/json"}

CONSUMPTION_RESULT_OK: int = 200
BAD_REQUEST: int = 400

API_OP_VALIDATE: str = "VALIDATE"

"""Data keys for Validation"""
KEY_REF_TOKEN = "refToken"
KEY_VALIDATE_RESPONSE = "validateResponse"
KEY_STATUS = "status"

"""Data constants for Validation status responses"""
STATUS_VALIDATION_ERROR = "It is session timeout or it is not validated yet"
STATUS_FAILURE = "FAILURE"

"""Data keys for Account Details"""
KEY_PREMISE_LIST = "premiseList"
KEY_ACCOUNT_TYPE = "accountType"
KEY_ACCOUINT = "account"
KEY_LINKED_ACCOUNT_LIST = "linkedAccountList"

"""Data keys for Premise"""
KEY_PREMISE_ID = "premiseId"
KEY_ADDRESS = "address"
KEY_ADDRESS_NUM = "addrNum"
KEY_ADDRESS_SUF = "addrSuf"
KEY_ADDRESS_NAME = "addrName"
KEY_ADDRESS_CITY = "addrCity"
KEY_ADDRESS_STATE = "addrState"
KEY_ADDRESS_ZIP = "addrZip"
KEY_DISTRICT = "district"
KEY_WARD = "ward"
KEY_METER_LIST = "meterList"

"""Data keys for Meter"""
KEY_METER_NUMBER = "meterNumber"
KEY_METER_MIU = "miu"
KEY_METER_MANUFACTURER_TYPE = "meterManufacturerType"
KEY_METER_SIZE = "meterSize"
KEY_METER_CLASS = "meterClass"
KEY_METER_INSTALL_DATE = "meterInstallDate"
KEY_METER_FIRST_READ_DATE = "firstReadDate"
KEY_METER_LAST_READ_DATE = "lastReadDate"
KEY_METER_LAST_READING = "lastReading"
KEY_METER_UNIT_OF_MEASURE = "unitofMeasure"

"""Data keys for Consumption"""
KEY_CONSUMPTION = "consumption"
KEY_CONSUMPTION_SUMMARY = "summary"
KEY_CONSUMPTION_INTERVAL_LIST = "intervalList"
KEY_CONSUMPTION_DATA = "consumption_data"
KEY_CONSUMPTION_UNITOFMEASURE = "unit_of_measure"

"""Data keys for Consumption Interval"""
KEY_CONSUMPTION_INTERVAL_TYPE = "consumption_value_type"
KEY_CONSUMPTION_VALUE_TYPE = "interval"
KEY_CONSUMPTION_START_DATE = "start_date"
KEY_CONSUMPTION_END_DATE = "end_date"
KEY_CONSUMPTION_TOTAL = "consumptionTotal"
KEY_CONSUMPTION_MIN = "consumptionMin"
KEY_CONSUMPTION_MAX = "consumptionMax"
KEY_CONSUMPTION_AVG = "consumptionAvg"
KEY_ERROR_MESSAGE = "errorMessage"
KEY_ERROR_STRING = "errorString"
INTERVAL_HOUR = "Hour"
INTERVAL_DAY = "Day"
INTERVAL_MONTH = "Month"

"""Data keys for general API responses"""
KEY_RESULT_CODE = "resultCode"

"""aiohttp_retry settings"""
AIOHTTP_RETRY_ATTEMPTS = 10
