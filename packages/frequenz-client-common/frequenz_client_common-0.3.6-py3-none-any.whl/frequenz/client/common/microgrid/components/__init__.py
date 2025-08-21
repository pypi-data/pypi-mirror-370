# License: MIT
# Copyright © 2022 Frequenz Energy-as-a-Service GmbH

"""Defines the components that can be used in a microgrid."""

from __future__ import annotations

import enum
from typing import final

# pylint: disable=no-name-in-module
from frequenz.api.common.v1.microgrid.components.components_pb2 import (
    ComponentCategory as PBComponentCategory,
)
from frequenz.api.common.v1.microgrid.components.components_pb2 import (
    ComponentErrorCode as PBComponentErrorCode,
)
from frequenz.api.common.v1.microgrid.components.components_pb2 import (
    ComponentStateCode as PBComponentStateCode,
)
from frequenz.core.id import BaseId
from typing_extensions import deprecated

# pylint: enable=no-name-in-module


@final
class ComponentId(BaseId, str_prefix="CID"):
    """A unique identifier for a microgrid component."""


@enum.unique
class ComponentCategory(enum.Enum):
    """Possible types of microgrid component."""

    UNSPECIFIED = PBComponentCategory.COMPONENT_CATEGORY_UNSPECIFIED
    """An unknown component category.

    Useful for error handling, and marking unknown components in
    a list of components with otherwise known categories.
    """

    GRID = PBComponentCategory.COMPONENT_CATEGORY_GRID
    """The point where the local microgrid is connected to the grid."""

    METER = PBComponentCategory.COMPONENT_CATEGORY_METER
    """A meter, for measuring electrical metrics, e.g., current, voltage, etc."""

    INVERTER = PBComponentCategory.COMPONENT_CATEGORY_INVERTER
    """An electricity generator, with batteries or solar energy."""

    CONVERTER = PBComponentCategory.COMPONENT_CATEGORY_CONVERTER
    """A DC-DC converter."""

    BATTERY = PBComponentCategory.COMPONENT_CATEGORY_BATTERY
    """A storage system for electrical energy, used by inverters."""

    EV_CHARGER = PBComponentCategory.COMPONENT_CATEGORY_EV_CHARGER
    """A station for charging electrical vehicles."""

    CRYPTO_MINER = PBComponentCategory.COMPONENT_CATEGORY_CRYPTO_MINER
    """A crypto miner."""

    ELECTROLYZER = PBComponentCategory.COMPONENT_CATEGORY_ELECTROLYZER
    """An electrolyzer for converting water into hydrogen and oxygen."""

    CHP = PBComponentCategory.COMPONENT_CATEGORY_CHP
    """A heat and power combustion plant (CHP stands for combined heat and power)."""

    RELAY = PBComponentCategory.COMPONENT_CATEGORY_RELAY
    """A relay.

    Relays generally have two states: open (connected) and closed (disconnected).
    They are generally placed in front of a component, e.g., an inverter, to
    control whether the component is connected to the grid or not.
    """

    PRECHARGER = PBComponentCategory.COMPONENT_CATEGORY_PRECHARGER
    """A precharge module.

    Precharging involves gradually ramping up the DC voltage to prevent any
    potential damage to sensitive electrical components like capacitors.

    While many inverters and batteries come equipped with in-built precharging
    mechanisms, some may lack this feature. In such cases, we need to use
    external precharging modules.
    """

    FUSE = PBComponentCategory.COMPONENT_CATEGORY_FUSE
    """A fuse."""

    VOLTAGE_TRANSFORMER = PBComponentCategory.COMPONENT_CATEGORY_VOLTAGE_TRANSFORMER
    """A voltage transformer.

    Voltage transformers are used to step up or step down the voltage, keeping
    the power somewhat constant by increasing or decreasing the current.  If voltage is
    stepped up, current is stepped down, and vice versa.

    Note:
        Voltage transformers have efficiency losses, so the output power is
        always less than the input power.
    """

    HVAC = PBComponentCategory.COMPONENT_CATEGORY_HVAC
    """A Heating, Ventilation, and Air Conditioning (HVAC) system."""

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(
        cls, component_category: PBComponentCategory.ValueType
    ) -> ComponentCategory:
        """Convert a protobuf ComponentCategory message to ComponentCategory enum.

        Args:
            component_category: protobuf enum to convert

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(t.value == component_category for t in ComponentCategory):
            return ComponentCategory.UNSPECIFIED
        return cls(component_category)

    def to_proto(self) -> PBComponentCategory.ValueType:
        """Convert a ComponentCategory enum to protobuf ComponentCategory message.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        return self.value


