# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=no-name-in-module,import-error

import logging
import os
import re
from collections import OrderedDict
from pathlib import Path

from pydash import get

from azure.ml.component._pipeline_validator import CycleValidator, _ModuleNode
from azure.ml.component._restclients.designer.models import ComputeSetting, ModuleDto, ParameterType, PipelineGraph
from azure.ml.component._util._utils import _sanitize_python_variable_name
from azure.ml.component.dsl._graph_2_code._code_generator import (
    PIPELINE_IDENTIFIER_TRIM_LEN,
    CodeFileHeaderGenerator,
    DesignerServiceCaller,
    GraphPackageUtil,
    NotebookGenerator,
)
from azure.ml.component.dsl._graph_2_code._code_generator import PipelineCodeGenerator as V1PipelineCodeGenerator
from azure.ml.component.dsl._graph_2_code._code_generator import PipelinePackageGenerator as V1PipelinePackageGenerator
from azure.ml.component.dsl._graph_2_code._code_generator import (
    Run,
    RunScript,
    TaskQueue,
    TimerContext,
    get_new_dir_name_if_exists,
)
from azure.ml.component.dsl._graph_2_code._component_node_generator import ComponentCodeGenerator, ControlCodeGenerator
from azure.ml.component.dsl._graph_2_code._utils import DataUtil
from azure.ml.component.dsl._graph_2_code._utils import GraphUtil as V1GraphUtil
from azure.ml.component.dsl._graph_2_code._utils import (
    _equal_to_enum_val,
    _get_list_attr_with_empty_default,
    _get_module_file_name,
    _get_pipeline_identifier,
    _normalize_string_param_val,
)
from mldesigner._compare._compare import az_ml_logger


class V2CycleValidator(CycleValidator):
    @staticmethod
    def _construct_graph_from_dto(pipeline_steps, edges):
        graph_nodes = {n.id: _ModuleNode(n.id, [], []) for n in pipeline_steps}
        for e in edges or []:
            source_node = graph_nodes.get(e.source_output_port.node_id)
            target_node = graph_nodes.get(e.destination_input_port.node_id)
            if source_node and target_node:
                source_node.outputs.append(
                    (e.source_output_port.port_name, f"{target_node.node_id}.{e.destination_input_port.port_name}")
                )
                target_node.inputs.append(
                    (e.destination_input_port.port_name, f"{source_node.node_id}.{e.source_output_port.port_name}")
                )

            if source_node and not target_node:
                if e.destination_input_port.graph_port_name:
                    # no target node means this node has pipeline level output
                    graph_port_name = e.destination_input_port.graph_port_name
                    source_node.outputs.append((e.source_output_port.port_name, f"parent.{graph_port_name}"))
            if target_node and not source_node:
                if e.source_output_port.graph_port_name:
                    graph_port_name = e.source_output_port.graph_port_name
                    # no source node means this node has pipeline level input
                    target_node.inputs.append((e.destination_input_port.port_name, f"parent.{graph_port_name}"))
        return list(graph_nodes.values())


