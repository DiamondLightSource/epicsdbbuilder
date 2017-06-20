# EPICS Database Building Framework

# Helper function to export all named modules
def ExportModules(globs, base_module, modulenames):
    names = []
    for modulename in modulenames:
        # This code for importing the module could be simplified by using
        # importlib.import_module(), but that's only available for Python 2.7
        module = __import__(
            '%s.%s' % (base_module, modulename),
            globals(), locals(), [modulename], 0)

        for name in module.__all__:
            globs[name] = getattr(module, name)
        names.extend(module.__all__)
    return names

__all__ = ExportModules(globals(),
    'epicsdbbuilder',
    ['dbd', 'recordbase', 'fanout', 'recordset', 'recordnames', 'parameter'])
