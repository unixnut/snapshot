from operator import attrgetter
from collections import namedtuple


class Snapshot(object):

    def __init__(self, *names, **named):
        """
        :param names: names of attributes of the owner to be copied to the namedtuple directly
        :param named: dict of name, string/callables:
            - if string: the dot separated location of the tuple value in the object
            - if callable: called to get the tuple value from the object
        """
        self.names = names + tuple(named)  #
        self.get_tuple = self._get_getter(names, named)
        self.tuple_type = None

    def __set_name__(self, cls, name):
        """ create the namedtuple class (subclass of tuple) """
        self.tuple_type = namedtuple(name, self.names)

    def _get_getter(self, names, named):
        """ create function that applies all getters to an object """
        getters = [attrgetter(n) for n in names]
        for name, getter in named.items():
            if isinstance(getter, str):
                getters.append(attrgetter(getter))
            elif callable(getter):
                getters.append(getter)
            else:
                raise ValueError(f"{name} in {self.__class__.__name__} must either be string (attr name) or callable")

        def get_namedtuple(obj):
            return self.tuple_type(*(g(obj) for g in getters))

        return get_namedtuple

    def __get__(self, obj, cls=None):
        """ descriptors __get__ method """
        if obj is None:
            return self
        return self.get_tuple(obj)

    def __call__(self, objs):
        """ iterator over a number of snapshots created from 'objs' """
        return map(self.get_tuple, objs)


if __name__ == '__main__':
    """ small example: """

    class Some(object):
        snapshot = Snapshot('a', b='b', c=lambda obj: obj.c, r=lambda obj: obj.d ** 2, ea='e.a')

        def __init__(self, a, b, c=None, d=None, e=None):
            self.a = a
            self.b = b
            self.c = c
            self.d = d
            self.e = e


    some = Some(1, 2, 3, 4, Some('ea', 0, 0, 0, 0))

    snap = some.snapshot
    assert (snap.a, snap.b, snap.c, snap.r, snap.ea) == (1, 2, 3, 16, 'ea')

    a, b, c, r, ea = snap
    assert (a, b, c, r, ea) == (1, 2, 3, 16, 'ea')

