# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import concurrent.futures
import logging
from itertools import islice
from typing import List, Tuple

from tqdm.auto import tqdm

from mldesigner._azure_ai_ml import Component
from mldesigner._utils import update_logger_level


class ComponentOperations:
    """This class is added to mldesigner because list_component_versions has extra dependency tqdm."""

    def __init__(self, operations: "CoreComponentOperations"):
        self.operations = operations

    def list_component_versions(self, max_result=None) -> Tuple[List[Component], List[str]]:
        """List all component latest versions in current workspace/registry.

        For each component container, the latest component version will be returned.
        """
        containers = list(islice(self.operations.list(), max_result))
        desc = "Listing components in '{}'".format(self.operations._registry_name or self.operations._workspace_name)
        # set root logger level to CRITICAL to avoid logs during update of progress bar
        with tqdm(total=len(containers), desc=desc, unit="component", position=0) as progress_bar, update_logger_level(
            logging.CRITICAL
        ):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(self.operations._get_latest_version, c.name): c.name for c in containers}

            components = []
            warnings = []
            for future in concurrent.futures.as_completed(futures):
                progress_bar.update(1)
                name = futures[future]
                try:
                    component = future.result()
                    components.append(component)
                # pylint: disable=broad-except
                except Exception as e:
                    # only catch Exception to allow KeyboardInterrupt
                    warnings.append(f"Failed to load {name} due to {e}")
        return components, warnings
