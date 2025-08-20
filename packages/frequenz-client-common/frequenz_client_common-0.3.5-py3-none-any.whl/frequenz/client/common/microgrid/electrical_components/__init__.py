# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines the electrical components that can be used in a microgrid."""
from __future__ import annotations

import enum
from typing import final

# pylint: disable=no-name-in-module
from frequenz.api.common.v1alpha8.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponentCategory as PBElectricalComponentCategory,
)
from frequenz.api.common.v1alpha8.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponentDiagnosticCode as PBElectricalComponentDiagnosticCode,
)
from frequenz.api.common.v1alpha8.microgrid.electrical_components.electrical_components_pb2 import (
    ElectricalComponentStateCode as PBElectricalComponentStateCode,
)
from frequenz.core.id import BaseId
from typing_extensions import deprecated

# pylint: enable=no-name-in-module


@final
class ElectricalComponentId(BaseId, str_prefix="CID"):
    """A unique identifier for a microgrid electrical component."""


@enum.unique
class ElectricalComponentCategory(enum.Enum):
    """Possible types of microgrid electrical component."""

    UNSPECIFIED = (
        PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_UNSPECIFIED
    )
    """An unknown component category.

    Useful for error handling, and marking unknown components in
    a list of components with otherwise known categories.
    """

    GRID_CONNECTION_POINT = (
        PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_GRID_CONNECTION_POINT
    )
    """The point where the local microgrid is connected to the grid."""

    METER = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_METER
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc."""

    INVERTER = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_INVERTER
    """An electricity generator, with batteries or solar energy."""

    CONVERTER = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_CONVERTER
    """An electricity converter, e.g., a DC-DC converter."""

    BATTERY = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_BATTERY
    """A storage system for electrical energy, used by inverters."""

    EV_CHARGER = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_EV_CHARGER
    """A station for charging electrical vehicles."""

    CRYPTO_MINER = (
        PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_CRYPTO_MINER
    )
    """A device for mining cryptocurrencies."""

    ELECTROLYZER = (
        PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_ELECTROLYZER
    )
    """A device for splitting water into hydrogen and oxygen using electricity."""

    CHP = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_CHP
    """A heat and power combustion plant (CHP stands for combined heat and power)."""

    BREAKER = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_BREAKER
    """A relay, used for switching electrical circuits on and off."""

    PRECHARGER = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_PRECHARGER
    """A precharger, used for preparing electrical circuits for switching on."""

    POWER_TRANSFORMER = (
        PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_POWER_TRANSFORMER
    )
    """A transformer, used for changing the voltage of electrical circuits."""

    HVAC = PBElectricalComponentCategory.ELECTRICAL_COMPONENT_CATEGORY_HVAC
    """A heating, ventilation, and air conditioning (HVAC) system."""

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(
        cls, component_category: PBElectricalComponentCategory.ValueType
    ) -> ElectricalComponentCategory:
        """Convert a protobuf ElectricalComponentCategory message to enum.

        Args:
            component_category: protobuf enum to convert

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(t.value == component_category for t in ElectricalComponentCategory):
            return ElectricalComponentCategory.UNSPECIFIED
        return cls(component_category)

    def to_proto(self) -> PBElectricalComponentCategory.ValueType:
        """Convert a ElectricalComponentCategory enum to protobuf message.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        return self.value


@enum.unique
class ElectricalComponentStateCode(enum.Enum):
    """All possible states of a microgrid electrical component."""

    UNSPECIFIED = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_UNSPECIFIED
    )
    """Default value when the component state is not explicitly set."""

    UNKNOWN = PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_UNKNOWN
    """State when the component is in an unknown or undefined condition.

    This is used when the sender is unable to classify the component into any
    other state.
    """

    UNAVAILABLE = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_UNAVAILABLE
    )
    """State when the component is not available for use."""

    SWITCHING_OFF = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_SWITCHING_OFF
    )
    """State when the component is in the process of switching off."""

    OFF = PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_OFF
    """State when the component has successfully switched off."""

    SWITCHING_ON = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_SWITCHING_ON
    )
    """State when the component is in the process of switching on from an off state."""

    STANDBY = PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_STANDBY
    """State when the component is in standby mode, and not immediately ready for operation."""

    READY = PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_READY
    """State when the component is fully operational and ready for use."""

    CHARGING = PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_CHARGING
    """State when the component is actively consuming energy."""

    DISCHARGING = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_DISCHARGING
    )
    """State when the component is actively producing or releasing energy."""

    ERROR = PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_ERROR
    """State when the component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_UNPLUGGED
    )
    """The Electric Vehicle (EV) charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_STATION  # noqa: E501
    )
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_EV  # noqa: E501
    )
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_STATION  # noqa: E501
    )
    """The EV charging cable is locked at the charging station end, indicating
    readiness for charging."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_EV  # noqa: E501
    )
    """The EV charging cable is locked at the vehicle end, indicating that charging is active."""

    RELAY_OPEN = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_RELAY_OPEN
    )
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_RELAY_CLOSED
    )
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_OPEN
    )
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_PRECHARGING
    )
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = (
        PBElectricalComponentStateCode.ELECTRICAL_COMPONENT_STATE_CODE_PRECHARGER_CLOSED
    )
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(
        cls, component_state: PBElectricalComponentStateCode.ValueType
    ) -> ElectricalComponentStateCode:
        """Convert a protobuf ElectricalComponentStateCode message to enum.

        Args:
            component_state: protobuf enum to convert

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(c.value == component_state for c in ElectricalComponentStateCode):
            return ElectricalComponentStateCode.UNSPECIFIED
        return cls(component_state)

    def to_proto(self) -> PBElectricalComponentStateCode.ValueType:
        """Convert a ElectricalComponentStateCode enum to protobuf message.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        return self.value


