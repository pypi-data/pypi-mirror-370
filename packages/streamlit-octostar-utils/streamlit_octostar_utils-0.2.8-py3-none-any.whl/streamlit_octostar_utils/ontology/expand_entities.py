from itertools import groupby, chain
import time
import uuid
from octostar.utils.ontology import multiquery_ontology
from octostar.utils.exceptions import StopAsyncIterationWithResult

from .inheritance import is_child_concept

REL_FETCHED_FIELDS = [
    "os_relationship_name",
    "os_entity_uid_from",
    "os_entity_uid_to",
    "os_entity_uid",
    "os_entity_type_from",
    "os_entity_type_to",
    "os_workspace",
]
TARGETS_FETCHED_FIELDS = ["os_entity_uid", "os_concept", "entity_label", "os_workspace"]


class ExecutionMetrics:
    def __init__(self):
        self.n_queries = 0
        self.n_relationships = 0
        self.n_target_entities = 0
        self.exec_time = 0.0
        self.exec_times = {}
        self.n_cancelled_queries = 0
        self.relationship_names = set()
        self.timeout = 0

    def print_metrics(self):
        print("Execution Metrics:")
        print(f"  Execution Time: {self.exec_time}")
        print(f"  Per-Type Execution Times: {self.exec_times}")
        print(f"  Number of Queries: {self.n_queries}")
        print(f"  Number of Cancelled Queries: {self.n_cancelled_queries}")
        print(f"  Timeout per Query: {self.timeout}")
        print(f"  Number of Relationships: {self.n_relationships}")
        print(f"  Number of Target Entities: {self.n_target_entities}")
        print(f"  Relationship Names: {self.relationship_names}")


async def _get_stream_result(stream):
    result = None
    try:
        async for _ in stream:
            pass
    except StopAsyncIterationWithResult as e:
        result = e.value
    return result


def _left_join(left_list, right_list, left_keys, right_keys):
    left_keys = left_keys if isinstance(left_keys, (list, tuple)) else [left_keys]
    right_keys = right_keys if isinstance(right_keys, (list, tuple)) else [right_keys]

    def _make_composite_key(item, keys):
        return tuple(item[key] for key in keys)

    left_list.sort(key=lambda item: _make_composite_key(item, left_keys))
    right_list.sort(key=lambda item: _make_composite_key(item, right_keys))
    left_groups = groupby(
        left_list, key=lambda item: _make_composite_key(item, left_keys)
    )
    right_groups = groupby(
        right_list, key=lambda item: _make_composite_key(item, right_keys)
    )
    right_dict = {key: list(group) for key, group in right_groups}
    result = []
    for left_key_val, left_items in left_groups:
        left_items = list(left_items)
        associated_rights = right_dict.get(left_key_val, [])
        for left_item in left_items:
            result.append((left_item, associated_rights))
    return result