@enum.unique
class ComponentStateCode(enum.Enum):
    """All possible states of a microgrid component."""

    UNSPECIFIED = PBComponentStateCode.COMPONENT_STATE_CODE_UNSPECIFIED
    """Default value when the component state is not explicitly set."""

    UNKNOWN = PBComponentStateCode.COMPONENT_STATE_CODE_UNKNOWN
    """State when the component is in an unknown or undefined condition.

    This is used when the sender is unable to classify the component into any
    other state.
    """
    SWITCHING_OFF = PBComponentStateCode.COMPONENT_STATE_CODE_SWITCHING_OFF
    """State when the component is in the process of switching off."""

    OFF = PBComponentStateCode.COMPONENT_STATE_CODE_OFF
    """State when the component has successfully switched off."""

    SWITCHING_ON = PBComponentStateCode.COMPONENT_STATE_CODE_SWITCHING_ON
    """State when the component is in the process of switching on from an off state."""

    STANDBY = PBComponentStateCode.COMPONENT_STATE_CODE_STANDBY
    """State when the component is in standby mode, and not immediately ready for operation."""

    READY = PBComponentStateCode.COMPONENT_STATE_CODE_READY
    """State when the component is fully operational and ready for use."""

    CHARGING = PBComponentStateCode.COMPONENT_STATE_CODE_CHARGING
    """State when the component is actively consuming energy."""

    DISCHARGING = PBComponentStateCode.COMPONENT_STATE_CODE_DISCHARGING
    """State when the component is actively producing or releasing energy."""

    ERROR = PBComponentStateCode.COMPONENT_STATE_CODE_ERROR
    """State when the component is in an error state and may need attention."""

    EV_CHARGING_CABLE_UNPLUGGED = (
        PBComponentStateCode.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_UNPLUGGED
    )
    """The Electric Vehicle (EV) charging cable is unplugged from the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_STATION = (
        PBComponentStateCode.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_STATION
    )
    """The EV charging cable is plugged into the charging station."""

    EV_CHARGING_CABLE_PLUGGED_AT_EV = (
        PBComponentStateCode.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_PLUGGED_AT_EV
    )
    """The EV charging cable is plugged into the vehicle."""

    EV_CHARGING_CABLE_LOCKED_AT_STATION = (
        PBComponentStateCode.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_STATION
    )
    """The EV charging cable is locked at the charging station end, indicating
    readiness for charging."""

    EV_CHARGING_CABLE_LOCKED_AT_EV = (
        PBComponentStateCode.COMPONENT_STATE_CODE_EV_CHARGING_CABLE_LOCKED_AT_EV
    )
    """The EV charging cable is locked at the vehicle end, indicating that charging is active."""

    RELAY_OPEN = PBComponentStateCode.COMPONENT_STATE_CODE_RELAY_OPEN
    """The relay is in an open state, meaning no current can flow through."""

    RELAY_CLOSED = PBComponentStateCode.COMPONENT_STATE_CODE_RELAY_CLOSED
    """The relay is in a closed state, allowing current to flow."""

    PRECHARGER_OPEN = PBComponentStateCode.COMPONENT_STATE_CODE_PRECHARGER_OPEN
    """The precharger circuit is open, meaning it's not currently active."""

    PRECHARGER_PRECHARGING = (
        PBComponentStateCode.COMPONENT_STATE_CODE_PRECHARGER_PRECHARGING
    )
    """The precharger is in a precharging state, preparing the main circuit for activation."""

    PRECHARGER_CLOSED = PBComponentStateCode.COMPONENT_STATE_CODE_PRECHARGER_CLOSED
    """The precharger circuit is closed, allowing full current to flow to the main circuit."""

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(
        cls, component_state: PBComponentStateCode.ValueType
    ) -> ComponentStateCode:
        """Convert a protobuf ComponentStateCode message to ComponentStateCode enum.

        Args:
            component_state: protobuf enum to convert

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(c.value == component_state for c in ComponentStateCode):
            return ComponentStateCode.UNSPECIFIED
        return cls(component_state)

    def to_proto(self) -> PBComponentStateCode.ValueType:
        """Convert a ComponentStateCode enum to protobuf ComponentStateCode message.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        return self.value