class GraphUtil(V1GraphUtil):  # pylint: disable=too-many-instance-attributes
    def _get_pipeline_param_2_actual_val(self):  # pylint: disable=too-many-statements
        # mapping from python name to count
        py_name_count = {}
        # mapping from pipeline param to py name
        pipeline_param_2_py_name = {}
        # mapping from py name to actual val
        pipeline_params_2_actual_val = {}

        def get_unique_py_name(param_name):
            # Returns unique python name for param_name
            candidate = _sanitize_python_variable_name(param_name)
            if candidate not in py_name_count.keys():
                py_name_count[candidate] = 1
            else:
                count = py_name_count[candidate] + 1
                py_name_count[candidate] = count
                candidate += f"_{count}"
            pipeline_param_2_py_name[param_name] = candidate
            return candidate

        # parameters
        for param in _get_list_attr_with_empty_default(self.graph.entity_interface, "parameters"):
            py_name = get_unique_py_name(param.name)
            if param.default_value == "":
                # unprovided optional pipeline param's default value will be "", set None for that case
                pipeline_params_2_actual_val[py_name] = None
            elif (
                _equal_to_enum_val(param.type, ParameterType.INT)
                or _equal_to_enum_val(param.type, ParameterType.DOUBLE)
                or _equal_to_enum_val(param.type, ParameterType.BOOL)
            ):
                pipeline_params_2_actual_val[py_name] = param.default_value
            else:
                pipeline_params_2_actual_val[py_name] = _normalize_string_param_val(param.default_value)

        # data parameters
        for param in _get_list_attr_with_empty_default(self.graph.entity_interface, "data_path_parameter_list"):
            py_name = get_unique_py_name(param.name)
            if get(param, "default_value.data_set_reference", None) is None:
                # Override 1.5 generate tool to compare v2 run after remove data access mode setting
                dataset_id = get(param, "default_value.asset_definition.asset_id", None)
                dataset_version = re.findall('versions/([^/&?}\n"]+)', dataset_id) if dataset_id else None
                # pylint: disable=unsubscriptable-object
                dataset_version = dataset_version[0] if dataset_version else None
            else:
                dataset_id = get(param, "default_value.data_set_reference.id", None)
                dataset_version = get(param, "default_value.data_set_reference.version", None)
            saved_dataset_id = get(param, "default_value.saved_data_set_reference.id", None)
            relative_path = get(param, "default_value.literal_value.relative_path", None)
            if not saved_dataset_id:
                # the saved dataset id is not record in the DataPathParameterList, try to retrieve from DataSource
                if not dataset_version:
                    # the dataset version is also null, just find the dataset with the same Id
                    matched_datasource = next((d for d in self.graph.graph_data_sources if d.id == dataset_id), None)
                    if matched_datasource:
                        dataset_version = matched_datasource.dataset_version_id
                        saved_dataset_id = matched_datasource.saved_dataset_id
                else:
                    matched_datasource = next(
                        (
                            d
                            for d in self.graph.graph_data_sources
                            if (d.id == dataset_id and d.dataset_version_id == dataset_version)
                        ),
                        None,
                    )
                    if matched_datasource:
                        saved_dataset_id = matched_datasource.saved_dataset_id

            dataset_key = DataUtil.get_dataset_mapping_key(dataset_id, saved_dataset_id, dataset_version, relative_path)

            if dataset_key not in self.dataset_id_2_name.keys():
                if saved_dataset_id:
                    pipeline_params_2_actual_val[
                        py_name
                    ] = f"Dataset.get_by_id({self.workspace_name}, '{saved_dataset_id}')"
                    # pylint: disable=attribute-defined-outside-init,unrecognized-inline-option
                    self.used_dataset = True
                elif dataset_id:
                    pipeline_params_2_actual_val[py_name] = f"Dataset.get_by_id({self.workspace_name}, '{dataset_id}')"
                    # pylint: disable=attribute-defined-outside-init,unrecognized-inline-option
                    self.used_dataset = True
                else:
                    # Override 1.5 generate tool to compare v2 run to deal with linking empty data box (optional and
                    # default value is None)
                    az_ml_logger.warning(
                        "Unknown DataSetPathParameter %s. datasetId:%s, savedDatasetId:%s, " "version:%s",
                        param.name,
                        dataset_id,
                        saved_dataset_id,
                        dataset_version,
                    )
            else:
                pipeline_params_2_actual_val[py_name] = self.dataset_id_2_name[dataset_key]

        # input ports
        inputs = _get_list_attr_with_empty_default(self.graph.entity_interface, "ports.inputs")
        for input_port in inputs:
            py_name = get_unique_py_name(input_port.name)
            pipeline_params_2_actual_val[py_name] = None
        return pipeline_param_2_py_name, pipeline_params_2_actual_val


