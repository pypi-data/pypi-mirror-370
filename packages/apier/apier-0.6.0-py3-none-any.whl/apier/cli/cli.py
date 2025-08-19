import json
import os
import sys
import warnings
from pathlib import Path
from typing import Iterable

import click
import yaml

from apier.core.api.merge import merge_spec_files, MergeWarning
from apier.core.build import build as build_api_client
from apier.core.renderer import builtin_template_map

# Global variable to control the verbosity of the warning messages
_VERBOSE = False

# Built-in templates for client generation
built_in_templates = builtin_template_map.keys()


def warning_handler(message, category, filename, lineno, file=None, line=None):
    """Custom warning handler that formats the warning messages."""
    if isinstance(message, MergeWarning):
        msg = f"Merge Warning ({message.spec_filename}): {message}"
    else:
        msg = f"{category.__name__}: {message}"

    if _VERBOSE:
        msg = f"{filename}:{lineno}: " + click.style(msg, fg="yellow")

    click.echo(msg)


warnings.showwarning = warning_handler


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.pass_context
def cli(ctx):
    """CLI for generating API clients from OpenAPI files."""
    pass


@click.command()
@click.option(
    "--input",
    "-i",
    "input_",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help="One or more OpenAPI files or directories. If a directory is "
    "provided, all files within will be used.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
    help="Output directory for the generated API client code.",
)
@click.option(
    "--template",
    "-t",
    type=click.Choice(built_in_templates),
    help="Template name for client generation (allowed: python-tree).",
)
@click.option(
    "--custom-template",
    type=click.Path(exists=True),
    help="Path to a custom template directory for client generation.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Overwrite the output directory if it already exists.",
)
@click.pass_context
def build(ctx, input_, output, template, custom_template, overwrite):
    """
    Generate an API client from OpenAPI files.

    This command takes one or more OpenAPI files or directories (via --input/-i)
    and generates the client code in the specified output directory.
    If multiple OpenAPI files are provided, they will be merged before
    generating the client.

    You must provide either --template to use a built-in template ('python-tree')
    or --custom-template to define the client structure.
    """
    # Ensure either --template or --custom-template is provided
    if not template and not custom_template:
        raise click.UsageError(
            "Either --template or --custom-template " "must be provided.", ctx=ctx
        )
    if template and custom_template:
        raise click.UsageError(
            "--template and --custom-template cannot " "be used together.", ctx=ctx
        )

    if custom_template:
        template = Path(custom_template)

    input_files = _get_file_list(input_)

    if not overwrite and os.path.exists(output):
        raise click.UsageError(
            f"Output directory '{output}' already "
            f"exists. Use --overwrite to replace it.",
            ctx=ctx,
        )

    context = ctx.params.copy()
    context["verbose"] = _VERBOSE
    context["output_logger"] = click.echo

    build_api_client(context, template, input_files, output)
    click.echo(click.style(f"\n🎉 API client generated in '{output}'", fg="green"))


@click.command()
@click.option(
    "--input",
    "-i",
    "input_",
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help="One or more OpenAPI files or directories to merge. "
    "If a directory is provided, all files within will be used.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output file path for the merged OpenAPI spec.",
)
@click.option(
    "--overwrite", is_flag=True, help="Overwrite the output file if it already exists."
)
@click.pass_context
def merge(ctx, input_, output, overwrite):
    """
    Merge multiple OpenAPI files into one.

    This command takes one or more OpenAPI files or directories (via --input/-i)
    and merges them into a single OpenAPI file.

    The resulting merged file is written to the specified output path.
    """
    input_files = _get_file_list(input_)

    if not overwrite and os.path.exists(output):
        raise click.UsageError(
            f"Output file '{output}' already exists. "
            f"Use --overwrite to replace it.",
            ctx=ctx,
        )

    merged_spec = merge_spec_files(*input_files)

    with open(output, "w") as f:
        if output.endswith(".json"):
            json.dump(merged_spec, f, indent=2)
        else:
            yaml.dump(merged_spec, f, sort_keys=False, allow_unicode=True)

    click.echo(click.style(f"\n🎉 OpenAPI files merged into '{output}'", fg="green"))


def _get_file_list(inputs: Iterable[str]) -> list[str]:
    files = []
    for path in inputs:
        if os.path.isdir(path):
            files.extend(
                [
                    os.path.join(path, f)
                    for f in os.listdir(path)
                    if os.path.isfile(os.path.join(path, f))
                ]
            )
        else:
            files.append(path)
    return files


cli.add_command(build)
cli.add_command(merge)

if __name__ == "__main__":
    # Remove "--verbose" from the command line arguments to avoid click errors
    if "--verbose" in sys.argv:
        sys.argv.remove("--verbose")
        _VERBOSE = True

    try:
        cli.main(standalone_mode=False)
    except click.UsageError as e:
        click.echo(e.ctx.get_help() + "\n")
        click.echo(
            click.style(f"Usage Error: {e.format_message()}", fg="red"), err=True
        )
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        if _VERBOSE:
            raise
