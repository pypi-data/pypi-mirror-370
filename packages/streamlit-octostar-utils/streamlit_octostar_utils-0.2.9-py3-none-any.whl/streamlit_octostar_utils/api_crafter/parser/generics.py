from abc import ABC, abstractmethod
import secrets
from copy import deepcopy


class Match(ABC):
    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def load(self, parser):
        self.parser = parser

    @abstractmethod
    def apply_match(self, value):
        raise NotImplementedError()


class Rule(ABC):
    def __init__(self, **params):
        self.params = params
        self.salt = secrets.token_hex(16)

    def __eq__(self, other):
        self.__hash__() == other.__hash__()

    def __hash__(self):
        return int(self.unique_hex(), 16)

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def load(self, parser):
        self.parser = parser

    @abstractmethod
    def unique_hex(self):
        raise NotImplementedError()

    @abstractmethod
    def apply_rule(self, field, value):
        raise NotImplementedError()


class Parameters(ABC):
    def __init__(self):
        pass


class Entry(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.original_value = deepcopy(value)
        self.used = False

    def load(self, parser):
        self.parser = parser
        parser.curr_entries.append(self)


class Signal(ABC):
    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def send(self, parser, **params):
        raise NotImplementedError()


class CombineField(ABC):
    def __init__(self, field, **params):
        self.field = field
        self.params = params

    def load(self, parser):
        self.parser = parser

    @abstractmethod
    def combine_field(self, data, entity):
        raise NotImplementedError()


class Info(ABC):
    def __init__(self):
        pass
