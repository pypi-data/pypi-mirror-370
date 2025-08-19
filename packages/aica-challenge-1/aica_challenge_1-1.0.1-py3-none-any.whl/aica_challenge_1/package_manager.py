import importlib
import importlib.metadata
import pkgutil
import re
import subprocess
import sys
import zipfile

from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from typing import Optional, List, Tuple, Set, Dict

from cyst.api.host.service import ActiveServiceDescription


@dataclass
class InstalledAgent:
    name: str
    package: str
    description: str


@dataclass
class InstalledPackage:
    name: str
    path: str
    dir: str
    version: str
    description: str

    def __lt__(self, other):
        return self.dir < other.dir


@dataclass
class PackageList:
    installed: List[InstalledPackage] = field(default_factory=lambda: [])
    available: List[str] = field(default_factory=lambda: [])


class PackageManager:
    def __init__(self, agents_path: str | Path = ""):
        if not agents_path:
            self._package_path: Path = Path(__file__).parent / "agents"
        elif isinstance(agents_path, str):
            self._package_path: Path = Path(agents_path)
        else:
            self._package_path = agents_path

    @staticmethod
    def list_installed_agents() -> Dict[str, InstalledAgent]:
        ignored_services = ["firewall", "forward_shell", "reverse_shell", "scripted_actor"]
        result = {}
        for service in importlib.metadata.entry_points(group="cyst.services"):
            if service.name in ignored_services:
                continue
            service_description: ActiveServiceDescription = service.load()
            result[service.name] = InstalledAgent(
                service.name,
                service.dist.name,
                service_description.description
            )
        return result

    def check_packages(self) -> PackageList:
        result = PackageList()

        packages_on_path = set([x.parts[-1] for x in self._package_path.iterdir() if x.is_dir()])
        installed_packages = set()

        for module in pkgutil.iter_modules():
            if hasattr(module.module_finder, "path"):
                module_path = Path(module.module_finder.path)
                module_dir = module_path.parts[-2]
                if module_path.is_relative_to(self._package_path):
                    installed_packages.add(module_dir)
                    metadata = importlib.metadata.metadata(module.name)
                    result.installed.append(InstalledPackage(
                        metadata.get("Name"),
                        str(module_path),
                        module_dir,
                        metadata.get("Version"),
                        metadata.get("Summary")
                    ))

        result.available = list(packages_on_path - installed_packages)

        return result

    def list_installed_packages(self) -> List[InstalledPackage]:
        return self.check_packages().installed

    def list_available_packages(self) -> List[str]:
        return self.check_packages().available

    def install_package(self, name: str) -> Tuple[bool, str, str]:
        for installed_package in self.list_installed_packages():
            if name == installed_package.dir:
                return True, "", ""

        result = subprocess.run(["poetry", "add", "-e", str(self._package_path / name)], capture_output=True)
        if result.returncode == 0:
            sys.path.append(str(self._package_path / name / "src"))
            return True, "", ""
        else:
            return False, str(result.stdout), str(result.stderr)

    def install_all(self) -> bool:
        failure = False
        for available_package in sorted(self.list_available_packages()):
            failure |= self.install_package(available_package)
        return not failure

    def remove_package(self, name: str) -> Tuple[bool, str, str]:
        for installed_package in self.list_installed_packages():
            if name == installed_package.dir:
                result = subprocess.run(["poetry", "remove", installed_package.name], capture_output=True)
                if result.returncode == 0:
                    sys.path.remove(installed_package.path)
                    return True, "", ""
                else:
                    return False, str(result.stdout), str(result.stderr)
        return True, "", ""

    def remove_all(self) -> bool:
        failure = False
        for installed_agent in sorted(self.list_installed_packages()):
            failure |= self.remove_package(installed_agent.dir)
        return not failure

    def init_agent(self, agent_name: str) -> Tuple[bool, str]:
        if not re.match("^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", agent_name, re.IGNORECASE):
            print(f"Agent name '{agent_name}' does not conform to package name convention. See PEP 503 and 508")
            return False, agent_name

        normalized_name = re.sub(r"[-_.]+", "-", agent_name).lower()
        normalized_dir_name = re.sub(r"-+", "_", normalized_name)

        agent_path = Path(self._package_path / normalized_name)
        if agent_path.exists():
            print(f"Agent with name '{agent_name}' already present at '{agent_path}'. Init aborted.")
            return False, normalized_name

        print(f"Initiating an agent with normalized name: {normalized_name}")

        agent_path.mkdir()

        agent_zip = zipfile.ZipFile(Path(__file__).parent / "agent_template._zip")
        agent_zip.extractall(agent_path)

        # The template need a couple of renamings. We provide the template, so only the happy path is considered.
        # - directory in src
        # - name in pyproject.toml
        # - name in ActiveServiceDescription
        agent_src_dir = agent_path / "src" / "agent_name"
        agent_src_dir.rename(agent_path / "src" / normalized_dir_name)

        # The desire to one-line intensifies
        agent_pyproject = Template((agent_path / "pyproject.toml").read_text())
        (agent_path / "pyproject.toml").write_text(agent_pyproject.substitute(agent_name=normalized_name, agent_path=normalized_dir_name))

        agent_source = Template((agent_path / "src" / normalized_dir_name / "main.py").read_text())
        (agent_path / "src" / normalized_dir_name / "main.py").write_text(agent_source.substitute(agent_name=normalized_name))

        print(f"Agent '{normalized_name}' successfully initiated")

        return True, normalized_name