# coding=utf-8
"""
This module contains values expressed in different units
"""

import logging
import random
import typing

import dataclasses
import inflect

from elib_wx import avwx

LOGGER = logging.getLogger('elib.wx')

_CONVERT = inflect.engine()


def _gauss(mean: float, sigma: int) -> int:
    return int(random.gauss(mean, sigma))


@dataclasses.dataclass
class Unit:
    """
    Represents a unit
    """
    coef: float
    short: str
    long: str
    precision: int
    padding: typing.Optional[int] = None


# @dataclasses.dataclass
class Value:
    """
    Base class
    """
    default_unit: str  # noqa
    units: typing.Dict[str, Unit]
    _raw_value: float

    def __init__(self, value: typing.Union[int, float], unit: typing.Optional[str] = None) -> None:
        if unit is None:
            unit = self.default_unit
        self.set_value(value, unit)
        self._validate()

    def set_value(self, value: typing.Union[int, float], unit: typing.Optional[str] = None) -> None:
        """
        Sets the raw value for this Value

        :param value: value to set
        :type value: int or float
        :param unit: unit of value
        :type unit: str
        """
        _unit = self._get_unit_from_dict(unit)
        self._raw_value = value / _unit.coef

    def _get_unit_from_dict(self, unit: typing.Optional[str] = None) -> Unit:
        if unit is None:
            _unit = self.units[self.default_unit]
        else:
            if unit.lower() not in self.units:
                raise ValueError(f'unknown unit: {unit}')
            _unit = self.units[unit.lower()]
        return _unit

    def value(self, unit: typing.Optional[str] = None) -> float:
        """
        Value for this length

        :param unit: optional units
        :type unit: str
        :return: value
        :rtype: float
        """
        _unit = self._get_unit_from_dict(unit)
        if _unit.precision <= 0:
            return int(round(self._raw_value * _unit.coef, _unit.precision))

        return round(self._raw_value * _unit.coef, _unit.precision)

    @staticmethod
    def _pad(unit: Unit, value: typing.Union[str, int, float]) -> str:
        if unit.padding is None:
            return str(value)
        return str(value).zfill(unit.padding)

    def as_str(self, unit: typing.Optional[str] = None) -> str:
        """
        Get value as a string, with unit suffix/prefix

        :param unit: (optional) desired unit
        :type unit: str
        :return: value as a string
        :rtype: str
        """
        _unit = self._get_unit_from_dict(unit)
        _value = self.value(unit)
        _padded = self._pad(_unit, _value)
        return f'{_padded}{_unit.short}'

    def as_str_all_units(self) -> str:
        """
        :return: all possible representations of this value
        :rtype: str
        """
        _out = [self.as_str(_unit) for _unit in self.units]
        return ', '.join(_out)

    def spoken(self, unit: typing.Optional[str] = None) -> str:
        """
        :param unit: optional unit
        :type unit: str
        :return: speech compatible value and unit
        :rtype: str
        """
        _unit = self._get_unit_from_dict(unit)
        _value = str(self.value(unit))
        _padded = self._pad(_unit, _value)
        if '.' in _padded:
            val1, val2 = _padded.split('.')
            _spoken = avwx.core.spoken_number(val1) + ' point ' + avwx.core.spoken_number(val2)
        else:
            _spoken = avwx.core.spoken_number(_padded)
        unit_part = f' {_unit.long}' if _unit.long else ''
        return f'{_spoken}{unit_part}'

    def spoken_all_units(self) -> str:
        """
        :return: speech compatible value and unit for all possible representations of this value
        :rtype: str
        """
        _out = [self.spoken(_unit) for _unit in self.units]
        return ', '.join(_out)

    def to_string(self, unit: typing.Optional[str] = None, spoken: bool = False, all_units: bool = False) -> str:
        """
        Returns this value as a string

        :param unit: unit to convert the value into
        :type unit: str
        :param spoken: whether or not to make the returned string compatible with TTS engines
        :type spoken: bool
        :param all_units: whether or not to return all possible units for this value
        :type all_units: bool
        :return: value with units as string
        :rtype: str
        """
        if spoken:
            if all_units:
                return self.spoken_all_units()
            return self.spoken(unit)

        if all_units:
            return self.as_str_all_units()

        return self.as_str(unit)

    def __str__(self) -> str:
        return self.as_str()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._raw_value}, "{self.default_unit}")'

    def _validate(self) -> None:
        pass


