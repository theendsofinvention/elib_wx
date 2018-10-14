# coding=utf-8

import logging
import typing
from pathlib import Path

import pytest

import elib_wx


class CustomHandler(logging.Handler):
    """
    (very simple) logging handler to write all received messages to a text file
    """

    def emit(self, record):
        """No op"""
        pass

    def __init__(self):
        self.msg: typing.List[logging.LogRecord] = []
        super(CustomHandler, self).__init__()
        self.setLevel(logging.INFO)

    def handle(self, record: logging.LogRecord):
        """Append the message to the queue"""
        self.msg.append(record)

    def process(self, data_file: Path):
        """Writes all received message to the output file"""
        print('writing results to output file')
        with data_file.open(encoding='utf8', mode='w') as stream:
            for record in self.msg:
                if record.levelno >= 30:
                    stream.write('WARNING: ' + self.format(record) + '\n')
                else:
                    stream.write(self.format(record) + '\n')


@pytest.mark.last
@pytest.mark.long
def test_generate_data_for_review(all_metar_strings, examples_data_file, with_db):
    elib_wx_logger = logging.getLogger('elib.wx')
    elib_wx_logger.propagate = True
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    handler = CustomHandler()
    logger.addHandler(handler)
    logger.addHandler(logging.StreamHandler())

    counter = 1
    for metar_str in all_metar_strings:
        try:
            logger.info('# example %s', counter)
            logger.info('## raw metar:\n%s', metar_str)
            wx = elib_wx.Weather(metar_str)
            logger.info(
                '## speech produced by third party library\n%s',
                elib_wx.avwx.speech.metar(wx.metar_data, wx.metar_units)
            )
            try:
                logger.info('## speech meant to be read:\n%s', wx.as_str())
                logger.info('## speech meant to be used in TTS engine to produce MP3 files:\n%s', wx.as_speech())
            except IndexError:
                pytest.fail(metar_str)
            dcs_weather = wx.generate_dcs_weather()
            logger.info('## DCS weather:\n%s', dcs_weather.__repr__())
            logger.info('-' * 300)
            counter += 1
        except elib_wx.BadStationError:
            pass

    print('writing test result to:', examples_data_file)
    handler.process(examples_data_file)
