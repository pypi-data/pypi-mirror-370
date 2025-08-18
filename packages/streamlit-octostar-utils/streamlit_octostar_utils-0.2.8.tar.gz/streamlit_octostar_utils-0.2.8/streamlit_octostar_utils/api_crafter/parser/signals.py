from .generics import Signal, Entry
from .info import EntityInfo, RelationshipInfo
import uuid


class SpawnChildrenEntitySignal(Signal):
    def __init__(self):
        super().__init__()

    def send(
        self,
        parser,
        parent_entity,
        new_concept_name,
        new_relationship_name,
        new_fields=dict(),
        **params
    ):
        if parent_entity:
            parents = [parent_entity.unique_id]
        else:
            parents = list()
        new_entity = EntityInfo(
            str(uuid.uuid4()), new_concept_name, new_fields, parents
        )
        parser.curr_entities.append(new_entity)
        if new_relationship_name and parent_entity:
            new_relationship = RelationshipInfo(
                parent_entity.unique_id, new_entity.unique_id, new_relationship_name
            )
            parser.curr_relationships.append(new_relationship)
        return new_entity


class ChangeContextSignal(Signal):
    def __init__(self, open_new_stack=True, continue_from_next_rule=False):
        super().__init__()
        self.open_new_stack = open_new_stack
        self.continue_from_next_rule = continue_from_next_rule

    def send(self, parser, new_context, **params):
        new_context_value = {}
        for k, v in new_context.value.items():
            if isinstance(v, Entry):
                new_context_value[k] = Entry(k, v.original_value)
                new_context_value[k].value = v.value
            else:
                new_context_value[k] = Entry(k, v)
        new_context.value = new_context_value
        [entry.load(parser) for entry in new_context.value.values()]
        parser.curr_context = new_context.value
        if not self.continue_from_next_rule:
            parser.curr_rule_index = 0
        if self.open_new_stack:
            parser.curr_indent += 1
            parser._apply_rules_stack(
                parser.curr_rules,
                parser.curr_context,
                parser.curr_referred_entity,
                parser.curr_rule_index,
                parser.curr_combine_rules,
                parser.curr_indent,
            )


class ChangeContextRuleSignal(Signal):
    def __init__(self, open_new_stack=True):
        super().__init__()
        self.open_new_stack = open_new_stack

    def send(self, parser, new_rules, **params):
        parser.curr_rules = new_rules
        parser.curr_rule_index = 0
        if self.open_new_stack:
            parser.curr_indent += 1
            parser._apply_rules_stack(
                parser.curr_rules,
                parser.curr_context,
                parser.curr_referred_entity,
                parser.curr_rule_index,
                parser.curr_combine_rules,
                parser.curr_indent,
            )


class ChangeContextEntitySignal(Signal):
    def __init__(self, open_new_stack=True):
        super().__init__()
        self.open_new_stack = open_new_stack

    def send(
        self,
        parser,
        new_entity_info,
        inherits_rules_from_concepts,
        new_rules,
        new_combine_rules,
        **params
    ):
        parser.curr_referred_entity = new_entity_info
        parent_rules, parent_combine_rules = parser._get_concept_rules(
            inherits_rules_from_concepts
        )
        parser.curr_combine_rules = {
            k: v
            for k, v in parser.curr_combine_rules.items()
            if k not in new_combine_rules.keys()
        }
        parser.curr_combine_rules = {**new_combine_rules, **parent_combine_rules}
        all_rules = {k: v for k, v in parent_rules.items() if k not in new_rules.keys()}
        all_rules = {**new_rules, **all_rules}
        ChangeContextRuleSignal(open_new_stack=False).send(parser, all_rules)
        if self.open_new_stack:
            parser.curr_indent += 1
            parser._apply_rules_stack(
                parser.curr_rules,
                parser.curr_context,
                parser.curr_referred_entity,
                parser.curr_rule_index,
                parser.curr_combine_rules,
                parser.curr_indent,
            )


class AddGlobalConceptSignal(Signal):
    def __init__(self, concept):
        super().__init__()
        self.concept = concept

    def send(self, parser, **params):
        key = self.concept.concept_label or self.concept.concept_name
        parser.concepts.update({key: self.concept})