class Length(Value):
    """Represents a distance between two points"""
    default_unit = 'm'
    units = {
        'm': Unit(1, 'm', 'meters', 0),
        'sm': Unit(0.00062136994949495, 'SM', 'miles', 2),
    }


class Visibility(Value):
    """Represents a distance between two points"""
    default_unit = 'm'
    units = {
        'm': Unit(1, 'm', 'meters', -2),
        'sm': Unit(0.00062136994949495, 'SM', 'miles', 1),
    }

    def value(self, unit: typing.Optional[str] = None) -> float:
        """
        Value for this length

        :param unit: optional units
        :type unit: str
        :return: value
        :rtype: float
        """
        if (unit is None or unit == 'm') and self._raw_value == 9999.0:
            return 9999

        return super(Visibility, self).value(unit)


class Pressure(Value):
    """Represents a pressure"""
    default_unit = 'mmhg'
    units = {
        'mmhg': Unit(1, 'mmHg', 'millimeters of mercury', 0),
        'hpa': Unit(1.33322387415, 'hPa', 'hecto Pascals', 0),
        'inhg': Unit(0.039370079197446, 'inHg', 'inches of mercury', 2),
    }


class Direction(Value):
    """
    Represents a cardinal direction, in degrees
    """
    default_unit = 'degrees'
    units = {
        'degrees': Unit(1, '', '', 0, 3)
    }

    def _validate(self):
        if not 0 <= self.value() <= 359:
            _normalized = self.normalize(self.value())
            LOGGER.warning('invalid direction: %s°; normalizing to: %s°', self.value(), _normalized)
            self.set_value(_normalized)

    @staticmethod
    def normalize(value: float) -> float:
        """
        Normalizes the direction to anything between 0 and 360

        :param value: original value
        :type value: float
        :return: normalized value
        :rtype: float
        """
        return value % 360

    @staticmethod
    def random_value() -> float:
        """
        Creates a random
        :return:
        :rtype:
        """
        return random.randint(0, 359)  # nosec

    @staticmethod
    def random() -> 'Direction':
        """
        Creates a random direction value

        :return: random direction
        :rtype: Direction
        """
        return Direction(Direction.random_value())

    def reverse(self) -> 'Direction':
        """
        Reverses a given direction

        :return: reversed direction
        :rtype: Direction
        """
        return Direction(self.normalize(self.value() - 180))


class WindDirection(Direction):
    """
    Represents the direction of the wind
    """

    def __init__(self, value: typing.Optional[typing.Union[int, float]], unit: typing.Optional[str] = None) -> None:
        if value is None:
            value = self.random_value()
        super(WindDirection, self).__init__(value, unit)

    def randomize_at_2000m(self) -> 'WindDirection':
        """
        Creates a randomized wind direction at 2000M for DCS

        :return: random wind direction
        :rtype: WindDirection
        """
        value = _gauss(self.value(), 40)
        normalized_value = self.normalize(value)
        return WindDirection(normalized_value)

    def randomize_at_8000m(self) -> 'WindDirection':
        """
        Creates a randomized wind direction at 8000M for DCS

        :return: random wind direction
        :rtype: WindDirection
        """
        value = _gauss(self.value(), 80)
        normalized_value = self.normalize(value)
        return WindDirection(normalized_value)

    def reverse(self) -> 'WindDirection':
        """
        Reveres the wind direction

        :return: reversed wind direction
        :rtype: WindDirection
        """
        return WindDirection(self.normalize(self.value() - 180))

    @staticmethod
    def random() -> 'WindDirection':
        """
        Creates a random Wind direction

        :return: random wind direction
        :rtype: WindDirection
        """
        return WindDirection(Direction.random_value())


class Speed(Value):
    """
    Represents a speed
    """
    default_unit = 'm/s'
    units = {
        'm/s': Unit(1, 'm/s', 'meters per second', 0),
        'kmh': Unit(3.6, 'km/h', 'kilometers per hour', 0),
        'kt': Unit(1.9438444924406, 'kts', 'knots', 0)
    }


