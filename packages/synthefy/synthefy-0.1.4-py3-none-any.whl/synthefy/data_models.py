from typing import Any, List, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel, field_validator


class SingleEvalSamplePayload(BaseModel):
    sample_id: Any
    history_timestamps: List[str]
    history_values: List[Optional[float]]
    target_timestamps: List[str]
    target_values: List[Optional[float]]
    forecast: bool = True
    metadata: bool = False
    leak_target: bool = False
    column_name: Optional[str] = None

    @field_validator("history_timestamps", "target_timestamps")
    @classmethod
    def validate_timestamps_not_empty(cls, v):
        """Validate that timestamp lists are not empty."""
        if not v:
            raise ValueError("Timestamps cannot be empty")
        return v

    @field_validator("history_values", "target_values")
    @classmethod
    def validate_values_not_empty(cls, v):
        """Validate that values lists are not empty."""
        if not v:
            raise ValueError("Values cannot be empty")
        return v

    @field_validator("history_values", "target_values")
    @classmethod
    def validate_values_json_compliant(cls, v):
        """Convert NaN values to None for JSON compliance."""
        if v is None:
            return v
        return [
            None if (isinstance(val, float) and np.isnan(val)) else val
            for val in v
        ]

    @field_validator("history_values", "target_values")
    @classmethod
    def validate_values_length_match_timestamps(cls, v, info):
        """Validate that values and timestamps have the same length."""
        if info.data.get("history_timestamps") and info.data.get(
            "history_values"
        ):
            if len(info.data["history_timestamps"]) != len(
                info.data["history_values"]
            ):
                raise ValueError(
                    f"History timestamps and values must have the same length. "
                    f"Got {len(info.data['history_timestamps'])} and {len(info.data['history_values'])}"
                )

        if info.data.get("target_timestamps") and info.data.get(
            "target_values"
        ):
            if len(info.data["target_timestamps"]) != len(
                info.data["target_values"]
            ):
                raise ValueError(
                    f"Target timestamps and values must have the same length. "
                    f"Got {len(info.data['target_timestamps'])} and {len(info.data['target_values'])}"
                )

        return v


class SingleSampleForecastPayload(BaseModel):
    model_config = {"protected_namespaces": ()}

    sample_id: Any
    timestamps: List[str]
    values: List[Optional[float]]
    model_name: str

    @field_validator("values")
    @classmethod
    def validate_values_json_compliant(cls, v):
        """Convert NaN values to None for JSON compliance."""
        if v is None:
            return v
        return [
            None if (isinstance(val, float) and np.isnan(val)) else val
            for val in v
        ]

    @field_validator("values")
    @classmethod
    def validate_values_length_match_timestamps(cls, v, info):
        """Validate that values and timestamps have the same length."""
        if info.data.get("timestamps") and len(info.data["timestamps"]) != len(
            v
        ):
            raise ValueError(
                f"Timestamps and values must have the same length. "
                f"Got {len(info.data['timestamps'])} and {len(v)}"
            )
        return v

    @field_validator("model_name")
    @classmethod
    def validate_model_name_not_empty(cls, v):
        """Validate that model name is not empty."""
        if not v or not v.strip():
            raise ValueError("model_name cannot be empty or whitespace")
        return v.strip()


