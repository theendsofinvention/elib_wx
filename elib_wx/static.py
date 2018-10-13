# coding=utf-8
"""
elib_wx static values
"""

import typing

UNIT_TRANSLATION = {
    'mb': 'millibars',
    'hpa': 'hecto pascals',
    'in': 'inches',
    'inhg': 'inches of mercury',
    'mmhg': 'millimeters of mercury',
    'c': 'celsius',
    'f': 'fahrenheit',
}
CLOUD_METAR_TO_DCS: typing.Dict[str, typing.Tuple[int, int]] = {
    'SKC': (0, 0),
    'CLR': (0, 0),
    'NSC': (0, 0),
    'NCD': (0, 0),
    'FEW': (1, 3),
    'SCT': (4, 6),
    'BKN': (7, 8),
    'OVC': (9, 10),
    '///': (0, 0),
    'VV': (0, 0)
}
CLOUD_DCS_TO_METAR: typing.Dict[int, str] = {
    0: 'SKC',
    1: 'FEW',
    2: 'FEW',
    3: 'FEW',
    4: 'SCT',
    5: 'SCT',
    6: 'SCT',
    7: 'BKN',
    8: 'BKN',
    9: 'OVC',
    10: 'OVC',
}
CLOUD_TRANSLATIONS = {
    'OVC': 'Overcast layer at {}',
    'BKN': 'Broken layer at {}',
    'SCT': 'Scattered clouds at {}',
    'FEW': 'Few clouds at {}',
    'VV': 'Vertical visibility up to {}',
    'CLR': 'Sky Clear',
    'SKC': 'Sky Clear',
    'AC': 'Altocumulus',
    'ACC': 'Altocumulus Castellanus',
    'AS': 'Altostratus',
    'CB': 'Cumulonimbus',
    'CC': 'Cirrocumulus',
    'CI': 'Cirrus',
    'CS': 'Cirrostratus',
    'CU': 'Cumulus',
    'C': 'Cumulus',
    'FC': 'Fractocumulus',
    'FS': 'Fractostratus',
    'NS': 'Nimbostratus',
    'SC': 'Stratocumulus',
    'ST': 'Stratus',
    'TCU': 'Towering Cumulus'
}
PRESSURE_TENDENCIES = {
    '0': 'Increasing, then decreasing',
    '1': 'Increasing, then steady',
    '2': 'Increasing steadily or unsteadily',
    '3': 'Decreasing or steady, then increasing',
    '4': 'Steady',
    '5': 'Decreasing, then increasing',
    '6': 'Decreasing, then steady',
    '7': 'Decreasing steadily or unsteadily',
    '8': 'Steady or increasing, then decreasing',
}
