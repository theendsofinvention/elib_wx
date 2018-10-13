# coding=utf-8
"""
Testing utilities
"""

import typing


class _TestValue:

    def __init__(self,
                 *,
                 attr_name: str,
                 expected_result,
                 get_value: typing.Optional[bool] = False,
                 units: typing.Optional[str] = None):
        self.attr_name = attr_name
        self.get_value = get_value
        self.units = units
        self.expected_result = expected_result

    def _get_value(self, _obj) -> typing.Any:
        if self.get_value:
            return getattr(_obj, self.attr_name).value(self.units)

        return getattr(_obj, self.attr_name)

    def verify(self, _obj: typing.Any) -> typing.Tuple[typing.Any, typing.Any]:
        return self.expected_result, self._get_value(_obj)


class _TestCall:

    def __init__(self, attr_name: str, expected: typing.Any, *args, **kwargs):
        self.attr_name = attr_name
        self.args = args
        self.kwargs = kwargs
        self.expected_result = expected

    def _get_value(self, _obj) -> typing.Any:
        return getattr(_obj, self.attr_name)(*self.args, **self.kwargs)

    def verify(self, _obj: typing.Any) -> typing.Tuple[typing.Any, typing.Any]:
        return self.expected_result, self._get_value(_obj)