@enum.unique
class ComponentErrorCode(enum.Enum):
    """All possible errors that can occur across all microgrid component categories."""

    UNSPECIFIED = PBComponentErrorCode.COMPONENT_ERROR_CODE_UNSPECIFIED
    """Default value. No specific error is specified."""

    UNKNOWN = PBComponentErrorCode.COMPONENT_ERROR_CODE_UNKNOWN
    """The component is reporting an unknown or an undefined error, and the sender
    cannot parse the component error to any of the variants below."""

    SWITCH_ON_FAULT = PBComponentErrorCode.COMPONENT_ERROR_CODE_SWITCH_ON_FAULT
    """Error indicating that the component could not be switched on."""

    UNDERVOLTAGE = PBComponentErrorCode.COMPONENT_ERROR_CODE_UNDERVOLTAGE
    """Error indicating that the component is operating under the minimum rated
    voltage."""

    OVERVOLTAGE = PBComponentErrorCode.COMPONENT_ERROR_CODE_OVERVOLTAGE
    """Error indicating that the component is operating over the maximum rated
    voltage."""

    OVERCURRENT = PBComponentErrorCode.COMPONENT_ERROR_CODE_OVERCURRENT
    """Error indicating that the component is drawing more current than the
    maximum rated value."""

    OVERCURRENT_CHARGING = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_OVERCURRENT_CHARGING
    )
    """Error indicating that the component's consumption current is over the
    maximum rated value during charging."""

    OVERCURRENT_DISCHARGING = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_OVERCURRENT_DISCHARGING
    )
    """Error indicating that the component's production current is over the
    maximum rated value during discharging."""

    OVERTEMPERATURE = PBComponentErrorCode.COMPONENT_ERROR_CODE_OVERTEMPERATURE
    """Error indicating that the component is operating over the maximum rated
    temperature."""

    UNDERTEMPERATURE = PBComponentErrorCode.COMPONENT_ERROR_CODE_UNDERTEMPERATURE
    """Error indicating that the component is operating under the minimum rated
    temperature."""

    HIGH_HUMIDITY = PBComponentErrorCode.COMPONENT_ERROR_CODE_HIGH_HUMIDITY
    """Error indicating that the component is exposed to high humidity levels over
    the maximum rated value."""

    FUSE_ERROR = PBComponentErrorCode.COMPONENT_ERROR_CODE_FUSE_ERROR
    """Error indicating that the component's fuse has blown."""

    PRECHARGE_ERROR = PBComponentErrorCode.COMPONENT_ERROR_CODE_PRECHARGE_ERROR
    """Error indicating that the component's precharge unit has failed."""

    PLAUSIBILITY_ERROR = PBComponentErrorCode.COMPONENT_ERROR_CODE_PLAUSIBILITY_ERROR
    """Error indicating plausibility issues within the system involving this
    component."""

    UNDERVOLTAGE_SHUTDOWN = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_UNDERVOLTAGE_SHUTDOWN
    )
    """Error indicating system shutdown due to undervoltage involving this
    component."""

    EV_UNEXPECTED_PILOT_FAILURE = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_EV_UNEXPECTED_PILOT_FAILURE
    )
    """Error indicating unexpected pilot failure in an electric vehicle (EV)
    component."""

    FAULT_CURRENT = PBComponentErrorCode.COMPONENT_ERROR_CODE_FAULT_CURRENT
    """Error indicating fault current detected in the component."""

    SHORT_CIRCUIT = PBComponentErrorCode.COMPONENT_ERROR_CODE_SHORT_CIRCUIT
    """Error indicating a short circuit detected in the component."""

    CONFIG_ERROR = PBComponentErrorCode.COMPONENT_ERROR_CODE_CONFIG_ERROR
    """Error indicating a configuration error related to the component."""

    ILLEGAL_COMPONENT_STATE_CODE_REQUESTED = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_ILLEGAL_COMPONENT_STATE_CODE_REQUESTED
    )
    """Error indicating an illegal state requested for the component."""

    HARDWARE_INACCESSIBLE = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_HARDWARE_INACCESSIBLE
    )
    """Error indicating that the hardware of the component is inaccessible."""

    INTERNAL = PBComponentErrorCode.COMPONENT_ERROR_CODE_INTERNAL
    """Error indicating an internal error within the component."""

    UNAUTHORIZED = PBComponentErrorCode.COMPONENT_ERROR_CODE_UNAUTHORIZED
    """Error indicating that the component is unauthorized to perform the
    last requested action."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_STATION
    )
    """Error indicating electric vehicle (EV) cable was abruptly unplugged from
    the charging station."""

    EV_CHARGING_CABLE_UNPLUGGED_FROM_EV = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_UNPLUGGED_FROM_EV
    )
    """Error indicating electric vehicle (EV) cable was abruptly unplugged from
    the vehicle."""

    EV_CHARGING_CABLE_LOCK_FAILED = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_LOCK_FAILED
    )
    """Error indicating electric vehicle (EV) cable lock failure."""

    EV_CHARGING_CABLE_INVALID = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_EV_CHARGING_CABLE_INVALID
    )
    """Error indicating an invalid electric vehicle (EV) cable."""

    EV_CONSUMER_INCOMPATIBLE = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_EV_CONSUMER_INCOMPATIBLE
    )
    """Error indicating an incompatible electric vehicle (EV) plug."""

    BATTERY_IMBALANCE = PBComponentErrorCode.COMPONENT_ERROR_CODE_BATTERY_IMBALANCE
    """Error indicating a battery system imbalance."""

    BATTERY_LOW_SOH = PBComponentErrorCode.COMPONENT_ERROR_CODE_BATTERY_LOW_SOH
    """Error indicating a low state of health (SOH) detected in the battery."""

    BATTERY_BLOCK_ERROR = PBComponentErrorCode.COMPONENT_ERROR_CODE_BATTERY_BLOCK_ERROR
    """Error indicating a battery block error."""

    BATTERY_CONTROLLER_ERROR = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_BATTERY_CONTROLLER_ERROR
    )
    """Error indicating a battery controller error."""

    BATTERY_RELAY_ERROR = PBComponentErrorCode.COMPONENT_ERROR_CODE_BATTERY_RELAY_ERROR
    """Error indicating a battery relay error."""

    BATTERY_CALIBRATION_NEEDED = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_BATTERY_CALIBRATION_NEEDED
    )
    """Error indicating that battery calibration is needed."""

    RELAY_CYCLE_LIMIT_REACHED = (
        PBComponentErrorCode.COMPONENT_ERROR_CODE_RELAY_CYCLE_LIMIT_REACHED
    )
    """Error indicating that the relays have been cycled for the maximum number of
    times."""

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(
        cls, component_error_code: PBComponentErrorCode.ValueType
    ) -> ComponentErrorCode:
        """Convert a protobuf ComponentErrorCode message to ComponentErrorCode enum.

        Args:
            component_error_code: protobuf enum to convert

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(c.value == component_error_code for c in ComponentErrorCode):
            return ComponentErrorCode.UNSPECIFIED
        return cls(component_error_code)

    def to_proto(self) -> PBComponentErrorCode.ValueType:
        """Convert a ComponentErrorCode enum to protobuf ComponentErrorCode message.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        return self.value
