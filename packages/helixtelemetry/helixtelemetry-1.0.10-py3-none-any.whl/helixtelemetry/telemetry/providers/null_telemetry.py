import logging
from contextlib import contextmanager, asynccontextmanager
from logging import Logger
from typing import (
    Optional,
    Dict,
    Any,
    Iterator,
    AsyncIterator,
    override,
    Mapping,
    Union,
    ClassVar,
    List,
)

from opentelemetry.metrics import NoOpCounter, NoOpUpDownCounter, NoOpHistogram

from helixtelemetry.telemetry.context.telemetry_context import TelemetryContext
from helixtelemetry.telemetry.metrics.telemetry_counter import TelemetryCounter
from helixtelemetry.telemetry.metrics.telemetry_histogram_counter import (
    TelemetryHistogram,
)
from helixtelemetry.telemetry.metrics.telemetry_up_down_counter import (
    TelemetryUpDownCounter,
)
from helixtelemetry.telemetry.providers.telemetry import Telemetry
from helixtelemetry.telemetry.spans.null_telemetry_span_wrapper import (
    NullTelemetrySpanWrapper,
)
from helixtelemetry.telemetry.spans.telemetry_span_wrapper import TelemetrySpanWrapper
from helixtelemetry.telemetry.structures.telemetry_attribute_value import (
    TelemetryAttributeValue,
)
from helixtelemetry.telemetry.structures.telemetry_parent import TelemetryParent


class NullTelemetry(Telemetry):
    telemetry_provider: ClassVar[str] = "NullTelemetry"

    def __init__(
        self,
        *,
        telemetry_context: TelemetryContext,
        log_level: Optional[Union[int, str]],
    ) -> None:
        super().__init__(
            telemetry_context=telemetry_context,
            log_level=log_level,
        )
        self._logger: Logger = logging.getLogger(__name__)
        # get_logger sets the log level to the environment variable LOGLEVEL if it exists
        self._logger.setLevel(log_level or "INFO")

    @override
    def track_exception(
        self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

    @override
    async def track_exception_async(
        self, exception: Exception, additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        pass

    @override
    async def flush_async(self) -> None:
        pass

    @override
    async def shutdown_async(self) -> None:
        pass

    @contextmanager
    @override
    def trace(
        self,
        *,
        name: str,
        attributes: Optional[Mapping[str, TelemetryAttributeValue]] = None,
        telemetry_parent: Optional[TelemetryParent],
        start_time: int | None = None,
    ) -> Iterator[TelemetrySpanWrapper]:
        yield NullTelemetrySpanWrapper(
            name=name,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    @asynccontextmanager
    @override
    async def trace_async(
        self,
        *,
        name: str,
        attributes: Optional[Mapping[str, TelemetryAttributeValue]] = None,
        telemetry_parent: Optional[TelemetryParent],
        start_time: int | None = None,
        add_attribute: Optional[List[str]] = None,
    ) -> AsyncIterator[TelemetrySpanWrapper]:
        yield NullTelemetrySpanWrapper(
            name=name,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    @override
    def get_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        telemetry_parent: Optional[TelemetryParent],
        attributes: Optional[Mapping[str, TelemetryAttributeValue]] = None,
        add_attribute: Optional[List[str]] = None,
    ) -> TelemetryCounter:
        """
        Get a counter metric
        :param name: Name of the counter
        :param unit: Unit of the counter
        :param description: Description
        :param attributes: Optional attributes
        :param telemetry_parent: telemetry parent
        :return: The Counter metric
        """
        return TelemetryCounter(
            counter=NoOpCounter(
                name=name,
                unit=unit,
                description=description,
            ),
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    @override
    def get_up_down_counter(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        telemetry_parent: Optional[TelemetryParent],
        attributes: Optional[Mapping[str, TelemetryAttributeValue]] = None,
    ) -> TelemetryUpDownCounter:
        """
        Get an up_down_counter metric

        :param name: Name of the up_down_counter
        :param unit: Unit of the up_down_counter
        :param description: Description
        :param attributes: Optional attributes
        :param telemetry_parent: telemetry parent
        :return: The Counter metric
        """
        return TelemetryUpDownCounter(
            counter=NoOpUpDownCounter(
                name=name,
                unit=unit,
                description=description,
            ),
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    @override
    def get_histogram(
        self,
        *,
        name: str,
        unit: str,
        description: str,
        telemetry_parent: Optional[TelemetryParent],
        attributes: Optional[Mapping[str, TelemetryAttributeValue]] = None,
    ) -> TelemetryHistogram:
        """
        Get a histograms metric

        :param name: Name of the histograms
        :param unit: Unit of the histograms
        :param description: Description
        :param attributes: Optional attributes
        :param telemetry_parent: telemetry parent
        :return: The Counter metric
        """
        return TelemetryHistogram(
            histogram=NoOpHistogram(
                name=name,
                unit=unit,
                description=description,
            ),
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )
