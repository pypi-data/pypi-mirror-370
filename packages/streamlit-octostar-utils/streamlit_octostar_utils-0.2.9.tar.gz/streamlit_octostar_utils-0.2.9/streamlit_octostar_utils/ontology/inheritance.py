def is_child_concept(type, parent_type, ontology):
    return type == parent_type or parent_type in ontology["concepts"][type]["parents"]