class PipelineCodeGenerator(V1PipelineCodeGenerator):  # pylint: disable=too-many-instance-attributes
    # Override 1.5 PipelineCodeGenerator init to call overridden GraphUtil

    def __init__(
        self,
        graph: PipelineGraph,
        pkg_util: GraphPackageUtil,
        logger,
        definition: ModuleDto = None,
        is_root=False,
        module_name=None,
        run: Run = None,
        header: str = None,
        **kwargs,
    ):
        super(V1PipelineCodeGenerator, self).__init__(logger=logger, **kwargs)  # pylint: disable=bad-super-call
        # TODO(1548752): change interface, url, install commands, module name, display name, etc

        self.util = GraphUtil(graph, pkg_util, definition)
        self.pkg_util = pkg_util
        self._is_root = is_root
        self._experiment_name = self.DEFAULT_EXPERIMENT_NAME if not run else run.experiment.name
        self.header = header if header else CodeFileHeaderGenerator(logger=logger).to_component_entry_code()
        if is_root:
            self.definition = None
            self.name = self.DEFAULT_PIPELINE_NAME if not run else _get_pipeline_identifier(run)
            self.description = None
            self.module_name = self.DEFAULT_MODULE_NAME if not module_name else module_name
            self._pipeline_func_name = _sanitize_python_variable_name(self.name)
            self.target_file = _get_module_file_name(self.module_name)
            self._pipeline_runsettings = self.get_pipeline_runsettings()
        else:
            if not definition:
                raise RuntimeError("Definition is required for sub pipeline.")
            self.definition = definition
            self.name = definition.module_name
            self.description = definition.description
            self.module_name = self.pkg_util.component_id_2_module_name[self.definition.module_version_id]
            self._pipeline_func_name = self.pkg_util.component_id_2_func_name[self.definition.module_version_id]
            # sub graphs will be generated in Subgraph folder
            self.target_file = os.path.join(
                self.pkg_util.SUBGRAPH_PACKAGE_NAME, _get_module_file_name(self.module_name)
            )
            self._pipeline_runsettings = {}

        self._workspace_name = self.util.workspace_name

        self._node_generators = [
            *[ComponentCodeGenerator(node, self.util, self.logger) for node in self.util.sorted_nodes],
            *[ControlCodeGenerator(node, self.util, self.logger) for node in self.util.node_id_2_control.values()],
        ]

        self._graph_nodes = self._calculate_graph_nodes()

        # Mapping from global dataset name to def
        self._global_datasets = self.util.global_dataset_py_name_2_def

        # Mapping from user dataset name to def
        self._user_datasets = self.util.user_dataset_py_name_2_def

        # Mapping from component func name to module version id
        self._anonymous_components_2_def = OrderedDict()
        # Mapping from component func name to component definition
        self._global_components_2_def = OrderedDict()
        # Mapping from component func name to component definition
        self._custom_components_2_def = OrderedDict()
        # Mapping from component func name to it's module name
        self._sub_pipeline_func_name_2_module = OrderedDict()
        # Mapping from generated component func name to it's module name
        self._generated_component_func_2_module = OrderedDict()
        self._get_components()

    def _calculate_graph_nodes(self):
        nodes = V2CycleValidator._construct_graph_from_dto(  # pylint: disable=protected-access
            self.util.all_nodes, self.util.graph.edges
        )
        return {node.node_id: node for node in nodes}


