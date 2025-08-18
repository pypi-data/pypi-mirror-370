from enum import Enum
from .generics import Info, CombineField


class EntityInfo(Info):
    def __init__(self, unique_id, concept_name, fields=dict(), parents=list()):
        self.fields = fields
        self.concept_name = concept_name
        self.unique_id = unique_id
        self.parents = parents


class RelationshipInfo(Info):
    def __init__(self, concept_from, concept_to, name):
        self.concept_from = concept_from
        self.concept_to = concept_to
        self.name = name


class CombineFieldInfo(Info):
    def __init__(self, combiner, data):
        self.combiner = combiner
        self.data = data
