import pandas as pd
from subprocess import run
from io import StringIO
from typing import Union
import logging
from traceback import format_exc
from .async_pandas import read_cmd_async


def read_cmd(cmd: str, sep='\t') -> Union[pd.DataFrame, str]:
    """
    Parse the command result to a pandas dataframe
    """
    run_res = run(
        cmd,
        shell=True,
        capture_output=True,
        )
    if run_res.returncode != 0:
        error_msg = run_res.stderr.decode('utf-8')
        logging.error(error_msg)
        return error_msg
    value = run_res.stdout.decode('utf-8')
    output = StringIO(
        value
    )
    try:
        df = pd.read_csv(output, sep=sep)
        return df
    except KeyboardInterrupt as e:
        raise e
    except Exception:
        logging.error(format_exc())
        return value
