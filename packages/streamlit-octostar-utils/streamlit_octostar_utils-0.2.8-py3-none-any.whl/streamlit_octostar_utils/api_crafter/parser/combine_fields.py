from .generics import CombineField
from .info import CombineFieldInfo, EntityInfo, RelationshipInfo
from itertools import islice
import uuid
import json


class CombineFieldLast(CombineField):
    def __init__(self, field, primitive_types_only=True, **params):
        super().__init__(
            field, **{**params, **{"primitive_types_only": primitive_types_only}}
        )

    def combine_field(self, data, entity):
        primitive_types_only = False
        if (
            "primitive_types_only" in self.params
            and self.params["primitive_types_only"]
        ):
            primitive_types_only = True
        if data:
            last_dict_elem = next(islice(iter(data), len(data) - 1, len(data)))
            last_elem = data[last_dict_elem][-1]
            if primitive_types_only and isinstance(last_elem, (dict, list)):
                if len(last_elem) == 1:
                    last_elem = next(last_elem)
                else:
                    raise ValueError(
                        "Primitive type only are allowed in output for field "
                        + self.field
                    )
            if last_elem:
                return last_elem
            else:
                return ""
        else:
            return ""


class CombineFieldFirst(CombineField):
    def __init__(self, field, primitive_types_only=True, **params):
        super().__init__(
            field, **{**params, **{"primitive_types_only": primitive_types_only}}
        )

    def combine_field(self, data, entity):
        primitive_types_only = False
        if (
            "primitive_types_only" in self.params
            and self.params["primitive_types_only"]
        ):
            primitive_types_only = True
        if data:
            first_dict_elem = next(islice(iter(data), 0, 1))
            first_elem = data[first_dict_elem][0]
            if primitive_types_only and isinstance(first_elem, (dict, list)):
                if len(first_elem) == 1:
                    first_elem = next(first_elem)
                else:
                    raise ValueError(
                        "Primitive type only are allowed in output for field "
                        + self.field
                    )
            return first_elem
        else:
            return ""


class CombineFieldCustom(CombineField):
    def __init__(self, field, custom_fn, **params):
        super().__init__(field, **params)
        self.custom_fn = custom_fn

    def combine_field(self, data, entity):
        if data:
            return self.custom_fn(data, entity)
        else:
            return ""


class CombineFieldJSON(CombineField):
    def __init__(self, field, indent=None, **params):
        super().__init__(field, **params)
        self.params = {**self.params, **{"indent": indent}}

    def combine_field(self, data, entity):
        if data:
            if "indent" in self.params and self.params["indent"]:
                indent = self.params["indent"]
            else:
                indent = 4
            return json.dumps(data, indent=indent)
        else:
            return ""


class CombineFieldConcat(CombineField):
    def concat(self, data, dict_sep="", list_sep="", as_flat_list=False):
        def _list_flatten(in_list):
            in_list = list(in_list)
            if in_list == []:
                return in_list
            if isinstance(in_list[0], list):
                return _list_flatten(in_list[0]) + _list_flatten(in_list[1:])
            return in_list[:1] + _list_flatten(in_list[1:])

        if as_flat_list:
            return _list_flatten([[elem for elem in ls] for ls in data.values()])
        else:
            return dict_sep.join(
                [list_sep.join([elem for elem in ls]) for ls in data.values()]
            )

    def __init__(self, field, dict_sep="", list_sep="", as_flat_list=False, **params):
        super().__init__(field, **params)
        self.params = {**self.params, **{"as_flat_list": as_flat_list}}
        self.list_sep = list_sep
        self.dict_sep = dict_sep

    def combine_field(self, data, entity):
        if data:
            if "as_flat_list" in self.params and self.params["as_flat_list"]:
                as_flat_list = True
            else:
                as_flat_list = False
            return self.concat(data, self.dict_sep, self.list_sep, as_flat_list)
        else:
            return ""


class CombineFieldSpawn(CombineField):
    def __init__(self, field, inner_combiner=None, **params):
        super().__init__(field, **params)
        self.inner_combiner = inner_combiner
        if not self.inner_combiner:
            self.inner_combiner = CombineFieldCustom(
                field, lambda d, e: d
            )  # Special combiner that should return a list or dict of lists

    def combine_field(self, data, entity):
        def _list_flatten(in_list):
            in_list = list(in_list)
            if in_list == []:
                return in_list
            if isinstance(in_list[0], list):
                return _list_flatten(in_list[0]) + _list_flatten(in_list[1:])
            return in_list[:1] + _list_flatten(in_list[1:])

        value_dicts = dict()
        all_params = list()
        entity_relationships = (
            [
                rel
                for rel in self.parser.curr_relationships
                if rel.concept_from == entity.unique_id
            ],
            [
                rel
                for rel in self.parser.curr_relationships
                if rel.concept_to == entity.unique_id
            ],
        )
        for field_key, field_value in entity.fields.items():
            if isinstance(field_value, CombineFieldInfo) and isinstance(
                field_value.combiner, CombineFieldSpawn
            ):
                values = field_value.combiner.inner_combiner.combine_field(
                    field_value.data, entity
                )
                value_dicts[field_key] = dict()
                if isinstance(values, list):
                    value_dicts[field_key]["-1"].extend(values)
                    all_params.append("-1")
                elif isinstance(values, dict):
                    for key, elems in values.items():
                        if key not in value_dicts:
                            value_dicts[field_key][key] = list()
                        value_dicts[field_key][key].extend(elems)
                        all_params.append(key)
        all_params = {
            param: max(
                [len(inner_dict.get(param, [])) for inner_dict in value_dicts.values()]
            )
            for param in all_params
        }
        value_lists = dict()
        for field_key, inner_dicts in value_dicts.items():
            if field_key not in value_lists:
                value_lists[field_key] = list()
            for param_name in inner_dicts.keys():
                inner_dicts[param_name].extend(
                    [None] * (all_params[param_name] - len(inner_dicts[param_name]))
                )
        keys = list(value_dicts.keys())
        value_lists = [
            _list_flatten([inner_dict[key] for key in sorted(list(inner_dict.keys()))])
            for inner_dict in value_dicts.values()
        ]
        if value_lists:
            maxlen = max([len(ls) for ls in value_lists])
            [ls.extend([None] * (maxlen - len(ls))) for ls in value_lists]
            combined_fields = [
                {keys[i]: value_lists[i][j] for i in range(len(keys))}
                for j in range(maxlen)
            ]
            first_elem_fields = combined_fields.pop(0)
            entity.fields = {**entity.fields, **first_elem_fields}
            for combined_fields_elem in combined_fields:
                new_fields = entity.fields
                new_fields = {**entity.fields, **combined_fields_elem}
                new_entity = EntityInfo(
                    str(uuid.uuid4()),
                    entity.concept_name,
                    new_fields,
                    parents=entity.parents,
                )
                new_rels = [
                    RelationshipInfo(new_entity.unique_id, rel.concept_to, rel.name)
                    for rel in entity_relationships[0]
                ] + [
                    RelationshipInfo(rel.concept_from, new_entity.unique_id, rel.name)
                    for rel in entity_relationships[1]
                ]
                self.parser.curr_entities.append(new_entity)
                self.parser.curr_relationships.extend(new_rels)
