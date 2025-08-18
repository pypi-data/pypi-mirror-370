from itertools import islice
from copy import deepcopy
import json
import hashlib
import uuid
from .combine_fields import CombineFieldLast
from .generics import Entry
from .parameters import ConsolidationParameters
from .info import CombineFieldInfo, EntityInfo, RelationshipInfo
import itertools
import numpy as np
from rapidfuzz.distance import Levenshtein
from scipy.spatial.distance import squareform
import logging
from enum import Enum
import importlib
import importlib.util

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENTITIES_NAMESPACE = b"octostar.api_parser.entities"


class EntitiesParserRuleset(object):
    def __init__(
        self,
        source_file,
        parameters,
        ruleset_var_name="CONCEPTS",
        parameters_var_name="PARAMETERS",
    ):
        self.source_file = source_file
        self.parameters = parameters
        self.ruleset_var_name = ruleset_var_name
        self.parameters_var_name = parameters_var_name

    def load(self, full_ruleset, parser):
        globals()[self.parameters_var_name] = self.parameters
        spec = importlib.util.spec_from_file_location(
            "dynamic_module", self.source_file
        )
        dynamic_module = importlib.util.module_from_spec(spec)
        setattr(dynamic_module, self.parameters_var_name, self.parameters)
        spec.loader.exec_module(dynamic_module)
        tree = getattr(dynamic_module, self.ruleset_var_name)
        for start_rule, start_match in tree.items():
            start_rule.load(parser)
            start_match.load(parser)
        full_ruleset = {k: v for k, v in full_ruleset.items() if k not in tree.keys()}
        full_ruleset = {**tree, **full_ruleset}
        del globals()[self.parameters_var_name]
        return full_ruleset


class EntitiesInvalidReason(Enum):
    VALID = 0
    INVALID_TYPE = 10
    INVALID_PROPERTIES = 11
    INVALID_REL_TYPE = 20
    UNKNOWN_UUID = 21
    WRONG_SOURCE_OR_TARGET_TYPE = 22
    
    
EntityDict = dict
InvalidErrorDict = dict


