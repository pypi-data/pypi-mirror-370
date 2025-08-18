from typing import TYPE_CHECKING

from velopix import ReconstructionAlgorithms as _mod

TrackFollowing: type = _mod.TrackFollowing
GraphDFS: type = _mod.GraphDFS
SearchByTripletTrie: type = _mod.SearchByTripletTrie

if TYPE_CHECKING:
    from typing import List, Tuple, Optional
    from ..DetectorEvent import Hit, Event, Track

    class TrackFollowing:
        def __init__(
            self,
            max_slopes: Optional[Tuple[float, float]] = ...,
            max_tolerance: Optional[Tuple[float, float]] = ...,
            max_scatter: Optional[float] = ...,
            min_track_length: Optional[int] = ...,
            min_strong_track_length: Optional[int] = ...
        ) -> None: ...

        def are_compatible(self, hit0: Hit, hit1: Hit) -> bool: ...
        def check_tolerance(self, hit0: Hit, hit1: Hit, hit2: Hit) -> bool: ...
        def solve(self, event: Event) -> List[Track]: ...
        def solve_batch(self, events: List[Event]) -> List[Track]: ...

    class GraphDFS:
        def __init__(
            self,
            max_slopes: Optional[Tuple[float, float]] = ...,
            max_tolerance: Optional[Tuple[float, float]] = ...,
            max_scatter: Optional[float] = ...,
            minimum_root_weight: Optional[int] = ...,
            weight_assignment_iterations: Optional[int] = ...,
            allowed_skip_modules: Optional[int] = ...,
            allow_cross_track: Optional[bool] = ...,
            clone_ghost_killing: Optional[bool] = ...
        ) -> None: ...

        def solve(self, event: Event) -> List[Track]: ...
        def solve_batch(self, events: List[Event]) -> List[Track]: ...

    class SearchByTripletTrie:
        def __init__(
            self,
            max_scatter: Optional[float] = ...,
            min_strong_track_length: Optional[int] = ...,
            allowed_missed_modules: Optional[int] = ...
        ) -> None: ...

        def solve(self, event: Event) -> List[Track]: ...
        def solve_batch(self, events: List[Event]) -> List[Track]: ...