class ForecastV2Request(BaseModel):
    samples: List[List[SingleEvalSamplePayload]]
    model: str

    @classmethod
    def from_dfs(
        cls,
        history_dfs: List[pd.DataFrame],
        target_dfs: List[pd.DataFrame],
        target_col: str,
        timestamp_col: str,
        metadata_cols: List[str],
        leak_cols: List[str],
        model: str,
    ) -> "ForecastV2Request":
        """
        Create a ForecastV2Request from pandas DataFrames.

        Args:
            history_dfs: List of DataFrames containing historical data
            target_dfs: List of DataFrames containing target data
            target_col: Name of the target column
            timestamp_col: Name of the timestamp column
            metadata_cols: List of metadata column names
            leak_cols: List of columns that should be marked as leak_target=True

        Returns:
            ForecastRequest with samples created from the DataFrames
        """
        # Validate inputs before processing
        cls._validate_dataframe_inputs(
            history_dfs,
            target_dfs,
            target_col,
            timestamp_col,
            metadata_cols,
            leak_cols,
        )

        samples = []

        for i, (history_df, target_df) in enumerate(
            zip(history_dfs, target_dfs)
        ):
            sample_row = []

            # Create sample for target column
            target_sample = SingleEvalSamplePayload(
                sample_id=target_col,
                history_timestamps=history_df[timestamp_col]
                .astype(str)
                .tolist(),
                history_values=cls._convert_nan_to_none(
                    history_df[target_col].tolist()
                ),
                target_timestamps=target_df[timestamp_col].astype(str).tolist(),
                target_values=cls._convert_nan_to_none(
                    target_df[target_col].tolist()
                ),
                forecast=True,
                metadata=False,
                leak_target=target_col in leak_cols,
                column_name=target_col,
            )
            sample_row.append(target_sample)

            # Create samples for metadata columns
            for col in metadata_cols:
                if col in history_df.columns and col in target_df.columns:
                    metadata_sample = SingleEvalSamplePayload(
                        sample_id=col,
                        history_timestamps=history_df[timestamp_col]
                        .astype(str)
                        .tolist(),
                        history_values=cls._convert_nan_to_none(
                            history_df[col].tolist()
                        ),
                        target_timestamps=target_df[timestamp_col]
                        .astype(str)
                        .tolist(),
                        target_values=cls._convert_nan_to_none(
                            target_df[col].tolist()
                        ),
                        forecast=False,
                        metadata=True,
                        leak_target=col in leak_cols,
                        column_name=col,
                    )
                    sample_row.append(metadata_sample)

            samples.append(sample_row)

        return cls(samples=samples, model=model)

    @staticmethod
    def _convert_nan_to_none(values):
        """Convert NaN values to None for JSON compliance."""
        return [
            None if (isinstance(val, float) and np.isnan(val)) else val
            for val in values
        ]

    @classmethod
    def _validate_dataframe_inputs(
        cls,
        history_dfs: List[pd.DataFrame],
        target_dfs: List[pd.DataFrame],
        target_col: str,
        timestamp_col: str,
        metadata_cols: List[str],
        leak_cols: List[str],
    ) -> None:
        """
        Validate DataFrame inputs before processing.

        Raises:
            ValueError: If validation fails
        """
        # Check that lists have the same length
        if len(history_dfs) != len(target_dfs):
            raise ValueError(
                f"history_dfs and target_dfs must have the same length. "
                f"Got {len(history_dfs)} and {len(target_dfs)}"
            )

        if not history_dfs:
            raise ValueError("history_dfs and target_dfs cannot be empty")

        # Check that all DataFrames have the same columns
        all_required_cols = {target_col, timestamp_col} | set(metadata_cols)

        for i, (history_df, target_df) in enumerate(
            zip(history_dfs, target_dfs)
        ):
            # Check history DataFrame columns
            missing_in_history = all_required_cols - set(history_df.columns)
            if missing_in_history:
                raise ValueError(
                    f"History DataFrame {i} is missing required columns: {missing_in_history}"
                )

            # Check target DataFrame columns
            missing_in_target = all_required_cols - set(target_df.columns)
            if missing_in_target:
                raise ValueError(
                    f"Target DataFrame {i} is missing required columns: {missing_in_target}"
                )

            # Check that all DataFrames have the same columns (for consistency)
            if i > 0:
                if set(history_dfs[0].columns) != set(history_df.columns):
                    raise ValueError(
                        f"All history DataFrames must have the same columns. "
                        f"DataFrame 0: {set(history_dfs[0].columns)}, "
                        f"DataFrame {i}: {set(history_df.columns)}"
                    )

                if set(target_dfs[0].columns) != set(target_df.columns):
                    raise ValueError(
                        f"All target DataFrames must have the same columns. "
                        f"DataFrame 0: {set(target_dfs[0].columns)}, "
                        f"DataFrame {i}: {set(target_df.columns)}"
                    )

        # Check that leak columns are a strict subset of metadata columns
        leak_set = set(leak_cols)
        metadata_set = set(metadata_cols)

        if not leak_set.issubset(metadata_set):
            invalid_leak_cols = leak_set - metadata_set
            raise ValueError(
                f"Leak columns must be a subset of metadata columns. "
                f"Invalid leak columns: {invalid_leak_cols}"
            )

        # Check that target_col is not in metadata_cols (to avoid duplication)
        if target_col in metadata_cols:
            raise ValueError(
                f"target_col '{target_col}' should not be in metadata_cols to avoid duplication"
            )

        # Check that timestamp_col is not in metadata_cols (to avoid confusion)
        if timestamp_col in metadata_cols:
            raise ValueError(
                f"timestamp_col '{timestamp_col}' should not be in metadata_cols to avoid confusion"
            )

    @field_validator("samples")
    @classmethod
    def validate_samples_structure(cls, v):
        """Validate that samples have consistent structure."""
        if not v:
            raise ValueError("samples cannot be empty")

        # Check that all sample rows have at least one sample
        for i, sample_row in enumerate(v):
            if not sample_row:
                raise ValueError(f"Sample row {i} cannot be empty")

            # Check that all samples in a row have the same timestamps
            if len(sample_row) > 1:
                first_timestamps = sample_row[0].history_timestamps
                first_target_timestamps = sample_row[0].target_timestamps

                for j, sample in enumerate(sample_row[1:], 1):
                    if sample.history_timestamps != first_timestamps:
                        raise ValueError(
                            f"All samples in row {i} must have the same history timestamps. "
                            f"Sample 0: {len(first_timestamps)} timestamps, "
                            f"Sample {j}: {len(sample.history_timestamps)} timestamps"
                        )

                    if sample.target_timestamps != first_target_timestamps:
                        raise ValueError(
                            f"All samples in row {i} must have the same target timestamps. "
                            f"Sample 0: {len(first_target_timestamps)} timestamps, "
                            f"Sample {j}: {len(sample.target_timestamps)} timestamps"
                        )

        return v

    @field_validator("model")
    @classmethod
    def validate_model_name(cls, v):
        """Validate that model name is not empty."""
        if not v or not v.strip():
            raise ValueError("model cannot be empty or whitespace")
        return v.strip()