async def expand_otm(
    expanded_entities,
    entities_by_concept,
    ontology_rels,
    concepts_to_otm_rels,
    metrics,
    client,
    timeout,
    limit,
):
    start_time = time.time()
    otm_queries = []
    target_fields = ",".join(
        ["`" + rel_field + "`" for rel_field in TARGETS_FETCHED_FIELDS]
    )
    for concept_name, rels in concepts_to_otm_rels.items():
        for rel_name in rels:
            rel = ontology_rels[rel_name]
            source_properties = rel["source_properties"].split(",")
            source_properties_values = [
                [entity[p] for p in source_properties]
                for entity in entities_by_concept[concept_name]
            ]
            source_properties_values = [
                values
                for values in source_properties_values
                if all(value is not None for value in values)
            ]
            if source_properties_values:
                target_prop_names = rel["target_properties"].split(",")
                target_prop_names = ",".join(
                    ["`" + prop + "`" for prop in target_prop_names]
                )
                source_properties_values = ",".join(
                    [
                        "(" + ",".join(["'" + value + "'" for value in values]) + ")"
                        for values in source_properties_values
                    ]
                )
                if target_prop_names and source_properties_values:
                    query = f"""SELECT {target_fields} FROM `etimbr`.`{rel['target_concept']}` WHERE ({target_prop_names}) IN ({source_properties_values}) LIMIT {limit}"""
                    otm_queries.append(
                        {
                            "concept_name": concept_name,
                            "query": query,
                            "relationship_name": rel_name,
                            "source_properties": rel["source_properties"].split(","),
                            "target_properties": rel["target_properties"].split(","),
                        }
                    )
    otm_queries = {str(i): otm_queries[i] for i in range(len(otm_queries))}
    otm_stream = multiquery_ontology.streaming(
        sql_queries={
            query_id: query_data["query"]
            for query_id, query_data in otm_queries.items()
        },
        client=client,
        timeout=timeout,
    )
    metrics.n_queries += len(otm_queries)
    all_results = await _get_stream_result(otm_stream)
    for query_id, data in all_results.items():
        if data == None:
            metrics.n_cancelled_queries += 1
        if not data:
            continue
        query_data = otm_queries[query_id]
        data = _left_join(
            [
                e[0]
                for e in expanded_entities.values()
                if e[0]["os_concept"] == query_data["concept_name"]
            ],
            data,
            query_data["source_properties"],
            query_data["target_properties"],
        )
        data = {
            e[0]["os_entity_uid"]: (
                e[0],
                {
                    r["os_entity_uid"]: (
                        {"os_relationship_name": query_data["relationship_name"]},
                        {r["os_entity_uid"]: r},
                    )
                    for r in e[1]
                },
            )
            for e in data
        }
        for entity_id, entities in data.items():
            if entity_id not in expanded_entities:
                expanded_entities[entity_id] = [entities[0], {}]
            for sub_entity_id, sub_entities in entities[1].items():
                if sub_entity_id not in expanded_entities[entity_id][1]:
                    expanded_entities[entity_id][1][sub_entity_id] = [
                        sub_entities[0],
                        {},
                    ]
                expanded_entities[entity_id][1][sub_entity_id][1].update(
                    sub_entities[1]
                )
    metrics.exec_times["otm"] = time.time() - start_time
    return expanded_entities


async def expand_mtm_mixed(
    expanded_entities,
    entities_by_concept,
    ontology,
    concepts_to_mixed_rels,
    ontology_rels,
    metrics,
    client,
    timeout,
    limit,
):
    start_time = time.time()
    mixed_queries = []
    match_patterns = {}
    rel_fields = ",".join(["`" + rel_field + "`" for rel_field in REL_FETCHED_FIELDS])
    for concept_name, rels in concepts_to_mixed_rels.items():
        if concept_name not in match_patterns:
            match_patterns[concept_name] = []
        match_patterns[concept_name].extend(
            [entity["os_entity_uid"] for entity in entities_by_concept[concept_name]]
        )
    for concept_name, entity_ids in match_patterns.items():
        rels = concepts_to_mixed_rels[concept_name]
        entity_ids = ",".join(["'" + uid + "'" for uid in entity_ids])
        for rel_name in rels:
            rel = ontology_rels[rel_name]
            target_concept = rel["target_concept"]
            relationship_fields = ",".join(
                [
                    f"`{rel_name}[{target_concept}]_"
                    + prop
                    + "` AS "
                    + "`rel__"
                    + prop
                    + "`"
                    for prop in REL_FETCHED_FIELDS
                ]
            )
            target_fields = ",".join(
                [
                    f"`{rel_name}[{target_concept}]."
                    + prop
                    + "` AS "
                    + "`tgt__"
                    + prop
                    + "`"
                    for prop in TARGETS_FETCHED_FIELDS
                ]
            )
            all_fields = (
                f"{relationship_fields}, {target_fields}, `os_entity_uid`".strip(", ")
            )
            if entity_ids:
                mixed_queries.append(
                    {
                        "query": f"SELECT {all_fields} FROM `dtimbr`.`{concept_name}` WHERE `os_entity_uid` IN ({entity_ids}) LIMIT {limit}"
                    }
                )
    mixed_queries = {str(i): mixed_queries[i] for i in range(len(mixed_queries))}
    metrics.n_queries += len(mixed_queries)
    local_stream = multiquery_ontology.streaming(
        sql_queries={
            query_id: query_data["query"]
            for query_id, query_data in mixed_queries.items()
        },
        client=client,
        timeout=timeout / 2.0,
    )
    all_results = await _get_stream_result(local_stream)
    for (
        _,
        data,
    ) in (
        all_results.items()
    ):  ## TO BE TESTED (data is always empty at the moment due to timbr bug)
        if data == None:
            metrics.n_cancelled_queries += 1
        if not data:
            continue
        data = _left_join(
            [e[0] for e in expanded_entities.values()],
            data,
            "os_entity_uid",
            "os_entity_uid",
        )
        for elem in data:
            elem["#rel__os_entity_uid"] = elem["rel__os_entity_uid"] or (
                "temp-" + str(uuid.uuid4())
            )
        data = {
            e[0]["os_entity_uid"]: (
                e[0],
                {
                    rt["#rel__os_entity_uid"]: (
                        {k[5:]: v for k, v in rt.items() if k.startswith("rel__")},
                        {
                            rt["tgt__os_entity_uid"]: {
                                k[5:]: v for k, v in rt.items() if k.startswith("tgt__")
                            }
                        },
                    )
                    for rt in e[1]
                },
            )
            for e in data
        }
        data = {
            e[0]["os_entity_uid"]: (
                e[0],
                {r["os_entity_uid"]: ({}, {r["os_entity_uid"]: r}) for r in e[1]},
            )
            for e in data
        }
        for entity_id, entities in data.items():
            if entity_id not in expanded_entities:
                expanded_entities[entity_id] = [entities[0], {}]
            for sub_entity_id, sub_entities in entities[1].items():
                if sub_entity_id not in expanded_entities[entity_id][1]:
                    expanded_entities[entity_id][1][sub_entity_id] = [
                        sub_entities[0],
                        {},
                    ]
                expanded_entities[entity_id][1][sub_entity_id][1].update(
                    sub_entities[1]
                )
    metrics.exec_times["mtm_mixed"] = time.time() - start_time
    return expanded_entities


