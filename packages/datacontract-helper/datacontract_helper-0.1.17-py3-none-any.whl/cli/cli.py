
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
    print("is cli")


@cli.command()
@click.pass_context
def validate(ctx):
    cmd = commands.Validate()
    cmd.do_run()


@cli.command()
@click.pass_context
def publish_package(ctx):
    cmd = commands.PublishPackage()
    cmd.do_run()

    
