from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum, auto
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedAsDataclass, relationship
from typing import List, Optional, Dict, Set


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class RunSpecification(Base):
    __tablename__ = "challenge_run_specification"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(init=True, default="")
    description: Mapped[str] = mapped_column(init=True, default="")
    agent_name: Mapped[str] = mapped_column(init=True, default="")
    scenario: Mapped[str] = mapped_column(init=True, default="Random")
    variant: Mapped[int] = mapped_column(init=True, default=-1)
    max_time: Mapped[int] = mapped_column(init=True, default=100)
    max_actions: Mapped[int] = mapped_column(init=True, default=100)
    max_episodes: Mapped[int] = mapped_column(init=True, default=100)
    max_parallel: Mapped[int] = mapped_column(init=True, default=1)

    @staticmethod
    def copy(other: 'RunSpecification'):
        return RunSpecification(other.name + "_copy", other.description, other.agent_name, other.scenario, other.variant,
                                other.max_time, other.max_episodes, other.max_parallel)


class DBRun(Base):
    __tablename__ = "challenge_run_statistics"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    status: Mapped[str] = mapped_column(init=True)
    details: Mapped[str] = mapped_column(init=True)
    episodes: Mapped[List['DBEpisode']] = relationship(argument="DBEpisode",
                                                       back_populates="run",
                                                       cascade="all, delete")

    specification_id: Mapped[int] = mapped_column(ForeignKey("challenge_run_specification.id"), init=True)
    specification: Mapped[RunSpecification] = relationship()


class DBEpisode(Base):
    __tablename__ = "challenge_episode_statistics"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    episode_number: Mapped[int] = mapped_column(init=True)
    stdout: Mapped[str] = mapped_column(init=True)
    stderr: Mapped[str] = mapped_column(init=True)
    cyst_run_id: Mapped[str] = mapped_column(init=True)
    status: Mapped[str] = mapped_column(init=True)

    run_id: Mapped[int] = mapped_column(ForeignKey("challenge_run_statistics.id"), init=True)
    run: Mapped[DBRun] = relationship(back_populates="episodes")


class RunStatus(Enum):
    INIT = auto()
    RUNNING = auto()
    FINISHED = auto()
    ERROR = auto()


@dataclass
class Episode:
    cyst_run_id: str
    stdout: str
    stderr: str
    run: int = -1
    status: RunStatus = RunStatus.RUNNING


@dataclass
class Run:
    specification: RunSpecification
    executor: Optional[ProcessPoolExecutor] = None
    status: RunStatus = RunStatus.INIT
    detail: str = ""
    # Replace with sets?
    running: Set[int] = field(default_factory=set)
    successful: Set[int] = field(default_factory=set)
    error: Set[int] = field(default_factory=set)
    episodes: Dict[int, Episode] = field(default_factory=dict)
    id: int = field(default=-1)
