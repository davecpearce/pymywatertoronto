""" Python wrapper for getting water consumption data from MyWaterToronto. """

from __future__ import annotations

import json
import logging
from aiohttp import ClientResponse, ClientSession
from aiohttp_retry import ExponentialRetry, RetryClient
from datetime import date, datetime
from http import HTTPStatus
from pytz import timezone, utc
from typing import Any, cast

from .const import (
    AIOHTTP_RETRY_ATTEMPTS,
    API_ACCOUNTDETAILS_URL,
    API_CONSUMPTION_URL,
    API_OP_VALIDATE,
    API_VALIDATE_URL,
    BAD_REQUEST,
    CONSUMPTION_RESULT_OK,
    HTTP_HEADERS,
    HTTP_MOVED_TEMPORARILY,
    INTERVAL_DAY,
    INTERVAL_HOUR,
    INTERVAL_MONTH,
    KEY_ADDRESS,
    KEY_CONSUMPTION,
    KEY_CONSUMPTION_DATA,
    KEY_CONSUMPTION_END_DATE,
    KEY_CONSUMPTION_INTERVAL_TYPE,
    KEY_CONSUMPTION_START_DATE,
    KEY_CONSUMPTION_SUMMARY,
    KEY_CONSUMPTION_TOTAL,
    KEY_CONSUMPTION_UNITOFMEASURE,
    KEY_CONSUMPTION_VALUE_TYPE,
    KEY_ERROR_MESSAGE,
    KEY_ERROR_STRING,
    KEY_METER_FIRST_READ_DATE,
    KEY_METER_LAST_READ_DATE,
    KEY_METER_LAST_READING,
    KEY_METER_LIST,
    KEY_METER_MIU,
    KEY_METER_NUMBER,
    KEY_METER_UNIT_OF_MEASURE,
    KEY_PREMISE_ID,
    KEY_PREMISE_LIST,
    KEY_REF_TOKEN,
    KEY_RESULT_CODE,
    KEY_STATUS,
    KEY_VALIDATE_RESPONSE,
    STATUS_FAILURE,
    STATUS_VALIDATION_ERROR,
)
from .enums import ConsumptionBuckets, LastPaymentMethod
from .errors import (
    AccountDetailsError,
    AccountNotValidatedError,
    ApiError,
    SessionValidationError,
    ValidateAccountInfoError,
)
from .format_date import (
    format_date,
    format_start_month,
    format_start_week,
    format_start_year,
)

_LOGGER = logging.getLogger(__name__)


