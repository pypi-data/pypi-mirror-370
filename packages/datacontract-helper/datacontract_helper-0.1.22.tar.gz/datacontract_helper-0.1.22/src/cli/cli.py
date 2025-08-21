import logging
import re
import click
import json
# from src import commands
import commands

log = logging.getLogger(__name__)


@click.group()
@click.pass_context
def cli(
    ctx,
):
    ctx.ensure_object(dict)
    print("is cli")


@cli.command()
# @click.option("--new-schema", required=True, envvar="new_schema", type=dict)
@click.option("--new-schema", required=True, envvar="NEW_SCHEMA", help="JSON string with schema")
# @click.option("--new-schema", required=True, envvar="NEW_SCHEMA_PATH", type=click.Path(exists=True), help="Path to JSON schema file")
@click.pass_context
def validate(ctx, new_schema: str):
    # try:
    #     with open(new_schema, 'r') as f:
    #         schema_data = json.load(f)
    # except (json.JSONDecodeError, IOError) as e:
    #     raise click.BadParameter(f"Error loading schema: {e}")
    
    try:
        new_schema = json.loads(new_schema)
    except json.JSONDecodeError as e:
        raise click.BadParameter(f"Invalid JSON: {e}")
    
    cmd = commands.Validate(new_schema=new_schema)
    cmd.do_run()


@cli.command()
@click.pass_context
def publish_package(ctx):
    cmd = commands.PublishPackage()
    cmd.do_run()
