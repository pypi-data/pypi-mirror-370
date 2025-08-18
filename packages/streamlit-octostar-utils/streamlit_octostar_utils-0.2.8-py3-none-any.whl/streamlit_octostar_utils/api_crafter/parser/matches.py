from .generics import Match
from .signals import (
    AddGlobalConceptSignal,
    ChangeContextEntitySignal,
    ChangeContextSignal,
    SpawnChildrenEntitySignal,
)
import itertools

import logging

logger = logging.getLogger(__name__)


class LiteralMatch(Match):
    def __init__(self, fields, keep=False, to_combine_param=None, **params):
        super().__init__(
            **{**{"keep": keep, "to_combine_param": to_combine_param}, **params}
        )
        if not isinstance(fields, list):
            fields = [fields]
        self.fields = fields

    def load(self, parser):
        super().load(parser)

    def apply_match(self, value):
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        param_name = None
        if "to_combine_param" in self.params and self.params["to_combine_param"]:
            param_name = self.params["to_combine_param"]
        return [{field: param_name for field in self.fields}], [
            {field: value.value for field in self.fields}
        ]


class EntityMatch(Match):
    def __init__(
        self,
        concept_name,
        parse_rules=None,
        inherits_rules_from_concepts=None,
        relationship_name=None,
        combine_rules=None,
        keep=True,
        push_context=False,
        **params
    ):
        super().__init__(**{**{"keep": keep, "push_context": push_context}, **params})
        self.concept_name = concept_name
        self.relationship_name = relationship_name
        if isinstance(inherits_rules_from_concepts, str):
            self.inherits_rules_from_concepts = [inherits_rules_from_concepts]
        else:
            self.inherits_rules_from_concepts = inherits_rules_from_concepts
        if not combine_rules:
            combine_rules = dict()
        self.combine_rules = combine_rules
        if not parse_rules:
            parse_rules = dict()
        self.parse_rules = parse_rules
        if not inherits_rules_from_concepts:
            inherits_rules_from_concepts = list()
        self.inherits_rules_from_concepts = inherits_rules_from_concepts

    def load(self, parser):
        super().load(parser)
        if self.parse_rules:
            for parse_rule, parse_match in self.parse_rules.items():
                parse_rule.load(self.parser)
                parse_match.load(self.parser)
        if self.combine_rules:
            for combine_rule in self.combine_rules.values():
                combine_rule.load(self.parser)

    def apply_match(self, value):
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        new_entity = SpawnChildrenEntitySignal().send(
            self.parser,
            self.parser.curr_referred_entity,
            self.concept_name,
            self.relationship_name,
            dict(),
        )
        if "push_context" not in self.params or not self.params["push_context"]:
            push_context = False
        else:
            push_context = True
        ChangeContextEntitySignal(open_new_stack=not push_context).send(
            self.parser,
            new_entity,
            self.inherits_rules_from_concepts,
            self.parse_rules,
            self.combine_rules,
        )
        if push_context:
            ChangeContextSignal().send(self.parser, value)
        return [], []


class ConceptMatch(Match):
    def __init__(
        self,
        concept_name,
        concept_label=None,
        parse_rules=None,
        inherits_rules_from_concepts=None,
        relationship_name=None,
        combine_rules=None,
        keep=False,
        **params
    ):
        super().__init__(**{**{"keep": keep}, **params})
        self.concept_name = concept_name
        self.concept_label = concept_label
        self.relationship_name = relationship_name
        if isinstance(inherits_rules_from_concepts, str):
            self.inherits_rules_from_concepts = [inherits_rules_from_concepts]
        else:
            self.inherits_rules_from_concepts = inherits_rules_from_concepts
        self.parse_rules = parse_rules
        if not combine_rules:
            combine_rules = dict()
        self.combine_rules = combine_rules
        if not parse_rules:
            parse_rules = dict()
        self.parse_rules = parse_rules
        if not inherits_rules_from_concepts:
            inherits_rules_from_concepts = list()
        self.inherits_rules_from_concepts = inherits_rules_from_concepts

    def load(self, parser):
        super().load(parser)
        if self.parse_rules:
            for parse_rule, parse_match in self.parse_rules.items():
                parse_rule.load(self.parser)
                parse_match.load(self.parser)
        if self.combine_rules:
            for combine_rule in self.combine_rules.values():
                combine_rule.load(self.parser)
        AddGlobalConceptSignal(self).send(self.parser)

    def apply_match(self, value):
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        new_entity = SpawnChildrenEntitySignal().send(
            self.parser,
            self.parser.curr_referred_entity,
            self.concept_name,
            self.relationship_name,
            dict(),
        )
        ChangeContextEntitySignal(open_new_stack=False).send(
            self.parser,
            new_entity,
            self.inherits_rules_from_concepts,
            self.parse_rules,
            self.combine_rules,
        )
        ChangeContextSignal().send(self.parser, value)
        return [], []


