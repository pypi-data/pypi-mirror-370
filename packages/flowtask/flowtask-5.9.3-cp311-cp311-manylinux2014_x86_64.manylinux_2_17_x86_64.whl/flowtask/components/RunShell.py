import subprocess
import asyncio
from typing import List
from collections.abc import Callable
from navconfig.logging import logging
from .flow import FlowComponent


class RunShell(FlowComponent):
    """
    RunShell.


    Overview

        Execute a Command to run a task

    .. table:: Properties
    :widths: auto


    +--------------+----------+-----------+-------------------------------------------------------+
    | Name         | Required | Summary                                                           |
    +--------------+----------+-----------+-------------------------------------------------------+
    | name         |   Yes    | Name of task                                                      |
    +--------------+----------+-----------+-------------------------------------------------------+
    | description  |   Yes    | Task description                                                  |
    +--------------+----------+-----------+-------------------------------------------------------+
    | steps        |   Yes    | Not assigned steps                                                |
    +--------------+----------+-----------+-------------------------------------------------------+
    | runtask      |   Yes    | This method runs the task                                         |
    +--------------+----------+-----------+-------------------------------------------------------+
    | program      |   Yes    | Program name                                                      |
    +--------------+----------+-----------+-------------------------------------------------------+
    | task         |   Yes    | Assign the run shell attribute                                    |
    +--------------+----------+-----------+-------------------------------------------------------+

    Return the list of arbitrary days
    """

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop = None,
        job: Callable = None,
        stat: Callable = None,
        **kwargs,
    ):
        """Init Method."""
        self.commands: List = []
        super(RunShell, self).__init__(loop=loop, job=job, stat=stat, **kwargs)

    async def start(self, **kwargs):
        return True

    async def close(self):
        pass

    async def run(self):
        for cmd in self.commands:
            if hasattr(self, "masks"):
                cmd = self.mask_replacement(cmd)
                logging.debug(">", cmd)
            try:
                result = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                ).communicate()
                logging.debug(result)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error in command: {e}")
                return False
