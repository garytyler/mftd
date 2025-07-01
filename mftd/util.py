class cached_classproperty:  # noqa: N801 # pylint: disable=invalid-name
    def __init__(self, f):
        self.f, self.name = f, f.__name__

    def __get__(self, obj, cls):
        if self.name not in cls.__dict__:
            setattr(cls, self.name, self.f(cls))  # cache on the *class*
        return cls.__dict__[self.name]
