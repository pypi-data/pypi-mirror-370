"""
Encapsulates a set of clips, along with task management functionality to
create them.
"""

from pathlib import Path
from typing import Iterable

from doit.cmd_base import Command, TaskLoader2
from doit.doit_cmd import DoitMain
from doit.task import Task

from .clip.clip import Clip
from .clip.operation import OperationParams
from .video.base import BaseVideo
from .video.raw import RawVideo, RawVideoCache

__all__ = [
    "Context",
]


class Context:
    """
    Container in which to store pending tasks to create targets associated
    with `Clip`s. Perform the clip processing by invoking `Context.doit()`.
    """

    __tasks: list[Task]

    def __init__(self):
        self.__tasks = []

    def forge(
        self,
        output: Path,
        inputs: Path | BaseVideo | Iterable[Path | BaseVideo],
        operation: OperationParams | None = None,
    ) -> Clip:
        """
        Creates a new clip from the given input(s) using the given operations.

        Adds a `doit` task to the associated context; user can then perform
        processing by invoking `Context.doit`.

        If any folder is passed as input, it is recursively traversed
        depth-first to form a list of input videos.

        :param output: Path to output file
        :param inputs: Path to one or more inputs, which may be a video or folder of videos
        :param operation: Parameters to apply to input
        """

        operation_ = operation or OperationParams()
        normalized_inputs = _normalize_inputs(inputs, operation_)

        valid_inputs = [
            v
            for v in normalized_inputs
            if not isinstance(v, RawVideo) or v.valid
        ]

        clip = Clip(output, valid_inputs, operation_, self)
        self.__tasks.append(clip._get_task())

        return clip

    def doit(self):
        """
        Invoke tasks to build all clips.

        :raises ChildProcessError: If any ffmpeg invocations failed
        """

        tasks = self.__tasks

        class Loader(TaskLoader2):
            def load_tasks(self, cmd: Command, pos_args: list[str]):
                return tasks

            def load_doit_config(self):
                return {}

        doit_main = DoitMain(task_loader=Loader(), config_filenames=())
        cmd = ["run"] + [task.name for task in tasks]

        ret = doit_main.run(cmd)
        if ret != 0:
            raise ChildProcessError(f"Got ret={ret}")


def _normalize_inputs(
    inputs: Iterable[Path | BaseVideo], operation: OperationParams
) -> list[BaseVideo]:
    inputs_ = inputs if isinstance(inputs, Iterable) else [inputs]

    def process_path(path: Path) -> list[BaseVideo]:
        """
        Return list of all videos from path, valid or invalid.
        """
        if path.is_file():
            return [RawVideo(path)]
        else:
            videos: list[BaseVideo] = []

            # add videos from this folder
            cache = RawVideoCache(path)
            videos += cache.videos

            # write cache if it doesn't already exist
            if operation.cache and not cache.cache_path.is_file():
                cache.write()

            # if recursing, add videos from subfolders
            if operation.recurse:
                for folder in sorted(
                    (
                        p
                        for p in path.iterdir()
                        if p.is_dir() and not p.name.startswith(".")
                    ),
                    key=lambda f: f.name,
                ):
                    videos += process_path(folder)

            return videos

    normalized_inputs: list[BaseVideo] = []

    for i in inputs_:
        if isinstance(i, BaseVideo):
            normalized_inputs.append(i)
        else:
            assert isinstance(i, Path)
            assert i.exists()
            normalized_inputs += process_path(i)

    return normalized_inputs
