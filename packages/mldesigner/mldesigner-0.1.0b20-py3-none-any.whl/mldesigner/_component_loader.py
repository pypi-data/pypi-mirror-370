# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument
import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from omegaconf import OmegaConf

from mldesigner._exceptions import UserErrorException


@dataclass
class StructuredComponentLoaderConfig:
    default_version: Optional[str] = None  # noqa: E704
    force_version: Optional[str] = None  # noqa: E701
    post_load: Optional[str] = None
    use_local: Optional[str] = "*"


class Config:
    CONFIG_KEY = ""
    STRUCTURED_CONFIG = None

    def __init__(self, default_config_path=None, config_key=None):
        structured_config = (
            OmegaConf.structured(self.STRUCTURED_CONFIG) if self.STRUCTURED_CONFIG else OmegaConf.create({})
        )
        # only load from config if exists
        if default_config_path and Path(default_config_path).exists():
            default_config = OmegaConf.load(default_config_path)
            if config_key:
                default_config = default_config.get(config_key, {})
            self.default_config = OmegaConf.merge(
                OmegaConf.to_container(structured_config, resolve=True), default_config
            )
        else:
            self.default_config = structured_config

    @classmethod
    def convert_to_absolute_path(cls, config, conf_keys, config_path):
        """
        Convert relative path to absolute path in the config.

        :param config: The config which need to be updated.
        :type config: DictConfig
        :param conf_keys: The config keys which need to be converted to absolute path in the config.
        :type conf_keys: List[str]
        :param config_path: Config file path.
        :type config_path: str or Path
        """
        config_parent_path = Path(config_path).parent
        for key in conf_keys:
            if OmegaConf.select(config, key):
                OmegaConf.update(config, key, (config_parent_path / config[key]).absolute().as_posix())


class ComponentsConfig(Config):
    CONFIG_KEY = "components"
    PATH_KEY = "path"
    NAME_KEY = "name"
    VERSION_KEY = "version"
    REGISTRY_KEY = "registry"

    def __init__(self, default_config_path=None, config_key=None):
        super(ComponentsConfig, self).__init__(default_config_path, config_key)
        if default_config_path:
            # Convert yaml path to absolute path.
            for _, component_config in self.default_config.items():
                self.convert_to_absolute_path(component_config, [self.PATH_KEY], default_config_path)

    @classmethod
    def create_single_component_config(cls, key, name=None, path=None, registry=None, version=None):
        """Create a component config which only contains one component config with key."""
        component_config = {
            # config items can not be object type translate to string.
            cls.PATH_KEY: Path(path).resolve().absolute().as_posix() if path else None,
            cls.NAME_KEY: name,
            cls.VERSION_KEY: version,
            cls.REGISTRY_KEY: registry,
        }
        component_config = {key: val for key, val in component_config.items() if val is not None}
        components_config = OmegaConf.create({key: component_config})
        return components_config


class ComponentLoaderConfig(Config):
    CONFIG_KEY = "component_loader"
    POST_LOAD_KEY = "post_load"
    STRUCTURED_CONFIG = StructuredComponentLoaderConfig

    def __init__(self, default_config_path, config_key):
        super(ComponentLoaderConfig, self).__init__(default_config_path, config_key)
        self._validate_use_local(self.default_config)

    @staticmethod
    def _validate_use_local(config):
        error_format = False
        if "use_local" not in config:
            use_local = "*"
        elif not config.use_local:
            use_local = None
        elif config.use_local == "*":
            use_local = "*"
        else:
            use_local = config.use_local
            if isinstance(use_local, str):
                use_local = [x.strip() for x in config.use_local.split(",")]
            if not use_local or not isinstance(use_local, list) or not all(use_local):
                error_format = True
            else:
                # Check use_local syntax valid, all items are prefixed by ! or not.
                is_other_local = use_local[0].startswith("!")
                error_format = not all([not (item.startswith("!") ^ is_other_local) for item in use_local])

        if error_format:
            raise UserErrorException(
                "Invalid value for `use_local`. Please follow one of the four patterns: \n"
                '1) use_local="", all components are remote\n'
                '2) use_local="*", all components are local\n'
                '3) use_local="COMPONENT_KEY_1, COMPONENT_KEY_2", only COMPONENT_KEY_1, COMPONENT_KEY_2 are local, '
                "everything else is remote\n"
                '4) use_local="!COMPONENT_KEY_1, !COMPONENT_KEY_2", '
                "all except for COMPONENT_KEY_1, COMPONENT_KEY_2 are local"
            )
        return use_local