class EntitiesParser(object):
    def __init__(self, parse_rulesets, ontology=None):
        self.concepts = dict()
        self.ruleset = dict()
        self.ontology = ontology
        if not isinstance(parse_rulesets, list):
            parse_rulesets = [parse_rulesets]
        for parse_ruleset in parse_rulesets:
            self.ruleset = parse_ruleset.load(self.ruleset, self)
        self._reset_parsing_vars()

    def _reset_parsing_vars(self):
        self.curr_entries = list()
        self.curr_entities = list()
        self.curr_relationships = list()
        self.curr_referred_entity = None
        self.curr_rules = None
        self.curr_combine_rules = dict()
        self.curr_indent = 0
        self.curr_rule_index = 0
        self.curr_context = None

    def _get_concept_rules(self, parent_concepts):
        parse_rules = dict()
        combine_rules = dict()
        if parent_concepts:
            parents = parent_concepts
            while parents:
                new_parents = list()
                for parent in parents:
                    parse_rules = {
                        k: v
                        for k, v in parse_rules.items()
                        if k not in self.concepts[parent].parse_rules.keys()
                    }
                    parse_rules = {**self.concepts[parent].parse_rules, **parse_rules}
                    combine_rules = {
                        k: v
                        for k, v in combine_rules.items()
                        if k not in self.concepts[parent].combine_rules.keys()
                    }
                    combine_rules = {
                        **self.concepts[parent].combine_rules,
                        **combine_rules,
                    }
                    new_parents.extend(
                        self.concepts[parent].inherits_rules_from_concepts
                    )
                    new_parents = list(set(new_parents))
                parents = list(set(new_parents))
        return parse_rules, combine_rules

    def _cull_entities(self, entities, relationships):
        removed_ids = list()
        for entity in entities:
            if "#extra_fields" in entity.fields:
                if not entity.fields["#extra_fields"]:
                    del entity.fields["#extra_fields"]
                else:
                    for extra_field in list(entity.fields["#extra_fields"].keys()):
                        if not entity.fields["#extra_fields"][extra_field]:
                            del entity.fields["#extra_fields"][extra_field]
            for field in list(entity.fields.keys()):
                if not entity.fields[field]:
                    del entity.fields[field]
            if not entity.fields and entity.parents:
                removed_ids.append(entity.unique_id)
        for entity in entities:
            entity.parents = [
                parent for parent in entity.parents if parent not in removed_ids
            ]
        entities = list(filter(lambda x: x.unique_id not in removed_ids, entities))
        entities = list({entity.unique_id: entity for entity in entities}.values())
        relationships = list(
            filter(
                lambda x: x.concept_from not in removed_ids
                and x.concept_to not in removed_ids,
                relationships,
            )
        )
        relationships = list(
            {
                rel.concept_from + rel.concept_to + rel.name: rel
                for rel in relationships
            }.values()
        )
        return entities, relationships

    def _apply_rules_stack(
        self, rules, context, referred_entity, rule_index, combine_rules, indent
    ):
        self.curr_rule_index = rule_index
        while rule_index < len(rules.keys()):
            rule = next(islice(iter(rules), rule_index, rule_index + 1))
            match = rules[rule]
            for entry_key, entry_elem in context.items():
                if not entry_elem.used and rule.apply_rule(entry_key, entry_elem):
                    # logger.info("  "*indent + "Applied rule " + str(rule) + " on " + entry_key)
                    combine_params_names_list, new_fields_list = match.apply_match(
                        entry_elem
                    )
                    if not isinstance(new_fields_list, list):
                        new_fields_list = [new_fields_list]
                    if not isinstance(combine_params_names_list, list):
                        combine_params_names_list = [combine_params_names_list]
                    for i in range(len(new_fields_list)):
                        # for k, v in new_fields_list[i].items():
                        # logger.info("  "*indent + "Pushing '" + str(v) + "' -> " + str(k))
                        new_fields = new_fields_list[i]
                        combine_params_names = combine_params_names_list[i]
                        for field_key, field_value in new_fields.items():
                            if (
                                combine_params_names
                                and field_key in combine_params_names.keys()
                                and combine_params_names[field_key]
                            ):
                                field_param_name = combine_params_names[field_key]
                            else:
                                if field_key in referred_entity.fields:
                                    field_param_name = str(
                                        len(referred_entity.fields[field_key].data)
                                    )
                                else:
                                    field_param_name = "0"
                            if field_key not in referred_entity.fields:
                                if field_key in combine_rules.keys():
                                    combiner = combine_rules[field_key]
                                else:
                                    combiner = CombineFieldLast(field_key)
                                    combiner.load(self)
                                referred_entity.fields[field_key] = CombineFieldInfo(
                                    combiner, {field_param_name: [field_value]}
                                )
                            else:
                                if (
                                    field_param_name
                                    not in referred_entity.fields[field_key].data
                                ):
                                    referred_entity.fields[field_key].data[
                                        field_param_name
                                    ] = list()
                                referred_entity.fields[field_key].data[
                                    field_param_name
                                ].append(field_value)
            # Refresh non-global current values when closing the rule stack
            rule_index += 1
            self.curr_rule_index = rule_index
            self.curr_referred_entity = referred_entity
            self.curr_rules = rules
            self.curr_combine_rules = combine_rules
            self.curr_context = context
            self.curr_indent = indent

    def _append_extra_fields(self, entities, entry):
        def _find_extra_fields_recursive(entry_dict):
            unused_fields = dict()
            if isinstance(entry_dict, dict):
                for key, value in entry_dict.items():
                    if isinstance(value, Entry):
                        if not value.used:
                            unused_fields[key] = value.original_value
                        else:
                            unused_fields.update(
                                _find_extra_fields_recursive(value.value)
                            )
            return unused_fields

        root_entity = list(filter(lambda x: not x.parents, entities))
        assert len(root_entity) <= 1
        if root_entity:
            root_entity = root_entity[0]
            unused_fields = dict()
            if "#extra_fields" not in root_entity.fields:
                root_entity.fields["#extra_fields"] = dict()
            unused_fields = _find_extra_fields_recursive(entry.value)
            root_entity.fields["#extra_fields"] = {
                **root_entity.fields["#extra_fields"],
                **unused_fields,
            }

    def _combine_fields(self, entities):
        for entity in entities:
            for field_key, field_value in entity.fields.items():
                if isinstance(field_value, CombineFieldInfo):
                    combined_value = field_value.combiner.combine_field(
                        field_value.data, entity
                    )
                    if combined_value is not None:
                        entity.fields[field_key] = combined_value
        return entities

    def _compute_deterministic_uuid(self, entity_fields, entity_type):
        new_uuid = str(
            uuid.uuid5(
                uuid.UUID(bytes=hashlib.md5(ENTITIES_NAMESPACE).digest()),
                hashlib.md5(
                    (
                        entity_type + "\n" + json.dumps(entity_fields, sort_keys=True)
                    ).encode("utf-8")
                ).hexdigest(),
            )
        )
        return new_uuid

    def _apply_deterministic_uuids(self, entities, relationships):
        rnd_to_det_map = dict()
        for entity in entities:
            rnd_to_det_map[entity.unique_id] = self._compute_deterministic_uuid(
                entity.fields, entity.concept_name
            )
        for entity in entities:
            entity.unique_id = rnd_to_det_map[entity.unique_id]
            entity.parents = [rnd_to_det_map[parent] for parent in entity.parents]
        for relationship in relationships:
            relationship.concept_from = rnd_to_det_map[relationship.concept_from]
            relationship.concept_to = rnd_to_det_map[relationship.concept_to]
        return entities, relationships

    def apply_rules(self, entry, endpoint=None, input=None, guessed_entity=None):
        entry = deepcopy(entry)
        for key in entry.keys():
            if key.startswith("#"):
                entry["_" + key] = entry.pop(key)
        entry["#endpoint"] = endpoint
        entry["#guessed_entity"] = guessed_entity
        entry["#input"] = input
        entry = Entry("0", entry)
        entry.load(self)
        entry = {"0": entry}

        self._reset_parsing_vars()
        self.curr_entities = list()
        self.curr_relationships = list()
        self.curr_rules = self.ruleset
        self.curr_context = entry

        self._apply_rules_stack(
            self.curr_rules,
            self.curr_context,
            self.curr_referred_entity,
            self.curr_rule_index,
            self.curr_combine_rules,
            self.curr_indent,
        )
        self.curr_entities = self._combine_fields(self.curr_entities)
        self._append_extra_fields(self.curr_entities, entry["0"])

        self.curr_entities, self.curr_relationships = self._cull_entities(
            self.curr_entities, self.curr_relationships
        )
        self.curr_entities, self.curr_relationships = self._apply_deterministic_uuids(
            self.curr_entities, self.curr_relationships
        )
        self.curr_entities, self.curr_relationships = self._cull_entities(
            self.curr_entities, self.curr_relationships
        )

        parsed_entities = self.curr_entities.copy()
        parsed_relationships = self.curr_relationships.copy()
        self._reset_parsing_vars()
        return parsed_entities, parsed_relationships

    def consolidate_entities(
        self, parsed_entities, parsed_relationships, consolidation_parameters=None
    ):
        def _list_flatten(in_list):
            in_list = list(in_list)
            if in_list == []:
                return in_list
            if isinstance(in_list[0], list):
                return _list_flatten(in_list[0]) + _list_flatten(in_list[1:])
            return in_list[:1] + _list_flatten(in_list[1:])

        if not consolidation_parameters:
            consolidation_parameters = ConsolidationParameters()
        consolidated_entities = list()
        consolidated_relationships = list()
        parsed_to_consolidated_relationships = list()
        parsed_entities = parsed_entities.copy()
        if consolidation_parameters.keep_roots:
            root_entities = list(filter(lambda x: not x.parents, parsed_entities))
            new_root_entities = [
                EntityInfo(
                    self._compute_deterministic_uuid(
                        root_entity.fields, root_entity.concept_name
                    ),
                    root_entity.concept_name,
                    root_entity.fields,
                    root_entity.parents,
                )
                for root_entity in root_entities
            ]
            consolidated_entities.extend(new_root_entities)
            parsed_to_consolidated_relationships.extend(
                [
                    RelationshipInfo(
                        root_entities[i].unique_id,
                        new_root_entities[i].unique_id,
                        "consolidated_to",
                    )
                    for i in range(len(root_entities))
                ]
            )
            parsed_entities = list(filter(lambda x: x.parents, parsed_entities))
        for concept_name, group in itertools.groupby(
            sorted(parsed_entities, key=lambda x: x.concept_name),
            lambda x: x.concept_name,
        ):
            group = list(group)
            index = np.array([elem.unique_id for elem in group], dtype=object)
            field_names = sorted(
                list(set(_list_flatten([list(elem.fields.keys()) for elem in group])))
            )
            sorted_group = [dict(sorted(elem.fields.items())) for elem in group]
            sorted_group = [
                {**{k: "" for k in field_names}, **elem.fields} for elem in group
            ]
            equal_tolerance = (
                0
                if concept_name not in consolidation_parameters.equality_tolerances
                else consolidation_parameters.equality_tolerances[concept_name]
            )
            equal_tolerance *= len(field_names)
            similar_tolerance = (
                2 * equal_tolerance
                if concept_name not in consolidation_parameters.similarity_tolerances
                else consolidation_parameters.similarity_tolerances[concept_name]
            )
            similar_tolerance *= len(field_names)
            sorted_strings = [str(list(elem.items())) for elem in sorted_group]
            distances = [
                Levenshtein.distance(i, j, score_cutoff=similar_tolerance)
                for (i, j) in itertools.combinations(sorted_strings, 2)
            ]
            distances = squareform(distances)
            equal_pairs = np.argwhere(distances <= equal_tolerance).tolist()
            equal_pairs = list(filter(lambda x: x[0] <= x[1], equal_pairs))
            similar_pairs = np.argwhere(distances <= similar_tolerance).tolist()
            similar_pairs = list(filter(lambda x: x[0] <= x[1], similar_pairs))
            similar_pairs = list(filter(lambda x: x not in equal_pairs, similar_pairs))
            equal_pairs = [index[pair] for pair in equal_pairs]
            similar_pairs = [index[pair] for pair in similar_pairs]
            parsed_to_consolidated_relationships.extend(
                [
                    RelationshipInfo(pair[0], pair[1], "same_as")
                    for pair in equal_pairs
                    if pair[0] != pair[1]
                ]
            )
            parsed_to_consolidated_relationships.extend(
                [
                    RelationshipInfo(pair[0], pair[1], "similar_to")
                    for pair in similar_pairs
                    if pair[0] != pair[1]
                ]
            )
            equal_groups = list()
            for elem in equal_pairs:
                elem = set(elem)
                inserted = False
                for i in range(len(equal_groups)):
                    if equal_groups[i].intersection(elem):
                        equal_groups[i] = equal_groups[i].union(elem)
                        inserted = True
                        break
                if not inserted:
                    equal_groups.append(elem)
            equal_groups = [list(sorted(group)) for group in equal_groups]
            for group in equal_groups:
                consolidated_fields = {}
                parents = set()
                for elem in group:
                    entity = next(x for x in parsed_entities if x.unique_id == elem)
                    consolidated_fields = {**entity.fields, **consolidated_fields}
                    parents = parents.union(set(entity.parents))
                consolidated_entity = EntityInfo(
                    self._compute_deterministic_uuid(consolidated_fields, concept_name),
                    concept_name,
                    consolidated_fields,
                    list(parents),
                )
                consolidated_entities.append(consolidated_entity)
                parsed_to_consolidated_relationships.extend(
                    [
                        RelationshipInfo(
                            elem, consolidated_entity.unique_id, "consolidated_to"
                        )
                        for elem in group
                    ]
                )
        entities_consolidation_map = {
            entity.unique_id: [
                rel.concept_from
                for rel in list(
                    filter(
                        lambda x: x.name == "consolidated_to"
                        and x.concept_to == entity.unique_id,
                        parsed_to_consolidated_relationships,
                    )
                )
            ]
            for entity in consolidated_entities
        }
        entities_consolidation_map = [
            {original_uid: consolidated_uid for original_uid in original_uids}
            for consolidated_uid, original_uids in entities_consolidation_map.items()
        ]
        entities_consolidation_map = dict(
            (key, d[key]) for d in entities_consolidation_map for key in d
        )
        for entity in consolidated_entities:
            entity.parents = list(
                set([entities_consolidation_map[parent] for parent in entity.parents])
            )
        consolidated_relationships = [
            (
                entities_consolidation_map[rel.concept_from],
                entities_consolidation_map[rel.concept_to],
                rel.name,
            )
            for rel in parsed_relationships
        ]
        consolidated_relationships = [
            RelationshipInfo(rel[0], rel[1], rel[2])
            for rel in set(consolidated_relationships)
        ]
        consolidated_entities, _ = self._cull_entities(consolidated_entities, [])
        return (
            consolidated_entities,
            consolidated_relationships,
            parsed_to_consolidated_relationships,
        )

    """
    def group_consolidated_entities(self, consolidated_entities, groupby_parameters=None):
        if not groupby_parameters:
            groupby_parameters = GroupbyParameters()
        def group_consolidated_entities_by_parent(self, parent_concept_name, to_concept_name, groupby_fields_dict):
            groupby_fields = list(groupby_fields_dict.values())
            children_concepts = list(filter(lambda x: parent_concept_name in x[1]['parents'], self.ontology['concepts'].items()))
            children_concepts = [c[0] for c in children_concepts]
            to_group_entities = list(filter(lambda x: x.concept_name in children_concepts, consolidated_entities))
            groupby_fields = sorted(groupby_fields)
            for entity in to_group_entities:
                for groupby_field in groupby_fields:
                    if groupby_field not in entity.fields or not entity.fields[groupby_field].strip():
                        entity.fields[groupby_field] = ''
            to_group_entities = list(filter(lambda x: any([x.fields[groupby_field] != '' for groupby_field in groupby_fields]), to_group_entities))
            order_func = lambda x: ",".join([x.fields[groupby_field] for groupby_field in groupby_fields])
            groupby_fields_dict_reversed = {v:k for k, v in groupby_fields_dict.items()}
            for _, group in itertools.groupby(sorted(to_group_entities, key=order_func), order_func):
                group = list(group)
                if len(group) > 1:
                    grouped_fields = {groupby_field: group[0].fields[groupby_field] for groupby_field in groupby_fields}
                    grouped_fields = {groupby_fields_dict_reversed[k]:v for k, v in grouped_fields.items()}
                    groupby_entity = EntityInfo(self._compute_deterministic_uuid(grouped_fields, to_concept_name),
                                                to_concept_name, grouped_fields)
                    groupby_entities.append(groupby_entity)
                    consolidated_to_groupby_relationships.extend([RelationshipInfo(entity.unique_id, groupby_entity.unique_id, "grouped_to") for entity in group])
            return groupby_entities, consolidated_to_groupby_relationships
        groupby_entities = list()
        consolidated_to_groupby_relationships = list()
        for _, groupby_dict in groupby_parameters.groups.items():
            parent_concept_name = groupby_dict['from']
            to_concept_name = groupby_dict['to']
            groupby_fields_dict = groupby_dict['fields']
            groupby_entities, consolidated_to_groupby_relationships = group_consolidated_entities_by_parent(self, parent_concept_name, to_concept_name, groupby_fields_dict)
        groupby_entities, consolidated_to_groupby_relationships = self._cull_entities(groupby_entities, consolidated_to_groupby_relationships)
        return groupby_entities, consolidated_to_groupby_relationships
    """

    def validate_and_format_entities(self, entities, relationships):
        if not self.ontology:
            raise RuntimeError("No ontology provided for validation!")
        ontology = self.ontology
        from streamlit_octostar_utils.ontology.validation import (
            validate_and_format_timbr_type,
        )
        from streamlit_octostar_utils.ontology.inheritance import is_child_concept

        processed_entities = []
        processed_relationships = []
        for entity in entities:
            if entity.concept_name not in ontology["concepts"]:
                processed_entities.append(
                    (
                        EntitiesInvalidReason.INVALID_TYPE,
                        entity,
                        {"error_message": f"{entity} has invalid concept name"},
                    )
                )
            entity_properties = [
                k
                for k in entity.fields.keys()
                if not k.startswith("#")
            ]
            ontology_properties = {
                e["property_name"]: e
                for e in ontology["concepts"][entity.concept_name]["allProperties"]
            }
            if any(prop not in ontology_properties for prop in entity_properties):
                processed_entities.append(
                    (
                        EntitiesInvalidReason.INVALID_PROPERTIES,
                        entity,
                        {
                            "error_message": f"{entity} has invalid entity properties: {str(set(entity_properties) - set(ontology_properties))}"
                        },
                    )
                )
            for prop in entity_properties:
                try:
                    entity.fields[prop] = validate_and_format_timbr_type(
                        ontology_properties[prop]["property_type"], entity.fields[prop]
                    )
                except:
                    processed_entities.append(
                        (
                            EntitiesInvalidReason.INVALID_PROPERTIES,
                            entity,
                            {
                                "error_message": f"{entity} has an invalid property type for property {prop}"
                            },
                        )
                    )
            processed_entities.append((EntitiesInvalidReason.VALID, entity, {}))
        ontology_relationships = {
            r["relationship_name"]: r for r in ontology["relationships"]
        }
        for rel in relationships:
            if rel.name not in ontology_relationships.keys():
                processed_relationships.append(
                    (
                        EntitiesInvalidReason.INVALID_REL_TYPE,
                        rel,
                        {"error_message": f"{rel} relationship name is invalid"},
                    )
                )
            entities_by_id = {e[1].unique_id: e[1] for e in processed_entities}
            if (
                rel.concept_from not in entities_by_id.keys()
                or rel.concept_to not in entities_by_id.keys()
            ):
                processed_relationships.append(
                    (
                        EntitiesInvalidReason.UNKNOWN_UUID,
                        rel,
                        {
                            "error_message": f"for {rel}, source concept or target concept are invalid"
                        },
                    )
                )
            ontology_relationship = ontology_relationships[rel.name]
            rel_concept_types = (
                entities_by_id[rel.concept_from].concept_name,
                entities_by_id[rel.concept_to].concept_name,
            )
            if not is_child_concept(
                rel_concept_types[0],
                ontology_relationship["concept"],
                ontology,
            ) or not is_child_concept(
                rel_concept_types[1],
                ontology_relationship["target_concept"],
                ontology,
            ):
                processed_relationships.append(
                    (
                        EntitiesInvalidReason.WRONG_SOURCE_OR_TARGET_TYPE,
                        rel,
                        {
                            "error_message": f"for {rel}, type for source concept or for target concept is invalid"
                        },
                    )
                )
            processed_relationships.append((EntitiesInvalidReason.VALID, rel, {}))
        return processed_entities, processed_relationships

    def replace_unique_id(self, id_from, id_to, entities, relationships):
        for entity in entities:
            if entity.unique_id == id_from:
                entity.unique_id = id_to
        for relationship in relationships:
            if relationship.concept_from == id_from:
                relationship.concept_from = id_to
            if relationship.concept_to == id_from:
                relationship.concept_to = id_to

    def to_linkchart(self, entities, relationships, label_fn):
        return_dict = {"records": list(), "relationships": list()}
        for entity in entities:
            return_dict["records"].append(
                {
                    "entity_id": entity.unique_id,
                    "os_entity_uid": entity.unique_id,
                    "entity_type": entity.concept_name,
                    "entity_label": label_fn(entity),
                    **entity.fields,
                }
            )
        for rel in relationships:
            return_dict["relationships"].append(
                {"from": rel.concept_from, "to": rel.concept_to, "label": rel.name}
            )
        return return_dict
