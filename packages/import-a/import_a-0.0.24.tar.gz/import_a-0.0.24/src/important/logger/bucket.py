from subprocess import run
from datetime import datetime
import uuid
import json
from pathlib import Path


def add_to_file(s3path, data):
    filename = (
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        f"-{uuid.uuid4()[:8]}.json"
        )
    temp_file = f"/tmp/{filename}"
    with open(temp_file, 'w') as f:
        f.write(json.dumps(data, indent=4,))

    run_res = run(
        f"aws s3 cp {temp_file} {Path(s3path) / filename}",
        shell=True)

    if run_res.returncode != 0:
        raise ValueError("Logging pushing error")