class ForecastV2Response(BaseModel):
    forecasts: List[List[SingleSampleForecastPayload]]

    def to_dfs(self) -> List[pd.DataFrame]:
        """
        Convert the ForecastResponse to a list of DataFrames.

        Returns:
            List of DataFrames where each DataFrame contains forecast columns.
            Empty timestamps/values are converted to NaN columns.
        """
        result_dfs = []

        for forecast_row in self.forecasts:
            # Find the first valid timestamp set (all timestamps in a row are assumed equal)
            timestamps = None
            for forecast in forecast_row:
                if forecast.timestamps and forecast.values:
                    timestamps = forecast.timestamps
                    break

            if not timestamps:
                # If no valid timestamps, return empty DataFrame
                result_dfs.append(pd.DataFrame())
                continue

            # Create DataFrame with timestamps as a regular column
            df = pd.DataFrame()
            df["timestamps"] = timestamps

            # Add each forecast as a column
            for forecast in forecast_row:
                column_name = forecast.sample_id

                if not forecast.timestamps or not forecast.values:
                    # Empty timestamps/values indicate NaN column
                    pass  # df[column_name] = np.nan
                else:
                    # Convert None back to NaN for DataFrame compatibility
                    values = [
                        np.nan if val is None else val
                        for val in forecast.values
                    ]
                    df[column_name] = values

            result_dfs.append(df)

        return result_dfs
