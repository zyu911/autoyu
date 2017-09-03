# -*- coding: utf-8 -*-


class Mapper(object):
    __mapper_relation = {}

    @staticmethod
    def register(cls, value):
        Mapper.__mapper_relation[cls] = value

    @staticmethod
    def exist(cls):
        if cls in Mapper.__mapper_relation:
            return True
        return False

    @staticmethod
    def value(cls):
        return Mapper.__mapper_relation[cls]


class MyType(type):
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        arg_list = list(args)
        if Mapper.exist(cls):
            value = Mapper.value(cls)
            arg_list.append(value)
        obj.__init__(*arg_list, **kwargs)
        return obj


class Test(object):
    def __init__(self):
        pass

    def te(self):
        print('test')


class Foo(metaclass=MyType):
    def __init__(self, test):
        self.test = test

    def f1(self):
        print(self.name)


class Bar(metaclass=MyType):
    def __init__(self, foo):
        self.foo = foo

    def f1(self):
        print(self.name)


Mapper.register(Foo, Test())
Mapper.register(Bar, Foo())
obj = Bar()
obj.foo.test.te()

