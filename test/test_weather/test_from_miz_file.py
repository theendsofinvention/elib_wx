# coding=utf-8

import inflect
import pytest

import elib_wx

_CONVERT = inflect.engine()


@pytest.mark.weather
def test_from_miz_caucasus(caucasus_test_file):
    wx = elib_wx.Weather(str(caucasus_test_file))
    assert str(caucasus_test_file) == wx.source
    assert 'MIZ file' == wx.source_type
    assert 9999 == wx.visibility.value()
    assert 20 == wx.temperature.value()
    assert wx.dew_point.value() < wx.temperature.value()
    assert 'NOSIG' == wx.remarks
    assert 'XXXX' == wx.station_icao
    assert 'unknown airport (XXXX)' == wx.station_name
    assert [] == wx.cloud_layers
    assert '040000Z' == wx.date_time.repr
    assert 180 == wx.wind_direction.value()
    assert 0 == wx.wind_speed.value()
    assert 0 == wx.wind_gust.value()
    assert [] == wx.wind_direction_range
    assert wx.wind_direction_is_variable is False
    assert [] == wx.other
    assert f'XXXX 040000Z 18000KTS 9999M 20/{wx.dew_point.value():02d} Q1013 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Thursday the 01st of September at 0400 zulu. Wind calm. CAVOK. ' \
           f'Temperature 20°C, 68°F. Dew point {wx.dew_point.value():02d}°C, {wx.dew_point.value(unit="f"):02d}°F. ' \
           f'Altimeter 760mmHg, 1013hPa, 29.92inHg. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Thursday the first of September at zero four zero zero zulu. ' \
           'Wind calm. cavok. Temperature two zero degrees celsius, six eight degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven six zero millimeters of mercury, ' \
           'one zero one three hecto Pascals, ' \
           'two nine point nine two inches of mercury. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_persian_gulf(persian_gulf_test_file):
    wx = elib_wx.Weather(str(persian_gulf_test_file))
    assert wx.source == str(persian_gulf_test_file)
    assert 'MIZ file' == wx.source_type
    assert '040000Z' == wx.date_time.repr
    assert f'XXXX 040000Z 18000KTS 9999M 20/{wx.dew_point.value():02d} Q1013 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Wednesday the 01st of June at 0400 zulu. Wind calm. CAVOK. ' \
           f'Temperature 20°C, 68°F. Dew point {wx.dew_point.value():02d}°C, {wx.dew_point.value(unit="f"):02d}°F. ' \
           f'Altimeter 760mmHg, 1013hPa, 29.92inHg. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Wednesday the first of June at zero four zero zero zulu. ' \
           'Wind calm. cavok. Temperature two zero degrees celsius, six eight degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven six zero millimeters of mercury, ' \
           'one zero one three hecto Pascals, ' \
           'two nine point nine two inches of mercury. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_nevada(nevada_test_file):
    wx = elib_wx.Weather(str(nevada_test_file))
    assert wx.source == str(nevada_test_file)
    assert 'MIZ file' == wx.source_type
    assert '150000Z' == wx.date_time.repr
    assert 'Weather for unknown airport (XXXX) on Wednesday the 01st of June at 1500 zulu. Wind calm. CAVOK. ' \
           f'Temperature 20°C, 68°F. Dew point {wx.dew_point.value():02d}°C, {wx.dew_point.value(unit="f"):02d}°F. ' \
           f'Altimeter 760mmHg, 1013hPa, 29.92inHg. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Wednesday the first of June at one five zero zero zulu. ' \
           'Wind calm. cavok. Temperature two zero degrees celsius, six eight degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven six zero millimeters of mercury, ' \
           'one zero one three hecto Pascals, ' \
           'two nine point nine two inches of mercury. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_wx1(wx_test_file_1):
    wx = elib_wx.Weather(str(wx_test_file_1))
    assert wx.source == str(wx_test_file_1)
    assert wx.source_type == 'MIZ file'
    assert 4710 == wx.visibility.value()
    assert 10 == wx.temperature.value()
    assert wx.dew_point.value() < wx.temperature.value()
    assert 'NOSIG' == wx.remarks
    assert 'XXXX' == wx.station_icao
    assert 'unknown airport (XXXX)' == wx.station_name
    assert [elib_wx.avwx.structs.Cloud(repr='SCT016', type='SCT', altitude=16, modifier=None)] == wx.cloud_layers
    assert '080000Z' == wx.date_time.repr
    assert 277 == wx.wind_direction.value()
    assert 5 == wx.wind_speed.value()
    assert 7 == wx.wind_gust.value()
    assert [] == wx.wind_direction_range
    assert wx.wind_direction_is_variable is False
    assert ['PO', 'RA'] == wx.other
    assert f'XXXX 080000Z 27710KTS 4710M PO RA SCT016 10/{wx.dew_point.value():02d} Q0987 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Wednesday the 01st of June at 0800 zulu. ' \
           'Wind 277 10kts (gusting 14kts knots). ' \
           'Visibility 4710m, 2.93SM. ' \
           'Temperature 10°C, 50°F. ' \
           f'Dew point {wx.dew_point.value()}°C, {wx.dew_point.value(unit="f")}°F. ' \
           'Altimeter 740mmHg, 987hPa, 29.13inHg. ' \
           'Dust Whirls. Rain. Scattered clouds at 1600ft. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Wednesday the first of June at zero eight zero zero zulu. ' \
           'Wind two seven seven one zero knots (gusting one four knots knots). ' \
           'Visibility four thousand seven hundred and ten meters, two point nine three miles. ' \
           'Temperature one zero degrees celsius, five zero degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven four zero millimeters of mercury, nine eight seven hecto Pascals, ' \
           'two nine point one three ' \
           'inches of mercury. ' \
           'Dust Whirls. Rain. Scattered clouds at one thousand six hundred feet. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_thunderstorm(wx_test_file_thunderstorm):
    wx = elib_wx.Weather(str(wx_test_file_thunderstorm))
    assert str(wx_test_file_thunderstorm) == wx.source
    assert 'MIZ file' == wx.source_type
    assert 4710 == wx.visibility.value()
    assert 10 == wx.temperature.value()
    assert wx.dew_point.value() < wx.temperature.value()
    assert 'NOSIG' == wx.remarks
    assert 'XXXX' == wx.station_icao
    assert 'unknown airport (XXXX)' == wx.station_name
    assert [elib_wx.avwx.structs.Cloud(repr='OVC016', type='OVC', altitude=16, modifier=None)] == wx.cloud_layers
    assert '080000Z' == wx.date_time.repr
    assert 277 == wx.wind_direction.value()
    assert 5 == wx.wind_speed.value()
    assert 7 == wx.wind_gust.value()
    assert [] == wx.wind_direction_range
    assert wx.wind_direction_is_variable is False
    assert ['DS', '+RATS'] == wx.other
    assert f'XXXX 080000Z 27710KTS 4710M DS +RATS OVC016 10/{wx.dew_point.value():02d} Q0987 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Wednesday the 01st of June at 0800 zulu. ' \
           'Wind 277 10kts (gusting 14kts knots). ' \
           'Visibility 4710m, 2.93SM. ' \
           'Temperature 10°C, 50°F. ' \
           f'Dew point {wx.dew_point.value()}°C, {wx.dew_point.value(unit="f")}°F. ' \
           'Altimeter 740mmHg, 987hPa, 29.13inHg. ' \
           'Duststorm. Heavy Rain Thunderstorm. Overcast layer at 1600ft. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Wednesday the first of June at zero eight zero zero zulu. ' \
           'Wind two seven seven one zero knots (gusting one four knots knots). ' \
           'Visibility four thousand seven hundred and ten meters, two point nine three miles. ' \
           'Temperature one zero degrees celsius, five zero degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven four zero millimeters of mercury, nine eight seven hecto Pascals, ' \
           'two nine point one three ' \
           'inches of mercury. ' \
           'Duststorm. Heavy Rain Thunderstorm. Overcast layer at one thousand six hundred feet. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_snow(wx_test_file_snow):
    wx = elib_wx.Weather(str(wx_test_file_snow))
    assert str(wx_test_file_snow) == wx.source
    assert 'MIZ file' == wx.source_type
    assert 4710 == wx.visibility.value()
    assert -7.6 == wx.temperature.value()
    assert wx.dew_point.value() < wx.temperature.value()
    assert 'NOSIG' == wx.remarks
    assert 'XXXX' == wx.station_icao
    assert 'unknown airport (XXXX)' == wx.station_name
    assert [elib_wx.avwx.structs.Cloud(repr='OVC016', type='OVC', altitude=16, modifier=None)] == wx.cloud_layers
    assert '080000Z' == wx.date_time.repr
    assert 277 == wx.wind_direction.value()
    assert 5 == wx.wind_speed.value()
    assert 7 == wx.wind_gust.value()
    assert [] == wx.wind_direction_range
    assert wx.wind_direction_is_variable is False
    assert ['DS', 'SN', 'FZ'] == wx.other
    assert f'XXXX 080000Z 27710KTS 4710M DS SN FZ OVC016 ' \
           f'M-7.6/M{wx.dew_point.value():02d} Q0987 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Saturday the 01st of January at 0800 zulu. ' \
           'Wind 277 10kts (gusting 14kts knots). ' \
           'Visibility 4710m, 2.93SM. ' \
           'Temperature -7.6°C, 18°F. ' \
           f'Dew point {wx.dew_point.value()}°C, {wx.dew_point.value(unit="f")}°F. ' \
           'Altimeter 740mmHg, 987hPa, 29.13inHg. ' \
           'Duststorm. Snow. Freezing. Overcast layer at 1600ft. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Saturday the first of January at zero eight zero zero zulu. ' \
           'Wind two seven seven one zero knots (gusting one four knots knots). ' \
           'Visibility four thousand seven hundred and ten meters, two point nine three miles. ' \
           'Temperature minus seven point six degrees celsius, one eight degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven four zero millimeters of mercury, nine eight seven hecto Pascals, two nine point one ' \
           'three inches of mercury. ' \
           'Duststorm. Snow. Freezing. Overcast layer at one thousand six hundred feet. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_snowstorm(wx_test_file_snowstorm):
    wx = elib_wx.Weather(str(wx_test_file_snowstorm))
    assert str(wx_test_file_snowstorm) == wx.source
    assert 'MIZ file' == wx.source_type
    assert 4710 == wx.visibility.value()
    assert -7.6 == wx.temperature.value()
    assert wx.dew_point.value() < wx.temperature.value()
    assert 'NOSIG' == wx.remarks
    assert 'XXXX' == wx.station_icao
    assert 'unknown airport (XXXX)' == wx.station_name
    assert [elib_wx.avwx.structs.Cloud(repr='OVC016', type='OVC', altitude=16, modifier=None)] == wx.cloud_layers
    assert '080000Z' == wx.date_time.repr
    assert 277 == wx.wind_direction.value()
    assert 5 == wx.wind_speed.value()
    assert 7 == wx.wind_gust.value()
    assert [] == wx.wind_direction_range
    assert wx.wind_direction_is_variable is False
    assert ['DS', '+BLSN', 'FZ'] == wx.other
    assert f'XXXX 080000Z 27710KTS 4710M DS +BLSN FZ OVC016 ' \
           f'M-7.6/M{wx.dew_point.value():02d} Q0987 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Saturday the 01st of January at 0800 zulu. ' \
           'Wind 277 10kts (gusting 14kts knots). ' \
           'Visibility 4710m, 2.93SM. ' \
           'Temperature -7.6°C, 18°F. ' \
           f'Dew point {wx.dew_point.value()}°C, {wx.dew_point.value(unit="f")}°F. ' \
           'Altimeter 740mmHg, 987hPa, 29.13inHg. ' \
           'Duststorm. Heavy Blowing Snow. Freezing. Overcast layer at 1600ft. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Saturday the first of January at zero eight zero zero zulu. ' \
           'Wind two seven seven one zero knots (gusting one four knots knots). ' \
           'Visibility four thousand seven hundred and ten meters, two point nine three miles. ' \
           'Temperature minus seven point six degrees celsius, one eight degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven four zero millimeters of mercury, nine eight seven hecto Pascals, two nine point one ' \
           'three inches of mercury. ' \
           'Duststorm. Heavy Blowing Snow. Freezing. Overcast layer at one thousand six hundred feet. ' \
           'No significant change.' == wx.as_speech()


