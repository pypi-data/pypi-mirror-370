# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# cspell: ignore wsid, graphid

import re

from mldesigner._exceptions import UserErrorException


def _get_entry_index_value(entries, index):
    if len(entries) >= index + 1:
        return entries[index]
    return None


def _parse_designer_url(url: str):
    """
    assume there are only 7 kinds of valid url
    draft: /Normal/{draft_id}?wsid=/subscriptions/{sub_id}/resourcegroups/{rg}/workspaces/{ws}
    run: /pipelineruns/id/{exp_id}/{run_id}?wsid=/subscriptions/{sub_id}/resourcegroups/{rg}/workspaces/{ws}
    run: /pipelineruns/{exp_name}/{run_id}?wsid=/subscriptions/{sub_id}/resourcegroups/{rg}/workspaces/{ws}
    run: /runs/{run_id}?wsid=/subscriptions/{run_id}/resourcegroups/{rg}/workspaces/{ws}
    sub_graph: /runs/{run_id}?subscriptions/{run_id}/resourcegroups/{rg}/workspaces/{ws}/{node_id}?graphid={graphid}
    endpoint: /endpoint/{endpoint_id}/xxx
    published pipeline: /endpoint/{endpoint_id}/xxx/publishedpipeline/{published_pipeline_id}
    """
    entries = re.split(r"[/&?]", url)
    subscription_id = None
    resource_group = None
    workspace_name = None
    draft_id = None
    run_id = None
    endpoint_id = None
    published_pipeline_id = None

    for i, entry in enumerate(entries):
        entry = entry.lower()
        if entry == "runs":
            run_id = _get_entry_index_value(entries, i + 1)
        elif entry == "pipelineruns":
            if _get_entry_index_value(entries, i + 1) == "id":
                run_id = _get_entry_index_value(entries, i + 3)
            else:
                run_id = _get_entry_index_value(entries, i + 2)
        elif entry == "normal":
            draft_id = _get_entry_index_value(entries, i + 1)
        elif entry == "subscriptions":
            subscription_id = _get_entry_index_value(entries, i + 1)
        elif entry == "resourcegroups":
            resource_group = _get_entry_index_value(entries, i + 1)
        elif entry == "workspaces":
            workspace_name = _get_entry_index_value(entries, i + 1)
        elif entry == "endpoint":
            endpoint_id = _get_entry_index_value(entries, i + 1)
        elif entry == "publishedpipeline":
            published_pipeline_id = _get_entry_index_value(entries, i + 1)

    if draft_id is None and run_id is None and endpoint_id is None and published_pipeline_id is None:
        raise UserErrorException("Invalid url. No draft_id, run_id, endpoint_id, published_pipeline_id found.")

    if subscription_id is None or resource_group is None or workspace_name is None:
        raise UserErrorException("Invalid url. No subscription_id, resource_group or workspace_name found")

    return (
        subscription_id,
        resource_group,
        workspace_name,
        draft_id,
        run_id,
        endpoint_id,
        published_pipeline_id,
    )
