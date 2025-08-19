from .ITracer import ITracer
from .IControllerUnit import IControllerUnit
from .ActivationType import ActivationType
from abc import ABC, abstractmethod

class ContecActivation(ABC):
    _tracer: ITracer

    def __init__(self, tracer: ITracer, startActivationNumber: int, controllerUnit: IControllerUnit, activationType: ActivationType) -> None:
        self._tracer = tracer
        self.__StartActivationNumber = startActivationNumber
        self.__ControllerUnit = controllerUnit
        self.__ActivationType = activationType
        self.__IsHealthy = controllerUnit.IsHealthy

    @property
    def Tracer(self) -> ITracer:
        return self._tracer

    @property
    def StartActivationNumber(self) -> int:
        return self.__StartActivationNumber

    @property
    def ControllerUnit(self) -> IControllerUnit:
        return self.__ControllerUnit

    @property
    def ActivationType(self) -> ActivationType:
        return self.__ActivationType

    @property
    def IsHealthy(self) -> bool:
        return self.__IsHealthy

    @abstractmethod
    def ParseStateRegisters(self, stateRegisters: list[int]) -> None:
        '''
            Parsing the state registers when read from the controllers, and update the activation state.
            stateRegisters - Array of 3 ushorts:
                [0] - Represents on/off state and the pusher state (low byte is on/off and high byte is pusher state).
                [1-2] - Represents the blinds opening ratio.
        '''
        pass

    def IsByteOn(data: int, offset: int) -> bool:
        mask = 0x01 << offset
        return (data & mask) > 0
    
    def BitField(n):
        res = [1 if digit=='1' else 0 for digit in bin(n)[2:]]
        return [0 for i in range(8 - len(res))] + res