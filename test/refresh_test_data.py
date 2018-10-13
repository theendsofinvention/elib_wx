# coding=utf-8
"""
Utility file to (re)generate a Base64, UTF8 encoded date file containing test METAR strings
"""
import base64
import logging
import pprint
import typing
from pathlib import Path

LOGGER = logging.getLogger('elib.wx')

# Path to METAR test files pulled from NOAA anonymous FTP
_PATH_TO_METAR_DIR = Path('../METARs').resolve().absolute()

# Path to UTF8/Base64 encoded list of METAR strings
TEST_DATA_FILE = Path('./test/test_files/test_data').resolve().absolute()

# UTF8 encoded separator for test data file
SEPARATOR = separator = '\n'.encode('utf8')


def iterate_metar_files() -> typing.Iterator[Path]:
    """
    Iterates over all METAR text files

    :return: METAR files
    :rtype: Iterator of Path
    """
    LOGGER.info('iterating over METAR files in: %s', _PATH_TO_METAR_DIR)
    for file in _PATH_TO_METAR_DIR.iterdir():
        yield file


def iterate_test_data() -> typing.Iterator[str]:
    """
    Iterates over METAR stored in the test data file

    :return: METAR strings
    :rtype: Iterator of strings
    """
    raw_data = TEST_DATA_FILE.read_bytes().split(SEPARATOR)
    for encoded_metar in raw_data:
        yield base64.b64decode(encoded_metar).decode('utf8')


def main():
    """
    Refreshes the base64 "test_data" file using METAR text files pulled from NOAA anonymous FTP service.
    """

    # Setup basic console logging
    elib_wx_logger = logging.getLogger('elib.wx')
    elib_wx_logger.propagate = True
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    test_data = []
    corrupt_files = []

    for file in iterate_metar_files():
        try:
            metar_data = file.read_text(encoding='utf8')
        except UnicodeDecodeError:
            corrupt_files.append(file.name)
        else:
            metar_str = metar_data.split('\n')[1]
            encoded_metar_str = base64.b64encode(metar_str.encode('utf8'))
            test_data.append(encoded_metar_str)

    logger.warning('corrupted METAR file:\n%s', pprint.pformat(corrupt_files, indent=4))

    logger.info('writing result to: %s', TEST_DATA_FILE)
    TEST_DATA_FILE.write_bytes(SEPARATOR.join(test_data))


if __name__ == '__main__':
    main()
