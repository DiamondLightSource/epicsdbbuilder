from . import recordset

__all__ = ['Parameter']


# A Parameter is used to wrap a template parameter before being assigned to a
# record field.
class Parameter:
    __ParameterNames = set()

    def __init__(self, name, description = '', default = None):
        # Ensure names aren't accidentially overwritten
        assert name not in self.__ParameterNames, \
            'Parameter name "%s" already defined' % name
        self.__ParameterNames.add(name)

        self.__name = name
        self.__default = default

        # Add the description as metadata to the current record set
        lines = description.split('\n')
        recordset.recordset.AddHeaderLine(
            '#%% macro, %s, %s' % (name, lines[0]))
        for line in lines[1:]:
            recordset.AddHeaderLine('#  %s' % line)

    def __str__(self):
        if self.__default is None:
            return '$(%s)' % self.__name
        else:
            return '$(%s=%s)' % (self.__name, self.__default)

    def __repr__(self):
        return "Parameter" + str(self)[1:]

    def Validate(self, record, field):
        pass
