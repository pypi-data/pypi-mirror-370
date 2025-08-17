from minjiang_client.languages import lang as lang
from minjiang_client.qc.hamiltonian import DRIVE as DRIVE, DRIVEX as DRIVEX, DRIVEY as DRIVEY, DRIVEZ as DRIVEZ, ON as ON
from minjiang_client.qc.simulator import Simulator as Simulator

class SimulatorMinjiang1Qubit2Level(Simulator):
    f_max_q01: float
    def __init__(self, dt: float) -> None: ...
    def pre_compile_wave_package(self) -> None: ...
