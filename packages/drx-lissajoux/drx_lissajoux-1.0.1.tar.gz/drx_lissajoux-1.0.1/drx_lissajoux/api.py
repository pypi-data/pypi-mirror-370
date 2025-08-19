"""Lissajoux network API"""

import logging
from enum import Enum
from typing import overload
from xml.etree import ElementTree as XML

from drx_protocol.const import DEFAULT_PORT, DEFAULT_TIMEOUT
from drx_protocol.exceptions import InvalidParameter
from drx_protocol.protocol import drx_bool
from drx_protocol.protocol import drx_command as cmd
from drx_protocol.protocol import drx_enum, drx_float, drx_int, drx_property, drx_protocol

_LOGGER = logging.getLogger(__name__)


class ChillerStatusEnum(Enum):
    """Possible states for the chiller"""

    ok = 0
    error = 1
    unstable = 2
    notconnected = 3


class ChillerErrorEnum(Enum):
    """Possible errors for the chiller"""

    ok = 0
    communication_error = 1
    up_temp_limit = 2
    low_temp_limit = 3
    power_failure = 4
    thermostat_alarm = 5
    internal_sensor_disconnect = 6
    external_sensor_disconnect = 7
    high_temp_cutoff = 8
    low_temp_cutoff = 9
    output_failure = 10
    auto_tuning_alarm = 11
    low_fluid_level = 12
    status_error = 13
    modbus_error = 14
    low_flow_rate = 15


class InterlockEnum(Enum):
    """Possible interlock states"""

    ok = 0
    fault = 1
    unknown = 2


class Lissajoux:
    """Lissajoux network API class."""

    F1_power_enabled = drx_bool("SwX")
    F2_power_enabled = drx_bool("SwY")
    F1_power = drx_float("PwX")
    F2_power = drx_float("PwY")
    F1_phase = drx_float("PhX")
    F2_phase = drx_float("PhY")
    F1_frequency = drx_float("Frq")
    Cavity_temperature_setpoint = drx_float("Tsp")
    Driver_temperature_setpoint = drx_float("Tsd")
    Cavity_water_flow_control_enabled = drx_bool("Flc")
    Cavity_water_flow_setpoint = drx_float("Fls")
    Cavity_water_flow = drx_float("Flg")
    F1_transmitted_power = drx_float("TrX")
    F2_transmitted_power = drx_float("TrY")
    F1_reflected_power = drx_float("RfX")
    F2_reflected_power = drx_float("RfY")
    Cavity_temperature = drx_float("Tcv")
    Driver_temperature = drx_float("Tdr")
    Upconverter_temperature = drx_float("Tuc")
    Synthesizer_temperature = drx_float("Tsy")
    F1_amplifier_temperature = drx_float("Ta1")
    F2_amplifier_temperature = drx_float("Ta2")
    Enviroment_temperature = drx_float("Ten")
    Enviroment_temperature_coarse = drx_float("Tec")
    Enviroment_humidity = drx_float("Hen")
    F1_amplifier_current = drx_float("Ca1")
    F2_amplifier_current = drx_float("Ca2")
    Pickup_signal_power = drx_int("Pic")
    Cavity_water_temperature = drx_float("Tin")
    Driver_water_temperature = drx_float("Tid")
    Cavity_chiller_power_ratio = drx_int("CPR")
    Driver_chiller_power_ratio = drx_int("CPd")
    Cavity_chiller_status = drx_enum("Cst", ChillerStatusEnum)
    Driver_chiller_status = drx_enum("CSd", ChillerStatusEnum)
    Interlock_status = drx_int("Ist")
    Cavity_chiller_error = drx_enum("Cst", ChillerErrorEnum, offset=200)
    Driver_chiller_error = drx_enum("CSd", ChillerErrorEnum, offset=300)
    PSU_5_volt = drx_float("V05")
    PSU_5p5_volt = drx_float("V55")
    PSU_15_volt = drx_float("V15")
    PSU_m15_volt = drx_float("Vm5")
    PSU_24_volt = drx_float("V24")
    PSU_5V_current = drx_float("I05")
    PSU_5p5V_current = drx_float("I55")
    PSU_15V_current = drx_float("I15")
    PSU_m15V_current = drx_float("Im5")
    PSU_24V_current = drx_float("I24")

    def __init__(
        self,
        host: str,
        key_file: str | None = None,
        serial: str | None = None,
        organization: str | None = None,
        signature: str | None = None,
        port: int = DEFAULT_PORT,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        # If key_file is given, extract the serial, organization and signature from it
        if key_file is not None:
            xml_tree = XML.parse(key_file)
            xml_root = xml_tree.getroot()
            key_dict = xml_root.attrib
            serial = key_dict.get("serial", serial)
            organization = key_dict.get("organization", organization)
            signature = key_dict.get("signature", signature)

        if serial is None or organization is None or signature is None:
            raise InvalidParameter(
                "Not enough input parameters to Lissajoux class, "
                "use Lissajoux(host='192.168.1.100', key_file='./key_file.xml') or "
                "Lissajoux(host='192.168.1.100', serial=..., organization=..., signature=...)"
            )

        self._protocol = drx_protocol(host, serial, organization, signature, port, timeout)
        self._cache: dict[str, cmd] = {}

    def get_state(self) -> None:
        """Get the state of all properties and store in the cache"""
        # construct the list of commands from the drx properties
        cmds: list[cmd] = []
        for attribute in Lissajoux.__dict__.values():
            if isinstance(attribute, drx_property):
                cmds.append(cmd(attribute.cmd))
        # send the commands and store the results in the cache
        self._cache = self.send_command(cmds)

    def close(self) -> None:
        """Disconnect from the DrX device"""
        self._protocol.close()

    @property
    def available_properties(self) -> list[str]:
        """Get a list of the available properties of the Lissajoux"""
        props: list[str] = []
        for name, attribute in Lissajoux.__dict__.items():
            if isinstance(attribute, (property, drx_property)):
                props.append(name)
        return props

    @overload
    def send_command(self, command: list[cmd]) -> dict[str, cmd]: ...

    @overload
    def send_command(self, command: cmd) -> cmd: ...

    def send_command(self, command: list[cmd] | cmd) -> dict[str, cmd] | cmd:
        """Send a list of commands to the lissajoux and get the response"""
        return self._protocol.send_command(command)

    def _interlock_value(self, shift: int) -> InterlockEnum | None:
        """Internal function to retrieve the interlock status"""
        val = self.Interlock_status
        if val is None:
            return None
        return InterlockEnum(val >> shift & 3)

    @property
    def global_interlock(self) -> InterlockEnum | None:
        """Global interlock status from cache"""
        return self._interlock_value(0)

    @property
    def f1_amp_temp_interlock(self) -> InterlockEnum | None:
        """F1 amplifier temperature interlock status from cache"""
        return self._interlock_value(2)

    @property
    def f2_amp_temp_interlock(self) -> InterlockEnum | None:
        """F2 amplifier temperature interlock status from cache"""
        return self._interlock_value(4)

    @property
    def cavity_chiller_interlock(self) -> InterlockEnum | None:
        """Cavity chiller interlock status from cache"""
        return self._interlock_value(6)

    @property
    def driver_chiller_interlock(self) -> InterlockEnum | None:
        """Driver chiller interlock status from cache"""
        return self._interlock_value(8)

    @property
    def external_interlock(self) -> InterlockEnum | None:
        """External interlock status from cache"""
        return self._interlock_value(10)

    @property
    def heatsink_interlock(self) -> InterlockEnum | None:
        """Heatsink interlock status from cache"""
        return self._interlock_value(12)
