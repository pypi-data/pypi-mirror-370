import typing as t

FREQUENCIES = t.Literal[
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "quarterly",
    "yearly",
]

PL_RANGES = t.Literal["1h", "1d", "1w", "1mo", "3mo", "1y"]

# Only the non-time identifiers
FREQUENCY_PL_INTERVAL: t.Final[t.Mapping[FREQUENCIES, PL_RANGES]] = {
    "hourly": "1h",
    "daily": "1d",
    "weekly": "1w",
    "monthly": "1mo",
    "quarterly": "1q",
    "yearly": "1y",
}