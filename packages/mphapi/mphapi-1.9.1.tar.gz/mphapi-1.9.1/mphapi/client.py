import urllib.parse
from typing import Annotated, Any, Mapping, Optional, Sequence

import requests
from pydantic import BaseModel, StrictBool, TypeAdapter

from .claim import Claim, RateSheet
from .fields import camel_case_model_config, field_name
from .response import Response, Responses

Header = Mapping[str, str | bytes | None]


class PriceConfig(BaseModel):
    """PriceConfig is used to configure the behavior of the pricing API"""

    model_config = camel_case_model_config

    contract_ruleset: Optional[str] = None
    """set to the name of the ruleset to use for contract pricing"""

    price_zero_billed: Optional[StrictBool] = False
    """set to true to price claims with zero billed amounts (default is false)"""

    is_commercial: Optional[StrictBool] = False
    """set to true to crosswalk codes from commercial codes Medicare won't pay for to substitute codes they do pay for (e.g. 99201 to G0463)"""

    disable_cost_based_reimbursement: Optional[StrictBool] = False
    """set to true to disable cost-based reimbursement for line items paid as a percent of cost"""

    use_commercial_synthetic_for_not_allowed: Optional[StrictBool] = False
    """set to true to use a synthetic Medicare price for line-items that are not allowed by Medicare"""

    use_drg_from_grouper: Annotated[
        Optional[StrictBool], field_name("useDRGFromGrouper")
    ] = False
    """set to true to always use the DRG from the inpatient grouper"""

    use_best_drg_price: Annotated[StrictBool, field_name("useBestDRGPrice")]
    """set to true to use the best DRG price between the price on the claim and the price from the grouper"""

    override_threshold: Optional[float] = 0
    """set to a value greater than 0 to allow the pricer flexibility to override NCCI edits and other overridable errors and return a price"""

    include_edits: Optional[StrictBool] = False
    """set to true to include edit details in the response"""

    continue_on_edit_fail: Optional[StrictBool] = False
    """set to true to continue to price the claim even if there are edit failures"""

    continue_on_provider_match_fail: Optional[StrictBool] = False
    """set to true to continue with a average provider for the geographic area if the provider cannot be matched"""

    disable_machine_learning_estimates: Optional[StrictBool] = False
    """set to true to disable machine learning estimates (applies to estimates only)"""

    assume_impossible_anesthesia_units_are_minutes: Optional[StrictBool] = False
    """set to true to divide impossible anesthesia units by 15 (max of 96 anesthesia units per day) (default is false)"""

    fallback_to_max_anesthesia_units_per_day: Optional[StrictBool] = False
    """set to true to fallback to the maximum anesthesia units per day (default is false which will error if there are more than 96 anesthesia units per day)"""

    allow_partial_results: Optional[StrictBool] = False
    """set to true to return partially repriced claims. This can be useful to get pricing on non-erroring line items, but should be used with caution"""


# It may be a bit jarring to see this import not at the top of the file. This is
# intentional as `.pricing` depends on `PriceConfig`.
from .pricing import Pricing  # noqa: E402


class Client:
    url: str
    headers: Header

    def __init__(self, apiKey: str, isTest: bool = False, url: str | None = None):
        if url is None:
            if isTest:
                self.url = "https://api-test.myprice.health"
            else:
                self.url = "https://api.myprice.health"
        else:
            self.url = url

        self.headers = {"x-api-key": apiKey}

    def _do_request(
        self,
        path: str,
        json: Any | None,
        method: str = "POST",
        headers: Header = {},
    ) -> requests.Response:
        return requests.request(
            method,
            urllib.parse.urljoin(self.url, path),
            json=json,
            headers={**self.headers, **headers},
        )

    def _receive_response[Model: BaseModel](
        self,
        path: str,
        body: BaseModel,
        response_model: type[Model],
        method: str = "POST",
        headers: Header = {},
    ) -> Model:
        """
        Raises:
            ValueError
                When response cannot be decoded.
            mphapi.APIError
                The error returned when the api returns an error.
        """

        response = self._do_request(
            path,
            body.model_dump(mode="json", by_alias=True, exclude_none=True),
            method,
            headers,
        )

        return (
            Response[response_model]
            .model_validate_json(response.content, strict=True)
            .result()
        )

    def _receive_responses[Model: BaseModel](
        self,
        path: str,
        body: Sequence[BaseModel],
        response_model: type[Model],
        method: str = "POST",
        headers: Header = {},
    ) -> list[Model]:
        """
        Raises:
            ValueError
                When response cannot be decoded.
            mphapi.APIError
                The error returned when the api returns an error.
        """

        response = self._do_request(
            path,
            TypeAdapter(type(body)).dump_python(
                body, mode="json", by_alias=True, exclude_none=True
            ),
            method,
            headers,
        )

        return (
            Responses[response_model]
            .model_validate_json(response.content, strict=True)
            .results()
        )

    def estimate_rate_sheet(self, *inputs: RateSheet) -> list[Pricing]:
        """
        Raises:
            ValueError
                When response cannot be decoded.
            mphapi.APIError
                The error returned when the api returns an error.
        """

        return self._receive_responses(
            "/v1/medicare/estimate/rate-sheet",
            inputs,
            Pricing,
        )

    def estimate_claims(self, config: PriceConfig, *inputs: Claim) -> list[Pricing]:
        """
        Raises:
            ValueError
                When response cannot be decoded.
            mphapi.APIError
                The error returned when the api returns an error.
        """

        return self._receive_responses(
            "/v1/medicare/estimate/claims",
            inputs,
            Pricing,
            headers=self._get_price_headers(config),
        )

    def price(self, config: PriceConfig, input: Claim) -> Pricing:
        """
        Raises:
            ValueError
                When response cannot be decoded.
            mphapi.APIError
                The error returned when the api returns an error.
        """

        return self._receive_response(
            "/v1/medicare/price/claim",
            input,
            Pricing,
            headers=self._get_price_headers(config),
        )

    def price_batch(self, config: PriceConfig, *input: Claim) -> list[Pricing]:
        """
        Raises:
            ValueError
                When response cannot be decoded.
            mphapi.APIError
                The error returned when the api returns an error.
        """

        return self._receive_responses(
            "/v1/medicare/price/claims",
            input,
            Pricing,
            headers=self._get_price_headers(config),
        )

    def _get_price_headers(self, config: PriceConfig) -> Header:
        headers: Header = {}
        if config.price_zero_billed:
            headers["price-zero-billed"] = "true"

        if config.is_commercial:
            headers["is-commercial"] = "true"

        if config.disable_cost_based_reimbursement:
            headers["disable-cost-based-reimbursement"] = "true"

        if config.use_commercial_synthetic_for_not_allowed:
            headers["use-commercial-synthetic-for-not-allowed"] = "true"

        if config.override_threshold is not None and config.override_threshold > 0:
            headers["override-threshold"] = str(config.override_threshold)

        if config.include_edits:
            headers["include-edits"] = "true"

        if config.use_drg_from_grouper:
            headers["use-drg-from-grouper"] = "true"

        if config.use_best_drg_price:
            headers["use-best-drg-price"] = "true"

        if config.continue_on_edit_fail:
            headers["continue-on-edit-fail"] = "true"

        if config.continue_on_provider_match_fail:
            headers["continue-on-provider-match-fail"] = "true"

        if config.disable_machine_learning_estimates:
            headers["disable-machine-learning-estimates"] = "true"

        return headers
