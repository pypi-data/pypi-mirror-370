# License: MIT
# Copyright © 2024 Frequenz Energy-as-a-Service GmbH

"""Module to define the metrics used with the common client."""

import enum
from typing import Self

# pylint: disable=no-name-in-module
from frequenz.api.common.v1.metrics.metric_sample_pb2 import Metric as PBMetric
from typing_extensions import deprecated

# pylint: enable=no-name-in-module


@enum.unique
class Metric(enum.Enum):
    """List of supported metrics.

    AC energy metrics information:
    * This energy metric is reported directly from the component, and not a
    result of aggregations in our systems. If a component does not have this
    metric, this field cannot be populated.
    * Components that provide energy metrics reset this metric from time to
    time. This behaviour is specific to each component model. E.g., some
    components reset it on UTC 00:00:00.
    * This energy metric does not specify the timestamp since when the energy
    was being accumulated, and therefore can be inconsistent.
    """

    # Default value
    UNSPECIFIED = PBMetric.METRIC_UNSPECIFIED

    # DC electricity metrics
    DC_VOLTAGE = PBMetric.METRIC_DC_VOLTAGE
    DC_CURRENT = PBMetric.METRIC_DC_CURRENT
    DC_POWER = PBMetric.METRIC_DC_POWER

    # General AC electricity metrics
    AC_FREQUENCY = PBMetric.METRIC_AC_FREQUENCY
    AC_VOLTAGE = PBMetric.METRIC_AC_VOLTAGE
    AC_VOLTAGE_PHASE_1_N = PBMetric.METRIC_AC_VOLTAGE_PHASE_1_N
    AC_VOLTAGE_PHASE_2_N = PBMetric.METRIC_AC_VOLTAGE_PHASE_2_N
    AC_VOLTAGE_PHASE_3_N = PBMetric.METRIC_AC_VOLTAGE_PHASE_3_N
    AC_VOLTAGE_PHASE_1_PHASE_2 = PBMetric.METRIC_AC_VOLTAGE_PHASE_1_PHASE_2
    AC_VOLTAGE_PHASE_2_PHASE_3 = PBMetric.METRIC_AC_VOLTAGE_PHASE_2_PHASE_3
    AC_VOLTAGE_PHASE_3_PHASE_1 = PBMetric.METRIC_AC_VOLTAGE_PHASE_3_PHASE_1
    AC_CURRENT = PBMetric.METRIC_AC_CURRENT
    AC_CURRENT_PHASE_1 = PBMetric.METRIC_AC_CURRENT_PHASE_1
    AC_CURRENT_PHASE_2 = PBMetric.METRIC_AC_CURRENT_PHASE_2
    AC_CURRENT_PHASE_3 = PBMetric.METRIC_AC_CURRENT_PHASE_3

    # AC power metrics
    AC_APPARENT_POWER = PBMetric.METRIC_AC_APPARENT_POWER
    AC_APPARENT_POWER_PHASE_1 = PBMetric.METRIC_AC_APPARENT_POWER_PHASE_1
    AC_APPARENT_POWER_PHASE_2 = PBMetric.METRIC_AC_APPARENT_POWER_PHASE_2
    AC_APPARENT_POWER_PHASE_3 = PBMetric.METRIC_AC_APPARENT_POWER_PHASE_3
    AC_ACTIVE_POWER = PBMetric.METRIC_AC_ACTIVE_POWER
    AC_ACTIVE_POWER_PHASE_1 = PBMetric.METRIC_AC_ACTIVE_POWER_PHASE_1
    AC_ACTIVE_POWER_PHASE_2 = PBMetric.METRIC_AC_ACTIVE_POWER_PHASE_2
    AC_ACTIVE_POWER_PHASE_3 = PBMetric.METRIC_AC_ACTIVE_POWER_PHASE_3
    AC_REACTIVE_POWER = PBMetric.METRIC_AC_REACTIVE_POWER
    AC_REACTIVE_POWER_PHASE_1 = PBMetric.METRIC_AC_REACTIVE_POWER_PHASE_1
    AC_REACTIVE_POWER_PHASE_2 = PBMetric.METRIC_AC_REACTIVE_POWER_PHASE_2
    AC_REACTIVE_POWER_PHASE_3 = PBMetric.METRIC_AC_REACTIVE_POWER_PHASE_3

    # AC power factor
    AC_POWER_FACTOR = PBMetric.METRIC_AC_POWER_FACTOR
    AC_POWER_FACTOR_PHASE_1 = PBMetric.METRIC_AC_POWER_FACTOR_PHASE_1
    AC_POWER_FACTOR_PHASE_2 = PBMetric.METRIC_AC_POWER_FACTOR_PHASE_2
    AC_POWER_FACTOR_PHASE_3 = PBMetric.METRIC_AC_POWER_FACTOR_PHASE_3

    # AC energy metrics - Please be careful when using and check Enum docs
    AC_APPARENT_ENERGY = PBMetric.METRIC_AC_APPARENT_ENERGY
    AC_APPARENT_ENERGY_PHASE_1 = PBMetric.METRIC_AC_APPARENT_ENERGY_PHASE_1
    AC_APPARENT_ENERGY_PHASE_2 = PBMetric.METRIC_AC_APPARENT_ENERGY_PHASE_2
    AC_APPARENT_ENERGY_PHASE_3 = PBMetric.METRIC_AC_APPARENT_ENERGY_PHASE_3
    AC_ACTIVE_ENERGY = PBMetric.METRIC_AC_ACTIVE_ENERGY
    AC_ACTIVE_ENERGY_PHASE_1 = PBMetric.METRIC_AC_ACTIVE_ENERGY_PHASE_1
    AC_ACTIVE_ENERGY_PHASE_2 = PBMetric.METRIC_AC_ACTIVE_ENERGY_PHASE_2
    AC_ACTIVE_ENERGY_PHASE_3 = PBMetric.METRIC_AC_ACTIVE_ENERGY_PHASE_3
    AC_ACTIVE_ENERGY_CONSUMED = PBMetric.METRIC_AC_ACTIVE_ENERGY_CONSUMED
    AC_ACTIVE_ENERGY_CONSUMED_PHASE_1 = (
        PBMetric.METRIC_AC_ACTIVE_ENERGY_CONSUMED_PHASE_1
    )
    AC_ACTIVE_ENERGY_CONSUMED_PHASE_2 = (
        PBMetric.METRIC_AC_ACTIVE_ENERGY_CONSUMED_PHASE_2
    )
    AC_ACTIVE_ENERGY_CONSUMED_PHASE_3 = (
        PBMetric.METRIC_AC_ACTIVE_ENERGY_CONSUMED_PHASE_3
    )
    AC_ACTIVE_ENERGY_DELIVERED = PBMetric.METRIC_AC_ACTIVE_ENERGY_DELIVERED
    AC_ACTIVE_ENERGY_DELIVERED_PHASE_1 = (
        PBMetric.METRIC_AC_ACTIVE_ENERGY_DELIVERED_PHASE_1
    )
    AC_ACTIVE_ENERGY_DELIVERED_PHASE_2 = (
        PBMetric.METRIC_AC_ACTIVE_ENERGY_DELIVERED_PHASE_2
    )
    AC_ACTIVE_ENERGY_DELIVERED_PHASE_3 = (
        PBMetric.METRIC_AC_ACTIVE_ENERGY_DELIVERED_PHASE_3
    )
    AC_REACTIVE_ENERGY = PBMetric.METRIC_AC_REACTIVE_ENERGY
    AC_REACTIVE_ENERGY_PHASE_1 = PBMetric.METRIC_AC_REACTIVE_ENERGY_PHASE_1
    AC_REACTIVE_ENERGY_PHASE_2 = PBMetric.METRIC_AC_REACTIVE_ENERGY_PHASE_2
    AC_REACTIVE_ENERGY_PHASE_3 = PBMetric.METRIC_AC_REACTIVE_ENERGY_PHASE_3

    # AC harmonics
    AC_TOTAL_HARMONIC_DISTORTION_CURRENT = (
        PBMetric.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT
    )
    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_1 = (
        PBMetric.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_1
    )
    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_2 = (
        PBMetric.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_2
    )
    AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_3 = (
        PBMetric.METRIC_AC_TOTAL_HARMONIC_DISTORTION_CURRENT_PHASE_3
    )

    # General BMS metrics
    BATTERY_CAPACITY = PBMetric.METRIC_BATTERY_CAPACITY
    BATTERY_SOC_PCT = PBMetric.METRIC_BATTERY_SOC_PCT
    BATTERY_TEMPERATURE = PBMetric.METRIC_BATTERY_TEMPERATURE

    # General inverter metrics
    INVERTER_TEMPERATURE = PBMetric.METRIC_INVERTER_TEMPERATURE
    INVERTER_TEMPERATURE_CABINET = PBMetric.METRIC_INVERTER_TEMPERATURE_CABINET
    INVERTER_TEMPERATURE_HEATSINK = PBMetric.METRIC_INVERTER_TEMPERATURE_HEATSINK
    INVERTER_TEMPERATURE_TRANSFORMER = PBMetric.METRIC_INVERTER_TEMPERATURE_TRANSFORMER

    # EV charging station metrics
    EV_CHARGER_TEMPERATURE = PBMetric.METRIC_EV_CHARGER_TEMPERATURE

    # General sensor metrics
    SENSOR_WIND_SPEED = PBMetric.METRIC_SENSOR_WIND_SPEED
    SENSOR_WIND_DIRECTION = PBMetric.METRIC_SENSOR_WIND_DIRECTION
    SENSOR_TEMPERATURE = PBMetric.METRIC_SENSOR_TEMPERATURE
    SENSOR_RELATIVE_HUMIDITY = PBMetric.METRIC_SENSOR_RELATIVE_HUMIDITY
    SENSOR_DEW_POINT = PBMetric.METRIC_SENSOR_DEW_POINT
    SENSOR_AIR_PRESSURE = PBMetric.METRIC_SENSOR_AIR_PRESSURE
    SENSOR_IRRADIANCE = PBMetric.METRIC_SENSOR_IRRADIANCE

    @classmethod
    @deprecated("Use `frequenz.client.common.enum_proto.enum_from_proto` instead.")
    def from_proto(cls, metric: PBMetric.ValueType) -> Self:
        """Convert a protobuf Metric value to Metric enum.

        Args:
            metric: Metric to convert.
        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(m.value == metric for m in cls):
            return cls(Metric.UNSPECIFIED)

        return cls(metric)

    def to_proto(self) -> PBMetric.ValueType:
        """Convert a Metric object to protobuf Metric.

        Returns:
            Protobuf message corresponding to the Metric object.
        """
        return self.value
