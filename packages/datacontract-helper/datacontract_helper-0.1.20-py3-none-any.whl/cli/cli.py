import logging
import re
import click

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
@click.option("--new-schema", required=True, envvar="new_schema", type=dict)
@click.pass_context
def validate(ctx, new_schema: dict):
    cmd = commands.Validate(new_schema=new_schema)
    cmd.do_run()


@cli.command()
@click.pass_context
def publish_package(ctx):
    cmd = commands.PublishPackage()
    cmd.do_run()