class ComponentLoader:
    """
    Load component in different ways through the config.
    ComponentLoader exposes two public methods set_override_config and load_component.
    set_override_config is a class method, it's used to set the override config when loading the component.
    load_component is used to load the component in different ways(local, workspace, registry).

    The component loader provides the following features:
        - Determine the component to be loaded remotely or locally through the component config loader
        - Modify the runsettings of a specific type of component after the component loaded
        - Execute user-defined function after the component loaded.

    Example of loading component by ComponentLoader:
    .. code-block:: python
        # Init component loader
        component_loader = ComponentLoader(default_component_config_path)
        # Load the component by name
        component_func = component_loader.load_component(name=<component name>)
        # Create component
        component = component_func()

        # The post function is executed after component loaded.
        def post_load_func(component: azure.ml.component.Component):
            # Update component runsettings after loading.
            component.runsettings.resource_layout.node_count = 1

    Example of component config and component loader config:
    .. code-block:: yaml
        components:
          component1:
            name: my_component
            version: component_version
            registry: test_registry
            path: ../components/my_component/component_version/component1.spec.yaml
        component_loader:
          use_local: '*'
          post_load: <module_name>:<function_name>
    """

    _override_components_config = None
    _override_component_loader_config = None

    def __init__(self, components_config, default_component_loader_config_path):
        """
        Init component loader.

        :param components_config: The default component config.
        :param components_config: ComponentsConfig
        :param default_component_loader_config_path: Default component loader config path
        :type default_component_loader_config_path: str or Path
        """
        self._components_config = components_config

        self._file_components_config = ComponentsConfig(
            default_config_path=default_component_loader_config_path, config_key=ComponentsConfig.CONFIG_KEY
        ).default_config

        self._component_loader_config = ComponentLoaderConfig(
            default_config_path=default_component_loader_config_path, config_key=ComponentLoaderConfig.CONFIG_KEY
        ).default_config

    @staticmethod
    def _get_post_component_load_func(component_loader_config):
        """
        Get the user defined post_component_load function from component loader config.

        :param component_loader_config: Component loader config
        :type component_loader_config: DictConfig
        :return: post_component_load function
        :rtype: func
        """
        post_load_func_name = component_loader_config.get(ComponentLoaderConfig.POST_LOAD_KEY, None)
        if post_load_func_name:
            if ":" not in post_load_func_name:
                raise UserErrorException(
                    "Wrong format of post_load in the component loader config, "
                    "please use <module_name>:<post_load_func_name>"
                )
            module_name, func_name = post_load_func_name.rsplit(":", 1)
            try:
                module = importlib.import_module(module_name)
                return getattr(module, func_name)
            except Exception as e:
                raise UserErrorException(
                    f'Cannot import the post component load function "{func_name}"' f' from the module "{module_name}"'
                ) from e
        else:
            return None

    @staticmethod
    def is_load_component_from_local(component_name, component_loader_config):
        """
        Check whether the component is loaded from local.

        use_local="", all components are remote'
        use_local="*", all components are local
        use_local="component1, component2", only component1, component2 are local, everything else is remote
        use_local="!component1, !component2", all except for component1, component2 are local
        Throw exceptions in other situations

        :param component_name: Component name
        :param component_loader_config: Component loader config.
        :return: Whether component load from local.
        :rtype: bool
        """
        # pylint: disable=protected-access
        use_local = ComponentLoaderConfig._validate_use_local(component_loader_config)
        if not use_local:
            # If use_local='', all components will be loaded from remote.
            return False
        if isinstance(use_local, str) and use_local == "*":
            # If use_local='*', all components will be loaded from local.
            return True
        if use_local[0].startswith("!"):
            # If !component_name in use_local, the component will be loaded from remote.
            return f"!{component_name}" not in use_local

        # If component name in use_local, the component will be loaded from local.
        return component_name in use_local

    @classmethod
    def _load_component_by_config(cls, component_name, component_config, component_loader):
        """
        Load component by component loader config.

        If the component_name is specified from local, it will use component yaml to load component.
        If the component_name is specified from remote, it will first use workspace/registry id to load if id exists.
        Then, if name and version exists, it will use default workspace to load component.
        If only name exists, it will load default version from default workspace.

        :param component_name: Component name
        :type component_name: str
        :param component_config: Component config
        :type component_config: DictConfig
        :param component_loader: Config of component loader
        :type component_loader: DictConfig

        :return: Component entity or component id
        :rtype: azure.ai.ml.entities.Component or str
        """
        from mldesigner._azure_ai_ml import load_component

        if (
            cls.is_load_component_from_local(component_name, component_loader)
            and ComponentsConfig.PATH_KEY in component_config
        ):
            # Load component by yaml file.
            component = load_component(source=component_config.path)
        elif "version" in component_config:
            # Load component by component name and version.
            default_version = (
                component_loader.get("force_version")
                or component_config.get("version")
                or component_loader.get("default_version")
            )
            if "registry" in component_config:
                component = f"azureml://registries/{component_config.registry}" \
                            f"/components/{component_config.name}/versions/{default_version}"
            else:
                component = f"{component_config.name}:{default_version}"
        elif "name" in component_config:
            component = component_config.name
        else:
            raise UserErrorException("Cannot load component through the component config.")
        return component

    @classmethod
    def set_override_config(cls, components_config=None, component_loader_config=None):
        """
        Set the override config when loading component.

        It will set component config and component loader config to the override config of ComponentLoader.
        Override config of ComponentLoader has higher priority than the object config.
        When loading the component, it will first use override config.

        :param components_config: Override component config
        :type components_config: DictConfig
        :param component_loader_config: Override config of component loader
        :type component_loader_config: DictConfig
        """
        cls._override_component_loader_config = component_loader_config
        cls._override_components_config = components_config

    def load_component(self, name):
        """
        Load the component by name.

        It will use the name to get the config of the component and component loader.
        Then it will use these configs to load the components. Override config of ComponentLoader has higher priority
        than the default config. If not found override config, it will use the default config to load the component.


        :param name: The name of the component to be loaded
        :type name: str
        :return: Component definition
        :rtype: Union[azure.ai.ml.entities.Component, str]
        """
        if self._override_components_config:
            # If override config exists, use override config to load component.
            component_config = self._override_components_config.get(name) or self._components_config.get(name)
        elif self._file_components_config.get(name):
            # If override config does not exist, use default config to load component.
            component_config = self._file_components_config.get(name)
        else:
            # Otherwise, use the component config from the component loader config.
            component_config = self._components_config.get(name)
        if not component_config:
            raise UserErrorException(f"Cannot find {name} in the components config.")

        # Get the component function by config
        component_loader_config = self._override_component_loader_config or self._component_loader_config
        return self._load_component_by_config(name, component_config, component_loader_config)

    def apply_post_load_func(self, node):
        """
        Apply post load function to the node if specified in config.

        :param node: Node object inside pipeline.
        :return: node object after post load function applied.
        """

        component_loader_config = self._override_component_loader_config or self._component_loader_config
        post_component_load_func = self._get_post_component_load_func(component_loader_config)
        if post_component_load_func:
            try:
                # Execute user defined function after component load.
                post_component_load_func(node)
            except Exception as e:
                raise UserErrorException(f"Post component load func failed. {e}")
        return node
