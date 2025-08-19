from typing import Callable
from .IControllerUnit import IControllerUnit
from .ContecOnOffActivation import ContecOnOffActivation
from .ContecBlindActivation import ContecBlindActivation
from .CommunicationManager import CommunicationManager
from .ContecConectivityConfiguration import ContecConectivityConfiguration
from .ActivationType import ActivationType
from .ContecActivation import ContecActivation
from .RegistersMapping import RegistersMapping
from threading import Lock
from .ITracer import ITracer
from asyncio import Future, Semaphore

class TaskToExecute:
    def __init__(self, functionToPerforme: Callable[[int], int]):
        self.__FunctionToPerforme = functionToPerforme
        self.__TaskToComplete = Future()

    @property
    def FunctionToPerforme(self) -> Callable[[int], int]:
        return self.__FunctionToPerforme

    @property
    def TaskToComplete(self) -> Future:
        return self.__TaskToComplete

class ControllerUnit(IControllerUnit):
    _communicator: CommunicationManager
    _contecConfiguration: ContecConectivityConfiguration
    _activations: list[ContecActivation]
    _lock: Lock
    _tracer: ITracer
    _pendingChangeActivationTasks: list[TaskToExecute]
    _readyToChangeActivationSignal: Semaphore
    ActivationsRegister: int = 0
    NumberOfActivations: int = 8

    def __init__(self, tracer: ITracer, contecConfiguration: ContecConectivityConfiguration, communicator: CommunicationManager, unitId: int) -> None:
        self._lock = Lock()
        self._tracer = tracer
        self.__UnitId = unitId
        self._communicator = communicator
        self._contecConfiguration = contecConfiguration
        self.IsHealthy = False
        self._readyToChangeActivationSignal = Semaphore()
        self._pendingChangeActivationTasks = []
        self._activations = []

    @property
    def UnitId(self) -> int:
        return self.__UnitId

    @property
    def IsHealthy(self) -> bool:
        return self.__IsHealthy

    @IsHealthy.setter
    def IsHealthy(self, var) -> None:
        self.__IsHealthy = var
    
    def AddExistingActivation(self, contecActivation: ContecActivation) -> None:
        self._lock.acquire()
        try:
            self._activations.append(contecActivation)
        finally:
            self._lock.release()

    async def UpdateCurrentStatus(self) -> None:
        registers = await self._communicator.ReadInputRegistersAsync(self.UnitId, RegistersMapping.ActivationsState, 3)
        if len(registers) != 3:
            raise Exception("Unexpected number of registers")
        
        # Saving the current ActivationsRegister so when we need to change the activation state,
        # we will change only the desired state, while leaving the rest of the states as is.
        self.ActivationsRegister = registers[0]
        self._lock.acquire()
        try:
            for activation in self._activations:
                activation.ParseStateRegisters(registers)
        finally:
            self._lock.release()
    
    async def ChangeActivationRegister(self, mask: int, shouldTurnOn: bool) -> None:
        def UpdateRegister(reg: int) -> int:
            if shouldTurnOn:
                return reg | mask
            else:
                return reg & (~mask)
        executer: bool
        myTask = TaskToExecute(UpdateRegister)
        self._lock.acquire()
        try:
            executer = len(self._pendingChangeActivationTasks) == 0
            self._pendingChangeActivationTasks.append(myTask)
        finally:
            self._lock.release()
        
        if executer:
            async with self._readyToChangeActivationSignal:
                pendingChangeActivationTasks: list[TaskToExecute]
                self._lock.acquire()
                try:
                    pendingChangeActivationTasks = self._pendingChangeActivationTasks
                    self._pendingChangeActivationTasks = []
                finally:
                    self._lock.release()
                
                currentRegValue = await self._communicator.ReadInputRegistersAsync(self.UnitId, RegistersMapping.ActivationsState, 1)
                currentRegValue = currentRegValue[0]
                for pendingChangeActivationTask in pendingChangeActivationTasks:
                    currentRegValue = pendingChangeActivationTask.FunctionToPerforme(currentRegValue)
                try:
                    await self.SetRegisterValue(RegistersMapping.ActivationsState, currentRegValue)
                    for pendingChangeActivationTask in pendingChangeActivationTasks:
                        pendingChangeActivationTask.TaskToComplete.set_result(True)
                except Exception as e:
                    for pendingChangeActivationTask in pendingChangeActivationTasks:
                        pendingChangeActivationTask.TaskToComplete.set_exception(e)
        
        await myTask.TaskToComplete
        
    async def SetRegisterValue(self, registerNumber: int, value: int) -> None:
        await self._communicator.WriteSingleRegisterAsync(self.UnitId, registerNumber, value)

    async def DiscoverAsync(self) -> list[ContecActivation]:
        registers: list[int] = await self._communicator.ReadInputRegistersAsync(self.UnitId, 10, self.NumberOfActivations * 2)
        allActivations: list[ContecActivation] = []
        self._lock.acquire()
        try:
            i = 0
            while i < self.NumberOfActivations:
                try:
                    isBlind = registers[1 + (i * 2)] > 0
                    if isBlind:
                        # First, sanity check. For blinds, i must be even number.
                        if (i % 2) != 0:
                            self._tracer.TraceError(f"Try to set up Contec blind with odd activation number {i}.")
                            continue

                        # Make sure we don't already have any entity in the following activation.
                        if any(contecActivation.StartActivationNumber == i + 1 for contecActivation in self._activations):
                            self._tracer.TraceError(f"While trying to set up Contec blind for activation {i}, found already existing activation in the next odd number {i + 1}.")
                            continue

                        activation: ContecActivation = next((activation for activation in self._activations if activation.StartActivationNumber == i), None)
                        if activation != None:
                            # We already have this entity. Just make sure it's of blind type.
                            if activation.ActivationType != ActivationType.Blind:
                                self._tracer.TraceError(f"While discovering blind in activation {i}, we found already existing activation of type {activation.ActivationType}")
                        
                            continue

                        # Add this blind activation.
                        allActivations.append(ContecBlindActivation(self._tracer, i, self))
                        i += 1

                    else:
                        activation: ContecActivation = next((activation for activation in self._activations if activation.StartActivationNumber == i), None)
                        if activation != None:
                            # We already have this entity. Just make sure it's of blind type.
                            if activation.ActivationType != ActivationType.OnOff:
                                self._tracer.TraceError(f"While discovering on-off in activation {i}, we found already existing activation of type {activation.ActivationType}")
                        
                            continue

                        allActivations.append(ContecOnOffActivation(self._tracer, i, self))
                finally:
                    i += 1
            
            # Sanity check - The logic built in a way that we should discover everything once. We can't discover only half of the
            # activations, and later discover the rest. So we should check that if we found something, we don't already have any
            # activation, and vice versa.
            if len(allActivations) != 0 and self._activations != None and len(self._activations) > 0:
                message: str = f"Illegal state! Contec controller {self.UnitId} discovered {allActivations.Count} new activations, while there are already {self._activations.Count} existing activations."
                self._tracer.TraceError(message)
                raise Exception(message)
            
            for contecActivation in allActivations:
                self._activations.append(contecActivation)

        finally:
            self._lock.release()
        
        self._tracer.TraceVerbose(f"Done creating controller {self.UnitId} activations")
        return allActivations

        