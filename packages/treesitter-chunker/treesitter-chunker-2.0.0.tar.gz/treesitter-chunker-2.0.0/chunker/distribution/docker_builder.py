"""
Docker Image Builder for multi-platform distribution

Handles building and managing Docker images for the chunker
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


class DockerBuilder:
    """Handles Docker image building and management"""

    def __init__(self):
        self.docker_cmd = shutil.which("docker")
        self.buildx_available = self._check_buildx()

    def build_image(
        self,
        tag: str,
        platforms: list[str] | None = None,
        dockerfile_path: Path | None = None,
    ) -> tuple[bool, str]:
        """
        Build Docker image for distribution

        Args:
            tag: Docker image tag
            platforms: List of platforms (linux/amd64, linux/arm64)
            dockerfile_path: Path to Dockerfile (defaults to ./Dockerfile)

        Returns:
            Tuple of (success, image_id)
        """
        if not self.docker_cmd:
            return False, "Docker not found. Please install Docker."
        if platforms is None:
            platforms = ["linux/amd64"]
        if dockerfile_path is None:
            dockerfile_path = Path("Dockerfile")
        if not dockerfile_path.exists():
            return False, f"Dockerfile not found at {dockerfile_path}"
        try:
            subprocess.run([self.docker_cmd, "info"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            return False, "Docker daemon is not running"
        if len(platforms) > 1 and self.buildx_available:
            return self._build_multiplatform(tag, platforms, dockerfile_path)
        return self._build_single_platform(tag, dockerfile_path)

    def _check_buildx(self) -> bool:
        """Check if Docker buildx is available"""
        if not self.docker_cmd:
            return False
        try:
            subprocess.run(
                [self.docker_cmd, "buildx", "version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _build_multiplatform(
        self,
        tag: str,
        platforms: list[str],
        dockerfile_path: Path,
    ) -> tuple[bool, str]:
        """Build multi-platform image using buildx"""
        try:
            builder_name = "treesitter-chunker-builder"
            inspect_result = subprocess.run(
                [self.docker_cmd, "buildx", "inspect", builder_name],
                capture_output=True,
                check=False,
            )
            if inspect_result.returncode != 0:
                subprocess.run(
                    [
                        self.docker_cmd,
                        "buildx",
                        "create",
                        "--name",
                        builder_name,
                        "--use",
                    ],
                    check=True,
                )
            subprocess.run([self.docker_cmd, "buildx", "use", builder_name], check=True)
            platform_str = ",".join(platforms)
            build_cmd = [
                self.docker_cmd,
                "buildx",
                "build",
                "--platform",
                platform_str,
                "-t",
                tag,
                "-f",
                str(dockerfile_path),
                ".",
                "--push",
            ]
            result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            image_id = self._extract_image_id(result.stdout)
            if not image_id:
                image_id = f"multi-platform-{tag}"
            return True, image_id
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            return False, f"Multi-platform build failed: {error_msg}"

    def _build_single_platform(
        self,
        tag: str,
        dockerfile_path: Path,
    ) -> tuple[bool, str]:
        """Build single platform image"""
        try:
            build_cmd = [
                self.docker_cmd,
                "build",
                "-t",
                tag,
                "-f",
                str(dockerfile_path),
                ".",
            ]
            subprocess.run(build_cmd, capture_output=True, text=True, check=True)
            inspect_result = subprocess.run(
                [self.docker_cmd, "inspect", tag, "--format={{.Id}}"],
                capture_output=True,
                text=True,
                check=True,
            )
            image_id = inspect_result.stdout.strip()
            return True, image_id
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            return False, f"Build failed: {error_msg}"

    @staticmethod
    def _extract_image_id(build_output: str) -> str | None:
        """Extract image ID from build output"""
        for line in build_output.splitlines():
            if "writing image" in line and "sha256:" in line:
                parts = line.split("sha256:")
                if len(parts) > 1:
                    return "sha256:" + parts[1].split()[0]
        return None

    def verify_image(self, tag: str) -> tuple[bool, dict[str, Any]]:
        """Verify Docker image is built correctly"""
        if not self.docker_cmd:
            return False, {"error": "Docker not found"}
        try:
            result = subprocess.run(
                [self.docker_cmd, "inspect", tag],
                capture_output=True,
                text=True,
                check=True,
            )
            image_info = json.loads(result.stdout)[0]
            return True, {
                "id": image_info["Id"],
                "created": image_info["Created"],
                "size": image_info["Size"],
                "architecture": image_info["Architecture"],
                "os": image_info["Os"],
                "layers": len(image_info.get("RootFS", {}).get("Layers", [])),
            }
        except (
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            IndexError,
        ) as e:
            return False, {"error": f"Failed to verify image: {e!s}"}