class ListExpandMatch(Match):
    class _int_iterator(object):
        def __init__(self):
            self.iterator = itertools.count()

        def __iter__(self):
            return self.iterator

        def __next__(self):
            return "_" + str(next(self.iterator))

    def __init__(self, prefix=None, labels_iter=_int_iterator, keep=False, **params):
        super().__init__(**{**{"keep": keep}, **params})
        self.labels_iter = labels_iter
        self.prefix = prefix

    def load(self, parser):
        super().load(parser)

    def apply_match(self, value):
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        prefix = self.prefix
        if prefix is None:
            prefix = value.key
        new_value = dict()
        labels_iter = self.labels_iter()
        for i in range(len(value.value)):
            key = prefix + str(next(labels_iter))
            new_value[key] = value.value[i]
        value.value = new_value
        ChangeContextSignal().send(self.parser, value)
        return [], []


class DictExpandMatch(Match):
    def __init__(self, prefix="", keep=False, **params):
        super().__init__(**{**{"keep": keep}, **params})
        self.prefix = prefix

    def load(self, parser):
        super().load(parser)

    def apply_match(self, value):
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        prefix = self.prefix
        if prefix is None:
            prefix = value.key
        new_value = dict()
        for k, v in value.value.items():
            key = prefix + k
            new_value[key] = v
        value.value = new_value
        ChangeContextSignal().send(self.parser, value)
        return [], []


class DiscardMatch(Match):
    def __init__(self, **params):
        super().__init__(**params)

    def load(self, parser):
        super().load(parser)

    def apply_match(self, value):
        value.used = True
        return [], []


class FunctionMatch(Match):
    def __init__(self, fn, keep=False, to_combine_param=None, **params):
        super().__init__(
            **{**{"keep": keep, "to_combine_param": to_combine_param}, **params}
        )
        self.fn = fn

    def load(self, parser):
        super().load(parser)

    def apply_match(self, value):
        param_name = None
        if "to_combine_param" in self.params and self.params["to_combine_param"]:
            param_name = self.params["to_combine_param"]
        func_return = self.fn(value.value)
        return_value = None
        if isinstance(func_return, (str, list)):
            inner_matcher = LiteralMatch(func_return, to_combine_param=param_name)
            inner_matcher.load(self.parser)
            return_value = inner_matcher.apply_match(value)
        elif isinstance(func_return, Match):
            inner_matcher = func_return
            inner_matcher.load(self.parser)
            return_value = inner_matcher.apply_match(value)
        elif isinstance(func_return, dict):
            return_value = [{key: param_name for key in func_return.keys()}], [
                func_return
            ]
        else:
            raise AttributeError("Invalid return type for FunctionMatch")
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        return return_value


class ManyMatch(Match):
    def __init__(self, matches, keep=False, **params):
        super().__init__(**{**{"keep": keep}, **params})
        self.matches = matches

    def load(self, parser):
        super().load(parser)
        for match in self.matches:
            match.load(parser)

    def apply_match(self, value):
        return_list = list()
        value_original_used = value.used
        value_once_used = value.used
        for match in self.matches:
            return_list.append(match.apply_match(value))
            value_once_used = value_once_used or value.used
            value.used = value_original_used  # Reset usage until end of matches
        value.used = value.used or value_once_used
        if "keep" not in self.params or not self.params["keep"]:
            value.used = True
            logger.info("Setting " + value.key + " to used")
        return list(
            itertools.chain.from_iterable([elem[0] for elem in return_list])
        ), list(itertools.chain.from_iterable([elem[1] for elem in return_list]))