class MyWaterToronto:
    """Main class to perform MyWaterToronto API requests."""

    def __init__(
        self,
        session: ClientSession,
        account_number: str,
        client_number: str,
        last_name: str,
        postal_code: str,
        last_payment_method: LastPaymentMethod,
    ) -> None:
        """Initialize."""
        self._session = session
        self._retry_client = RetryClient(session)
        self._account_number = account_number
        self._client_number = client_number
        self._last_name = last_name
        self._postal_code = postal_code
        self._last_payment_method = last_payment_method

        self._ref_token: str = None

        self._account_details: dict[str, Any] = None

        self._consumption_buckets = None

        self._retry_options = ExponentialRetry(
            attempts=AIOHTTP_RETRY_ATTEMPTS,
            statuses={BAD_REQUEST},
            evaluate_response_callback=self._async_evaluate_response,
        )

    async def async_validate_account(self) -> bool:
        """Validate account information with MyWaterToronto."""

        url = API_VALIDATE_URL

        payload = {
            "API_OP": API_OP_VALIDATE,
            "ACCOUNT_NUMBER": self.account_number_full,
            "LAST_NAME": self._last_name,
            "POSTAL_CODE": self._postal_code,
            "LAST_PAYMENT_METHOD": self._last_payment_method.value,
        }

        async with self._retry_client.post(
            url=url,
            retry_options=self._retry_options,
            headers=HTTP_HEADERS,
            json=payload,
            verify_ssl=False,
        ) as resp:
            if (resp.status == HTTP_MOVED_TEMPORARILY) or (
                resp.real_url.name == "something-went-wrong.html"
            ):
                raise ValidateAccountInfoError("Invalid account information")
            if resp.status != HTTPStatus.OK:
                json.loads(await resp.text())
                raise ApiError(
                    f"Invalid response from MyWaterToronto API: {resp.status}"
                )
            _LOGGER.debug(
                "Data retrieved from %s, status: %s", url, resp.status
            )  # noqa: E501
            data = await resp.json()

        _LOGGER.debug(
            "Data retrieved from validate --> %s", json.dumps(data, indent=4)
        )  # noqa: E501

        if KEY_VALIDATE_RESPONSE not in data:
            raise (
                f"{KEY_VALIDATE_RESPONSE} key could not be found in MyWaterToronto Validation Response: {data}"  # noqa: E501
            )

        if KEY_REF_TOKEN not in data[KEY_VALIDATE_RESPONSE]:
            raise ApiError(
                f"{KEY_REF_TOKEN} key could not be found in MyWaterToronto Validation Response: {data}"  # noqa: E501
            )
        self._ref_token = data[KEY_VALIDATE_RESPONSE][KEY_REF_TOKEN]

        _LOGGER.debug(
            "Ref token retrieved from validate --> %s", self._ref_token
        )  # noqa: E501

        return True

    async def _async_evaluate_response(self, response: ClientResponse) -> bool:
        data = await response.json()
        if KEY_RESULT_CODE in data:
            result_code = data[KEY_RESULT_CODE]
            if result_code == BAD_REQUEST:
                return False

        return True

    async def async_get_account_details(self) -> dict[str, Any]:
        """Get the account details from MyWaterToronto."""

        # Check if there is a ref token"""
        if not self._ref_token:
            raise AccountNotValidatedError(
                "The account has not been validated yet"
            )  # noqa: E501

        params_json = {
            "API_OP": "ACCOUNTDETAILS",
            "ACCOUNT_NUMBER": self.account_number_full,
        }
        params = {"refToken": self._ref_token, "json": json.dumps(params_json)}

        url = API_ACCOUNTDETAILS_URL
        async with self._retry_client.get(
            url=url,
            retry_options=self._retry_options,
            headers=HTTP_HEADERS,
            params=params,
            verify_ssl=False,
        ) as resp:

            if resp.status != HTTPStatus.OK:
                json.loads(await resp.text())
                raise ApiError(
                    f"Invalid response from MyWaterToronto API: {resp.status}"
                )
            _LOGGER.debug(
                "Data retrieved from %s, status: %s", url, resp.status
            )  # noqa: E501
            data = await resp.json()

        _LOGGER.debug(
            "Data retrieved from account details --> %s",
            json.dumps(data, indent=4),  # noqa: E501
        )

        if KEY_PREMISE_LIST not in data:
            raise AccountDetailsError(
                f"Premise list could not be found in MyWaterToronto Account Details response: {data}"  # noqa: E501
            )

        if KEY_METER_LIST not in data[KEY_PREMISE_LIST][0]:
            raise AccountDetailsError(
                f"Meter list could not be found in MyWaterToronto Account Details response: {data}"  # noqa: E501
            )

        self._account_details = cast(
            dict[str, Any], data if isinstance(data, dict) else data[0]
        )
        return self.account_details

    async def _async_update_consumption_buckets(
        self,
        meter: dict[str, Any],
        current_date: date | None = None,
    ) -> None:

        if current_date:
            _current_date = current_date
        else:
            _current_date = utc.localize(datetime.utcnow()).astimezone(
                timezone("Canada/Eastern")
            )

        if _current_date.month == 1:
            ytd_interval = INTERVAL_DAY
        else:
            ytd_interval = INTERVAL_MONTH

        self._consumption_buckets = {
            ConsumptionBuckets.TOTAL_USAGE: {
                KEY_CONSUMPTION_VALUE_TYPE: ConsumptionBuckets.TOTAL_USAGE.value,  # noqa: E501
                KEY_CONSUMPTION_INTERVAL_TYPE: INTERVAL_MONTH,
                KEY_CONSUMPTION_START_DATE: meter[KEY_METER_FIRST_READ_DATE],
                KEY_CONSUMPTION_END_DATE: format_date(_current_date),
            },
            ConsumptionBuckets.TODAY_USAGE: {
                KEY_CONSUMPTION_VALUE_TYPE: ConsumptionBuckets.TODAY_USAGE.value,  # noqa: E501
                KEY_CONSUMPTION_INTERVAL_TYPE: INTERVAL_HOUR,
                KEY_CONSUMPTION_START_DATE: format_date(_current_date),
                KEY_CONSUMPTION_END_DATE: format_date(_current_date),
            },
            ConsumptionBuckets.WEEK_TO_DATE_USAGE: {
                KEY_CONSUMPTION_VALUE_TYPE: ConsumptionBuckets.WEEK_TO_DATE_USAGE.value,  # noqa: E501
                KEY_CONSUMPTION_INTERVAL_TYPE: INTERVAL_DAY,
                KEY_CONSUMPTION_START_DATE: format_start_week(_current_date),
                KEY_CONSUMPTION_END_DATE: format_date(_current_date),
            },
            ConsumptionBuckets.MONTH_TO_DATE_USAGE: {
                KEY_CONSUMPTION_VALUE_TYPE: ConsumptionBuckets.MONTH_TO_DATE_USAGE.value,  # noqa: E501
                KEY_CONSUMPTION_INTERVAL_TYPE: INTERVAL_DAY,
                KEY_CONSUMPTION_START_DATE: format_start_month(_current_date),
                KEY_CONSUMPTION_END_DATE: format_date(_current_date),
            },
            ConsumptionBuckets.YEAR_TO_DATE_USAGE: {
                KEY_CONSUMPTION_VALUE_TYPE: ConsumptionBuckets.YEAR_TO_DATE_USAGE.value,  # noqa: E501
                KEY_CONSUMPTION_INTERVAL_TYPE: ytd_interval,
                KEY_CONSUMPTION_START_DATE: format_start_year(_current_date),
                KEY_CONSUMPTION_END_DATE: format_date(_current_date),
            },
        }

    async def _async_get_meter_info(
        self,
        meter_number: str,
    ) -> dict[str, Any]:

        selected_meter = None

        for premise in self._account_details[KEY_PREMISE_LIST]:
            for meter in premise[KEY_METER_LIST]:
                if meter[KEY_METER_NUMBER] == meter_number:
                    selected_meter = meter

        return cast(
            dict[str, Any],
            selected_meter
            if isinstance(selected_meter, dict)
            else selected_meter[0],  # noqa: E501
        )

    async def async_get_consumption(self, buckets=None) -> dict[str, Any]:
        """Get the meter consumption from MyWaterToronto."""

        _LOGGER.debug("Getting consumption data for account")

        account_consumption = {}
        account_consumption[KEY_PREMISE_LIST] = {}

        for premise in self.account_details[KEY_PREMISE_LIST]:
            _LOGGER.debug(
                "Getting consumption data for Premise ID: %s, address: %s",
                premise[KEY_PREMISE_ID],
                premise[KEY_ADDRESS],
            )

            premise_consumption = {
                KEY_ADDRESS: premise[KEY_ADDRESS],
                KEY_METER_LIST: {},
            }

            for meter in premise[KEY_METER_LIST]:
                meter_consumption = await self.async_get_meter_consumption(
                    meter, buckets=buckets
                )

                premise_consumption[KEY_METER_LIST][
                    meter[KEY_METER_NUMBER]
                ] = meter_consumption

            account_consumption[KEY_PREMISE_LIST][
                premise[KEY_PREMISE_ID]
            ] = premise_consumption

        return account_consumption

    async def async_get_meter_consumption(
        self, meter: dict[str, Any], buckets=None
    ) -> dict[str, Any]:
        """Get the meter consumption from MyWaterToronto for the specified meter."""  # noqa: E501

        _LOGGER.debug(
            "Getting consumption data for meter: %s", meter[KEY_METER_NUMBER]
        )  # noqa: E501

        meter_data = {
            KEY_METER_FIRST_READ_DATE: meter[KEY_METER_FIRST_READ_DATE],
            KEY_METER_LAST_READ_DATE: meter[KEY_METER_LAST_READ_DATE],
            KEY_CONSUMPTION_DATA: {},
        }

        for bucket in ConsumptionBuckets:
            """If a subset of buckets was selected, check if current bucket is
            selected otherwise skip bucket"""
            if buckets:
                if bucket not in buckets:
                    continue

            try:
                consumption = (
                    await self.async_get_meter_consumption_for_bucket(  # noqa E501
                        meter, consumption_bucket=bucket
                    )
                )
            except Exception as error:
                raise Exception("Error '%s'" % (error))
            else:
                _LOGGER.debug(
                    "Consumption for bucket %s is %s%s",
                    bucket.value,
                    consumption[KEY_CONSUMPTION],
                    consumption[KEY_CONSUMPTION_UNITOFMEASURE],
                )
                meter_data[KEY_CONSUMPTION_DATA][
                    bucket.value
                ] = consumption  # noqa E501

        return meter_data

    async def async_get_meter_consumption_for_bucket(  # noqa C901
        self,
        meter: dict[str, Any],
        consumption_bucket: ConsumptionBuckets | None,
    ) -> dict[str, Any]:
        """Get the meter consumption from MyWaterToronto for the specified bucket."""  # noqa: E501

        consumption_data = None

        if not consumption_bucket:
            _consumption_bucket = ConsumptionBuckets.TOTAL_USAGE
        else:
            _consumption_bucket = consumption_bucket

        if _consumption_bucket == ConsumptionBuckets.TOTAL_USAGE:
            # Add the current reading from account details
            consumption_data = {
                KEY_CONSUMPTION: meter[KEY_METER_LAST_READING].lstrip("0"),
                KEY_CONSUMPTION_UNITOFMEASURE: meter[
                    KEY_METER_UNIT_OF_MEASURE
                ],  # noqa: E501
            }
        else:
            # Check if there is a ref token
            if not self._ref_token:
                raise AccountNotValidatedError(
                    "The account has not been validated yet"
                )  # noqa: E501

            # Check if the consumption buckets have been defined
            if not self._consumption_buckets:
                await self._async_update_consumption_buckets(meter)

            consumption_bucket = self._consumption_buckets[_consumption_bucket]

            params_json = {
                "API_OP": "CONSUMPTION",
                "ACCOUNT_NUMBER": self.account_number_full,
                "MIU_ID": meter[KEY_METER_MIU],
                "START_DATE": consumption_bucket[KEY_CONSUMPTION_START_DATE],
                "END_DATE": consumption_bucket[KEY_CONSUMPTION_END_DATE],
                "INTERVAL_TYPE": consumption_bucket[
                    KEY_CONSUMPTION_INTERVAL_TYPE
                ],  # noqa: E501
            }

            params = {
                "refToken": self._ref_token,
                "json": json.dumps(params_json),
            }  # noqa: E501

            _LOGGER.debug("Params to retrieve consumption data: %s", params)

            url = API_CONSUMPTION_URL

            async with self._retry_client.get(
                url=url,
                retry_options=self._retry_options,
                headers=HTTP_HEADERS,
                params=params,
                verify_ssl=False,
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    error_text = json.loads(await resp.text())
                    raise ApiError(
                        f"Invalid response from MyWaterToronto Consumption API: {error_text}"  # noqa: E501
                    )
                if resp.content_type != "application/json":
                    raise ApiError(
                        "Response is not in application/json format form MyWaterToronto Consumption API"  # noqa: E501
                    )

                _LOGGER.debug(
                    "Data retrieved from %s, status: %s", url, resp.status
                )  # noqa: E501
                data = await resp.json()

            _LOGGER.debug(
                "Data retrieved from meter consumption --> %s",
                json.dumps(data, indent=4),
            )

            if KEY_RESULT_CODE not in data:
                if KEY_VALIDATE_RESPONSE in data:
                    validate_response = data[KEY_VALIDATE_RESPONSE]
                    status = validate_response[KEY_STATUS]
                    if status == STATUS_FAILURE:
                        error_message = validate_response[KEY_ERROR_MESSAGE]
                        if error_message == STATUS_VALIDATION_ERROR:
                            raise SessionValidationError(
                                "Session has timed out or it has not been validated yet"  # noqa: E501
                            )
                        else:
                            raise ApiError("Invalid consumption data returned")

            result_code = data[KEY_RESULT_CODE]

            if result_code == BAD_REQUEST:
                """
                The MyWaterToronto data returns a "Bad Request" error string
                when there is no data, typically for hourly data request
                """

                consumption_value = 0
            elif result_code != CONSUMPTION_RESULT_OK:
                raise ApiError(
                    f"Error returned from consumption data - resultCode: {result_code}, errorString: {data[KEY_ERROR_STRING]}"  # noqa: E501
                )
            else:
                if KEY_CONSUMPTION_SUMMARY not in data:
                    raise ApiError(
                        f"Consumption summary could not be found in MyWaterToronto Consumption response: {data}"  # noqa: E501
                    )

                if KEY_CONSUMPTION_TOTAL in data[KEY_CONSUMPTION_SUMMARY]:
                    consumption_value = data[KEY_CONSUMPTION_SUMMARY][
                        KEY_CONSUMPTION_TOTAL
                    ]  # noqa: E501
                else:
                    consumption_value = 0

            consumption_data = {
                KEY_CONSUMPTION: consumption_value,
                KEY_CONSUMPTION_UNITOFMEASURE: meter[
                    KEY_METER_UNIT_OF_MEASURE
                ],  # noqa: E501
            }

        return consumption_data

    @property
    def account_number_full(self) -> str | None:
        """Return full account number."""
        return self._account_number + "-" + self._client_number

    @property
    def account_details(self) -> dict[str, Any] | None:
        """Return account details."""
        return self._account_details
