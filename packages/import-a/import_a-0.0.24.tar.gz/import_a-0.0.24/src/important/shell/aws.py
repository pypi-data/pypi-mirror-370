import asyncio
from typing import Dict, Any
import json


async def ecr_list_images(
    repo_name: str
) -> Dict[str, Any]:
    """
    List all images in ECR
    """
    command = (
        "aws ecr list-images "
        f"--repository-name {repo_name}"
    )

    proc = await asyncio.subprocess.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    stdout = stdout.decode('utf-8')
    stderr = stderr.decode('utf-8')

    return_code = proc.returncode

    if return_code != 0:
        raise ValueError(f"Command execution error: {stderr}")

    try:
        data = json.loads(stdout)
        return data
    except json.JSONDecodeError:
        data = dict(
            returncode=proc.returncode,
            stdout=stdout,
            stderr=stderr,
        )
        return data
