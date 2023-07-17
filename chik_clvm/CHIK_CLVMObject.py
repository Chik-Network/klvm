import typing


class CHIK_CLVMObject:
    """
    This class implements the CHIK_CLVM Object protocol in the simplest possible way,
    by just having an "atom" and a "pair" field
    """

    atom: typing.Optional[bytes]

    # this is always a 2-tuple of an object implementing the CHIK_CLVM object
    # protocol.
    pair: typing.Optional[typing.Tuple[typing.Any, typing.Any]]
    __slots__ = ["atom", "pair"]

    def __new__(class_, v):
        if isinstance(v, CHIK_CLVMObject):
            return v
        self = super(CHIK_CLVMObject, class_).__new__(class_)
        if isinstance(v, tuple):
            if len(v) != 2:
                raise ValueError("tuples must be of size 2, cannot create CHIK_CLVMObject from: %s" % str(v))
            self.pair = v
            self.atom = None
        else:
            self.atom = v
            self.pair = None
        return self
