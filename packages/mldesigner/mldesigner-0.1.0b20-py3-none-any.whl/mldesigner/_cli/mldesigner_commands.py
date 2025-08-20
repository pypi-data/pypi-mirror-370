# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=line-too-long

import argparse
import sys

from mldesigner import generate
from mldesigner._compare._compare import compare
from mldesigner._compile._compile import compile as mldesigner_compile
from mldesigner._exceptions import UserErrorException
from mldesigner._execute._execute import _execute
from mldesigner._export._export import export
from mldesigner._utils import private_features_enabled


def _entry(argv):
    """
    CLI tools for mldesigner.
    """
    parser = argparse.ArgumentParser(
        prog="mldesigner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="A CLI tool for mldesigner. [Preview]",
    )

    subparsers = parser.add_subparsers()
    if private_features_enabled():
        add_parser_compare(subparsers)
        add_parser_export(subparsers)

    add_parser_generate(subparsers)
    add_parser_execute(subparsers)
    add_parser_compile(subparsers)

    args = parser.parse_args(argv)

    if args.action == "generate":
        generate(source=args.source, package_name=args.package_name, force_regenerate=args.force)

    elif args.action == "execute":
        processed_inputs = list_2_dict(args.inputs)
        processed_outputs = list_2_dict(args.outputs)
        _execute(source=args.source, name=args.name, inputs=processed_inputs, outputs=processed_outputs)

    elif args.action == "export":
        export(source=args.source, include_components=args.include_components)

    elif args.action == "compile":
        mldesigner_compile(
            source=args.source, name=args.name, output=args.output, ignore_file=args.ignore_file, debug=args.debug
        )

    elif args.action == "compare":
        diff_nodes = compare(
            job_url1=args.job_url1,
            job_url2=args.job_url2,
            target_file=args.target_file,
            debug=args.debug,
            reverse=args.reverse,
            flatten_list=args.flatten_list,
            non_skip=args.non_skip,
        )
        is_all_identical = all([diff_node.get("is_identical") for diff_node in diff_nodes])
        if is_all_identical:
            sys.exit(0)
        else:
            sys.exit(1)