async def expand_mtm_local(
    expanded_entities,
    entities_by_concept,
    ontology_rels,
    concepts_to_local_rels,
    metrics,
    client,
    timeout,
    limit,
):
    start_time = time.time()
    local_queries = {"from": [], "to": []}
    match_patterns = {}
    target_fields = ",".join(
        ["`" + rel_field + "`" for rel_field in TARGETS_FETCHED_FIELDS]
    )
    rel_fields = ",".join(["`" + rel_field + "`" for rel_field in REL_FETCHED_FIELDS])
    for concept_name in concepts_to_local_rels.keys():
        if concept_name not in match_patterns:
            match_patterns[concept_name] = []
        match_patterns[concept_name].extend(
            [entity["os_entity_uid"] for entity in entities_by_concept[concept_name]]
        )
    for concept_name, entity_ids in match_patterns.items():
        rel_names = concepts_to_local_rels[concept_name]
        inverse_names = [
            ontology_rels[rel_name]["inverse_name"] for rel_name in rel_names
        ]
        rel_names = ",".join(["'" + rel_name + "'" for rel_name in rel_names])
        inverse_names = ",".join(["'" + rel_name + "'" for rel_name in inverse_names])
        entity_ids = ",".join(["'" + uid + "'" for uid in entity_ids])
        if rel_names and inverse_names and entity_ids:
            local_queries["from"].append(
                {
                    "query": f"SELECT {rel_fields} FROM `timbr`.`os_workspace_relationship` WHERE `os_relationship_name` IN ({rel_names}) AND `os_entity_uid_from` IN ({entity_ids}) LIMIT {limit}"
                }
            )
            local_queries["to"].append(
                {
                    "query": f"SELECT {rel_fields} FROM `timbr`.`os_workspace_relationship` WHERE `os_relationship_name` IN ({inverse_names}) AND `os_entity_uid_to` IN ({entity_ids}) LIMIT {limit}"
                }
            )
    local_queries = {
        **{
            "from_" + str(i): local_queries["from"][i]
            for i in range(len(local_queries["from"]))
        },
        **{
            "to_" + str(i): local_queries["to"][i]
            for i in range(len(local_queries["to"]))
        },
    }
    metrics.n_queries += len(local_queries)
    local_stream = multiquery_ontology.streaming(
        sql_queries={
            query_id: query_data["query"]
            for query_id, query_data in local_queries.items()
        },
        client=client,
        timeout=timeout / 2.0,
    )
    all_results = await _get_stream_result(local_stream)
    middle_entities = []
    for query_id, data in all_results.items():
        if data == None:
            metrics.n_cancelled_queries += 1
        if not data:
            continue
        query_id = query_id.split("_")
        data = _left_join(
            [e[0] for e in expanded_entities.values()],
            data,
            "os_entity_uid",
            "os_entity_uid_" + query_id[0],
        )
        inverse_direction = "to" if query_id[0] == "from" else "from"
        data = {
            e[0]["os_entity_uid"]: (e[0], {r["os_entity_uid"]: (r, {}) for r in e[1]})
            for e in data
        }
        middle_entities.extend(
            [(inverse_direction, r) for e in data.values() for r in e[1].values()]
        )
        for entity_id, entities in data.items():
            if entity_id not in expanded_entities:
                expanded_entities[entity_id] = [entities[0], {}]
            for sub_entity_id, sub_entities in entities[1].items():
                if sub_entity_id not in expanded_entities[entity_id][1]:
                    expanded_entities[entity_id][1][sub_entity_id] = [
                        sub_entities[0],
                        {},
                    ]
                expanded_entities[entity_id][1][sub_entity_id][1].update(
                    sub_entities[1]
                )
    middle_entities = [
        {
            "entity_id": r[1][0]["os_entity_uid_" + r[0]],
            "concept_name": r[1][0]["os_entity_type_" + r[0]],
            "direction": r[0],
            "relationship": r[1],
        }
        for r in middle_entities
    ]
    middle_entities = sorted(middle_entities, key=lambda x: x["concept_name"])
    middle_entities = groupby(middle_entities, key=lambda x: x["concept_name"])
    middle_entities = {e[0]: list(e[1]) for e in middle_entities}
    local_queries_2 = []
    for concept_name, entities in middle_entities.items():
        entity_ids = ",".join(["'" + e["entity_id"] + "'" for e in entities])
        if entity_ids:
            local_queries_2.append(
                {
                    "query": f"SELECT {target_fields} FROM `timbr`.`{concept_name}` WHERE `os_entity_uid` IN ({entity_ids}) LIMIT {limit}"
                }
            )
    local_queries_2 = {str(i): local_queries_2[i] for i in range(len(local_queries_2))}
    metrics.n_queries += len(local_queries_2)
    local_stream_2 = multiquery_ontology.streaming(
        sql_queries={
            query_id: query_data["query"]
            for query_id, query_data in local_queries_2.items()
        },
        client=client,
        timeout=timeout / 2.0,
    )
    all_results = await _get_stream_result(local_stream_2)
    middle_entities = list(chain(*middle_entities.values()))
    for query_id, data in all_results.items():
        if data == None:
            metrics.n_cancelled_queries += 1
        if not data:
            continue
        data = _left_join(middle_entities, data, "entity_id", "os_entity_uid")
        for entry in data:
            relationship_targets = entry[0]["relationship"]
            for target_entity in entry[1]:
                relationship_targets[1][target_entity["os_entity_uid"]] = target_entity
        if data:
            for rel in data:
                targets = rel[0]["relationship"][1]
                rel_uid = rel[0]["relationship"][0]["os_entity_uid"]
                for entity in expanded_entities.values():
                    entity_rels = entity[1]
                    if rel_uid in entity_rels:
                        entity_rels[rel_uid][1].update(targets)
    metrics.exec_times["mtm_local"] = time.time() - start_time
    return expanded_entities


