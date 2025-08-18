import re
import hashlib
from .generics import Rule


class RegexRule(Rule):
    def __init__(
        self, regex, only_primitive_values=False, only_selected_values=None, **params
    ):
        super().__init__(
            **{**{"only_primitive_values": only_primitive_values}, **params}
        )
        self.regex = re.compile(f"^({regex})$", re.IGNORECASE)
        self.string = regex
        if only_selected_values:
            self.type_rule = TypeRule(only_selected_values)
        elif only_primitive_values:
            self.type_rule = TypeRule((str, bool, float, int))
        else:
            self.type_rule = TypeRule(object)

    def load(self, parser):
        super().load(parser)
        self.type_rule.load(parser)

    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.string) + ")"

    def unique_hex(self):
        return hashlib.md5((self.salt + self.regex.pattern).encode("utf-8")).hexdigest()

    def apply_rule(self, field, value):
        return self.type_rule.apply_rule(field, value) and (
            self.regex.search(field) is not None
        )


class BoolRule(Rule):
    def __init__(self, condition, **params):
        super().__init__(**params)
        self.condition = condition

    def load(self, parser):
        super().load(parser)

    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.condition) + ")"

    def unique_hex(self):
        return hashlib.md5(
            (self.salt + str(self.condition)).encode("utf-8")
        ).hexdigest()

    def apply_rule(self, field, value):
        if callable(self.condition):
            return self.condition(field, value)
        elif isinstance(self.condition, bool):
            return self.condition
        else:
            raise AttributeError("Invalid type for provided condition")


class TypeRule(Rule):
    def __init__(self, accepted_types, **params):
        super().__init__(**params)
        self.accepted_types = accepted_types
        if not isinstance(self.accepted_types, (list, tuple)):
            self.accepted_types = [self.accepted_types]
        self.accepted_types = tuple(self.accepted_types)

    def load(self, parser):
        super().load(parser)

    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.accepted_types) + ")"

    def unique_hex(self):
        return hashlib.md5(
            (self.salt + str(self.accepted_types)).encode("utf-8")
        ).hexdigest()

    def apply_rule(self, field, value):
        return isinstance(value.value, self.accepted_types)


class AndRule(Rule):
    def __init__(self, rules, **params):
        super().__init__(**params)
        self.rules = rules

    def load(self, parser):
        super().load(parser)

    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.rules) + ")"

    def unique_hex(self):
        return hashlib.md5(
            (self.salt + "".join([str(rule.__hash__()) for rule in self.rules])).encode(
                "utf-8"
            )
        ).hexdigest()

    def apply_rule(self, field, value):
        is_true = True
        for rule in self.rules:
            is_true = rule.apply_rule(field, value)
            if not is_true:
                break
        return is_true


class OrRule(Rule):
    def __init__(self, rules, **params):
        super().__init__(**params)
        self.rules = rules

    def load(self, parser):
        super().load(parser)

    def __str__(self):
        return self.__class__.__name__ + "(" + str(self.rules) + ")"

    def unique_hex(self):
        return hashlib.md5(
            (self.salt + "".join([str(rule.__hash__()) for rule in self.rules])).encode(
                "utf-8"
            )
        ).hexdigest()

    def apply_rule(self, field, value):
        is_true = False
        for rule in self.rules:
            is_true = rule.apply_rule(field, value)
            if is_true:
                break
        return is_true
