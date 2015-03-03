# EPICS Database Building Framework

# Helper function to export all named modules
def ExportModules(globs, *modulenames):
    names = []
    for modulename in modulenames:
        module = __import__(modulename, globs)
        for name in module.__all__:
            globs[name] = getattr(module, name)
        names.extend(module.__all__)
    return names

__all__ = ExportModules(globals(),
    'dbd', 'recordbase', 'fanout', 'recordset', 'recordnames', 'parameter')
