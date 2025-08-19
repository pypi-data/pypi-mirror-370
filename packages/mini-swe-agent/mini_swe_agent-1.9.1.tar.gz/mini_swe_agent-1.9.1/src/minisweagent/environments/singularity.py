#!/usr/bin/env python3

import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SingularityEnvironmentConfig:
    image: str
    cwd: str = "/"
    env: dict[str, str] = field(default_factory=dict)
    """Environment variables to set in the container."""
    forward_env: list[str] = field(default_factory=list)
    """Environment variables to forward to the container."""
    timeout: int = 30
    """Timeout for executing commands in the container."""
    executable: str = os.getenv("MSWEA_SINGULARITY_EXECUTABLE", "singularity")
    """Path to the singularity executable."""


class SingularityEnvironment:
    def __init__(self, **kwargs):
        """Singularity environment. See `SingularityEnvironmentConfig` for kwargs."""
        self.logger = logging.getLogger("minisweagent.environment")
        self.config = SingularityEnvironmentConfig(**kwargs)
        self.sandbox_dir = Path(tempfile.gettempdir()) / f"minisweagent-{uuid.uuid4().hex[:8]}"
        subprocess.run(
            [self.config.executable, "build", "--sandbox", self.sandbox_dir, self.config.image],
            check=True,
        )

    def get_template_vars(self) -> dict[str, Any]:
        return asdict(self.config)

    def execute(self, command: str, cwd: str = "") -> dict[str, Any]:
        """Execute a command in a Singularity container and return the result as a dict."""
        cmd = [self.config.executable, "exec"]

        # Do not inherit directories and env vars from host
        cmd.extend(["--contain", "--cleanenv"])

        work_dir = cwd or self.config.cwd
        if work_dir and work_dir != "/":
            cmd.extend(["--pwd", work_dir])

        for key in self.config.forward_env:
            if (value := os.getenv(key)) is not None:
                cmd.extend(["--env", f"{key}={value}"])
        for key, value in self.config.env.items():
            cmd.extend(["--env", f"{key}={value}"])

        cmd.extend(["--writable", str(self.sandbox_dir), "bash", "-c", command])
        result = subprocess.run(
            cmd,
            text=True,
            timeout=self.config.timeout,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        return {"output": result.stdout, "returncode": result.returncode}

    def cleanup(self):
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)

    def __del__(self):
        """Cleanup sandbox when object is destroyed."""
        self.cleanup()
