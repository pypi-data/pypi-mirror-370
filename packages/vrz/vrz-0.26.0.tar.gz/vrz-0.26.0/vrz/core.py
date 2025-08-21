from pathlib import Path
import shlex
import subprocess
import tempfile
import tomllib
import requests as request


class Poetry:
    def __init__(self, working_dir: Path = None):
        self.working_dir = working_dir

    @classmethod
    def init_project(cls, path: Path = None):
        """
        Initializes a new Poetry project in the specified directory.
        If no path is provided, a temporary directory is created.

        Returns:
            Poetry: An instance of the Poetry class associated with the project directory.
        """
        if path is None:
            temp_dir = tempfile.TemporaryDirectory()
            project_path = Path(temp_dir.name)
            project_path._temp_dir = temp_dir
        else:
            project_path = Path(path)
            project_path.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            shlex.split("poetry init -n"),
            check=True,
            capture_output=True,
            text=True,
            cwd=project_path,
        )

        return cls(working_dir=project_path)

    def is_poetry_project(self, directory: Path = None) -> bool:
        """Check whether the directory is a Poetry project.

        A directory is considered a Poetry project when it contains a
        ``pyproject.toml`` file created by Poetry. This may be a legacy
        ``[tool.poetry]`` configuration or a modern PEP 621 ``[project]``
        table using Poetry's build backend.

        Args:
            directory (Path, optional): Directory to check. If ``None``, the
                instance's ``working_dir`` is used.

        Returns:
            bool: ``True`` if the directory represents a Poetry project,
            ``False`` otherwise.
        """
        dir_path = Path(directory) if directory is not None else self.working_dir
        if dir_path is None:
            return False

        pyproject = dir_path / "pyproject.toml"
        if not pyproject.is_file():
            return False

        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return False

        # Poetry 1.x uses the legacy ``[tool.poetry]`` table
        tool = data.get("tool", {})
        if "poetry" in tool:
            return True

        # Poetry 2.x uses PEP 621 ``[project]`` table with Poetry's build backend
        project = data.get("project")
        build_backend = data.get("build-system", {}).get("build-backend")
        if project and build_backend == "poetry.core.masonry.api":
            return True

        return False
    
    def version_bump_minor(self):
        subprocess.run(
            shlex.split("poetry version minor"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.working_dir,
        )

    def version_read(self):
        output = subprocess.run(
            shlex.split("poetry version -s"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.working_dir,
        )
        return output.stdout.strip()

    def is_published(self, package_name):
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = request.get(url)
        return response.status_code != 404

    def is_current_project_published(self):
        project_name = self.project_name()
        return self.is_published(project_name)

    def publish(self):
        try:
            subprocess.run(
                shlex.split("poetry publish --build"),
                check=True,
                capture_output=True,
                text=True,
                cwd=self.working_dir,
            )
        except subprocess.CalledProcessError as e:
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
            raise    
        return True

    def project_name(self):
        output = subprocess.run(
            shlex.split("poetry version"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.working_dir,
        )
        return output.stdout.split()[0].strip()

class Git:
    def is_git_repo(self):
        try:
            subprocess.run(
                shlex.split("git rev-parse --is-inside-work-tree"),
                check=True,
                capture_output=True,
                text=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def create_tag(self, tag_name):
        subprocess.run(
            shlex.split(f"git tag {tag_name}"),
            check=True,
            capture_output=True,
            text=True,
        )

    def push_tag(self, tag_name):
        subprocess.run(
            shlex.split(f"git push origin {tag_name}"),
            check=True,
            capture_output=True,
            text=True,
        )

    def push(self):
        subprocess.run(
            shlex.split("git push"),
            check=True,
            capture_output=True,
            text=True,
        )

    def add(self, file: str):
        subprocess.run(
            shlex.split(f"git add {file}"),
            check=True,
            capture_output=True,
            text=True,
        )

    def commit(self, message: str):
        subprocess.run(
            shlex.split(f"git commit -m '{message}'"),
            check=True,
            capture_output=True,
            text=True,
        )

    def list_tags(self):
        """Return list of Git tags sorted alphanumerically ascending."""
        result = subprocess.run(
            shlex.split("git tag --list --sort=version:refname"),
            check=True,
            capture_output=True,
            text=True,
        )
        tags = result.stdout.strip().splitlines()
        return tags


class VersionSubstitution:
    def replace_version(self, file_path: str, old_version: str, new_version: str):
        with open(file_path, "r") as file:
            content = file.read()

        new_content = content.replace(old_version, new_version)

        with open(file_path, "w") as file:
            file.write(new_content)
