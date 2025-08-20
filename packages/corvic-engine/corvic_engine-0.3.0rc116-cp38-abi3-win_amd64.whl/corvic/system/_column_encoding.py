import math
from typing import Final, cast

import numpy as np
import polars as pl
import structlog

REFERENCE_YEAR: Final = 1900
"""Reference year for normalizing year in Datetime encoder"""

MAX_NUMBER_OF_YEARS: Final = 200
"""Maximum number of years for normalizing year in Datetime encoder"""

_logger = structlog.get_logger()


def encode_one_hot(to_encode: pl.Series) -> tuple[pl.Series, list[str]]:
    encoded = to_encode.to_dummies()
    return (
        encoded.select(
            pl.concat_list(pl.all()).alias("val").cast(pl.List(pl.Boolean))
        ).to_series(),
        encoded.columns,
    )


def encode_min_max_scale(
    to_encode: pl.Series, range_min: float, range_max: float
) -> pl.Series:
    from sklearn.preprocessing import MinMaxScaler

    encoder = MinMaxScaler(
        feature_range=(
            range_min,
            range_max,
        )
    )
    return pl.Series(
        encoder.fit_transform(to_encode.to_numpy().reshape(-1, 1)).flatten()
    )


def encode_label_boolean(
    to_encode: pl.Series, neg_label: int, pos_label: int
) -> pl.Series:
    from sklearn.preprocessing import LabelBinarizer

    encoder = LabelBinarizer(
        neg_label=neg_label,
        pos_label=pos_label,
    )
    return pl.Series(encoder.fit_transform(to_encode.to_numpy().reshape(-1)))


def encode_label(to_encode: pl.Series, *, normalize: bool) -> pl.Series:
    from sklearn.preprocessing import LabelEncoder

    encoder = LabelEncoder()
    encoded = encoder.fit_transform(to_encode.to_numpy().reshape(-1)).flatten()
    # `classes_` is only set after fit,
    # Creating custom typestubs will not solve this typing issue.
    if normalize and hasattr(encoder, "classes_"):
        classes_ = cast(list[int], encoder.classes_)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        max_class: int = len(classes_) - 1
        if max_class > 0:
            encoded = encoded.astype(np.float64)
            encoded /= max_class

    return pl.Series(encoded)


def encode_kbins(
    to_encode: pl.Series, n_bins: int, method: str, strategy: str
) -> pl.Series:
    from sklearn.preprocessing import KBinsDiscretizer

    encoder = KBinsDiscretizer(
        n_bins=n_bins,
        encode=method,
        strategy=strategy,
        dtype=np.float32,
    )
    return pl.Series(
        encoder.fit_transform(to_encode.to_numpy().reshape(-1, 1)).flatten()
    )


def encode_boolean(to_encode: pl.Series, threshold: float) -> pl.Series:
    from sklearn.preprocessing import Binarizer

    encoder = Binarizer(
        threshold=threshold,
    )
    return pl.Series(
        encoder.fit_transform(to_encode.to_numpy().reshape(-1, 1)).flatten()
    )


def encode_max_abs_scale(to_encode: pl.Series) -> pl.Series:
    from sklearn.preprocessing import MaxAbsScaler

    encoder = MaxAbsScaler()
    try:
        encoded = encoder.fit_transform(
            np.nan_to_num(to_encode.to_numpy()).reshape(-1, 1)
        ).flatten()
    except ValueError:
        encoded = np.array([])

    return pl.Series(encoded)


def encode_standard_scale(
    to_encode: pl.Series, *, with_mean: bool, with_std: bool
) -> pl.Series:
    from sklearn.preprocessing import StandardScaler

    encoder = StandardScaler(
        with_mean=with_mean,
        with_std=with_std,
    )
    return pl.Series(
        encoder.fit_transform(to_encode.to_numpy().reshape(-1, 1)).flatten()
    )


def encode_duration(to_encode: pl.Series) -> pl.Series:
    if to_encode.dtype != pl.Duration:
        raise ValueError("Invalid arguments, expected a duration series")
    if to_encode.is_null().all():
        return pl.zeros(len(to_encode), dtype=pl.Float32, eager=True)

    return to_encode.dt.total_seconds().cast(pl.Float32).fill_null(0.0)


def _get_cyclic_encoding(
    to_encode: pl.Series,
    period: int,
) -> tuple[pl.Series, pl.Series]:
    sine_series = (
        (2 * math.pi * to_encode / period).sin().alias(f"{to_encode.name}_sine")
    )
    cosine_series = (
        (2 * math.pi * to_encode / period).cos().alias(f"{to_encode.name}_cosine")
    )
    return sine_series, cosine_series


def encode_datetime(to_encode: pl.Series) -> pl.Series:
    match to_encode.dtype:
        case pl.Date | pl.Time:
            pass
        case pl.Datetime:
            to_encode = to_encode.dt.replace_time_zone("UTC")
        case _:
            raise ValueError(
                "Invalid arguments column could not be endoded as datetime"
            )

    if to_encode.is_null().all():
        zero_vector = pl.zeros(11, dtype=pl.Float32, eager=True)
        return pl.Series([zero_vector] * len(to_encode), dtype=pl.List(pl.Float32))

    n = len(to_encode)
    year_norm = pl.zeros(n, dtype=pl.Float32, eager=True).alias("year")
    month_sine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("month_sine")
    month_cosine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("month_cosine")
    day_sine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("day_sine")
    day_cosine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("day_cosine")
    hour_sine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("hour_sine")
    hour_cosine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("hour_cosine")
    minute_sine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("minute_sine")
    minute_cosine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("minute_cosine")
    second_sine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("second_sine")
    second_cosine = pl.zeros(n, dtype=pl.Float32, eager=True).alias("second_cosine")

    if to_encode.dtype in [pl.Date, pl.Datetime]:
        try:
            year = to_encode.dt.year().cast(pl.Float32).alias("year")
            month = to_encode.dt.month().cast(pl.Float32).alias("month")
            day = to_encode.dt.day().cast(pl.Float32).alias("day")

            year_norm = (year - REFERENCE_YEAR) / MAX_NUMBER_OF_YEARS
            month_sine, month_cosine = _get_cyclic_encoding(month, 12)
            day_sine, day_cosine = _get_cyclic_encoding(day, 31)
        except pl.exceptions.PanicException as e:
            _logger.exception("Error extracting datetime", exc_info=e)

    if to_encode.dtype in [pl.Time, pl.Datetime]:
        try:
            hour = to_encode.dt.hour().cast(pl.Float32).alias("hour")
            minute = to_encode.dt.minute().cast(pl.Float32).alias("minute")
            second = to_encode.dt.second().cast(pl.Float32).alias("second")

            hour_sine, hour_cosine = _get_cyclic_encoding(hour, 24)
            minute_sine, minute_cosine = _get_cyclic_encoding(minute, 60)
            second_sine, second_cosine = _get_cyclic_encoding(second, 60)
        except pl.exceptions.PanicException as e:
            _logger.exception("Error extracting datetime", exc_info=e)

    return pl.DataFrame(
        [
            year_norm.fill_null(0.0),
            month_sine.fill_null(0.0),
            month_cosine.fill_null(0.0),
            day_sine.fill_null(0.0),
            day_cosine.fill_null(0.0),
            hour_sine.fill_null(0.0),
            hour_cosine.fill_null(0.0),
            minute_sine.fill_null(0.0),
            minute_cosine.fill_null(0.0),
            second_sine.fill_null(0.0),
            second_cosine.fill_null(0.0),
        ]
    ).select(pl.concat_list(pl.all()).alias(to_encode.name))[to_encode.name]
