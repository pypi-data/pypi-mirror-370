from copy import deepcopy
import uuid
from functools import wraps
import json
import jwt
from typing import List, Union, Optional, Callable
import base64
from pydantic import BaseModel, ConfigDict, Field
import itertools
import asyncio
from enum import Enum
from typing import Dict, Any
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from octostar.utils.workspace import read_file, upsert_entities, write_file
from octostar.utils.ontology import fetch_ontology_data
from octostar.utils.workspace.permissions import get_permissions, PermissionLevel
from octostar.api.ontology import relationship_mappings
from octostar.client import make_client

from ..core.dict import recursive_update_dict, travel_dict, jsondict_hash
from ..core.timestamp import now, string_to_datetime
from .fastapi import DefaultErrorRoute, Route
from ..ontology.inheritance import is_child_concept as is_child_concept_fn
from ..ontology.expand_entities import expand_entities

RELATIONSHIP_ENTITY_NAME = "os_relationship"
LOCAL_RELATIONSHIP_ENTITY_NAME = "os_workspace_relationship"
FILE_ENTITY_NAME = "os_file"
GENERIC_RELATIONSHIP_NAME = "related_to"
FILE_RELATIONSHIP_NAME = "generator_of"
TAG_RELATIONSHIP_NAME = "has_tag"
TAG_ENTITY_NAME = "os_tag"


