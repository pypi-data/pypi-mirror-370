import os
from typing import List

import httpx
import pandas as pd

from synthefy.data_models import ForecastV2Request, ForecastV2Response

BASE_URL = "https://prod.synthefy.com"
ENDPOINT = "/api/v2/foundation_models/forecast/stream"


class SynthefyAPIClient:
    def __init__(self, api_key: str | None = None, timeout: float = 120.0):
        if api_key is None:
            api_key = os.getenv("SYNTHEFY_API_KEY")
            if api_key is None:
                raise ValueError(
                    "API key must be provided either as a parameter or through SYNTHEFY_API_KEY environment variable"
                )

        self.client = httpx.Client(base_url=BASE_URL, timeout=timeout)
        self.api_key = api_key

    def forecast(self, request: ForecastV2Request) -> ForecastV2Response:
        response = self.client.post(
            ENDPOINT,
            json=request.model_dump(),
            headers={"X-API-KEY": self.api_key},
        )

        response.raise_for_status()
        response_data = response.json()
        return ForecastV2Response(**response_data)

    def forecast_dfs(
        self,
        history_dfs: List[pd.DataFrame],
        target_dfs: List[pd.DataFrame],
        target_col: str,
        timestamp_col: str,
        metadata_cols: List[str],
        leak_cols: List[str],
        model: str,
    ) -> List[pd.DataFrame]:
        request = ForecastV2Request.from_dfs(
            history_dfs,
            target_dfs,
            target_col,
            timestamp_col,
            metadata_cols,
            leak_cols,
            model,
        )

        response = self.forecast(request)

        return response.to_dfs()