class PipelinePackageGenerator(V1PipelinePackageGenerator):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        service_caller: DesignerServiceCaller,
        root_graph: PipelineGraph,
        url: str,
        pipeline_identifier: str,
        include_components: str = None,
        target_dir=None,
        root_run: Run = None,
        description: str = None,
        tags: str = None,
        display_name: str = None,
        pipeline_name=None,
    ):
        self.url = url
        self.service_caller = service_caller
        self.logger = az_ml_logger
        self.pipeline_identifier = pipeline_identifier
        self.description = description
        self.tags = tags
        self.display_name = display_name
        self.root_run = root_run
        # Override 1.5 PipelinePackageGenerator init to deal with v2 run root_graph.default_compute is None
        if isinstance(root_graph, PipelineGraph) and root_graph.default_compute is None:
            root_graph.default_compute = ComputeSetting()

        self.default_compute_target = root_graph.default_compute.name
        try:
            self.continue_on_step_failure = root_run.properties["azureml.continue_on_step_failure"]
        except AttributeError:
            self.continue_on_step_failure = None
        if not pipeline_name:
            pipeline_name = self.pipeline_identifier
        self.pipeline_name = pipeline_name

        if not target_dir:
            target_dir = self.pipeline_identifier[:PIPELINE_IDENTIFIER_TRIM_LEN]
            self.target_dir = get_new_dir_name_if_exists(Path(target_dir))
        else:
            self.target_dir = Path(target_dir)
        az_ml_logger.debug("Generating code in %s", self.target_dir)

        self.workspace = self.service_caller._workspace
        # Mapping from graph id to graph entity
        self.graph_id_2_entity = {}
        # Mapping from graph id to definition
        self.graph_id_2_definition = {}

        self._get_graphs_for_anonymous_pipeline_components(root_graph)
        self.graphs = list(self.graph_id_2_entity.values())
        self.graphs.append(root_graph)
        # update None edge port name to empty string to mitigate AttributeError: 'NoneType' object has no attribute
        # 'lower'
        for graph in self.graphs:
            for edge in graph.edges:
                if edge.destination_input_port.port_name is None:
                    edge.destination_input_port.port_name = ""
                if edge.source_output_port.port_name is None:
                    edge.source_output_port.port_name = ""
        self.pkg_util = GraphPackageUtil(self.graphs, include_components=include_components, logger=self.logger)
        self._components_dir = self.target_dir / self.pkg_util.COMPONENT_PACKAGE_NAME
        self._pipelines_dir = self.target_dir / self.pkg_util.PIPELINE_PACKAGE_NAME
        self._sub_pipeline_dir = self._pipelines_dir / self.pkg_util.SUBGRAPH_PACKAGE_NAME
        self.run_script_path = self.target_dir / RunScript.TARGET_FILE

        self._file_header_generator = CodeFileHeaderGenerator(url=self.url, logger=self.logger)
        file_header = self._file_header_generator.to_component_entry_code()
        self._subgraph_generators = [
            PipelineCodeGenerator(
                graph,
                self.pkg_util,
                definition=self.graph_id_2_definition[id],
                run=self.root_run,
                header=file_header,
                logger=self.logger,
            )
            for id, graph in self.graph_id_2_entity.items()
        ]
        self._root_graph_generator = PipelineCodeGenerator(
            root_graph,
            self.pkg_util,
            is_root=True,
            module_name=self.pipeline_identifier,
            run=self.root_run,
            header=file_header,
            logger=self.logger,
        )

        self._run_generator = RunScript(
            root_pipeline_generator=self._root_graph_generator,
            header=file_header,
            run=self.root_run,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
            continue_on_step_failure=self.continue_on_step_failure,
            default_compute_target=self.default_compute_target,
        )
        self._notebook_generator = NotebookGenerator(
            root_pipeline_generator=self._root_graph_generator,
            url=self.url,
            run=self.root_run,
            description=self.description,
            tags=self.tags,
            display_name=self.display_name,
            continue_on_step_failure=self.continue_on_step_failure,
            default_compute_target=self.default_compute_target,
        )

    def _get_graphs_for_anonymous_pipeline_components(self, root_graph: PipelineGraph):
        self.logger.info("Fetching subgraph info for %s...", self.pipeline_name)
        with TimerContext() as timer_context:
            # Create a separate logger here since we don't want debug info show in console.
            logger = logging.getLogger("get_sub_graphs")
            with TaskQueue(_parent_logger=logger) as task_queue:

                def _get_graphs_recursively(graph_id, graph_definition=None, graph=None):
                    if graph is None:
                        graph = self.service_caller._get_pipeline_component_graph(  # pylint: disable=protected-access
                            graph_id=graph_id, skip_dataset_load=False
                        )
                        self.graph_id_2_entity[graph_id] = graph
                        self.graph_id_2_definition[graph_id] = graph_definition
                    subgraph_module_id_2_graph_id = {n.module_id: n.graph_id for n in graph.sub_graph_nodes}
                    for dto in graph.graph_module_dtos:  # cspell: ignore dtos
                        component_id = dto.module_version_id
                        # Override 1.5 generate tool to not only fetch anonymous subgraph like 1.5, v2 will register
                        # subgraph
                        if component_id in subgraph_module_id_2_graph_id.keys() and dto.job_type in (
                            "PipelineComponent",
                            "pipeline",
                        ):
                            graph_id = subgraph_module_id_2_graph_id[component_id]
                            if not graph_id:
                                graph_id = dto.module_entity.cloud_settings.sub_graph_config.graph_id
                            # Note: this may run multiple time for same sub graph if they share same graph id
                            if graph_id not in self.graph_id_2_entity.keys():
                                task_queue.add(_get_graphs_recursively, graph_id, dto)

                _get_graphs_recursively(graph_id=None, graph=root_graph)
                # Note: we added tasks that will dynamically add tasks to task queue
                # so we need to flush task queue until it has no tasks left
                while not task_queue._tasks.empty():  # pylint: disable=protected-access
                    task_queue.flush(source="iter_files_in_parallel")
        self.logger.info("Finished fetch subgraph info in %s seconds.", timer_context.get_duration_seconds())
