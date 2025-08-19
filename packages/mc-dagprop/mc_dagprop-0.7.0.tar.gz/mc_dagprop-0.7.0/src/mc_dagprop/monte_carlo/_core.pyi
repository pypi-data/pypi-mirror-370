# mc_dagprop/monte_carlo/_core.pyi
from collections.abc import Collection, Iterable, Mapping, Sequence

from numpy._typing import NDArray

from mc_dagprop.types import ActivityIndex, ActivityType, EventId, EventIndex, Second

class EventTimestamp:
    """
    Represents the earliest and latest timestamps of an event, and its actual timestamp.
    The actual timestamp is the one that is realized during the simulation.
    """

    earliest: Second
    latest: Second
    actual: Second

    def __init__(self, earliest: Second, latest: Second, actual: Second) -> None: ...

class Event:
    """
    Represents an event (node) with its earliest/latest window and actual timestamp.
    """

    event_id: EventId
    timestamp: EventTimestamp

    def __init__(self, event_id: EventId, timestamp: EventTimestamp) -> None: ...

class Activity:
    """
    Represents an activity (edge) in the DAG, with its minimal duration and type.
    """

    idx: ActivityIndex
    minimal_duration: Second
    activity_type: ActivityType

    def __init__(self, idx: ActivityIndex, minimal_duration: Second, activity_type: ActivityType) -> None: ...

class DagContext:
    """
    Wraps the DAG: a list of events, activities, a precedence list and a
    max?delay. ``precedence_list`` can be in any order; ``Simulator`` sorts it
    topologically and raises ``RuntimeError`` on cycles.
    """

    events: Sequence[Event]
    activities: Mapping[tuple[EventIndex, EventIndex], Activity]
    precedence_list: Sequence[tuple[EventIndex, list[tuple[EventIndex, ActivityIndex]]]]
    max_delay: Second

    def __init__(
        self,
        events: Sequence[Event],
        activities: Mapping[tuple[EventIndex, EventIndex], Activity],
        precedence_list: Sequence[tuple[EventIndex, Sequence[tuple[EventIndex, ActivityIndex]]]],
        max_delay: Second,
    ) -> None: ...

class SimResult:
    """
    The result of one run: realized times, per-activity delays, and causal predecessors.
    """

    realized: NDArray[Second]
    durations: NDArray[Second]
    cause_event: NDArray[EventIndex]

class GenericDelayGenerator:
    """
    Configurable delay generator. Supports per-``activity_type`` distributions:
    constant, exponential, gamma, and empirical (absolute or relative).
    """

    def __init__(self) -> None: ...
    def set_seed(self, seed: int) -> None: ...
    def add_constant(self, activity_type: ActivityType, factor: float) -> None: ...
    def add_exponential(self, activity_type: ActivityType, lambda_: float, max_scale: float) -> None: ...
    def add_gamma(
        self, activity_type: ActivityType, shape: float, scale: float, max_scale: float = float("inf")
    ) -> None: ...
    def add_empirical_absolute(
        self, activity_type: ActivityType, values: Collection[Second], weights: Collection[float]
    ) -> None: ...
    def add_empirical_relative(
        self, activity_type: ActivityType, factors: Collection[Second], weights: Collection[float]
    ) -> None: ...

class Simulator:
    """
    Monte Carlo DAG propagator: run single or batch simulations. ``precedence_list``
    in the provided ``DagContext`` may be in any order; it is sorted topologically
    and a ``RuntimeError`` is raised if cycles are detected.
    """

    def __init__(self, context: DagContext, generator: GenericDelayGenerator) -> None: ...
    def run(self, seed: int) -> SimResult: ...
    def run_many(self, seeds: Iterable[int]) -> list[SimResult]: ...