class WindSpeed(Speed):
    """
    Represents the speed of the wind
    """

    def __init__(self, value: typing.Optional[typing.Union[int, float]], unit: typing.Optional[str] = None) -> None:
        if value is None:
            value = 0
        super(WindSpeed, self).__init__(value, unit)

    @staticmethod
    def random_value() -> float:
        """
        :return: random wind direction
        :rtype: float
        """
        return random.triangular(low=0, high=15, mode=5)  # nosec

    @staticmethod
    def randomize(base_speed: 'WindSpeed',
                  offset: float = 0.0,
                  coef: float = 1.0,
                  sigma: typing.Optional[int] = None
                  ) -> 'WindSpeed':
        """
        Creates a random wind direction using a gaussian distribution model

        :param base_speed: base wind speed to derive the random speed from
        :type base_speed: WindSpeed
        :param offset: fixed offset to be added to base value
        :type offset: float
        :param coef: fixed multiplier for base wind speed
        :type coef: float
        :param sigma: gauss sigma
        :type sigma: int
        :return: randomized wind speed
        :rtype: WindSpeed
        """
        if base_speed is None:
            base_speed = WindSpeed.random()
        if sigma is None:
            int_sigma = int(base_speed.value() / 4)
        else:
            int_sigma = sigma
        value = _gauss(offset + base_speed.value() * coef, int_sigma)
        return WindSpeed(value=value)

    def randomize_at_2000m(self) -> 'WindSpeed':
        """
        :return: random wind at 2000m for DCS (based on self)
        :rtype: WindSpeed
        """
        return WindSpeed.randomize(self, offset=5, coef=2)

    def randomize_at_8000m(self) -> 'WindSpeed':
        """
        :return: random wind at 2000m for DCS (based on self)
        :rtype: WindSpeed
        """
        return WindSpeed.randomize(self, offset=10, coef=3)

    @staticmethod
    def random() -> 'WindSpeed':
        """
        :return: random WindSpeed
        :rtype: WindSpeed
        """
        return WindSpeed(WindSpeed.random_value(), 'kt')


class Altitude(Value):
    """
    Represents a height
    """
    default_unit = 'm'
    units = {
        'm': Unit(1, 'm', 'meters', 0),
        'ft': Unit(3.2808398950131, 'ft', 'feet', 0)
    }


class CloudBase(Altitude):
    """
    Represents the base of clouds
    """

    def value(self, unit: typing.Optional[str] = None):
        """
        Value for this CloudBase
        """
        return int(super(CloudBase, self).value(unit))

    # def _validate(self):
    #     if self.value() < 300:
    #         LOGGER.warning('cloud base too low: %s; normalizing at 300m', self.value())
    #         self.set_value(300)
    #     if self.value() > 5000:
    #         LOGGER.warning('cloud base too high: %s; normalizing at 5000m', self.value())


class Temperature(Value):
    """
    Represents a temperature
    """
    default_unit = 'c'
    units = {
        'c': Unit(1, '°C', 'degrees celsius', 0),
        'f': Unit(1.8, '°F', 'degrees fahrenheit', 0),
    }

    def make_dummy_dew_point(self) -> 'Temperature':
        """
        Creates a dummy, semi sensible dew point for this temperature

        Method used: http://www-das.uwyo.edu/~geerts/cwx/notes/chap06/dewpoint.html

        :return: dew point
        :rtype: Temperature
        """
        _value = self.value()
        _relative_humidity = random.triangular(low=65, high=75, mode=70)  # nosec
        _dew_point_value = int(round(_value - ((100 - _relative_humidity) / 5), 0))
        return Temperature(_dew_point_value, unit='c')

    def set_value(self, value: typing.Union[int, float], unit: typing.Optional[str] = None) -> None:
        """
        Sets the raw value for this Value

        :param value: value to set
        :type value: int or float
        :param unit: unit of value
        :type unit: str
        """
        if unit is None:
            unit = self.default_unit
        else:
            unit = unit.lower()
        if unit == 'c':
            self._raw_value = value
        elif unit == 'f':
            self._raw_value = int(round((value - 32) * 5 / 9, 0))
        else:
            raise ValueError(f'unknown unit: {unit}')

    def value(self, unit: typing.Optional[str] = None) -> float:
        """
        Value for this length

        :param unit: optional units
        :type unit: str
        :return: value
        :rtype: float
        """
        if unit:
            unit = unit.lower()
        else:
            unit = 'c'
        if unit == 'c':
            return round(self._raw_value, 1)

        if unit == 'f':
            return int(round((self._raw_value * 9 / 5) + 32, 0))

        raise ValueError(f'unknown unit: {unit}')
