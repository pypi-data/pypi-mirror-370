import streamlit as st

from octostar_streamlit.desktop import get_open_workspace_ids
from octostar.utils.ontology import query_ontology
from octostar.utils.workspace.permissions import get_permissions, PermissionLevel


def get_workspaces(client, prev_workspaces=None, include_closed=False):
    if not include_closed:
        workspace_ids = get_open_workspace_ids()
    else:
        workspace_ids = [
            w["os_entity_uid"]
            for w in client.execute(
                query_ontology.sync,
                f"SELECT `os_entity_uid` FROM `dtimbr`.`os_workspace`",
            )
        ]
    if not workspace_ids and prev_workspaces is not None:
        return prev_workspaces
    if not workspace_ids:
        st.stop()
    workspace_ids = ", ".join(
        ["'" + workspace_id + "'" for workspace_id in workspace_ids]
    )
    workspaces = client.execute(
        query_ontology.sync,
        f"SELECT `entity_label`, `os_entity_uid` FROM `dtimbr`.`os_workspace` WHERE `os_entity_uid` IN ({workspace_ids})",
    )
    workspaces_permissions = client.execute(
        get_permissions.sync, [w["os_entity_uid"] for w in workspaces]
    )
    workspaces = {
        workspace["os_entity_uid"]: {
            **workspace,
            "os_permission": workspaces_permissions.get(
                workspace["os_entity_uid"], PermissionLevel.NONE
            ),
        }
        for workspace in workspaces
    }
    return dict(
        filter(
            lambda x: x[1]["os_permission"] > PermissionLevel.NONE, workspaces.items()
        )
    )
