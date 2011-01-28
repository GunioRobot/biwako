import threading

class FieldMeta(type):
    _registry = threading.local()
    _registry.options = {}

    def __call__(cls, *args, **kwargs):
        if FieldMeta._registry.options:
            options = FieldMeta._registry.options.copy()
            options.update(kwargs)
        else:
            options = kwargs
        return super(FieldMeta, cls).__call__(*args, **options)


class Field(metaclass=FieldMeta):
    def __init__(self, label=None, *, size=None, offset=None, choices=(), **kwargs):
        self.label = label
        self.size = DynamicValue(size)
        self.offset = offset
        # TODO: Actually support choices properly later
        self.choices = choices

    def extract(self, obj):
        return self.decode(self.read(obj))

    def read(self, obj):
        size = self.size(obj)

        # If the size can be determined easily, read
        # that number of bytes and return it directly.
        if size is not None:
            return obj.read(size)

        # Otherwise, the field needs to supply its own
        # technique for determining how much data to read.
        raise NotImplementedError()

    def write(self, obj, value):
        # By default, this doesn't do much, but individual
        # fields can/should override it if necessary
        obj.write(value)

    def set_name(self, name):
        self.name = name
        label = self.label or name.replace('_', ' ')
        self.label = label.title()

    def attach_to_class(self, cls):
        cls._fields.append(self)

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            try:
                instance.__dict__[self.name] = instance._get_value(self)
            except IOError:
                raise AttributeError("Attribute %r has no data" % self.name)
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class DynamicValue:
    def __init__(self, value):
        self.value = value

    def __call__(self, obj):
        if isinstance(self.value, DynamicValue):
            return self.value(obj)
        elif isinstance(self.value, Field):
            return obj._get_value(self.value)
        elif hasattr(self.value, '__call__'):
            return self.value(obj)
        else:
            return self.value


# Special object used to instruct the reader to continue to the end of the file
def Remainder(obj):
    return -1


