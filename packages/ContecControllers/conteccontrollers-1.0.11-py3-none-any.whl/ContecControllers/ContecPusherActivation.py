from typing import Protocol
from .ITracer import ITracer
from .ActivationType import ActivationType
from .ContecActivation import ContecActivation
from .IControllerUnit import IControllerUnit


class StateChangeCallback(Protocol):
    def __call__(
        self, isPressed: bool
    ) -> None:
        """Define StateChangeCallback type."""

class ContecPusherActivation(ContecActivation):
    _stateChangeCallbacks: list[StateChangeCallback]

    def __init__(self, tracer: ITracer, activationNumber: int, controllerUnit: IControllerUnit) -> None:
        super().__init__(tracer, activationNumber, controllerUnit, ActivationType.Pusher)
        self._stateChangeCallbacks = []
        self.__IsPushed = False
    
    @property
    def IsPushed(self) -> bool:
        return self.__IsPushed
    
    def SetStateChangedCallback(self, stateChangeCallback: StateChangeCallback) -> None:
        self._stateChangeCallbacks.append(stateChangeCallback)
    
    def SetNewState(self, isPushed: bool):
        if self.IsPushed != isPushed:
            self.__IsPushed = isPushed
            self.Tracer.TraceInformation(f"Changed the state of pusher activation. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, new pushing state: {isPushed}.")
            for stateChangeCallback in self._stateChangeCallbacks:
                stateChangeCallback(isPushed)
    
    def ParseStateRegisters(self, stateRegisters: list[int]) -> None:
        raise Exception()