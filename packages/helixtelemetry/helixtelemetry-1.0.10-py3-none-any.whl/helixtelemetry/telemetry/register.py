from helixtelemetry.telemetry.factory.telemetry_factory import TelemetryFactory
from helixtelemetry.telemetry.providers.console_telemetry import ConsoleTelemetry
from helixtelemetry.telemetry.providers.null_telemetry import NullTelemetry
from helixtelemetry.telemetry.providers.open_telemetry import OpenTelemetry


def register() -> None:
    """
    Register the telemetry classes with the telemetry factory
    """

    TelemetryFactory.register_telemetry_class(
        name=NullTelemetry.telemetry_provider, telemetry_class=NullTelemetry
    )
    TelemetryFactory.register_telemetry_class(
        name=ConsoleTelemetry.telemetry_provider, telemetry_class=ConsoleTelemetry
    )

    TelemetryFactory.register_telemetry_class(
        name=OpenTelemetry.telemetry_provider,
        telemetry_class=OpenTelemetry,
    )
