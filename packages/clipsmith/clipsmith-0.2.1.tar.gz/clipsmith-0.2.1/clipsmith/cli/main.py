"""
CLI entry point.
"""

import logging
import sys
from pathlib import Path

import rich.traceback
import typer
from rich.console import Console
from rich.logging import RichHandler

from ..clip import DurationParams, OperationParams, ResolutionParams
from ..context import Context

rich.traceback.install(show_locals=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            console=Console(highlight=False),
            show_level=True,
            show_time=True,
            show_path=False,
        )
    ],
)

app = typer.Typer(
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def callback():
    pass


"""
TODO: options:

--overwrite: Overwrite output if out of date, passes -y to ffmpeg
--dry-run: Only list the ffmpeg operations which will be performed, passes --dry-run to doit
"""


@app.command(no_args_is_help=True)
def forge(
    inputs: list[Path] = typer.Argument(
        help="One or more paths to input video(s) or folder(s) of videos"
    ),
    output: Path = typer.Argument(help="Path to output video"),
    trim_start: float
    | None = typer.Option(None, help="Start offset (seconds) in input file(s)"),
    trim_end: float
    | None = typer.Option(None, help="End offset (seconds) in input file(s)"),
    dur_scale: float
    | None = typer.Option(None, help="Scale duration by scale factor"),
    dur_target: float
    | None = typer.Option(None, help="Scale duration to target (seconds)"),
    res_scale: float
    | None = typer.Option(None, help="Scale resolution by scale factor"),
    res_target: str
    | None = typer.Option(
        None, help="Scale resolution to target as WIDTH:HEIGHT"
    ),
    audio: bool = typer.Option(
        True,
        help="Whether to pass through audio to output (not yet supported with time scaling)",
    ),
    recurse: bool = typer.Option(
        False,
        help="Whether to recurse into input folder(s)",
    ),
    cache: bool = typer.Option(
        False,
        help="Whether to store a cache of video metadata in input folder(s)",
    ),
    log_level: str = typer.Option("info", help="Log level passed to ffmpeg"),
):
    """
    Create a video from one or more videos with specified operations applied
    """

    def parse_res(res: str) -> tuple[int, int]:
        split = res.split(":")
        assert len(split) == 2, f"Invalid resolution: {res}"
        return int(split[0]), int(split[1])

    # convert resolution target as typer assumes there can be multiple tuples
    res_target_ = None if res_target is None else parse_res(res_target)

    # setup context and operation
    context = Context()
    operation = OperationParams(
        duration_params=DurationParams(
            scale=dur_scale,
            target=dur_target,
            trim_start=trim_start,
            trim_end=trim_end,
        ),
        resolution_params=ResolutionParams(
            scale=res_scale,
            target=res_target_,
        ),
        audio=audio,
        recurse=recurse,
        cache=cache,
        log_level=log_level,
    )

    inputs_str = ", ".join([f"'{str(p)}'" for p in inputs])
    output_str = f"'{str(output)}'"
    logging.info(f"Forging:\n{inputs_str}\n  ->\n{output_str}")

    # setup forge task
    context.forge(output, inputs, operation=operation)

    # do it
    try:
        context.doit()
    except ChildProcessError:
        logging.error(f"Failed to run doit tasks")
        sys.exit(1)


# TODO: after playbooks implemented
# @app.command()
# def playbook(
#     file: Path = typer.Argument(help="Path to playbook in .yaml format"),
# ):
#     """
#     Run forge operations specified in a playbook file
#     """


# TODO: after profiles implemented
# @app.command()
# def profiles():
#    """
#    List all available profiles
#    """


def run():
    app()


if __name__ == "__main__":
    run()
