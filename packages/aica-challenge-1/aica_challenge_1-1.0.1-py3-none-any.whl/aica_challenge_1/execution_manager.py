import functools
import io
import os

from concurrent.futures import ProcessPoolExecutor, Future
from contextlib import redirect_stderr, redirect_stdout, nullcontext
from dataclasses import dataclass, field
from enum import Enum, auto
from random import choice
from sqlalchemy import create_engine, select, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, Session, relationship
from typing import Dict, Any, Optional, List, Self, Set, Tuple

from cyst.api.environment.environment import Environment
from cyst.api.utils.counter import Counter

from aica_challenge_1.package_manager import PackageManager
from aica_challenge_1.scenario_manager import ScenarioManager, ScenarioVariant
from aica_challenge_1.launcher import launch_simulation
from aica_challenge_1.execution_structures import Episode, DBEpisode, DBRun, RunStatus, RunSpecification, Run, Base


class ExecutionManager:
    def __init__(self, package_manager: PackageManager, scenario_manager: ScenarioManager):
        self._package_manager = package_manager
        self._scenario_manager = scenario_manager
        self._run_specifications: Dict[str, RunSpecification] = {}

        self._db = create_engine("sqlite+pysqlite:///aica_challenge.db")
        Base.metadata.create_all(self._db)

        with Session(self._db, expire_on_commit=False) as session:
            for obj in session.execute(select(RunSpecification)).scalars():
                self._run_specifications[obj.name] = obj

        self._runs: Dict[int, Run] = {}

    def list_run_specifications(self) -> List[str]:
        return sorted(self._run_specifications.keys())

    def get_run_specification(self, name: str) -> Optional[RunSpecification]:
        return self._run_specifications.get(name, None)

    def set_run_specification(self, specification: RunSpecification, old_specification: Optional[RunSpecification] = None) -> None:
        if old_specification and old_specification.name and old_specification.name != specification.name:
            del self._run_specifications[str(old_specification.name)]
        self._run_specifications[specification.name] = specification
        with Session(self._db, expire_on_commit=False) as session:
            session.add(specification)
            session.commit()

    def save_run_information(self, run: Run) -> None:
        with Session(self._db, expire_on_commit=False) as session:
            stmt = select(DBRun).where(DBRun.id == run.id)
            run_db: DBRun = session.scalars(stmt).one()

            details = f"Successfull episodes: {sorted(list(run.successful))}, failed episodes: {sorted(list(run.error))}"

            run.detail = details
            run_db.details = details

            # We set status to finished whenever there was at elast one successful episode
            status = RunStatus.FINISHED if run.successful else RunStatus.ERROR
            run.status = status
            run_db.status = str(status)

            session.commit()

    def get_run(self, run_id: int) -> Run:
        return self._runs[run_id]

    def get_runs(self) -> List[Tuple[int, RunStatus]]:
        result = []
        for k in sorted(self._runs.keys()):
            r = self._runs[k]
            result.append((k, self._runs[k].status))
        return result

    def execution_callback(self, episode_number: int, future: Future):
        if future.exception():
            print(f"The episode {episode_number} has been terminated.")
            return

        e: Episode = future.result()
        run = self._runs[e.run]
        run.episodes[episode_number] = e
        run.running.remove(episode_number)
        if e.status == RunStatus.FINISHED:
            run.successful.add(episode_number)
        else:
            run.error.add(episode_number)

        if not run.running:
            self.save_run_information(run)

    def execute(self, specification: RunSpecification | str, single_process=False) -> None:
        if isinstance(specification, str):
            spec_name = specification
            specification = self._run_specifications.get(specification, None)
            if not specification:
                raise ValueError(f"Run with the name '{spec_name}' not available in the system.")

        with Session(self._db, expire_on_commit=False) as session:
            # Refresh run specification
            specification = session.get(RunSpecification, specification.id)

            if not specification:
                raise ValueError(f"There was an error extracting run specification from the database")

            run = Run(specification)

            db_run = DBRun(
                status=str(RunStatus.INIT),
                details="",
                episodes=[],
                specification_id=specification.id,
                specification=specification
            )

            session.add(db_run)
            session.flush()

            if not specification.name:
                run.status = RunStatus.ERROR
                run.detail = "Run specification must have a name."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            if specification.agent_name not in self._package_manager.list_installed_agents():
                run.status = RunStatus.ERROR
                run.detail = f"Chosen agent '{specification.agent_name}' not installed in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_name = specification.scenario
            scenario = self._scenario_manager.get_scenario(scenario_name)

            if scenario_name == "Random":
                scenarios = self._scenario_manager.get_scenarios()
                if not scenarios:
                    run.status = RunStatus.ERROR
                    run.detail = "No scenarios installed in the system. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                s = choice(scenarios)
                scenario_name = s.short_path
                scenario = s

            if not scenario:
                run.status = RunStatus.ERROR
                run.detail = f"Chosen scenario '{specification.scenario}' not available."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            variant_id = specification.variant
            variants = scenario.variants

            if variant_id == -1:
                if not variants:
                    run.status = RunStatus.ERROR
                    run.detail = f"No variants of the scenario '{scenario_name}' exist. Cannot choose a random one."
                    db_run.status = str(RunStatus.ERROR)
                    db_run.details = run.detail
                    session.commit()
                    return
                variant_id = choice(list(variants.keys()))

            elif variant_id not in variants:
                run.status = RunStatus.ERROR
                run.detail = f"Variant '{variant_id}' of the scenario '{scenario_name}' is not available in the system."
                db_run.status = str(RunStatus.ERROR)
                db_run.details = run.detail
                session.commit()
                return

            scenario_variant = self._scenario_manager.get_scenario(scenario_name).variants[variant_id]

            run.id = db_run.id
            self._runs[run.id] = run

            run.status = RunStatus.RUNNING
            db_run.status = str(RunStatus.RUNNING)

            session.commit()

        if not single_process:
            run.executor = ProcessPoolExecutor(max_workers=specification.max_parallel)

            for e in range(specification.max_episodes):
                future: Future = run.executor.submit(launch_simulation, run.id, e, scenario_variant,
                                                     specification.agent_name, specification.max_time,
                                                     specification.max_actions, {})
                future.add_done_callback(functools.partial(self.execution_callback, e))
                run.running.add(e)
        else:
            for e in range(specification.max_episodes):
                ep = launch_simulation(run.id, e, scenario_variant, specification.agent_name, specification.max_time,
                                       specification.max_actions, {}, supress_output=False)

                if ep.status == RunStatus.FINISHED:
                    run.successful.add(e)
                else:
                    run.error.add(e)

            self.save_run_information(run)