@enum.unique
class ElectricalComponentDiagnosticCode(enum.Enum):
    """All diagnostics that can occur across electrical component categories."""

    UNSPECIFIED = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNSPECIFIED
    )
    """Default value. No specific error is specified."""

    UNKNOWN = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNKNOWN
    )
    """The component is reporting an unknown or an undefined error, and the sender
    cannot parse the component error to any of the variants below."""

    SWITCH_ON_FAULT = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_SWITCH_ON_FAULT
    )
    """Error indicating that the component could not be switched on."""

    UNDERVOLTAGE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERVOLTAGE
    )
    """Error indicating that the component is operating under the minimum rated
    voltage."""

    OVERVOLTAGE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERVOLTAGE
    )
    """Error indicating that the component is operating over the maximum rated
    voltage."""

    OVERCURRENT = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT
    )
    """Error indicating that the component is drawing more current than the
    maximum rated value."""

    OVERCURRENT_CHARGING = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT_CHARGING  # noqa: E501
    )
    """Error indicating that the component's consumption current is over the
    maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERCURRENT_DISCHARGING  # noqa: E501
    )
    """Error indicating that the component's production current is over the
    maximum rated value during discharging."""

    OVERTEMPERATURE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_OVERTEMPERATURE
    )
    """Error indicating that the component is operating over the maximum rated
    temperature."""

    UNDERTEMPERATURE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNDERTEMPERATURE
    )
    """Error indicating that the component is operating under the minimum rated
    temperature."""

    HIGH_HUMIDITY = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HIGH_HUMIDITY
    )
    """Error indicating that the component is exposed to high humidity levels over
    the maximum rated value."""

    FUSE_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FUSE_ERROR
    )
    """Error indicating that the component's fuse has blown."""

    PRECHARGE_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PRECHARGE_ERROR
    )
    """Error indicating that the component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_PLAUSIBILITY_ERROR
    )
    """Error indicating plausibility issues within the system involving this
    component."""

    EV_UNEXPECTED_PILOT_FAILURE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_UNEXPECTED_PILOT_FAILURE  # noqa: E501
    )
    """Error indicating unexpected pilot failure in an electric vehicle (EV)
    component."""

    FAULT_CURRENT = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_FAULT_CURRENT
    )
    """Error indicating fault current detected in the component."""

    SHORT_CIRCUIT = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_SHORT_CIRCUIT
    )
    """Error indicating a short circuit detected in the component."""

    CONFIG_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_CONFIG_ERROR
    )
    """Error indicating a configuration error related to the component."""

    ILLEGAL_COMPONENT_STATE_CODE_REQUESTED = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_ILLEGAL_COMPONENT_STATE_CODE_REQUESTED  # noqa: E501
    )
    """Error indicating an illegal state requested for the component."""

    HARDWARE_INACCESSIBLE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_HARDWARE_INACCESSIBLE  # noqa: E501
    )
    """Error indicating that the hardware of the component is inaccessible."""

    INTERNAL = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_INTERNAL
    )
    """Error indicating an internal error within the component."""

    UNAUTHORIZED = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_UNAUTHORIZED
    )
    """Error indicating that the component is unauthorized to perform the
    last requested action."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION  # noqa: E501
    )
    """Error indicating electric vehicle (EV) cable was abruptly unplugged from
    the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_EV  # noqa: E501
    )
    """Error indicating electric vehicle (EV) cable was abruptly unplugged from
    the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_LOCK_FAILED  # noqa: E501
    )
    """Error indicating electric vehicle (EV) cable lock failure."""

    EV_CHARGING_CABLE_INVALID = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CHARGING_CABLE_INVALID  # noqa: E501
    )
    """Error indicating an invalid electric vehicle (EV) cable."""

    EV_CONSUMER_INCOMPATIBLE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_EV_CONSUMER_INCOMPATIBLE  # noqa: E501
    )
    """Error indicating an incompatible electric vehicle (EV) plug."""

    BATTERY_IMBALANCE = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_IMBALANCE
    )
    """Error indicating a battery system imbalance."""

    BATTERY_LOW_SOH = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_LOW_SOH
    )
    """Error indicating a low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_BLOCK_ERROR
    )
    """Error indicating a battery block error."""

    BATTERY_CONTROLLER_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_CONTROLLER_ERROR  # noqa: E501
    )
    """Error indicating a battery controller error."""

    BATTERY_RELAY_ERROR = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_RELAY_ERROR
    )
    """Error indicating a battery relay error."""

    BATTERY_CALIBRATION_NEEDED = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_BATTERY_CALIBRATION_NEEDED  # noqa: E501
    )
    """Error indicating that battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = (
        PBElectricalComponentDiagnosticCode.ELECTRICAL_COMPONENT_DIAGNOSTIC_CODE_RELAY_CYCLE_LIMIT_REACHED  # noqa: E501
    )
    """Error indicating that the relays have been cycled for the maximum number of
    times."""

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(
        cls, component_error_code: PBElectricalComponentDiagnosticCode.ValueType
    ) -> ElectricalComponentDiagnosticCode:
        """Convert a protobuf ElectricalComponentDiagnosticCode message to enum.

        Args:
            component_error_code: protobuf enum to convert

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(
            c.value == component_error_code for c in ElectricalComponentDiagnosticCode
        ):
            return ElectricalComponentDiagnosticCode.UNSPECIFIED
        return cls(component_error_code)

    def to_proto(self) -> PBElectricalComponentDiagnosticCode.ValueType:
        """Convert a ElectricalComponentDiagnosticCode enum to protobuf message.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        return self.value
