from enum import Enum
from typing import Protocol

from .ITracer import ITracer
from .IControllerUnit import IControllerUnit
from .ActivationType import ActivationType
from .ContecActivation import ContecActivation
from .RegistersMapping import RegistersMapping
from .ContecPusherActivation import ContecPusherActivation

class BlindState(Enum):
    Stop = 0,
    MovingUp = 1,
    MovingDown = 2

class StateChangeCallback(Protocol):
    def __call__(
        self, movingDirection: BlindState, blindOpeningPercentage: int
    ) -> None:
        """Define StateChangeCallback type."""

class ContecBlindActivation(ContecActivation):
    _stateChangeCallbacks: list[StateChangeCallback]

    def __init__(self, tracer: ITracer, activationNumber: int, controllerUnit: IControllerUnit) -> None:
        super().__init__(tracer, activationNumber, controllerUnit, ActivationType.Blind)
        self._stateChangeCallbacks = []
        self.__BlindOpeningPercentage = 0
        self.__MovingDirection = BlindState.Stop
        self.__UpPusher = ContecPusherActivation(tracer, activationNumber, controllerUnit)
        self.__DownPusher = ContecPusherActivation(tracer, activationNumber + 1, controllerUnit)
    
    @property
    def BlindOpeningPercentage(self) -> int:
        return self.__BlindOpeningPercentage
    
    @property
    def MovingDirection(self) -> BlindState:
        return self.__MovingDirection

    @property
    def UpPusher(self) -> ContecPusherActivation:
        return self.__UpPusher

    @property
    def DownPusher(self) -> ContecPusherActivation:
        return self.__DownPusher

    def SetStateChangedCallback(self, stateChangeCallback: StateChangeCallback)-> None:
        self._stateChangeCallbacks.append(stateChangeCallback)

    def SetNewState(self, movingDirection: BlindState, blindOpeningPercentage: int) -> None:
        if self.MovingDirection != movingDirection or self.BlindOpeningPercentage != blindOpeningPercentage:
            self.__MovingDirection = movingDirection
            self.__BlindOpeningPercentage = blindOpeningPercentage
            self.Tracer.TraceInformation(f"Changed the state of Blind activation. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, moving direction: {movingDirection}, opening percentage: {blindOpeningPercentage}.")
            for stateChangeCallback in self._stateChangeCallbacks:
                stateChangeCallback(movingDirection, blindOpeningPercentage)

    async def SetBlindsState(self, openingPercent: int):
        if openingPercent > 100:
            raise Exception("The opening percentage can't be greater then 100%.")

        if openingPercent == self.BlindOpeningPercentage:
            # Nothing to do.
            return

        self.Tracer.TraceInformation(f"Requesting to change Blind activation. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, requested opening: {openingPercent}.")
        blindSetValueRegister: int = int(RegistersMapping.FirstBlindsOpeningRequest + (self.StartActivationNumber / 2))
        await self.ControllerUnit.SetRegisterValue(blindSetValueRegister, openingPercent)
        self.Tracer.TraceInformation(f"Request to change Blind activation is done. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, requested opening: {openingPercent}.")

    def ParseStateRegisters(self, stateRegisters: list[int]) -> None:
        nextActivationNumber: int = self.StartActivationNumber + 1
        activationsPushersState, activationsOnOffState = stateRegisters[0].to_bytes(2, "big")
        self.UpPusher.SetNewState(ContecActivation.IsByteOn(activationsPushersState, self.StartActivationNumber))
        self.DownPusher.SetNewState(ContecActivation.IsByteOn(activationsPushersState, nextActivationNumber))
        additionalStateBytes: list[int] = stateRegisters[int(1 + (self.StartActivationNumber / 4))].to_bytes(2, "little") # if StartActivationNumber is in range 0-8, the indexes will be 1,1,1,1,2,2,2,2
        openingRatio: int = additionalStateBytes[int(int(self.StartActivationNumber / 2) % 2)] # if StartActivationNumber is in range 0-8, the indexes will be 0,0,1,1,0,0,1,1
        blindState: BlindState = BlindState.MovingUp if ContecActivation.IsByteOn(activationsOnOffState, self.StartActivationNumber) else BlindState.MovingDown if ContecActivation.IsByteOn(activationsOnOffState, nextActivationNumber) else BlindState.Stop
        self.SetNewState(blindState, openingRatio)