async def expand_entities(
    entities,
    ontology,
    relationship_mappings_info,
    client,
    relationship_names_by_entity_type=None,
    batch_size=10000,
    avg_limit_per_entity=20,
    timeout=10.0,
):
    metrics = ExecutionMetrics()
    metrics.timeout = timeout
    start_time = time.time()
    ordered_entities = sorted(entities, key=lambda x: x["entity_type"])
    ordered_entities = list({e["os_entity_uid"]: e for e in entities}.values())
    entity_batches = [
        ordered_entities[i : i + batch_size]
        for i in range(0, len(ordered_entities), batch_size)
    ]
    expanded_entities = {}
    for batch in entity_batches:
        new_entities = await expand_entities_batch(
            batch,
            ontology,
            relationship_mappings_info,
            relationship_names_by_entity_type,
            metrics,
            client,
            avg_limit_per_entity,
            timeout,
        )
        expanded_entities.update(new_entities)
    metrics.exec_time = time.time() - start_time
    for _, entity_data in expanded_entities.items():
        for rel in entity_data[1].values():
            if rel[0]:
                metrics.n_relationships += 1
                metrics.relationship_names.add(rel[0]["os_relationship_name"])
            metrics.n_target_entities += len(rel[1])
    metrics.relationship_names = list(metrics.relationship_names)
    expanded_entities = [
        (e[0], [(r[0], list(r[1].values())[0]) for r in e[1].values()])
        for e in expanded_entities.values()
    ]
    return expanded_entities, metrics


