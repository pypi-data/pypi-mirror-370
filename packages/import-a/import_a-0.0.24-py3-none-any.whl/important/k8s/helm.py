from important.shell.pandas import (
    read_cmd, read_cmd_async
)
import pandas as pd
from subprocess import run
import asyncio
import logging


def list_release(
    namespace: str,
    max_hit: int = 20
) -> pd.DataFrame:
    res = read_cmd(f"helm list -n {namespace} -m {max_hit}")
    if type(res) == str:
        raise ValueError(f"Command execution error: {res}")
    return res


async def list_release_async(
    namespace: str,
    max_hit: int = 20
) -> pd.DataFrame:
    res = await read_cmd_async(f"helm list -n {namespace} -m {max_hit}")
    if type(res) == str:
        raise ValueError(f"Command execution error: {res}")
    return res


def read_release_revisions(
    release: str,
    namespace: str,
    max_hit: int = 20,
) -> pd.DataFrame:
    """
    Read the version list under a release
    """
    command = f"helm history {release} -n {namespace} --max {max_hit}"
    res = read_cmd(command)
    if type(res) == str:
        logging.error(command)
        raise ValueError(f"Command execution error: {res}")
    return res


async def read_release_revisions_async(
    release: str,
    namespace: str,
    max_hit: int = 20,
) -> pd.DataFrame:
    """
    Read the version list under a release
    The async version
    """
    command = f"helm history {release} -n {namespace} --max {max_hit}"
    res = await read_cmd_async(
        command)
    if type(res) == str:
        logging.error(command)
        raise ValueError(f"Command execution error: {res}")
    return res


def rollback_release(
    release: str,
    revision: str,
    namespace: str
) -> pd.DataFrame:
    """
    Rollback a release to a specific revision
    Revision is an integer number, but here we input the string format
    Revision can be found in the output of
    `helm history <release> -n <namespace>`
    """
    command = f"helm rollback {release} {revision} -n {namespace}"
    run_res = run(
        command,
        shell=True,
        capture_output=True,
    )
    if run_res.returncode != 0:
        error_msg = run_res.stderr.decode('utf-8')
        logging.error()
        raise ValueError(f"Command execution error: {error_msg}")

    release_revisions_df = read_release_revisions(release, namespace)
    return release_revisions_df


async def rollback_release_async(
    release: str,
    revision: str,
    namespace: str
) -> pd.DataFrame:
    """
    Rollback a release to a specific revision
    Revision is an integer number, but here we input the string format
    Revision can be found in the output of
    `helm history <release> -n <namespace>`
    The async version of rollback_release
    """
    command = f"helm rollback {release} {revision} -n {namespace}"
    run_res = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await run_res.communicate()
    if run_res.returncode != 0:
        error_msg = stderr.decode('utf-8')
        logging.error(command)
        raise ValueError(f"Command execution error: {error_msg}")

    release_revisions_df = await read_release_revisions_async(
        release, namespace)
    return release_revisions_df