@pytest.mark.weather
def test_from_miz_heavy_dust(wx_test_file_heavy_dust):
    wx = elib_wx.Weather(str(wx_test_file_heavy_dust))
    assert str(wx_test_file_heavy_dust) == wx.source
    assert 'MIZ file' == wx.source_type
    assert 4710 == wx.visibility.value()
    assert 10 == wx.temperature.value()
    assert wx.dew_point.value() < wx.temperature.value()
    assert 'NOSIG' == wx.remarks
    assert 'XXXX' == wx.station_icao
    assert 'unknown airport (XXXX)' == wx.station_name
    assert [elib_wx.avwx.structs.Cloud(repr='SCT016', type='SCT', altitude=16, modifier=None)] == wx.cloud_layers
    assert '080000Z' == wx.date_time.repr
    assert 277 == wx.wind_direction.value()
    assert 5 == wx.wind_speed.value()
    assert 7 == wx.wind_gust.value()
    assert [] == wx.wind_direction_range
    assert wx.wind_direction_is_variable is False
    assert ['DS', 'RA'] == wx.other
    assert f'XXXX 080000Z 27710KTS 4710M DS RA SCT016 ' \
           f'10/{wx.dew_point.value():02d} Q0987 NOSIG' == wx.raw_metar_str
    assert 'Weather for unknown airport (XXXX) on Wednesday the 01st of June at 0800 zulu. ' \
           'Wind 277 10kts (gusting 14kts knots). ' \
           'Visibility 4710m, 2.93SM. ' \
           'Temperature 10°C, 50°F. ' \
           f'Dew point {wx.dew_point.value()}°C, {wx.dew_point.value(unit="f")}°F. ' \
           'Altimeter 740mmHg, 987hPa, 29.13inHg. ' \
           'Duststorm. ' \
           'Rain. ' \
           'Scattered clouds at 1600ft. ' \
           'No significant change.' == wx.as_str()
    dew_point_c = _CONVERT.number_to_words(wx.dew_point.value(), group=1).replace(',', '')
    dew_point_f = _CONVERT.number_to_words(wx.dew_point.value(unit='f'), group=1).replace(',', '')
    assert 'Weather for unknown airport (XXXX) on Wednesday the first of June at zero eight zero zero zulu. ' \
           'Wind two seven seven one zero knots (gusting one four knots knots). ' \
           'Visibility four thousand seven hundred and ten meters, two point nine three miles. ' \
           'Temperature one zero degrees celsius, five zero degrees fahrenheit. ' \
           f'Dew point {dew_point_c} degrees celsius, {dew_point_f} degrees fahrenheit. ' \
           'Altimeter seven four zero millimeters of mercury, nine eight seven hecto Pascals, two nine point one ' \
           'three inches of mercury. ' \
           'Duststorm. ' \
           'Rain. ' \
           'Scattered clouds at one thousand six hundred feet. ' \
           'No significant change.' == wx.as_speech()