def safe_async_run(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(coro)
        else:
            return asyncio.run(coro)
    except RuntimeError:
        return asyncio.run(coro)


class NifiContentsPointerLocationModel(Enum):
    LOCAL = "local"
    ATTACHMENT = "attachment"


class NifiProxyEntityModel(BaseModel):
    entity_id: str
    entity_type: str


class NifiOTMRelationshipProxyModel(BaseModel):
    os_entity_uid_from: str
    os_entity_type_from: str
    os_entity_uid_to: str
    os_entity_type_to: str
    os_relationship_name: str


class NifiEntityModel(BaseModel):
    class RequestModel(BaseModel):
        class OntologyInfoModel(BaseModel):
            parents: List[str]
            relationships: List[str]

        class ContentsPointerModel(BaseModel):
            location: NifiContentsPointerLocationModel
            pointer: Optional[str] = None

        jwt: str
        ontology_name: str
        ontology_info: OntologyInfoModel
        entity_timestamp: Optional[str]
        sync_params: dict = Field(default_factory=dict)
        nifi_attributes: dict = Field(default_factory=dict)
        config: dict = Field(default_factory=dict)
        metrics: dict = Field(default_factory=dict)
        contents_pointer: Optional[ContentsPointerModel] = None
        is_temporary: bool = False
        exception: dict = Field(default_factory=dict)
        last_processor_name: Optional[str] = None
        fallback_os_workspace: Optional[str] = None

    class RecordModel(BaseModel):
        model_config = ConfigDict(extra="allow")
        entity_id: str
        os_entity_uid: str
        entity_type: str
        os_concept: str
        os_workspace: Optional[str] = None
        entity_label: Optional[str] = None

    request: RequestModel
    record: RecordModel
    annotations: Dict[str, Any] = Field(default_factory=dict)
    children: List[Union[NifiOTMRelationshipProxyModel, NifiProxyEntityModel]] = []
    contents: Optional[bytes] = None


NifiEntityModel.model_rebuild()


class NifiOTMRelationshipProxy(object):
    def __init__(
        self,
        os_entity_uid_from,
        os_entity_type_from,
        os_entity_uid_to,
        os_entity_type_to,
        os_relationship_name,
        drop_on_output=False,
    ):
        self.record = {
            "os_entity_uid_from": os_entity_uid_from,
            "os_entity_type_from": os_entity_type_from,
            "os_entity_uid_to": os_entity_uid_to,
            "os_entity_type_to": os_entity_type_to,
            "os_relationship_name": os_relationship_name,
        }
        self.drop_on_output = drop_on_output


class NifiEntityProxy(object):
    def __init__(
        self,
        context,
        uid,
        entity_type,
        output_as_child,
        output_as_independent,
        drop_on_output,
        proxy=None,
    ):
        self.context = context
        self.uid = uid
        self.entity_type = entity_type
        self.output_as_child = output_as_child
        self.output_as_independent = output_as_independent
        self.drop_on_output = drop_on_output
        self._proxy = proxy

    def __eq__(self, other):
        if isinstance(other, NifiEntity):
            return self.uid == other.record["entity_id"]
        elif isinstance(other, NifiEntityProxy):
            return self.uid == other.uid
        else:
            return False

    def fetch_proxy(self):
        def _recursive_search_expanded_proxy(entity, uid_to_search):
            found_entity = None
            for child_entity in entity.children_entities:
                if child_entity._proxy:
                    if child_entity.uid == uid_to_search:
                        found_entity = child_entity
                    else:
                        found_entity = _recursive_search_expanded_proxy(
                            child_entity._proxy, uid_to_search
                        )
                if found_entity:
                    return found_entity

        if not self._proxy:
            main_entities = itertools.chain(
                *[b.entities for b in self.context.in_batches]
            )
            main_entities = {e.record["entity_id"]: e for e in main_entities}
            if main_entities.get(self.uid):
                self._proxy = main_entities.get(self.uid)
                return self._proxy
            for entity in main_entities.values():
                found_entity = _recursive_search_expanded_proxy(entity, self.uid)
                if found_entity:
                    self._proxy = found_entity._proxy
                    return self._proxy
            ## TODO: Try to get the entity from the database with query_ontology()
            raise AttributeError(
                f"Cannot find children with UUID {self.uid}! It may exist in the database?"
            )

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            if not self._proxy:
                self.fetch_proxy()
            return getattr(self._proxy, name)

    def __setattr__(self, name, value):
        if name in (
            "context",
            "uid",
            "entity_type",
            "output_as_child",
            "output_as_independent",
            "drop_on_output",
            "_proxy",
        ):
            super().__setattr__(name, value)
        else:
            if not self._proxy:
                self.fetch_proxy()
            setattr(self._proxy, name, value)


class NifiFragmenter(object):
    def as_nifi_fragments(fragments, fragmenter_keylist):
        count = len(fragments)
        if count < 2:
            raise ValueError("Must have at least 2 entities for fragmentation")
        identifier = str(uuid.uuid4())
        for i, entity in enumerate(fragments):
            travel_dict(
                entity.request["nifi_attributes"], fragmenter_keylist.split("."), "w"
            )({"identifier": identifier, "count": count, "index": i})
            if "fragment" not in entity.request["config"]:
                entity.request["config"]["fragment"] = {}
            if "fragments_stack" not in entity.request["config"]["fragment"]:
                entity.request["config"]["fragment"]["fragments_stack"] = []
            entity.request["config"]["fragment"]["fragments_stack"].insert(
                0, fragmenter_keylist
            )
            entity.request["nifi_attributes"]["fragments_stack"] = entity.request[
                "config"
            ]["fragment"]["fragments_stack"]
            travel_dict(
                entity.request["config"]["fragment"], fragmenter_keylist.split("."), "w"
            )({"identifier": identifier, "count": count, "index": i})

    def push_defragment_strategy(fragment, defragmenter_config):
        pointer = fragment.request["config"]
        last_fragmenter_keylist = fragment.request["config"]["fragment"][
            "fragments_stack"
        ][0]
        for k in ("fragment." + last_fragmenter_keylist).split("."):
            if not pointer.get(k):
                pointer[k] = {}
            pointer = pointer[k]
        pointer["merge_params"] = recursive_update_dict(
            pointer.get("merge_params") or {}, defragmenter_config, lambda _, v2: v2
        )


class NifiEntityBatch(object):
    def __init__(self, entities, config, config_key):
        self.config = config
        self.entities = entities
        self.config_key = config_key


class NifiContextManager(object):
    HEADLESS_PROCESSOR_NAME = "headless"
    
    class SyncFlag(Enum):
        UPSERT_ENTITY_ALL = 0  # bool
        UPSERT_ENTITY_SPECIFIC_FIELDS = 1  # 'fields': list of record fields
        WRITE_CONTENTS = 10  # bool
        FETCH_RELATIONSHIPS = 20  # 'relationships': list of relationship names

    def __init__(self, json_data, lazy_sync=True):
        if not json_data:
            raise ValueError("Nifi context manager received list of 0 entities")
        self.permissions = {}
        self.in_batches = None
        self.out_entities = None
        self.nonlazy_sync_ids = set()
        self.lazy_sync = lazy_sync
        self.client, self.ontology_name = self.get_client(json_data)
        self._ontology = None

    @property
    def ontology(self):
        if not self._ontology:
            self._ontology = fetch_ontology_data.sync(
                ontology_name=self.ontology_name, client=self.client
            )
        return self._ontology

    def _config_get(entity, keylist):
        if keylist == NifiContextManager.HEADLESS_PROCESSOR_NAME:
            return {}
        config = entity.request["config"]
        return travel_dict(config, keylist.split("."), mode="r", default={})

    def get_client(self, json_data):
        all_jwts = [e["request"].get("jwt") for e in json_data]
        all_jwts = [j for j in all_jwts if j]
        assert len(set(all_jwts)) == 1  # jwt must be unique
        all_ontology_names = [e["request"].get("ontology_name") for e in json_data]
        all_ontology_names = [j for j in all_ontology_names if j]
        assert len(set(all_ontology_names)) == 1  # ontology name must be unique
        curr_user_jwt = all_jwts[0]
        curr_user_ontology = all_ontology_names[0]
        client = make_client(fixed_jwt=curr_user_jwt, ontology_name=curr_user_ontology)
        return client, curr_user_ontology

    def receive_input(self, json_data, processor_name) -> List["NifiEntityBatch"]:
        def _safe_decode(contents):
            return base64.b64decode(contents) if contents else None

        entities = []
        all_independent_uids = [e["record"]["entity_id"] for e in json_data]
        for elem in json_data:
            entities.append(
                NifiEntity(
                    self,
                    elem["request"],
                    elem["record"],
                    elem["annotations"],
                    all_independent_uids,
                    elem["children"],
                    _safe_decode(elem.get("contents")),
                )
            )
        entities = sorted(
            entities,
            key=lambda x: string_to_datetime(x.record.get("os_last_updated_at")),
        )
        entities = list({e.record["entity_id"]: e for e in entities}.values())
        entities = [
            (
                jsondict_hash(NifiContextManager._config_get(entity, processor_name)),
                entity,
            )
            for entity in entities
        ]
        entities = sorted(entities, key=lambda x: x[0])
        grouped_entities = []
        for _, group in itertools.groupby(entities, key=lambda x: x[0]):
            group = [e[1] for e in group]
            grouped_entities.append(
                NifiEntityBatch(
                    group,
                    NifiContextManager._config_get(group[0], processor_name),
                    processor_name,
                )
            )
        self.in_batches = grouped_entities
        return self.in_batches

    def __enter__(self):
        return self

    def get_workspaces_permissions(self, workspace_ids):
        permissions_to_fetch = list(
            set(workspace_ids).difference(set(list(self.permissions.keys())))
        )
        if permissions_to_fetch:
            permissions = get_permissions.sync(permissions_to_fetch, client=self.client)
            self.permissions.update(permissions)
        permissions = {}
        for k in workspace_ids:
            permissions[k] = self.permissions.get(k, PermissionLevel.NONE)
        return permissions

    def request_entity_sync(
        self,
        entity,
        parametrized_flags: Dict[SyncFlag, Any],
        merge_method=lambda _, v2: v2,
        now=False,
    ):
        entity.sync_params = recursive_update_dict(
            entity.request.get("sync_params") or {}, parametrized_flags, merge_method
        )
        if now:
            self.nonlazy_sync_ids.add(entity.record["entity_id"])

    def send_output(self, entity_batches, processor_name):
        def _process_entity(entity, processor_name):
            entities = []
            if processor_name != NifiContextManager.HEADLESS_PROCESSOR_NAME:
                entity.request["last_processor_name"] = processor_name
            entities.append(entity)
            for child_entity in entity.children_entities:
                if not child_entity.drop_on_output:
                    if (
                        child_entity.output_as_independent
                        or child_entity.output_as_child
                    ):
                        if processor_name != NifiContextManager.HEADLESS_PROCESSOR_NAME:
                            child_entity.request["last_processor_name"] = processor_name
                    if child_entity.output_as_independent:
                        if not child_entity._proxy:
                            child_entity.fetch_proxy()
                        entities.extend(
                            _process_entity(child_entity._proxy, processor_name)
                        )
            return entities

        entities = itertools.chain(*[b.entities for b in entity_batches])
        all_entities = []
        for entity in entities:
            all_entities.extend(_process_entity(entity, processor_name))
        all_entities = sorted(
            all_entities,
            key=lambda x: string_to_datetime(x.record.get("os_last_updated_at")),
        )
        self.out_entities = list(
            {e.record["entity_id"]: e for e in all_entities}.values()
        )
        self.sync_entities()
        return [entity for entity in self.jsonify(self.out_entities)["content"]]

    def raise_exception(self, entity, exc):
        error_response = DefaultErrorRoute.format_error(exc)
        entity.request["exception"]["code"] = error_response.status_code
        entity.request["exception"]["body"] = json.loads(error_response.body)["message"]
        travel_dict(
            entity.request["nifi_attributes"], ["invokehttp", "response", "body"], "w"
        )(entity.request["exception"]["body"])
        travel_dict(
            entity.request["nifi_attributes"], ["invokehttp", "response", "code"], "w"
        )(entity.request["exception"]["code"])
        entity.request["nifi_attributes"]["raised_exc"] = True

    def sync_entities(self):
        if not self.lazy_sync:
            entities = self.out_entities
        else:
            entities = [
                e
                for e in self.out_entities
                if e.record["entity_id"] in self.nonlazy_sync_ids
            ]
        if not entities:
            return
        reserved_fields = [
            "os_entity_uid",
            "entity_id",
            "entity_type",
            "os_concept",
            "entity_label",
            "os_created_at",
            "os_created_by",
            "os_last_updated_at",
            "os_last_updated_by",
        ]
        entities_to_upsert = []
        files_to_write = []
        fetch_relationships_entities = {}
        fetch_concept_relationships = {}
        # FIND ENTITIES TO UPSERT
        self._find_entities_to_upsert(entities, entities_to_upsert, reserved_fields)
        # FIND FILES TO WRITE
        for entity in entities:
            if entity.is_child_concept("os_file") and entity.sync_params.get(
                NifiContextManager.SyncFlag.WRITE_CONTENTS
            ):
                files_to_write.append(entity)
        # FIND RELATIONSHIPS TO FETCH
        for entity in entities:
            if entity.sync_params.get(NifiContextManager.SyncFlag.FETCH_RELATIONSHIPS):
                concept_name = entity.record["entity_type"]
                rels_to_fetch = entity.sync_params.get(
                    NifiContextManager.SyncFlag.FETCH_RELATIONSHIPS, []
                )
                for rel in rels_to_fetch:
                    if rel not in fetch_relationships_entities:
                        fetch_relationships_entities[rel] = []
                    fetch_relationships_entities[rel].append(entity)
                if concept_name not in fetch_concept_relationships:
                    fetch_concept_relationships[concept_name] = set()
                fetch_concept_relationships[concept_name] = fetch_concept_relationships[
                    concept_name
                ].union(set(rels_to_fetch))
        for k in fetch_concept_relationships.keys():
            fetch_concept_relationships[k] = list(fetch_concept_relationships[k])
        # UPSERT ENTITIES
        if entities_to_upsert:
            new_entities = upsert_entities.sync(
                [entity.write_os_workspace for entity, _ in entities_to_upsert],
                [
                    {
                        "entity_type": entity.record["os_concept"],
                        "os_entity_uid": entity.record["os_entity_uid"],
                        "os_last_updated_at": entity.request["entity_timestamp"],
                        "fields": {k: entity.record.get(k) for k in fields},
                    }
                    for entity, fields in entities_to_upsert
                ],
                client=self.client,
            )
            new_entities = {e["os_entity_uid"]: e for e in new_entities}
            for entity, _ in entities_to_upsert:
                entity.record = {
                    **entity.record,
                    **new_entities[entity.record["os_entity_uid"]],
                }
                entity.record["entity_id"] = entity.record["os_entity_uid"]
                entity.record["entity_type"] = entity.record["os_concept"]
                entity.record["entity_label"] = entity.label
                entity.request["is_temporary"] = False
                entity.request["entity_timestamp"] = entity.record["os_last_updated_at"]
        # WRITE FILES
        for file in files_to_write:
            new_file_record = write_file.sync(
                file.write_os_workspace,
                file.filepath,
                file.record["os_item_content_type"],
                file.contents,
                file.record["os_entity_uid"],
                client=self.client,
            )
            file.record = {**file.record, **new_file_record}
            file.record["entity_id"] = file.record["os_entity_uid"]
            file.record["entity_type"] = file.record["os_concept"]
            file.record["entity_label"] = file.label
            file.request["is_temporary"] = False
            file.request["entity_timestamp"] = file.record["os_last_updated_at"]
        # FETCH RELATIONSHIPS
        '''
        if fetch_relationships_entities:
            relationship_mappings_info = relationship_mappings.sync_detailed(
                client=self.client
            ).parsed.data.to_dict()
            expanded_entities, _ = safe_async_run(
                expand_entities(
                    [e.record for e in entities],
                    self.ontology,
                    relationship_mappings_info,
                    self.client,
                    fetch_concept_relationships,
                )
            )
            expanded_entities = {e[0]["os_entity_uid"]: e for e in expanded_entities}
            for entity in entities:
                found_entities = expanded_entities.get(entity.record["os_entity_uid"])
                if found_entities:
                    for rel, target in found_entities[1]:
                        is_mtm = bool(
                            rel.get("os_entity_uid_from")
                            and rel.get("os_entity_uid_to")
                        )
                        rel_type = "mtm" if is_mtm else "otm"
                        child_entity, child_rel = entity.add_child_entity(
                            target["os_workspace"],
                            target["os_concept"],
                            target,
                            os_relationship_name=rel["os_relationship_name"],
                            os_relationship_type=rel_type,
                        )
                        child_entity.record = {**child_entity.record, **target}
                        child_entity.record["entity_id"] = child_entity.record[
                            "os_entity_uid"
                        ]
                        child_entity.uid = child_entity.record["os_entity_uid"]
                        child_entity.request["is_temporary"] = False
                        child_entity.request["entity_timestamp"] = target.get(
                            "os_last_updated_at"
                        )
                        if not is_mtm:
                            child_rel.record["os_entity_uid_to"] = child_entity.record[
                                "os_entity_uid"
                            ]
                        else:
                            child_rel.record = {**child_rel.record, **rel}
                            child_rel.record["entity_id"] = child_rel.record[
                                "os_entity_uid"
                            ]
                            child_rel.uid = child_rel.record["os_entity_uid"]
                            child_rel.request["is_temporary"] = bool(
                                rel.get("os_entity_uid")
                            )
                            child_rel.request["entity_timestamp"] = rel.get(
                                "os_last_updated_at"
                            )
        '''
        # CLEAN SYNC PARAMS
        for entity in entities:
            entity.sync_params = {}

    def _find_entities_to_upsert(self, entities, entities_to_upsert, reserved_fields) -> None:
        for entity in entities:
            fields = set()

            if (
                    entity.sync_params.get(NifiContextManager.SyncFlag.UPSERT_ENTITY_ALL)
                    or entity.request["is_temporary"]
            ):
                fields = fields.union(set(list(entity.record.keys())))

            if entity.sync_params.get(
                    NifiContextManager.SyncFlag.UPSERT_ENTITY_SPECIFIC_FIELDS
            ):
                fields = fields.union(
                    set(
                        entity.sync_params.get(
                            NifiContextManager.SyncFlag.UPSERT_ENTITY_SPECIFIC_FIELDS,
                            {},
                        ).get("fields")
                        or []
                    )
                )
            if fields:
                entities_to_upsert.append(
                    (entity, [f for f in list(fields) if f not in reserved_fields])
                )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            return False
        if self.out_entities is None:
            raise AssertionError("Entities must be returned to the nifi context!")

    def jsonify(self, entities):
        def _recursive_collect_proxies(entities):
            children = []
            for entity in entities:
                if isinstance(entity, NifiEntityProxy):
                    children.extend(entity.children_entities)
                    children.extend(
                        _recursive_collect_proxies(entity.children_entities)
                    )
            return children

        all_proxies = _recursive_collect_proxies(entities)
        banned_entities = [e for e in all_proxies if not e.output_as_independent]
        entities = [e for e in entities if e not in banned_entities]
        return {
            "content": [e for e in [entity.to_json() for entity in entities] if e],
            "media_type": "application/json",
        }


class NifiEntity(object):
    def __init__(
        self, context, request, record, annotations, all_independent_uids, children=[], contents=None
    ):
        self.context = context
        self.request = request
        self.record = record
        self.annotations = annotations
        assert self.record.get("os_entity_uid") and self.record.get("entity_id") and self.record["os_entity_uid"] == self.record["entity_id"]
        assert self.record.get("os_concept") and self.record.get("entity_type") and self.record["os_concept"] == self.record["entity_type"]
        if "entity_label" not in self.record:
            self.record["entity_label"] = self.label
        children = [c for c in children if isinstance(c, (str, dict))]
        full_entity_children = []
        proxy_otm_children = []
        proxy_entity_children = []
        for child in children:
            if "os_relationship_name" in child:
                proxy_otm_children.append(child)
            elif "request" in child:
                full_entity_children.append(child)
            else:
                proxy_entity_children.append(child)
        child_uids = [c["entity_id"] for c in proxy_entity_children] + [
            c["record"]["entity_id"] for c in full_entity_children
        ]
        child_types = [c["entity_type"] for c in proxy_entity_children] + [
            c["record"]["entity_type"] for c in full_entity_children
        ]
        output_as_child = [False] * len(proxy_entity_children) + [True] * len(
            full_entity_children
        )
        output_as_independent = [uid in all_independent_uids for uid in child_uids]
        full_entity_children = [
            NifiEntity(
                self.context,
                c["request"],
                c["record"],
                c["annotations"],
                all_independent_uids,
                c["children"],
                c["contents"],
            )
            for c in full_entity_children
        ]
        proxy_otm_children = [
            NifiOTMRelationshipProxy(**otm_child) for otm_child in proxy_otm_children
        ]
        child_proxies = [None] * len(proxy_entity_children) + full_entity_children
        self.children = [
            NifiEntityProxy(
                self.context,
                child_uids[i],
                child_types[i],
                output_as_child[i],
                output_as_independent[i],
                False,
                child_proxies[i],
            )
            for i in range(len(child_uids))
        ]
        self.children.extend(proxy_otm_children)
        self._contents = contents
        self.drop_on_output = False

    def __eq__(self, other):
        if isinstance(other, NifiEntity):
            return self.record["entity_id"] == other.record["entity_id"]
        elif isinstance(other, NifiEntityProxy):
            return self.record["entity_id"] == other.uid
        else:
            return False

    @property
    def sync_params(self):
        return {
            NifiContextManager.SyncFlag[k]: v
            for k, v in (self.request.get("sync_params") or {}).items()
        }

    @sync_params.setter
    def sync_params(self, new_params):
        self.request["sync_params"] = {
            (k.name if isinstance(k, NifiContextManager.SyncFlag) else k): v
            for k, v in new_params.items()
        }

    @property
    def metadata(self):
        return self.annotations
    @metadata.setter
    def metadata(self, new_metadata):
        self.annotations = new_metadata

    @property
    def contents(self):
        if not self._contents:
            contents_pointer = self.contents_pointer
            if contents_pointer["location"] == "attachment":
                self._contents = read_file.sync(
                    contents_pointer["pointer"].split("/")[0],
                    contents_pointer["pointer"].split("/")[-1],
                    False,
                    client=self.context.client,
                )
        return self._contents

    @property
    def contents_pointer(self):
        contents_pointer = deepcopy(self.request["contents_pointer"])
        ptr_location = contents_pointer.get("location")
        if ptr_location == "attachment" and not contents_pointer.get("pointer"):
            contents_pointer["pointer"] = (
                f"{self.record['os_workspace']}/{self.record['os_entity_uid']}"
            )
        return self.request["contents_pointer"]

    @contents_pointer.setter
    def contents_pointer(self, new_value):
        self.request["contents_pointer"] = new_value

    @contents.setter
    def contents(self, new_contents):
        self._contents = new_contents

    @property
    def children_entities(self):
        return list(filter(lambda x: isinstance(x, NifiEntityProxy), self.children))

    @property
    def relationships(self):
        return list(
            filter(
                lambda x: isinstance(x, NifiOTMRelationshipProxy)
                or is_child_concept_fn(
                    x.entity_type, RELATIONSHIP_ENTITY_NAME, self.context.ontology
                ),
                self.children,
            )
        )

    @property
    def write_os_workspace(self):
        permissions = self.context.get_workspaces_permissions(
            [
                e
                for e in [
                    self.record.get("os_workspace"),
                    self.request.get("fallback_os_workspace"),
                ]
                if e
            ]
        )
        if (
            self.record.get("os_workspace")
            and (
                permissions.get(self.record.get("os_workspace")) or PermissionLevel.NONE
            )
            >= PermissionLevel.WRITE
        ):
            return self.record["os_workspace"]
        elif (
            self.request.get("fallback_os_workspace")
            and (
                permissions.get(self.request.get("fallback_os_workspace"))
                or PermissionLevel.NONE
            )
            >= PermissionLevel.WRITE
        ):
            return self.request["fallback_os_workspace"]
        else:
            return None

    @property
    def label(self):
        if not self.context.ontology:
            return None
        label_fields = self.context.ontology["concepts"][
            self.record.get("os_concept") or self.record.get("entity_type")
        ]["labelKeys"]
        label_fields = [field for field in label_fields if field]
        label = " ".join(
            [(self.record.get(field) or "") for field in label_fields]
        ).strip()
        if not label:
            label = None
        return label

    @property
    def filepath(self):
        return self.record.get("#path") or self.label

    @property
    def jwt_data(self):
        return jwt.decode(
            self.request["jwt"],
            algorithms=["ES256"],
            options={"verify_signature": False},
        )

    def update_last_timestamp(self):
        self.record["os_last_updated_at"] = now()

    def is_child_concept(self, type):
        entity_type = None
        if isinstance(self, NifiEntityProxy):
            entity_type = self.entity_type
            return entity_type == type or is_child_concept_fn(
                entity_type, type, self.context.ontology
            )
        else:
            entity_type = self.record["entity_type"]
            return (
                entity_type == type or type in self.request["ontology_info"]["parents"]
            )

    def is_fragmented(self) -> bool:
        return bool(self.request["config"].get("fragment", {}).get("fragments_stack"))

    def is_root_fragment(self, entity) -> bool:
        def _is_sub_fragment_recursive(fragment: dict) -> bool:
            if not isinstance(fragment, dict):
                return False
            if all(k in fragment for k in ["index", "count", "identifier"]):
                return fragment.get("index", 0) != 0
            for value in fragment.values():
                if isinstance(value, dict):
                    if _is_sub_fragment_recursive(value):
                        return True
            return False
        
        if not self.is_fragmented():
            return True
        fragment = entity.request.get("config", {}).get("fragment", {})
        return not _is_sub_fragment_recursive(fragment)

    def to_json(self):
        def _safe_encode(contents):
            return base64.b64encode(contents) if contents else None

        if self.drop_on_output:
            return
        proxy_entity_children = []
        proxy_otm_children = []
        full_entity_children = []
        for child in self.children:
            if isinstance(child, NifiOTMRelationshipProxy):
                proxy_otm_children.append(child)
            else:
                if child.drop_on_output:
                    pass
                elif child.output_as_child:
                    child.fetch_proxy()
                    full_entity_children.append(child)
                else:
                    proxy_entity_children.append(child)
        proxy_entity_children = list({c.uid: c for c in proxy_entity_children}.values())
        proxy_entity_children = [
            {"entity_id": c.uid, "entity_type": c.entity_type}
            for c in proxy_entity_children
        ]
        proxy_otm_children = list(
            {
                c.record["os_entity_uid_from"]
                + "|"
                + c.record["os_relationship_name"]
                + "|"
                + c.record["os_entity_uid_to"]: c
                for c in proxy_otm_children
            }.values()
        )
        proxy_otm_children = [c.record for c in proxy_otm_children]
        full_entity_children = sorted(
            full_entity_children,
            key=lambda x: string_to_datetime(x.record.get("os_last_updated_at")),
        )
        full_entity_children = list(
            {c.uid: c.to_json() for c in full_entity_children}.values()
        )
        children = full_entity_children + proxy_entity_children + proxy_otm_children
        return {
            "request": self.request,
            "record": self.record,
            "children": children,
            "annotations": self.annotations,
            "contents": _safe_encode(self._contents),
        }

    def _add_entity(self, os_workspace, entity_type, fields):
        now_time = now()
        random_id = str(uuid.uuid4())
        username = self.jwt_data["username"]
        child_request = {
            "jwt": self.request["jwt"],
            "ontology_name": self.request["ontology_name"],
            "ontology_info": {
                "parents": self.context.ontology["concepts"][entity_type]["parents"],
                "relationships": self.context.ontology["concepts"][entity_type][
                    "relationships"
                ],
            },
            "entity_timestamp": None,
            "sync_params": {},
            "nifi_attributes": {},
            "config": deepcopy(self.request["config"]),
            "metrics": {},
            "contents_pointer": None,
            "is_temporary": True,
            "exception": {},
            "last_processor_name": None,
            "fallback_os_workspace": self.request["fallback_os_workspace"],
        }
        child_entity = NifiEntity(
            self.context,
            child_request,
            {
                **fields,
                "os_workspace": os_workspace,
                "os_concept": entity_type,
                "entity_type": entity_type,
                "os_entity_uid": random_id,
                "entity_id": random_id,
                "os_created_at": now_time,
                "os_created_by": username,
                "os_last_updated_at": now_time,
                "os_last_updated_by": username,
            },
            {},
            [],
        )
        child_entity.record["entity_label"] = child_entity.label
        child_entity_proxy = NifiEntityProxy(
            self.context,
            child_entity.record["entity_id"],
            child_entity.record["entity_type"],
            True,
            False,
            False,
            child_entity,
        )
        self.children.append(child_entity_proxy)
        return child_entity_proxy

    def add_mtm_relationship(
        self,
        os_entity_uid_from,
        entity_type_from,
        os_entity_uid_to,
        entity_type_to,
        os_relationship_name,
        os_relationship_workspace,
        relationship_fields,
    ):
        return self._add_entity(
            os_relationship_workspace,
            (
                LOCAL_RELATIONSHIP_ENTITY_NAME
                if os_relationship_workspace
                else RELATIONSHIP_ENTITY_NAME
            ),
            {
                **relationship_fields,
                "os_entity_uid_from": os_entity_uid_from,
                "os_entity_type_from": entity_type_from,
                "os_entity_uid_to": os_entity_uid_to,
                "os_entity_type_to": entity_type_to,
                "os_relationship_name": os_relationship_name,
            },
        )

    def add_otm_relationship(
        self,
        os_entity_uid_from,
        entity_type_from,
        os_entity_uid_to,
        entity_type_to,
        os_relationship_name,
    ):
        new_rel = NifiOTMRelationshipProxy(
            os_entity_uid_from,
            entity_type_from,
            os_entity_uid_to,
            entity_type_to,
            os_relationship_name,
        )
        self.children.append(new_rel)
        return new_rel

    def add_child_entity(
        self,
        os_workspace,
        entity_type,
        fields,
        os_relationship_name=GENERIC_RELATIONSHIP_NAME,
        os_relationship_type="mtm",
    ):
        child_entity = self._add_entity(os_workspace, entity_type, fields)
        if os_relationship_type == "mtm":
            child_rel = self.add_mtm_relationship(
                self.record["os_entity_uid"],
                self.record["os_concept"],
                child_entity.record["os_entity_uid"],
                child_entity.record["os_concept"],
                os_relationship_name,
                os_workspace,
                {},
            )
        elif os_relationship_type == "otm":
            child_rel = self.add_otm_relationship(
                self.record["os_entity_uid"],
                self.record["os_concept"],
                child_entity.record["os_entity_uid"],
                child_entity.record["os_concept"],
                os_relationship_name,
            )
        else:
            raise ValueError(f"os_relationship_type is invalid! {os_relationship_type}")
        return child_entity, child_rel

    def add_child_file(
        self,
        os_workspace,
        full_filename,
        filetype,
        file,
        os_relationship_name=FILE_RELATIONSHIP_NAME,
        os_relationship_type="mtm",
    ):
        child_entity, child_rel = self.add_child_entity(
            os_workspace,
            FILE_ENTITY_NAME,
            {
                "os_item_name": full_filename.rsplit("/", 1)[-1],
                "os_item_content_type": filetype,
                "#path": full_filename,
                "os_has_attachment": True,
            },
            os_relationship_name,
            os_relationship_type,
        )
        child_entity._contents = file
        child_entity.request["contents_pointer"] = (
            NifiEntityModel.RequestModel.ContentsPointerModel(location="local")
        )
        return child_entity, child_rel

    def add_tag(self, os_workspace, name, group, order, color):
        return self.add_child_entity(
            os_workspace,
            "os_tag",
            {"name": name, "group": group, "order": order, "color": color},
            TAG_RELATIONSHIP_NAME,
            "mtm",
        )

    def add_metadata(
        self, json, merge_method: Callable[[Any, Any], Any], recurse: Union[bool, int] = False,
    ):
        if not self.metadata:
            self.metadata = {}
        self.metadata = recursive_update_dict(
            self.metadata, json, merge_method, recurse
        )

    def propagate_metadata(self, to_entity, fields=None, merge_method=lambda _, v2: v2):
        metadata_to_propagate = deepcopy(self.metadata)
        if fields:
            metadata_to_propagate = {k: v for k, v in self.metadata if k in fields}
        to_entity.metadata = recursive_update_dict(
            to_entity.metadata, metadata_to_propagate, merge_method
        )


def more_recent_than(record_a, record_b):
    return string_to_datetime(record_a.get("os_last_updated_at")) >= string_to_datetime(
        record_b.get("os_last_updated_at")
    )


class NifiRoute(Route):
    def __init__(self, app, tasks_routes, processor_name, celery_executor, router=None):
        self.app = app
        self._router = router
        self.routed_funcs = []
        self.tasks_routes = tasks_routes
        self.processor_name = processor_name
        self.celery_executor = celery_executor
        self.endpoints = {}
        self.define_routes()

    def register_route(self, op, nifi_task):
        self.endpoints[op.strip("/")] = nifi_task

    def define_routes(self):
        @Route.route(self, path="/task-state/{task_id}")
        async def get_task_status(task_id: str) -> JSONResponse:
            try:
                task_status = await self.tasks_routes.get_task(task_id, pop=False)
                task_status = task_status.model_dump(mode="json")["data"]["task_state"]
            except BaseException as e:
                raise ValueError(f"Could not fetch task state for task id {task_id}!\n{e}")
            return JSONResponse(task_status)

        @Route.route(self, path="/task-result/{task_id}")
        async def get_task_result(task_id: str) -> JSONResponse:
            try:
                return_data = await self.tasks_routes.get_task(task_id, pop=True)
                return_data = return_data.model_dump(mode="json")["data"]["data"]
            except BaseException as e:
                raise ValueError(f"Could not fetch task result for task id {task_id}\n{e}!")
            return JSONResponse(return_data)

        @Route.route(self, path="/{op}", methods=["POST"])
        async def send_task(op: str, request: Request) -> str:
            """
            Any request coming from Nifi should enter from here.
            Note that:
            - The **op** parameter should be any of the other endpoints, including path parameters
            - The body parameters should be a list of entities in Nifi format, which also replace form parameters
            - The query parameters should be set in the 'request.config.<<processor_name>>.<<route_name>>.<<suffix_name>>' entry of the entities
            """
            path_params = []
            op = op.split("/")
            if len(op) > 1:
                path_params = op[1:]
            op = op[0]
            query_params = request.query_params
            processor_suffix = query_params["processor_suffix"]
            body = await request.json()
            processor_name = (
                "processor."
                + self.processor_name
                + "."
                + op.replace("-", "_")
                + "."
                + processor_suffix
            )
            if op not in self.endpoints.keys():
                raise StarletteHTTPException(401, f"Route {op} is forbidden for NiFi.")
            task_id = await self.celery_executor.send_task(
                self.endpoints[op], args=[body, processor_name]
            )
            return task_id

    @staticmethod
    def nifi_task(celery_executor, *args, **opts):
        def decorator(func):
            @wraps(func)
            def nifi_func(task, body, processor_name, *args, **kwargs):
                with NifiContextManager(body) as nifi_context:
                    entity_batches = nifi_context.receive_input(body, processor_name)
                    entity_batches = func(
                        task,
                        nifi_context,
                        entity_batches,
                        processor_name,
                        *args,
                        **kwargs,
                    )
                    return nifi_context.send_output(entity_batches, processor_name)

            serialized_func = celery_executor.serialized_io(nifi_func)
            task_func = celery_executor.app.task(*args, **opts)(serialized_func)
            return task_func

        return decorator
