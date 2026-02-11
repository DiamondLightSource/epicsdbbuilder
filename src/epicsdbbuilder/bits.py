from .dbd import records


# Extend the automatically generated mbbiDirect and mbboDirect classes
# with bit and register methods so they behave a little like hardware.

def Extend_mbbiDirect(mbbiDirect):
    class mbbiDirect(mbbiDirect):
        def bit(self, offset):
            return _Bits(self, BIT_INPUT, records.bi, offset, 1)

        def register(self, offset, length):
            return _Bits(self, BIT_INPUT, records.bi, offset, length)

    return mbbiDirect


def Extend_mbboDirect(mbboDirect):
    class mbboDirect(mbboDirect):
        def bit(self, offset):
            return _Bits(self, BIT_OUTPUT, records.bo, offset, 1)

        def register(self, offset, length):
            return _Bits(self, BIT_OUTPUT, records.bo, offset, length)

    return mbboDirect


# List of classes which we can extend.
ClassExtensions = dict(
    mbbiDirect = Extend_mbbiDirect,
    mbboDirect = Extend_mbboDirect)


def ExtendClass(recordClass):
    try:
        extension = ClassExtensions[recordClass.__name__]
    except KeyError:
        return recordClass
    else:
        return extension(recordClass)






# ---------------------------------------------------------------------------
#
#   Record support


BIT_INPUT = 0
BIT_OUTPUT = 1

# Factory for building bits from an existing record.  The parent record
# (generally assumed to be an mbbi record) should present the bits to be
# read or written in fields B0 to BF.
#
# Depending on direction, bi or bo can be invoked to create records linking
# to the parent record.  Also bit and register can be used to postpone
# the creation of real records!
class _Bits:
    def __init__(self, parent, direction, factory, offset, length):
        assert 0 <= offset and offset + length <= 16, \
            'Bit field out of range'
        self.parent = parent
        self.direction = direction
        self.offset = offset
        self.length = length
        self._record = factory
        if direction == BIT_INPUT:
            self.bi = self._makeBit
            self._field = 'INP'
            self._linkage = 'CP'
        if direction == BIT_OUTPUT:
            self.bo = self._makeBit
            self._field = 'OUT'
            self._linkage = 'PP'

    # This function implements either bi or bo depending on direction.
    def _makeBit(self, record, bit=0, **fields):
        assert 0 <= bit and bit < self.length, 'Bit out of range'
        r = self._record(record, **fields)
        setattr(
            r, self._field,
            getattr(self.parent, 'B%X' % (self.offset + bit))(self._linkage))
        return r

    def bit(self, bit):
        return self.register(bit, 1)

    def register(self, offset, length):
        assert 0 <= offset and 0 < length and offset + length <= self.length, \
            'Bit field out of range'
        return _Bits(
            self.parent, self.direction, self._record,
            self.offset + offset, length)
