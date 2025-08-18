import asyncio
from typing import Dict, Union


async def shell_async(cmd: str) -> Dict[str, Union[int, str]]:
    """
    Run a command asynchronously
    """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    return dict(
        returncode=proc.returncode,
        stdout=stdout.decode('utf-8'),
        stderr=stderr.decode('utf-8'),
    )
