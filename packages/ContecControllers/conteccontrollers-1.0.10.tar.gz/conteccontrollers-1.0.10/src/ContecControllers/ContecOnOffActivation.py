
from typing import Protocol
from .ITracer import ITracer
from .ContecActivation import ContecActivation
from .ActivationType import ActivationType
from .IControllerUnit import IControllerUnit
from .ContecPusherActivation import ContecPusherActivation

class StateChangeCallback(Protocol):
    def __call__(
        self, isOn: bool
    ) -> None:
        """Define StateChangeCallback type."""

class ContecOnOffActivation(ContecActivation):
    _stateChangeCallbacks: list[StateChangeCallback]

    def __init__(self, tracer: ITracer, activationNumber: int, controllerUnit: IControllerUnit) -> None:
        super().__init__(tracer, activationNumber, controllerUnit, ActivationType.OnOff)
        self._stateChangeCallbacks = []
        self.__IsOn = False
        self.__Pusher = ContecPusherActivation(tracer, activationNumber, controllerUnit)

    @property
    def IsOn(self) -> bool:
        return self.__IsOn

    @property
    def Pusher(self) -> ContecPusherActivation:
        return self.__Pusher

    def SetStateChangedCallback(self, stateChangeCallback: StateChangeCallback) -> None:
        self._stateChangeCallbacks.append(stateChangeCallback)
    
    def SetNewState(self, isOn: bool):
        if self.IsOn != isOn:
            self.Tracer.TraceInformation(f"Changed the state of OnOff activation. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, new state: {isOn}.")
            self.__IsOn = isOn
            for stateChangeCallback in self._stateChangeCallbacks:
                stateChangeCallback(isOn)
        
    async def SetActivationState(self, isOn: bool) -> None:
        self.Tracer.TraceInformation(f"Requesting to change OnOff activation. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, requested state: {isOn}.")
        mask: int = 1 << self.StartActivationNumber
        await self.ControllerUnit.ChangeActivationRegister(mask, isOn)
        self.Tracer.TraceInformation(f"Request to change OnOff activation is done. Controller: {self.ControllerUnit.UnitId}, Activation: {self.StartActivationNumber}, requested state: {isOn}.")

    def ParseStateRegisters(self, stateRegisters: list[int]) -> None:
        activationsPushersState, activationsOnOffState = stateRegisters[0].to_bytes(2, "big")
        PusherPressed: bool = ContecActivation.IsByteOn(activationsPushersState, self.StartActivationNumber)
        self.Pusher.SetNewState(PusherPressed)
        isOn: bool = ContecActivation.IsByteOn(activationsOnOffState, self.StartActivationNumber)
        self.SetNewState(isOn)