def add_parser_compare(subparsers):  # add mldesigner compare for private preview
    """The parser definition of mldesigner compare"""

    epilog_compare = """
    Examples:

    # Compare graphs with url as input and judge whether two graphs are reused and identical.
    Graph compare detail will be stored in current folder as named "generated_diff_files.json"
    mldesigner compare --job_url1 ** --job_url2 **

    # Compare graphs with url as input and judge whether two graphs are reused and identical.
    Graph compare detail will be stored in target_file
    mldesigner compare --job_url1 ** --job_url2 ** --target_file **

    # Compare graphs with detailed debug information.
    mldesigner compare --job_url1 ** --job_url2 ** --debug

    # Compare graphs with reversed topological sorting.
    mldesigner compare --job_url1 ** --job_url2 ** --reverse

    # Compare graphs and output diff results with flatten list.
    mldesigner compare --job_url1 ** --job_url2 ** --flatten_list

    # Compare graphs and output diff results without skipping fields or modifying fields under specific rule if node
    isn't resused.
    mldesigner compare --job_url1 ** --job_url2 ** --non_skip
    """
    compare_parser = subparsers.add_parser(
        "compare",
        description="A CLI tool to compare graph.",
        help="Compare whether two pipeline graphs are identical, and record the difference. [Experimental]",
        epilog=epilog_compare,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    compare_parser.add_argument(
        "--job_url1",
        type=str,
        help="The first url of the pipeline run.",
    )
    compare_parser.add_argument(
        "--job_url2",
        type=str,
        help="The second url of the pipeline run.",
    )
    compare_parser.add_argument("--target_file", type=str, help="Path to export the graph compare detail.")
    compare_parser.add_argument(
        "--debug",
        action="store_true",
        help="Determines whether to show detailed debug information, default to be false.",
    )
    compare_parser.add_argument(
        "--reverse",
        action="store_true",
        help="Determines whether to compare graphs with reversed topological sorting, default to be false.",
    )
    compare_parser.add_argument(
        "--flatten_list",
        action="store_true",
        help="Determines whether to output diff results with flatten list, default to be false.",
    )
    compare_parser.add_argument(
        "--non_skip",
        action="store_true",
        help="Won't skip fields or modified fields under specific rule, default is False.",
    )
    compare_parser.set_defaults(action="compare")


def add_parser_generate(subparsers):
    """The parser definition of mldesigner generate"""

    epilog_generate = """
    Examples:

    # generate component functions for existing package
    mldesigner generate --source components/**/*.yaml

    # generate component functions from workspace
    mldesigner generate --source azureml://subscriptions/xxx/resourcegroups/xxx/workspaces/xxx

    # generate component functions from dynamic source
    mldesigner generate --source azureml://subscriptions/xxx/resourcegroups/xxx/workspaces/xxx components/**/*.yml

    # generate component functions from dynamic source, source configured in mldesigner.yml
    mldesigner generate --source mldesigner.yml

    # generate package from workspace
    mldesigner generate --source azureml://subscriptions/xxx/resourcegroups/xxx/workspaces/xxx --package-name my-cool-package
    """
    generate_parser = subparsers.add_parser(
        "generate",
        description="A CLI tool to generate component package.",
        help="For a set of source, generate a python module which contains component consumption functions and import it for use.",
        epilog=epilog_generate,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    generate_parser.add_argument(
        "--source",
        nargs="+",
        type=str,
        help="List of source need to be generated or path of source config yaml.",
    )
    generate_parser.add_argument("--package-name", type=str, help="Name of the generated python package.")
    generate_parser.add_argument(
        "--force", action="store_true", help="If specified, will always regenerate package from given source."
    )
    generate_parser.set_defaults(action="generate")


def add_parser_execute(subparsers):
    """The parser definition of mldesigner execute"""

    epilog_execute = """
    Examples:

    # Basic execute command with source file specified:
    mldesigner execute --source ./components.py

    # Execute with specified component name and inputs:
    mldesigner execute --source ./components.py --name sum_component --inputs a=1 b=2"""

    execute_parser = subparsers.add_parser(
        "execute",
        description="A CLI tool to execute component.",
        help="Execute a component in local host environment, execute source is a mldesigner component file path.",
        epilog=epilog_execute,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    execute_parser.add_argument(
        "--source", required=True, help="The file path that contains target mldesigner component to be executed."
    )
    execute_parser.add_argument(
        "--name",
        required=False,
        help=(
            "The component name of the target to be executed. Note it's not the function name but the component name. "
            "If not specified, will execute the first component inside the source file."
        ),
    )
    execute_parser.add_argument(
        "--inputs",
        nargs="*",
        required=False,
        help=("The input parameters for component to execute. (e.g.) '--inputs a=1 b=2'"),
    )
    execute_parser.add_argument(
        "--outputs",
        nargs="*",
        required=False,
        help=(
            "The customizable output path for component execution results. This is only meaningful when the component "
            "has 'uri_folder' or 'uri_file' output parameters. If not specified, output path will be the parameter name. "
            "(e.g.) '--outputs a=path0 b=path1'"
        ),
    )
    execute_parser.set_defaults(action="execute")


def add_parser_compile(subparsers):
    """The parser definition of mldesigner compile"""

    epilog_compile = """
    Examples:

    # Compile all components inside source file, compiled yaml components will be in the same folder with source file.
    mldesigner compile --source ./components.py

    # Compile specific component, result will be in the same folder with source file.
    mldesigner compile --source ./components.py --name train_component

    # Compile with detailed debug information.
    mldesigner compile --source ./components.py --debug

    # Compile yaml component, compiled component with its snapshot will be in .build/{component_name}/
    mldesigner compile --source ./my_component.yaml --output .build

    # Compile all components from multiple source files, each component result will be in .build/{component_name}/
    mldesigner compile --source ./components/**/*.py --output .build

    # Compile with additional ignore file
    mldesigner compile --source ./helloworld_component.yaml --ignore-file {path-to}/.amlignore
    """
    compile_parser = subparsers.add_parser(
        "compile",
        description="A CLI tool to compile SDK-defined components/pipelines to yaml files, or build yaml components/pipelines into component snapshot.",
        help="Compile SDK-defined components/pipelines to yaml files, or build yaml components/pipelines with snapshot.",
        epilog=epilog_compile,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    compile_parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="The file path that contains target mldesigner components/pipelines to be compiled.",
    )
    compile_parser.add_argument(
        "--name",
        type=str,
        help=(
            "The component name of the target to be executed. Note it's not the function name but the component name. "
            "If not specified, will compile all available components/pipelines inside the source file."
        ),
    )
    compile_parser.add_argument(
        "--output",
        type=str,
        help=(
            "The folder in which to put compiled results. If not specified, compiled files are in the same folder "
            "with source file. If specified, compiled component with its snapshot are in ./{output_folder}/{component_name}/"
        ),
    )
    compile_parser.add_argument(
        "--ignore-file",
        type=str,
        help=(
            "The file path that contains ignore patterns, determines what files will be ignored during compilation. "
            "Only supports '.gitignore' and '.amlignore' file. By default, the compilation will use ignore files "
            "in the component code folder. If specified, the specified ignore file will be used COMBINED with"
            "original ignore files in the component code folder."
        ),
    )
    compile_parser.add_argument(
        "--debug",
        action="store_true",
        help="Determines whether to show detailed debug information, default to be false.",
    )
    compile_parser.set_defaults(action="compile")


def add_parser_export(subparsers):
    # mldesigner export

    example_text = """
    Examples:

    # export pipeline run to code without component snapshot by URL
    mldesigner export --source "<pipeline_run_url>"

    # export full snapshot of a pipeline run by URL
    mldesigner export --source "<pipeline_run_url>" --include-components "*"

    # export pipeline with selected component snapshot by URL
    mldesigner export --source "<pipeline_run_url>" --include-components train:0.0.1 anonymous_component:guid_version
    """
    export_parser = subparsers.add_parser(
        "export",
        description="A CLI tool to export pipeline job from portal url to @pipeline code.",
        help="Export pipeline job to @pipeline code [Preview]",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    export_parser.add_argument(
        "--source",
        type=str,
        help="""Pipeline job source, currently supported format is pipeline run URL.""",
    )
    export_parser.add_argument(
        "--include-components",
        nargs="+",
        type=str,
        help="""Included components to download snapshot. Use * to export all components;
        Or separated string which contains a subset of components used in pipeline.
        Provided components can be name:version to download specific version of component
        or just name to download all versions of that component.""",
    )
    export_parser.set_defaults(action="export")


def main():
    """Entrance of mldesigner CLI."""
    command_args = sys.argv[1:]
    if len(command_args) == 0:
        command_args.append("-h")
    _entry(command_args)


def list_2_dict(input_list):
    """Transform a list ['a=1', 'b=2'] to dict {'a'='1', 'b'='2'}."""
    if input_list is None:
        return None
    res = {}
    try:
        for item in input_list:
            sep = "="
            if sep not in item:
                raise UserErrorException(f"'=' not in command parameter '{item}'")
            equal_index = item.find(sep)
            if equal_index in (0, len(item) - 1):
                raise UserErrorException(f"parameter name or value missed, got {item}")

            key, value = item.split(sep, 1)
            res[key] = value
    except Exception as e:
        raise UserErrorException(
            f"Incorrect parameter format: {str(e)}. Please make sure command arguments are like '--inputs a=1 b=2' "
            "or '--outputs a=path0 b=path1'"
        ) from e
    return res
