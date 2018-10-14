# coding=utf-8
"""
Simple dataclass representing values for a valid DCS weather, including specific constraints
"""
import typing

import dataclasses

from elib_wx import LOGGER


@dataclasses.dataclass
class DCSWeather:
    """
    Simple dataclass representing values for a valid DCS weather, including specific constraints
    """
    altimeter: int
    turbulence: int
    temperature: int
    wind_ground_speed: int
    wind_ground_dir: int
    wind_2000_speed: int
    wind_2000_dir: int
    wind_8000_speed: int
    wind_8000_dir: int
    precipitation_code: int
    cloud_density: int
    cloud_base: int
    cloud_thickness: int
    fog_enabled: bool
    fog_visibility: int
    fog_thickness: int
    dust_enabled: bool
    dust_density: int

    @staticmethod
    def normalize_altimeter(value: float) -> int:
        """
        Enforces DCS constraints for altimeter value
        """
        if value < 720:
            LOGGER.warning('altimeter value is too low, normalizing to 720 mmHg')
            return 720
        if value > 790:
            LOGGER.warning('altimeter value is too high, normalizing to 790 mmHg')
            return 790
        return int(value)

    @staticmethod
    def normalize_temperature(value: float) -> int:
        """
        Enforces DCS constraints for temperature value
        """
        if value < -20:
            LOGGER.warning('temperature value is too low, normalizing to -20° Celsius')
            return -20
        if value > 40:
            LOGGER.warning('temperature value is too high, normalizing to 40° Celsius')
            return 40
        return int(value)

    @staticmethod
    def normalize_turbulence(value: float) -> int:
        """
        Enforces DCS constraints for turbulence value
        """
        if value < 0:
            LOGGER.warning('turbulence value is too low, normalizing to 0')
            return 0
        if value > 60:
            LOGGER.warning('temperature value is too high, normalizing to 60')
            return 60
        return int(round(value, 0))

    @staticmethod
    def normalize_dust_density(value: float) -> int:
        """
        Enforces DCS constraints for dust density value
        """
        if value < 300:
            LOGGER.warning('dust density value is too low, normalizing to 300 meters')
            return 300
        if value > 3000:
            LOGGER.warning('dust density value is too high, normalizing to 3000 meters')
            return 3000
        return int(value)

    @staticmethod
    def normalize_fog_visibility(value: float) -> int:
        """
        Enforces DCS constraints for fog visibility value
        """
        if value < 0:
            LOGGER.warning('fog visibility value is too low, normalizing to 0 meters')
            return 0
        if value > 6000:
            LOGGER.warning('fog visibility value is too high, normalizing to 6000 meters')
            return 6000
        return int(value)

    @staticmethod
    def normalize_cloud_base(value: float) -> int:
        """
        Enforces DCS constraints for cloud base value
        """
        if value < 300:
            LOGGER.warning('cloud base value is too low, normalizing to 300 meters')
            return 300
        if value > 5000:
            LOGGER.warning('cloud base value is too high, normalizing to 5000 meters')
            return 5000
        return int(value)

    @staticmethod
    def normalize_cloud_thickness(value: float) -> int:
        """
        Enforces DCS constraints for cloud thickness value
        """
        if value < 200:
            LOGGER.warning('cloud thickness value is too low, normalizing to 200 meters')
            return 200
        if value > 2000:
            LOGGER.warning('cloud thickness value is too high, normalizing to 2000 meters')
            return 2000
        return int(value)

    @staticmethod
    def normalize_wind_speed(value: float, name: typing.Optional[str] = 'wind speed') -> int:
        """
        Enforces DCS constraints for wind speed value
        """
        if value < 0:
            LOGGER.warning('%s is too low, normalizing to 0 m/s', name)
            return 0
        if value > 50:
            LOGGER.warning('%s is too high, normalizing to 50 m/s', name)
            return 50
        return int(value)
