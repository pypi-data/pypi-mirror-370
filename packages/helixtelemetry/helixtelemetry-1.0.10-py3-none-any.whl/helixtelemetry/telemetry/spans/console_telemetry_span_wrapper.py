from typing import (
    Optional,
    Dict,
    Any,
    override,
    Mapping,
)

from helixtelemetry.telemetry.context.telemetry_context import TelemetryContext
from helixtelemetry.telemetry.spans.telemetry_span_wrapper import TelemetrySpanWrapper
from helixtelemetry.telemetry.structures.telemetry_attribute_value import (
    TelemetryAttributeValue,
)
from helixtelemetry.telemetry.structures.telemetry_parent import TelemetryParent


class ConsoleTelemetrySpanWrapper(TelemetrySpanWrapper):
    @override
    @property
    def span_id(self) -> Optional[str]:
        return (
            self._telemetry_parent.span_id
            if self._telemetry_parent is not None
            else None
        )

    @override
    @property
    def trace_id(self) -> Optional[str]:
        return (
            self._telemetry_parent.trace_id
            if self._telemetry_parent is not None
            else None
        )

    def __init__(
        self,
        *,
        name: str,
        attributes: Optional[Mapping[str, TelemetryAttributeValue]],
        telemetry_context: Optional[TelemetryContext],
        telemetry_parent: Optional[TelemetryParent],
    ) -> None:
        super().__init__(
            name=name,
            attributes=attributes,
            telemetry_parent=telemetry_parent,
        )

    @override
    def set_attributes(self, attributes: Dict[str, Any]) -> None:
        pass

    @override
    def end(self, *, end_time: int) -> None:
        pass
