# coding=utf-8
# noinspection SpellCheckingInspection
"""
This utility module (re)generates the airport database used to obtain the name of an airport from its ICAO, or vice-
versa.

The database is in SQLite format, and is located in "elib_wx/airports.db"

Database structure:
    CREATE TABLE airports (icao text, name text)

Instead of using CSV, the database can be browsed/edited with the SQLite browser tool freely available at:
    https://sqlitebrowser.org/

The module is to be run with the source CSV file path as its first and only argument.

Example CSV structure:
(note: only the name & ICAO (ident) are of interest at this stage)

Headers:
    id,
    ident,
    type,
    name,
    latitude_deg,
    longitude_deg,
    elevation_ft,
    continent,
    iso_country,
    iso_region,
    municipality,
    scheduled_service,
    gps_code,
    iata_code,
    local_code,
    home_link,
    wikipedia_link,
    keywords,
    score,
    last_updated

Data:
    2434,
    EGLL,
    large_airport,
    "London Heathrow Airport",
    51.4706,
    -0.461941,
    83,
    EU,
    GB,
    GB-ENG,
    London,
    1,
    EGLL,
    LHR,
    ,
    http://www.heathrowairport.com/,https://en.wikipedia.org/wiki/Heathrow_Airport,
    "LON, Londres",
    1251675,
    2018-09-16T02:32:35+00:00
"""

import csv
import sqlite3
import sys
from pathlib import Path

DB_FILE_PATH = Path('elib_wx/airports.db').resolve().absolute()


def _generate_db(source_csv: str):
    if not DB_FILE_PATH:
        raise FileNotFoundError(DB_FILE_PATH)
    db = sqlite3.connect(str(DB_FILE_PATH))
    try:
        db.execute('DROP TABLE airports')
        db.commit()
    except sqlite3.OperationalError as err:
        if 'no such table' in err.args[0]:
            pass
        else:
            raise
    db.execute('''CREATE TABLE airports (icao text, name text)''')
    db.commit()
    cursor = db.cursor()
    csv_file = Path(source_csv).resolve().absolute()
    print('CSV file:', csv_file)
    with csv_file.open(encoding='utf8') as stream:
        reader = csv.DictReader(stream)
        for airport in reader:
            airport_icao = airport['ident']
            airport_name = airport['name'].replace("'", "''")
            query = f"INSERT INTO airports VALUES ('{airport_icao}', '{airport_name}')"
            cursor.execute(query)
    print('all done, committing')
    db.commit()
    db.close()


if __name__ == '__main__':
    _generate_db(*sys.argv[1:])
