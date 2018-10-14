# coding=utf-8
"""
Interface to the "airports.db" package data file.
"""

import logging
import os
import sqlite3
import sys
import threading
import typing

import pkg_resources

LOGGER = logging.getLogger('elib.wx')

LOGGER.debug('reading airports.db')
DB_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'airports.db')
if not os.path.exists(DB_PATH):
    LOGGER.debug('airports.db not found locally, trying from pkg_resource')
    DB_PATH = pkg_resources.resource_filename('elib_wx', 'airports.db')
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(DB_PATH)
_DB = sqlite3.connect(DB_PATH, check_same_thread=False)
_DB_LOCK = threading.Lock()

DISABLE = False


def get_airport_name_from_icao(icao: str) -> str:
    """
    Obtains the name of an airport based on its ICAO code

    :param icao: ICAO code
    :type icao: str
    :return: airport name
    :rtype: str
    :raises exc.StationNotFoundError: raised when the ICAO code can't be found in the DB
    """
    if hasattr(sys, '_called_from_test'):
        if not hasattr(sys, '_enable_db'):
            return f'unknown airport ({icao})'
    with _DB_LOCK:
        icao = icao.upper()
        cursor = _DB.cursor()
        row: tuple = cursor.execute(f"SELECT name FROM airports WHERE icao = '{icao}'").fetchone()
        if row is None:
            # TODO: add issue page link
            LOGGER.warning('airport with ICAO "%s" not found; if you believe this is an error, please '
                           'contact me via the issue page of the project: %s',
                           icao, 'placeholder')
            return f'unknown airport ({icao})'
        airport_name: str = row[0]
        return airport_name


def find_icao_by_name(airport_name: str) -> typing.Dict[str, str]:
    """
    Finds all airports

    :param airport_name: name or part of the name of the airport to search for
    :type airport_name: str
    :return: dictionary of {icao: name} (may be empty)
    :rtype: dict
    """
    with _DB_LOCK:
        LOGGER.debug('looking for an airport named: %s', airport_name)
        cursor = _DB.cursor()
        search = cursor.execute(f"SELECT icao, name FROM airports WHERE UPPER(name) LIKE UPPER('%{airport_name}%');")
        result = search.fetchall()
        return {row[0]: row[1] for row in result}
