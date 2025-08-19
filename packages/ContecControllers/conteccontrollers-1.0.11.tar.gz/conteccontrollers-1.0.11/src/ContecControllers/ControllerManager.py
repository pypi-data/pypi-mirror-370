import asyncio
from datetime import timedelta, datetime
from .CommunicationManager import CommunicationManager
from .ContecConectivityConfiguration import ContecConectivityConfiguration
from .ControllersStatusReader import ControllersStatusReader
from .ControllerUnit import ControllerUnit
from .ActivationType import ActivationType
from .ContecOnOffActivation import ContecOnOffActivation
from .ContecBlindActivation import BlindState, ContecBlindActivation
from .ContecPusherActivation import ContecPusherActivation
from .ITracer import ConsoleTracer, ITracer

class ControllerManager:
    _controllerUnits: list[ControllerUnit]
    _controllersStatusReader: ControllersStatusReader
    _contecConectivityConfiguration: ContecConectivityConfiguration
    _communicationManager: CommunicationManager
    _tracer: ITracer

    def __init__(self, tracer: ITracer, contecConectivityConfiguration: ContecConectivityConfiguration) -> None:
        self._tracer = tracer
        self._contecConectivityConfiguration = contecConectivityConfiguration
        self._communicationManager = CommunicationManager(tracer, self._contecConectivityConfiguration.ControllerIp, self._contecConectivityConfiguration.ControllerPort)
        self._controllerUnits = []
        for i in range(self._contecConectivityConfiguration.NumberOfControllers):
            self._controllerUnits.append(ControllerUnit(tracer, self._contecConectivityConfiguration, self._communicationManager, i))
        
        self._controllersStatusReader = ControllersStatusReader(tracer, self._contecConectivityConfiguration, self._controllerUnits)
        self.__OnOffActivations = []
        self.__BlindActivations = []
    
    @property
    def OnOffActivations(self)-> list[ContecOnOffActivation]:
        return self.__OnOffActivations
    
    @property
    def BlindActivations(self)-> list[ContecBlindActivation]:
        return self.__BlindActivations

    @property
    def PusherActivations(self)-> list[ContecPusherActivation]:
        res: list[ContecPusherActivation] = []
        for onOffActivation in self.OnOffActivations:
            res.append(onOffActivation.Pusher)
        for blindActivation in self.BlindActivations:
            res.append(blindActivation.UpPusher)
            res.append(blindActivation.DownPusher)
        return res

    async def CloseAsync(self) -> None:
        await self._communicationManager.CloseAsync()
        await self._controllersStatusReader.Close()
    
    def Init(self) -> None:
        self._controllersStatusReader.Init()
        self._communicationManager.StartListening()

    async def DiscoverEntitiesAsync(self) -> None:
        for controllerUnit in self._controllerUnits:
            newActivations = await controllerUnit.DiscoverAsync()
            self._tracer.TraceInformation(f"Discovered {len(newActivations)} activations in controller {controllerUnit.UnitId}.")
            for activation in newActivations:
                if activation.ActivationType == ActivationType.Blind:
                    self.__BlindActivations.append(activation)
                else:
                    self.__OnOffActivations.append(activation)

    async def IsConnected(self, timeToWaitForConnection: timedelta) -> bool:
        destinationTime: datetime = datetime.now() + timeToWaitForConnection
        while datetime.now() < destinationTime:
            if self._communicationManager.IsConnected:
                return True
            await asyncio.sleep(0.25)
        return False

