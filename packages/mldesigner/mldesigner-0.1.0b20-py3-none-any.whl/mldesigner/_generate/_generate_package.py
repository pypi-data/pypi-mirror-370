# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Union

from mldesigner._exceptions import UserErrorException
from mldesigner._logger_factory import _LoggerFactory

generate_pkg_logger = _LoggerFactory.get_logger("generate")


def generate(
    *,
    source: Union[list, dict, str],
    package_name: str = None,
    force_regenerate: bool = False,
    **kwargs,
) -> None:
    """For a set of source assets, generate a python module which contains component consumption functions and import
    it for use.

    Supported source types:
       - components: component consumption functions


    :param source: List[source_identifier], dict[module_relative_path, List[source_identifier]] or str

        * None: we will generate a module with ml_client.from_config() if source not specified, not supported for now.

        * list example: specify as source pattern list and we will generate modules

            .. code-block:: python

                # workspace source assets, module name will be workspace name
                source = ["azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group}/
                          workspaces/{workspace_name}"]

                # registry source assets, module name will be registry name
                source = ["azureml://registries/HuggingFace"]

                # local source assets, module name will be "components"
                source = ["components/**/component_spec.yaml"]

        * dict example: component module name relative path as key and List[source_identifier] as value

            .. code-block:: python

                # module name with a source identifier
                source = {"path/to/component/module": "azureml://subscriptions/{subscription_id}/"
                                         "resourcegroups/{resource_group}/workspaces/{workspace_name}"}
                # module name with a list of source identifier
                source = {"path/to/component/module": ["azureml://subscriptions/{subscription_id}/"
                                          "resourcegroups/{resource_group}/workspaces/{workspace_name}",
                                          "components/**/component_spec.yaml"]}

        * str example: mldesigner.yaml, config file which contains the source dict

        .. note::

            module_relative_path: relative path of generate component module
                * When package name not provided, component module name relative path will relative to current folder
                * When package name is provided, component module name relative path will relative to
                  generated package folder
            components: single or list of glob string which specify a set of components. Example values:
                * source assets from workspace
                    1. all source assets
                        ``azureml://subscriptions/{subscription_id}/resource_group/{resource_group}/
                        workspaces/{workspace_name}``
                    2. components with name filter
                        ``azureml://subscriptions/{subscription_id}/resource_group/{resource_group}
                        /workspaces/{workspace_name}/components/microsoft_samples_*``
                * components from local yaml
                    ``components/**/component_spec.yaml``
                * components from registries
                    For registry concept, please see: `https://aka.ms/azuremlsharing`.
                    azureml://registries/HuggingFace  # All source assets in registry HuggingFace.
                    azureml://registries/HuggingFace/components/Microsoft*

    :type source: typing.Union[list, dict, str]
    :param package_name: name of the generated python package. Example: cool-component-package
        * If specified: we generate the module file to specified package.
            * If the cool-component-package folder does not exists, we will create a new skeleton package under
            ./cool-component-package and print info in command line and ask user to do:
            ``pip install -e ./cool-component-package``
            Then next user can do: 'from cool.component.package import component_func'
            * If the folder exists, we will try to update component folders inside .
        * If not specified, we generate the module directory under current directory.
    :type package_name: str
    :param force_regenerate: whether to force regenerate the python module file.
        * If True, will always regenerate component folder.
        * If False, will reuse previous generated file. If the existing file not valid, raise import error.
    :type force_regenerate: bool
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """
    # import locally so generate package interface don't depend on azure-ai-ml
    try:
        from mldesigner._generate._generate_package_impl import _generate
    except ImportError as e:
        err_msg = (
            "Please install generate extra dependencies by running `pip install mldesigner[pipeline]`, "
            f"currently got {e}"
        )
        raise UserErrorException(err_msg)

    return _generate(source=source, package_name=package_name, force_regenerate=force_regenerate, **kwargs)
