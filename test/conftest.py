# coding=utf-8
"""
Root conftest file
"""

import os
import sys
import typing
from pathlib import Path

import pytest
from mockito import unstub, verifyStubbedInvocationsAreUsed

from test.refresh_test_data import iterate_test_data

HERE = Path('.').resolve().absolute()


def pytest_configure(config):
    """
    Runs at tests startup

    Args:
        config: pytest config args
    """
    print('Pytest config:', config.option)
    setattr(sys, '_called_from_test', True)


# noinspection SpellCheckingInspection
def pytest_unconfigure(config):
    """Tear down"""
    assert config
    delattr(sys, '_called_from_test')


def pytest_addoption(parser):
    """
    Tests marked with "@pytest.mark.long" will be skipped unless "--long" is set on the command line.
    """
    parser.addoption("--long", action="store_true",
                     help="run long tests")


def pytest_runtest_setup(item):
    """
    Tests marked with "@pytest.mark.long" will be skipped unless "--long" is set on the command line.
    """
    long_marker = item.get_marker("long")
    if long_marker is not None and not item.config.getoption('long'):
        pytest.skip(f'{item.location}: skipping long tests')


@pytest.fixture(autouse=True)
def _global_tear_down(tmpdir, monkeypatch):
    """
    Maintains a sane environment between tests
    """
    try:
        monkeypatch.delenv('APPVEYOR')
    except KeyError:
        pass
    current_dir = os.getcwd()
    folder = Path(tmpdir).absolute()
    os.chdir(folder)
    yield
    verifyStubbedInvocationsAreUsed()
    unstub()
    os.chdir(current_dir)


@pytest.fixture(autouse=True)
def _clean_os_env():
    env = os.environ.copy()
    yield
    for key, value in env.items():
        os.environ[key] = value
    for key in os.environ.keys():
        if key not in env.keys():
            del os.environ[key]


@pytest.fixture(
    params=list(iterate_test_data()),
)
def metar_string(request) -> str:
    """Iterates over a little over 10k METAR strings"""
    yield request.param


@pytest.fixture()
def with_db():
    setattr(sys, '_enable_db', True)
    yield
    delattr(sys, '_enable_db')


@pytest.fixture()
def all_metar_strings() -> typing.List[str]:
    """Yields a little over 10k METAR strings as a list"""
    yield list(iterate_test_data())


@pytest.fixture()
def examples_data_file() -> Path:
    """Yields the path to a file containing Base64, UTF8 encoded METAR strings (a little over 10k of them)"""
    yield Path(HERE, 'examples.txt').absolute()


@pytest.fixture()
def caucasus_test_file() -> Path:
    return Path(HERE, 'test/test_files/test_caucasus.miz').resolve().absolute()


@pytest.fixture()
def nevada_test_file() -> Path:
    return Path(HERE, 'test/test_files/test_nevada.miz').resolve().absolute()


@pytest.fixture()
def persian_gulf_test_file() -> Path:
    return Path(HERE, 'test/test_files/test_persiangulf.miz').resolve().absolute()


@pytest.fixture()
def wx_test_file_1() -> Path:
    return Path(HERE, 'test/test_files/test_wx_1.miz').resolve().absolute()


@pytest.fixture()
def wx_test_file_heavy_dust() -> Path:
    return Path(HERE, 'test/test_files/test_wx_heavy_dust.miz').resolve().absolute()


@pytest.fixture()
def wx_test_file_snow() -> Path:
    return Path(HERE, 'test/test_files/test_wx_snow.miz').resolve().absolute()


@pytest.fixture()
def wx_test_file_snowstorm() -> Path:
    return Path(HERE, 'test/test_files/test_wx_snowstorm.miz').resolve().absolute()


@pytest.fixture()
def wx_test_file_thunderstorm() -> Path:
    return Path(HERE, 'test/test_files/test_wx_thunderstorm.miz').resolve().absolute()
