# coding=utf-8
"""
Applies Weather object to a MIZ file
"""
from pathlib import Path

import elib_miz

from elib_wx import LOGGER, exc
from elib_wx.weather_abc import WeatherABC


def apply_weather_to_miz(weather_object: WeatherABC,
                         source_file: str,
                         out_file: str,
                         *,
                         overwrite: bool = False
                         ) -> None:
    """
    Applies Weather object to a MIZ file

    :param weather_object: weather object to apply to MIZ file
    :type weather_object: WeatherABC
    :param source_file: path to the source MIZ file to edit
    :type source_file: str
    :param out_file: path to the MIZ file to write
    :type out_file: str
    :param overwrite: allow overwriting existing MIZ files
    :type overwrite: bool
    """
    out_file_path = Path(out_file).absolute()
    if out_file_path.exists() and not overwrite:
        raise exc.FileAlreadyExistsError(str(out_file_path))
    source_file_path = Path(source_file).absolute()
    if not source_file_path.exists():
        raise exc.SourceMizFileNotFoundError(str(source_file_path))
    with elib_miz.Miz(str(source_file_path)) as miz:
        miz.mission = weather_object.apply_to_mission_dict(miz.mission)
        LOGGER.info('writing output file: %s', out_file_path)
        miz.zip(str(out_file_path))