async def Main() -> None:
    #controllerManager = ControllerManager(ConsoleTracer(), ContecConectivityConfiguration(2, '127.0.0.1', 1234))
    controllerManager = ControllerManager(ConsoleTracer(), ContecConectivityConfiguration(9, '192.168.2.40', 502))
    controllerManager.Init()
    isConnected = await controllerManager.IsConnected(timedelta(seconds=5))
    if not isConnected:
        print("Not Connected!!!")
        await controllerManager.CloseAsync()
        print("Closed")
        return
    await controllerManager.DiscoverEntitiesAsync()

    #await asyncio.sleep(2)
    #print("Closing")
    #await controllerManager.CloseAsync()
    #print("Reopening")
    #controllerManager = ControllerManager(ConsoleTracer(), ContecConectivityConfiguration(9, '192.168.2.40', 502))
    #controllerManager.Init()
    #isConnected = await controllerManager.IsConnected(timedelta(seconds=5))
    #if not isConnected:
    #    print("Not Connected!!!")
    #    await controllerManager.CloseAsync()
    #    print("Closed")
    #    return
    #await controllerManager.DiscoverEntitiesAsync()

    onOffActivations: list[ContecOnOffActivation] = controllerManager.OnOffActivations
    blindActivations: list[ContecBlindActivation] = controllerManager.BlindActivations
    pusherActivations: list[ContecPusherActivation] = controllerManager.PusherActivations
    print(f"onOff - {len(onOffActivations)}. Blind - {len(blindActivations)}")
    import os
    clear = lambda: os.system('cls')

    def PrintStatus():
        clear()
        for onOff in onOffActivations:
            print(f"[OnOff] - {onOff.ControllerUnit.UnitId}-{onOff.StartActivationNumber} - {onOff.IsOn}. Pusher: {onOff.Pusher.IsPushed}")
        for blind in blindActivations:
            print(f"[Blind] - {blind.ControllerUnit.UnitId}-{blind.StartActivationNumber} - {blind.MovingDirection} ({blind.BlindOpeningPercentage}%). Up pusher: {blind.UpPusher.IsPushed}. Down Pusher: {blind.DownPusher.IsPushed}")
    for onOff in onOffActivations:
        def OnOffUpdated(isOn: bool):
            PrintStatus()
            print(f"isOn: {isOn}")
        onOff.SetStateChangedCallback(OnOffUpdated)
    for blind in blindActivations:
        def BlindUpdated(movingDirection: BlindState, blindOpeningPercentage: int):
            PrintStatus()
            print(f"movingDirection: {movingDirection}, blindOpeningPercentage: {blindOpeningPercentage}")
        blind.SetStateChangedCallback(BlindUpdated)
    
    for pusher in pusherActivations:
        def PusherUpdated(isPushed: bool):
            PrintStatus()
            print(f"is pushed: {isPushed}")
        pusher.SetStateChangedCallback(PusherUpdated)
    
    #await TurnOnOneByOne(onOffActivations, blindActivations)
    #await AggresivePlay(onOffActivations, blindActivations)
    #await ManualPlay(onOffActivations, blindActivations)
    await StaticState()

async def AggresivePlay(onOffActivations: list[ContecOnOffActivation], blindActivations: list[ContecBlindActivation]):
    open = True
    for i in range(1000):
        if i % 10 == 0:
            tasks = []
            for onOff in onOffActivations:
                tasks.append(asyncio.create_task(onOff.SetActivationState(open)))

            for blind in blindActivations:
                tasks.append(asyncio.create_task(blind.SetBlindsState(20 if open else 0)))
            
            open = not open
        await asyncio.wait(tasks)
        await asyncio.sleep(1)

async def TurnOnOneByOne(onOffActivations, blindActivations):
    onOffIndex = 0
    blindIndex = 0
    for i in range(1000):
        if (i + 5) % 10 == 0:
            await onOffActivations[onOffIndex].SetActivationState(not onOffActivations[onOffIndex].IsOn)
            onOffIndex += 1
            if onOffIndex == len(onOffActivations):
                onOffIndex = 0
        if i % 10 == 0:
            await blindActivations[blindIndex].SetBlindsState(100 - blindActivations[blindIndex].BlindOpeningPercentage)
            blindIndex += 1
            if blindIndex == len(blindActivations):
                blindIndex = 0

        await asyncio.sleep(2)

async def ManualPlay(onOffActivations, blindActivations):
    onOffIndex = 0
    blindIndex = 0
    for i in range(1000):
        input()
        if (i + 1) % 2 == 0:
            await onOffActivations[onOffIndex].SetActivationState(not onOffActivations[onOffIndex].IsOn)
            onOffIndex += 1
            if onOffIndex == len(onOffActivations):
                onOffIndex = 0
        if i % 2 == 0:
            await blindActivations[blindIndex].SetBlindsState(100 - blindActivations[blindIndex].BlindOpeningPercentage)
            blindIndex += 1
            if blindIndex == len(blindActivations):
                blindIndex = 0

        await asyncio.sleep(2)

async def StaticState():
    for i in range(100000):
        await asyncio.sleep(1)

if __name__ == "__main__":
    import pymodbus
    print(pymodbus.__version__)
    asyncio.run(Main())