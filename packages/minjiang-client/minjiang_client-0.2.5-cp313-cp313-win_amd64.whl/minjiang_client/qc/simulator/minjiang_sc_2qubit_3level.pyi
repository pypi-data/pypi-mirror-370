from minjiang_client.languages import lang as lang
from minjiang_client.qc.hamiltonian import CREATE as CREATE, DESTORY as DESTORY, DRIVE as DRIVE, DRIVEX as DRIVEX, DRIVEY as DRIVEY, DRIVEZ as DRIVEZ, DUFF as DUFF, ON as ON
from minjiang_client.qc.simulator import Simulator as Simulator

class SimulatorMinjiang2Qubit3Level(Simulator):
    def __init__(self, dt: float) -> None: ...
    def pre_compile_wave_package(self) -> None: ...
