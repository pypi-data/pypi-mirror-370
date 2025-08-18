import json
import os
import click

from converters.logic.ckan_helper.ckan_helper import (
    ckan_package_show,
    ckan_package_search_doi,
)
from converters.logic.constants import InputTypes, EnviDatConverter, ConverterExtension
from converters.logic.converter_service import converter_logic
from converters.logic.general_helpers import get_inputtype

converter_choices = [e for e in EnviDatConverter]
input_type_choices = [e for e in InputTypes]


@click.group()
def cli():
    pass


@click.command()
@click.argument("query")
@click.option(
    "--download",
    required=False,
    is_flag=True,
    help="If set, saves to current directory. Use --outputdir for custom location.",
)
@click.option(
    "--outputdir",
    type=click.Path(file_okay=False, writable=True),
    required=False,
    help="Optional: specify directory to save the result. Used only with --download.",
)
def get_data(query, outputdir, download):
    try:
        inputtype = get_inputtype(query)
        if inputtype == InputTypes.DOI:
            package = ckan_package_search_doi(query)
        else:
            package = ckan_package_show(query)
        pretty_json = json.dumps(package, indent=4)
        if download:
            directory = outputdir or "."
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(
                directory, f"{query.replace('/', '_')}_envidat.json"
            )
            with open(filename, "w", encoding="utf-8") as f:
                f.write(pretty_json)
            click.echo(f"Result saved to {filename}")
        else:
            click.echo(pretty_json)
    except Exception as e:
        click.echo(f"Error: {str(e)}")


@click.command()
@click.argument("query")
@click.option(
    "--converter",
    type=click.Choice(converter_choices, case_sensitive=False),
    required=True,
    help="Specify the converter. Options: " + ", ".join(converter_choices),
)
@click.option(
    "--environment",
    required=False,
    default="prod",
    help="Choose an environment specified in your config.ini",
)
@click.option(
    "--download",
    required=False,
    is_flag=True,
    help="If set, saves to current directory. Use --outputdir for custom location.",
)
@click.option(
    "--outputdir",
    type=click.Path(file_okay=False, writable=True),
    required=False,
    help="Optional: specify directory to save the result. Used only with --download.",
)
def convert(query, converter, download, outputdir, environment):
    try:
        inputtype = get_inputtype(query)
        result = converter_logic(converter, inputtype, query, False, environment)
        if download:
            directory = outputdir or "."
            os.makedirs(directory, exist_ok=True)
            extension = ConverterExtension[converter.name].value
            filename = os.path.join(
                directory, f"{query.replace('/', '_')}_{converter.value}.{extension}"
            )
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result)
            click.echo(f"Result saved to {filename}")
        else:
            click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}")


cli.add_command(get_data)
cli.add_command(convert)


def main():
    cli()


if __name__ == "__main__":
    main()
