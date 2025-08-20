# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
from pathlib import Path
from typing import List

from mldesigner._azure_ai_ml import Command, MLClient, Parallel, Pipeline, Spark, Sweep
from mldesigner._exceptions import UserErrorException
from mldesigner._export._parse_url import _parse_designer_url
from mldesigner._generate._generators.pipeline_generator import PipelineCodeGenerator
from mldesigner._utils import (
    AMLLabelledArmId,
    AMLVersionedArmId,
    _is_arm_id,
    _is_name_label,
    _is_name_version,
    get_credential_auth,
    parse_name_version,
)


def _get_component_from_component_str(client, component_str, node_name):
    """Process component str of different format and get component.

    :param client: MLClient, use MLClient.components.get() to get component.
    :param component_str: Used to extract component name and version/label.
        Current code can process component_str of AMLVersionedArmId, name:version and AMLLabelledArmId.
    :param node_name: Used to construct error message when component_str is invalid.
    :return:
    """
    if _is_arm_id(component_str):
        arm_id = AMLVersionedArmId(component_str)
        return client.components.get(name=arm_id.asset_name, version=arm_id.asset_version)
    if _is_name_version(component_str):
        asset_name, asset_version = parse_name_version(component_str)
        return client.components.get(name=asset_name, version=asset_version)
    if _is_name_label(component_str):
        arm_id = AMLLabelledArmId(component_str)
        return client.components.get(name=arm_id.asset_name, label=arm_id.asset_label)
    raise UserErrorException(
        f"""The component:{component_str} of node {node_name} is invalid.
        Current code suport component str in the format of name:version, AMLVersionedArmId and AMLLabelledArmId."""
    )


async def _load_component_from_pipeline(client, job_entity):
    """Get the component of node in job_entity.jobs.
    :param client: MLClient, passed to _get_component_from_component_str to get component
    :param job_entity: Used to get the component of node in job_entity.jobs
        type: Union[PipelineJob, PipelineComponent]
    """
    name2component_dict = {}
    subgraph_components = {}
    subgraphs = {}
    for node in job_entity.jobs.values():  # pylint: disable=no-member
        # pylint: disable=unidiomatic-typecheck
        if isinstance(node, (Command, Parallel, Spark)):
            # TODO: modify here when node.component is not a string
            component_str = node.component
        elif isinstance(node, Sweep):
            component_str = node.trial
        elif isinstance(node, Pipeline):
            component_str = node.component
            subgraphs[node._instance_id] = node  # pylint: disable=protected-access
            component = _get_component_from_component_str(client, component_str, node.name)
            subgraph_components[component_str] = component
            # loop through _load_component_from_pipeline to get component of nodes in PipelineComponent.jobs
            subgraph_name2component_dict, sub_subgraph_components, sub_subgraphs = await _load_component_from_pipeline(
                client, component
            )
            name2component_dict.update(subgraph_name2component_dict)
            subgraph_components.update(sub_subgraph_components)
            subgraphs.update(sub_subgraphs)
            continue
        else:
            node_type = type(node)
            raise UserErrorException(
                f"""Generating code for pipeline with {node_type} node is not supported currently.
                Currently node type Command, Parallel, Spark, Sweep, Pipeline is supported."""
            )
        component = _get_component_from_component_str(client, component_str, node.name)
        name2component_dict[component_str] = component
    return name2component_dict, subgraph_components, subgraphs


def _export(source: str, include_components: List[str] = None):  # pylint: disable=unused-argument
    """Export pipeline source to code.

    :param source: Pipeline job source, currently supported format is pipeline run URL
    :param include_components: Included components to download snapshot.
        Use * to export all components,
        Or list of components used in pipeline.
        If not specified, all components in pipeline will be exported without downloading snapshot.
    :return:
    """
    # get subscription_id, resource_group, workspace_name, run_id from url
    (
        subscription_id,
        resource_group,
        workspace_name,
        draft_id,
        run_id,
        endpoint_id,
        published_pipeline_id,
    ) = _parse_designer_url(source)

    # validate: raise error when the job type is not pipeline job
    if draft_id:
        raise UserErrorException("Invalid url. Export pipeline draft is not supported.")
    if endpoint_id:
        raise UserErrorException("Invalid url. Export pipeline endpoint is not supported.")
    if published_pipeline_id:
        raise UserErrorException("Invalid url. Export published pipeline is not supported.")

    credential = get_credential_auth()
    # get pipeline entity
    client = MLClient(
        credential=credential,
        resource_group_name=resource_group,
        subscription_id=subscription_id,
        workspace_name=workspace_name,
    )
    job_entity = client.jobs.get(run_id)

    # validate: raise error when the PipelineJob.jobs contain no nodes
    if len(job_entity.jobs) == 0:
        raise UserErrorException("Unsupported Pipeline Job: failed to retrieve child jobs.")

    pattern_to_components, subgraph_components, subgraphs = asyncio.run(
        _load_component_from_pipeline(client, job_entity)
    )
    pipeline_code_generator = PipelineCodeGenerator(
        asset=source,
        pipeline_entity=job_entity,
        target_dir=Path("."),
        force_regenerate=False,
        pattern_to_components=pattern_to_components,
        pattern_to_pipeline_components=subgraph_components,
        pattern_to_subgraph_nodes=subgraphs,
    )
    pipeline_code_generator.generate(target_dir=Path(f"./{str(job_entity.display_name)}"))
