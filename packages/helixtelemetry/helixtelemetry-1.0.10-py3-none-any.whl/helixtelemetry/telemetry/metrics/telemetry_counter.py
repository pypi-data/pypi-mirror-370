from typing import Optional, Dict, Union, Mapping, Set, Tuple
import threading

from opentelemetry.context import Context
from opentelemetry.metrics import Counter

from helixtelemetry.telemetry.structures.telemetry_attribute_value import (
    TelemetryAttributeValue,
    TelemetryAttributeValueWithoutNone,
)
from helixtelemetry.telemetry.structures.telemetry_parent import TelemetryParent
from helixtelemetry.telemetry.utilities.mapping_appender import append_mappings


class TelemetryCounter:
    """
    This class wraps the OpenTelemetry Counter class and adds the supplied attributes every time a metric is recorded

    """

    def __init__(
        self,
        *,
        counter: Counter,
        attributes: Optional[Mapping[str, TelemetryAttributeValue]],
        telemetry_parent: Optional[TelemetryParent],
    ) -> None:
        assert counter
        self._counter: Counter = counter
        self._attributes: Optional[Mapping[str, TelemetryAttributeValue]] = attributes
        self._telemetry_parent: Optional[TelemetryParent] = telemetry_parent
        self._initialized_time_series: Set[
            Tuple[Tuple[str, TelemetryAttributeValueWithoutNone], ...]
        ] = set()
        self._lock = threading.Lock()
        # NOTE: _initialized_time_series can grow unbounded if there are many unique attribute combinations.
        # Consider implementing cleanup/eviction if this becomes a problem.

    def add(
        self,
        amount: Union[int, float],
        attributes: Optional[Dict[str, bool | str | bytes | int | float | None]] = None,
        context: Optional[Context] = None,
    ) -> None:
        combined_attributes: Mapping[str, TelemetryAttributeValueWithoutNone] = (
            append_mappings(
                [
                    self._attributes,
                    self._telemetry_parent.attributes if self._telemetry_parent else {},
                    attributes,
                ]
            )
        )

        # Initialize the time series if it hasn't been initialized yet
        time_series_key = tuple(sorted(combined_attributes.items()))
        with self._lock:
            if time_series_key not in self._initialized_time_series:
                self._counter.add(
                    amount=0, attributes=combined_attributes, context=context
                )
                self._initialized_time_series.add(time_series_key)

        self._counter.add(
            amount=amount, attributes=combined_attributes, context=context
        )