async def expand_entities_batch(
    entities,
    ontology,
    relationship_mappings,
    relationship_names_by_entity_type,
    metrics,
    client,
    avg_limit_per_entity=20,
    timeout=10.0,
):
    limit = avg_limit_per_entity * len(entities)
    expanded_entities = {e["os_entity_uid"]: [e, {}] for e in entities}
    entities_by_concept = sorted(entities, key=lambda x: x["entity_type"])
    entities_by_concept = groupby(entities_by_concept, key=lambda x: x["entity_type"])
    entities_by_concept = {e[0]: list(e[1]) for e in entities_by_concept}
    ontology_rels = {r["relationship_name"]: r for r in ontology["relationships"]}
    concepts_to_rels = {
        cn: c["relationships"] for cn, c in ontology["concepts"].items()
    }
    concepts_to_mixed_rels = {}
    concepts_to_otm_rels = {}
    concepts_to_local_rels = {}
    for concept_name in entities_by_concept.keys():
        relationship_names = None
        if relationship_names_by_entity_type:
            relationship_names = set()
            for cn_name in relationship_names_by_entity_type.keys():
                if is_child_concept(concept_name, cn_name, ontology):
                    relationship_names = relationship_names.union(
                        set(relationship_names_by_entity_type[cn_name])
                    )
        rels = concepts_to_rels[concept_name]
        if relationship_names:
            rels = [r for r in rels if r in relationship_names]
        filtered_mtm_rels = []
        filtered_otm_rels = []
        filtered_local_mtm_rels = []
        for rel in rels:
            if not ontology_rels[rel]["is_mtm"]:
                filtered_otm_rels.append(rel)
            elif rel in relationship_mappings["unmapped"]:
                continue
            elif rel in relationship_mappings["local_only"]:
                filtered_local_mtm_rels.append(rel)
            else:
                filtered_mtm_rels.append(rel)
        concepts_to_mixed_rels[concept_name] = filtered_mtm_rels
        concepts_to_otm_rels[concept_name] = filtered_otm_rels
        concepts_to_local_rels[concept_name] = filtered_local_mtm_rels
    # OTM QUERIES: fetch target entities directly from the target tables with an IN statement
    expanded_entities = await expand_otm(
        expanded_entities,
        entities_by_concept,
        ontology_rels,
        concepts_to_otm_rels,
        metrics,
        client,
        timeout,
        limit,
    )
    # LOCAL MTM QUERIES: fetch relationships directly from the os_workspace_relationship table, then fetch target entities
    expanded_entities = await expand_mtm_local(
        expanded_entities,
        entities_by_concept,
        ontology_rels,
        concepts_to_local_rels,
        metrics,
        client,
        timeout,
        limit,
    )
    # MIXED MTM QUERIES: query via timbr to make the most of JOINs
    expanded_entities = await expand_mtm_mixed(
        expanded_entities,
        entities_by_concept,
        ontology,
        concepts_to_mixed_rels,
        ontology_rels,
        metrics,
        client,
        timeout,
        limit,
    )
    return expanded_entities
