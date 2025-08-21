# flake8: noqa
class ForceProperties:
    srp_coefficient: float
    drag_coefficient: float
    mass: float
    srp_area: float
    drag_area: float
    mean_motion_dot: float
    mean_motion_dot_dot: float
    def __init__(
        self,
        srp_coefficient: float,
        srp_area: float,
        drag_coefficient: float,
        drag_area: float,
        mass: float,
        mean_motion_dot: float,
        mean_motion_dot_dot: float,
    ) -> None: ...
