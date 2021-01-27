from decimal import Decimal
from .recordbase import quote_string
from .parameter import Parameter

__all__ = ['ConstArray']


class ConstArray:
    """Constant Link Values. EPICS Base 3.16.1 and above.

    Example: PY Source
    ------------------
    `r = records.lsi('r', INP=ConstArray(['Plain String not DBLINK']))`

    Example: Generated DB
    ---------------------
    `field(INP, ["Plain String not DBLINK"])`
    """

    def __init__(self, value):
        """Constructor.

        Parameters
        ----------
        value : iterator
            Homogeneous non-empty list of values.
        """
        self.value = value

    @property
    def value(self):
        """A list of values.
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = self._sanitize(value, 'ConstArray')

    def _sanitize(self, raw_value, context_name):
        try:
            value_list = list(raw_value)
        except TypeError:
            value_list = None
        assert value_list is not None, \
            f'{context_name} excepts iterable' \
            f' but {type(raw_value)} was provided.'

        numbers = False
        strings = False
        valid_types = (Parameter, str, int, float, bool, Decimal)
        for index, value in enumerate(value_list):
            assert isinstance(value, valid_types), \
                f'{context_name} expects a string or parameter as element' \
                f' but an element at the index {index} is {type(value)}.'

            if isinstance(value, (Parameter, str)):
                assert not numbers, \
                    f'{context_name} cannot mix strings' \
                    f' with an element at index {index} which is {type(value)}.'
                strings = True
            else:
                assert not strings, \
                    f'{context_name} cannot mix numbers' \
                    f' with an element at index {index} which is {type(value)}.'
                numbers = True
        return value_list

    def _format_constant(self, value):
        if isinstance(value, Parameter):
            return f'"{str(value)}"'
        if isinstance(value, str):
            return quote_string(value)
        if isinstance(value, bool):
            return '1' if value else '0'
        return str(value)

    def Validate(self, record, fieldname):
        context = f'ConstArray@{record}.{fieldname}'

        value = self._sanitize(self._value, context)

        # EPICS 7.0.3.1 does not consider "[]" as constant.
        assert len(value) > 0, \
            f'{context}: Empty iterable is not allowed.'

    def FormatDb(self, record, fieldname):
        formatted = [self._format_constant(v) for v in self._value]
        return '[{}]'.format(','.join(formatted))

    def __repr__(self):
        return f'<ConstArray {repr(self._value)}>'
