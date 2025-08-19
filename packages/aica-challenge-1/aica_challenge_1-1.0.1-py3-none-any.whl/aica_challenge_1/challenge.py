import inspect

from pathlib import Path
from typing import List, Dict

from aica_challenge_1.package_manager import PackageManager
from aica_challenge_1.scenario_manager import ScenarioManager
from aica_challenge_1.execution_manager import ExecutionManager, RunSpecification

from cyst.api.environment.environment import Environment

class Challenge:
    def __init__(self, challenge_dir: str = ""):
        caller_frame = inspect.currentframe().f_back
        if "__file__" in caller_frame.f_locals:
            caller_dir = Path(caller_frame.f_locals["__file__"]).parent
        else:
            caller_dir = Path.cwd()

        if challenge_dir:
            cd = Path(challenge_dir)
            if not cd.is_absolute():
                cd = caller_dir / cd
        else:
            cd = caller_dir

        if not self.check_init_state(cd):
            raise ValueError("Challenge environment not properly initiated", cd)

        self._package_manager = PackageManager(cd / "agents")
        self._scenario_manager = ScenarioManager(cd / "scenarios")
        self._execution_manager = ExecutionManager(self._package_manager, self._scenario_manager)

    @property
    def packages(self) -> PackageManager:
        return self._package_manager

    @property
    def scenarios(self) -> ScenarioManager:
        return self._scenario_manager

    @property
    def execution(self) -> ExecutionManager:
        return self._execution_manager

    # Convenience function
    def execute(self, run_specification: RunSpecification | str, single_process=False) -> None:
        self._execution_manager.execute(run_specification, single_process)

    @staticmethod
    def init_environment():
        caller_frame = inspect.currentframe().f_back
        if "__file__" in caller_frame.f_locals:
            caller_dir = Path(caller_frame.f_locals["__file__"]).parent
        else:
            caller_dir = Path.cwd()

        agents_path = caller_dir / "agents"
        scenarios_path = caller_dir / "scenarios"

        if not agents_path.exists():
            print(f"Creating new agents directory: {str(agents_path)}")
            agents_path.mkdir()

        if not scenarios_path.exists():
            print(f"Creating new scenarios directory: {str(scenarios_path)}")
            scenarios_path.mkdir()

    @staticmethod
    def check_init_state(challenge_dir: Path) -> bool:
        if not challenge_dir.exists():
            return False

        agents_path = challenge_dir / "agents"
        scenarios_path = challenge_dir / "scenarios"

        if not (agents_path.exists() and scenarios_path.exists()):
            return False

        return True

    @staticmethod
    def list_actions() -> List[Dict[str, str]]:
        result = []

        env = Environment.create()
        actions = env.resources.action_store.get_prefixed("ac1")

        for action in actions:
            result.append({
                "id": action.id,
                "description": action.description,
                "parameters": [x.name for x in action.parameters.values()]
            })

        return result
