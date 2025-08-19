from typing import Any, Dict, Optional, Type, Callable

from helixtelemetry.telemetry.providers.telemetry import Telemetry
from helixtelemetry.telemetry.spans.telemetry_span_creator import TelemetrySpanCreator
from helixtelemetry.telemetry.structures.telemetry_parent import TelemetryParent


class TelemetryFactory:

    _registry: Dict[str, type[Telemetry]] = {}

    def __init__(self, *, telemetry_parent: TelemetryParent) -> None:
        """
        Telemetry factory used to create telemetry instances based on the telemetry context


        :param telemetry_parent: telemetry parent
        """
        self.telemetry_parent = telemetry_parent

    @classmethod
    def register_telemetry_class(
        cls, *, name: str, telemetry_class: Type[Telemetry]
    ) -> None:
        registration_name = name

        # Validate that the class is a Telemetry subclass
        if not issubclass(telemetry_class, Telemetry):
            raise TypeError(
                f"{telemetry_class.__name__} must be a subclass of Telemetry"
            )

        # Register the class in the factory's registry
        cls._registry[registration_name] = telemetry_class

    @classmethod
    def register_telemetry(
        cls, name: str
    ) -> Callable[[Type[Telemetry]], Type[Telemetry]]:
        """
        Decorator to register Telemetry subclasses in the factory registry.

        Args:
            name (Optional[str], optional): Custom registration name.
                Defaults to the class name if not provided.

        Returns:
            Callable: A decorator function for registering Telemetry classes
        """

        def decorator(telemetry_class: Type[Telemetry]) -> Type[Telemetry]:
            # Use provided name or fallback to class name
            registration_name = name

            # Validate that the class is a Telemetry subclass
            if not issubclass(telemetry_class, Telemetry):
                raise TypeError(
                    f"{telemetry_class.__name__} must be a subclass of Telemetry"
                )

            # Register the class in the factory's registry
            cls._registry[registration_name] = telemetry_class

            return telemetry_class

        return decorator

    def create(self, *, log_level: Optional[str | int]) -> Telemetry:
        """
        Create a telemetry instance

        :return: telemetry instance
        """
        assert (
            self.telemetry_parent.telemetry_context.provider in self._registry
        ), f"Telemetry {self.telemetry_parent.telemetry_context.provider} not found in registry.  Did you register a class for it using register_telemetry_class()?"
        return self._registry[self.telemetry_parent.telemetry_context.provider](
            telemetry_context=self.telemetry_parent.telemetry_context,
            log_level=log_level,
        )

    def create_telemetry_span_creator(
        self, *, log_level: Optional[str | int]
    ) -> TelemetrySpanCreator:
        """
        Create a telemetry span creator

        :return: telemetry span creator
        """
        return TelemetrySpanCreator(
            telemetry=self.create(log_level=log_level),
        )

    # noinspection PyTypeChecker
    def __getstate__(self) -> Dict[str, Any]:
        raise NotImplementedError(
            "Serialization of TelemetrySpanCreator is not supported.  Did you accidentally try to send this object to a Spark worker?"
        )
