import os
import yaml
import json
import base64

from .entities_parser import EntitiesParser, EntitiesParserRuleset
from .parameters import ConsolidationParameters

# from octostar.client import impersonating_launching_user, dev_mode


# @impersonating_launching_user()
# @dev_mode(os.getenv('OS_DEV_MODE'))
def parse_root_nodes_to_linkchart(
    endpoint,
    source,
    body,
    transformResult,
    addToGraph,
    guess_entries_fn,
    guess_rulesets_fn,
    guess_entity_fn,
    get_parsed_label_fn,
    process_invalid_fn,
    ruleset_params,
    parser_name,
    client=None,
):
    # The correct ontological path should be source -> entry (api_response, non-parsed) -> account (root node, parsed) -> emails, people... (non-root nodes, parsed)
    # However, because this looks like a longer path in the linkchart and the requirement is not to while still having a two-steps procedure,
    # we need a way to replace the api_response with the parsed root.
    # Also because the linkchart will bug out by showing two nodes with the same UUID if they have different entity type
    # (the actual id is built with both but no way to externally control this),
    # the only solution (for now) is to compute the parsed nodes immediately to get the entity type and UUID they imply, but still show the raw data.
    # In the future hiding the middle node should really be a styling feature
    entries = guess_entries_fn(endpoint, transformResult)
    records = list()
    relationships = list()
    for entry in entries:
        guessed_entity = guess_entity_fn(endpoint, entry)
        ruleset_files, ruleset_parameters = guess_rulesets_fn(endpoint, entry)
        if isinstance(ruleset_params, list):
            for idx, ruleset_parameter in enumerate(ruleset_parameters):
                if ruleset_parameter and not ruleset_params[idx]:
                    pass
                else:
                    ruleset_parameters[idx] = ruleset_params[idx]
        parser = EntitiesParser(
            [
                EntitiesParserRuleset(
                    os.path.join("rulesets", ruleset_files[i]), ruleset_parameters[i]
                )
                for i in range(len(ruleset_files))
            ],
            client=client,
        )
        new_entry_entities, _ = parser.apply_rules(
            entry, endpoint, body, guessed_entity
        )
        new_entry_entities = list(filter(lambda x: not x.parents, new_entry_entities))
        processed_entities, processed_relationships = (
            parser.validate_and_format_entities(new_entry_entities, [])
        )
        processed_entities, processed_relationships = process_invalid_fn(
            processed_entities, processed_relationships
        )
        new_linkchart_elements = parser.to_linkchart(
            processed_entities, processed_relationships, get_parsed_label_fn
        )
        for new_linkchart_element in new_linkchart_elements["records"]:
            records.append(
                {
                    "#endpoint": endpoint,
                    "#original_entry": base64.b64encode(
                        json.dumps(entry).encode("utf-8")
                    ).decode("utf-8"),
                    "#parser": parser_name,
                    "#guessed_entity": guessed_entity,
                    "#is_empty": not bool(entry),
                    "#input": body,
                    "#ruleset_parameters": ruleset_parameters,
                    **new_linkchart_element,
                }
            )
            relationships.append(
                {
                    "from": source["os_entity_uid"],
                    "to": new_linkchart_element["os_entity_uid"],
                    "label": endpoint,
                }
            )
    if len(records) == 1 and ("#is_empty" not in records[0] or records[0]["#is_empty"]):
        records = list()
        relationships = list()
    addToGraph["records"].extend(records)
    addToGraph["relationships"].extend(relationships)
    addToGraph = {
        "records": addToGraph["records"],
        "relationships": addToGraph["relationships"],
    }
    return addToGraph


# @impersonating_launching_user()
# @dev_mode(os.getenv('OS_DEV_MODE'))
def parse_all_nodes_to_linkchart(
    sources,
    addToGraph,
    guess_rulesets_fn,
    get_parsed_label_fn,
    process_invalid_fn,
    client=None,
):
    with open(
        os.path.join(os.getcwd(), "rulesets", "consolidation_parameters.yaml")
    ) as file:
        consolidation_params_dict = yaml.safe_load(file)
    consolidation_parameters = ConsolidationParameters(
        equality_tolerances=consolidation_params_dict.get("tolerances", dict()).get(
            "equality", dict()
        ),
        similarity_tolerances=consolidation_params_dict.get("tolerances", dict()).get(
            "similarity", dict()
        ),
        keep_roots=True,
    )
    records = list()
    relationships = list()
    parsed_entities = list()
    parsed_relationships = list()
    for source in sources:
        endpoint = source["#endpoint"]
        guessed_entity = source["#guessed_entity"]
        body = source["#input"]
        entry = json.loads(
            base64.b64decode(source["#original_entry"].encode("utf-8")).decode("utf-8")
        )
        ruleset_files, _ = guess_rulesets_fn(endpoint, source)
        ruleset_parameters = source["#ruleset_parameters"]
        parser = EntitiesParser(
            [
                EntitiesParserRuleset(
                    os.path.join("rulesets", ruleset_files[i]), ruleset_parameters[i]
                )
                for i in range(len(ruleset_files))
            ],
            client=client,
        )
        new_entities, new_relationships = parser.apply_rules(
            entry, endpoint, body, guessed_entity
        )
        parsed_entities.extend(new_entities)
        parsed_relationships.extend(new_relationships)
    parser = EntitiesParser([])
    consolidated_entities, consolidated_relationships, _ = parser.consolidate_entities(
        parsed_entities, parsed_relationships, consolidation_parameters
    )
    processed_entities, processed_relationships = parser.validate_and_format_entities(
        consolidated_entities, consolidated_relationships
    )
    processed_entities, processed_relationships = process_invalid_fn(
        processed_entities, processed_relationships
    )
    new_linkchart_elements = parser.to_linkchart(
        processed_entities, processed_relationships, get_parsed_label_fn
    )
    for new_linkchart_element in new_linkchart_elements["records"]:
        records.append({"#is_empty": not bool(entry), **new_linkchart_element})
    relationships.extend(new_linkchart_elements["relationships"])
    if len(records) == 1 and ("#is_empty" not in records[0] or records[0]["#is_empty"]):
        records = list()
        relationships = list()
    for record in records:
        del record["#is_empty"]
    addToGraph["records"].extend(records)
    addToGraph["relationships"].extend(relationships)
    addToGraph = {
        "records": addToGraph["records"],
        "relationships": addToGraph["relationships"],
    }
    return addToGraph
