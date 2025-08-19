"""interface.py - define CLI interface
Copyright © 2025 John Liu
"""

import click

from batch_img.common import Common
from batch_img.const import MSG_BAD, MSG_OK
from batch_img.main import Main


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--version", is_flag=True, help="Show this tool's version")
def cli(ctx, version):  # pragma: no cover
    if not ctx.invoked_subcommand:
        if version:
            click.secho(Common.get_version())


@cli.command(help="Add internal border to image file(s), not expand the size")
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-bw",
    "--border_width",
    default=5,
    show_default=True,
    type=click.IntRange(min=0, max=30),
    help="Add border to image file(s) with the border_width. 0 - no border",
)
@click.option(
    "-bc",
    "--border_color",
    default="gray",
    show_default=True,
    help="Add border to image file(s) with the border_color string",
)
@click.option(
    "-o",
    "--output",
    default="",
    show_default=True,
    type=str,
    help="Output file path. If skipped, use the current dir path",
)
def border(src_path, border_width, border_color, output):
    options = {
        "src_path": src_path,
        "border_width": border_width,
        "border_color": border_color,
        "output": output,
    }
    res = Main.border(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)


@cli.command(
    help="Process image file(s) with default actions:\n"
    "1) resize to 1280; 2) add 5-pixel green color border; 3) auto-rotate if needed"
)
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-o",
    "--output",
    default="",
    show_default=True,
    type=str,
    help="Output file path. If skipped, use the current dir path",
)
def defaults(src_path, output):
    """Do the default action on the image file(s):
    * Resize to 1280 pixels as the max length
    * Add the border of 5 pixel width in green color
    * Auto-rotate if upside down or sideways
    """
    options = {"src_path": src_path, "output": output}
    res = Main.default_run(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)


@cli.command(help="Resize image file(s)")
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-l",
    "--length",
    is_flag=False,
    default=0,
    show_default=True,
    type=click.IntRange(min=0),
    help="Resize image file(s) on original aspect ratio to the length. 0 - no resize",
)
@click.option(
    "-o",
    "--output",
    default="",
    show_default=True,
    type=str,
    help="Output file path. If skipped, use the current dir path",
)
def resize(src_path, length, output):
    options = {"src_path": src_path, "length": length, "output": output}
    res = Main.resize(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)


@cli.command(help="Rotate image file(s)")
@click.argument(
    "src_path",
    required=True,
)
@click.option(
    "-a",
    "--angle",
    is_flag=False,
    default=0,
    show_default=True,
    type=click.IntRange(min=0),
    help="Rotate image file(s) to the clockwise angle. 0 - no rotate",
)
@click.option(
    "-o",
    "--output",
    default="",
    show_default=True,
    type=str,
    help="Output file path. If skipped, use the current dir path",
)
def rotate(src_path, angle, output):
    options = {
        "src_path": src_path,
        "angle": angle,
        "output": output,
    }
    res = Main.rotate(options)
    msg = MSG_OK if res else MSG_BAD
    click.secho(msg)
