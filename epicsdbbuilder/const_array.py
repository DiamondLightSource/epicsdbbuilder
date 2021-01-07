from decimal import Decimal
from .recordbase import quote_string
from .parameter import Parameter

__all__ = ['ConstArray']


class ConstArray:
    """Constant Link Values. EPICS Base 7.0.4.1 and above.

    Example: PY Source
    ------------------
    `r = records.lsi('r', INP=ConstArray(['Plain String not DBLINK']))`

    Example: Generated DB
    ---------------------
    `field(INP, ["Plain String not DBLINK"])`
    """

    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._assert_valid(value)
        self._value = value

    def _assert_valid(self, value, record=None, fieldname=None):
        id = 'ConstArray' \
            if record is None or fieldname is None \
            else f'ConstArray@{record}.{fieldname} :'

        assert isinstance(value, list) \
            or isinstance(value, tuple), \
            f'{id} expects a list or a tuple but [{type(value)}] was supplied.'

        numbers = False
        strings = False
        for index, value in enumerate(value):
            assert value is None \
                or isinstance(value, Parameter) \
                or isinstance(value, str) \
                or isinstance(value, int) \
                or isinstance(value, float) \
                or isinstance(value, bool) \
                or isinstance(value, Decimal), \
                f'{id} expects a string or parameter as element' \
                f' but an element at the index {index} is {type(value)}.'

            if isinstance(value, Parameter) or isinstance(value, str):
                assert not numbers, \
                    f'{id} cannot mix strings' \
                    f' with an element at index {index} which is {type(value)}.'
                strings = True
            elif value is not None:
                assert not strings, \
                    f'{id} cannot mix numbers' \
                    f' with an element at index {index} which is {type(value)}.'
                numbers = True

    def _format_constant(self, value):
        if isinstance(value, Parameter):
            return f'"{str(value)}"'
        if isinstance(value, str):
            return quote_string(value)
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)

    def Validate(self, record, fieldname):
        try:
            self._assert_valid(self._value)
            return True
        except AssertionError:
            return False

    def FormatDb(self, record, fieldname):
        if self._value is None or len(self._value) == 0:
            return ''
        formatted = [
            self._format_constant(v)
            for v in self._value if v is not None]
        if len(formatted) == 0:
            return ''
        return '[{}]'.format(','.join(formatted))

    def __repr__(self):
        return f'<ConstArray {repr(self._value)}>'
