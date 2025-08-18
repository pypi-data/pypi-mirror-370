from typing import List, Optional

class Hit:
    id: int
    x: float
    y: float
    z: float
    t: float
    module_number: int
    with_t: bool

    def __init__(
        self,
        x: float,
        y: float,
        z: float,
        hit_id: int,
        module: Optional[int] = ...,
        t: Optional[float] = ...,
        with_t: Optional[bool] = ...
    ) -> None: ...

class Track:
    hits: List[Hit]
    missed_last_module: bool
    missed_penultimate_module: bool

    def __init__(self, hits: List[Hit]) -> None: ...
    def add_hit(self, hit: Hit) -> None: ...

class Module:
    module_number: int
    z: float
    hit_start_index: int
    hit_end_index: int
    global_hits: List[Hit]

    def __init__(self, module_number: int, z: float, hit_start_index: int, hit_end_index: int, global_hits: List[Hit]) -> None: ...
    def hits(self) -> List[Hit]: ...

class Event:
    description: str
    montecarlo: object
    module_prefix_sum: List[int]
    number_of_hits: int
    module_zs: List[List[float]]
    hits: List[Hit]
    modules: List[Module]

    def __init__(self, json_data: object) -> None: ...