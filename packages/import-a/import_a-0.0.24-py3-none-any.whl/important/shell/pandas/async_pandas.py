from typing import Union
import pandas as pd
from io import StringIO
import logging
from traceback import format_exc
from important.shell.base import shell_async


async def read_cmd_async(
    cmd: str, sep='\t'
) -> Union[pd.DataFrame, str]:
    """
    Parse the command result to a pandas dataframe
    The async version
    cmd: str
        The shell command to run
    sep: str
    Return a dataframe if the command is successful
        and the string can actually be parsed into a dataframe
    Return the string if the command is successful
        but the string can not be parsed into a dataframe
    """
    run_res = await shell_async(cmd)
    if run_res['returncode'] != 0:
        return run_res['stderr']
    value = run_res['stdout']
    try:
        df = pd.read_csv(StringIO(value), sep=sep)
        return df
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        logging.error(format_exc())
        return value
