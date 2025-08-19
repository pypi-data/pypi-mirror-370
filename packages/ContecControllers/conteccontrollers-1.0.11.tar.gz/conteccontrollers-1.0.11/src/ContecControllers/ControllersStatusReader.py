import asyncio
from .ControllerUnit import ControllerUnit
from .Conductor import Conductor, Ticket
from .ContecConectivityConfiguration import ContecConectivityConfiguration
from .ITracer import ITracer

class ControllersStatusReader:
    _tracer: ITracer
    _controllerUnits: list[ControllerUnit]
    _contecConfiguration: ContecConectivityConfiguration
    _conductor: Conductor
    _currentControllerIndex: int
    _workerTask: asyncio.Task

    def __init__(self, tracer: ITracer, contecConfiguration: ContecConectivityConfiguration, controllerUnits: list[ControllerUnit]) -> None:
        self._tracer = tracer
        self._controllerUnits = controllerUnits
        self._contecConfiguration = contecConfiguration
        self._conductor = Conductor()
        self._currentControllerIndex = 0

    def Init(self) -> None:
        self._workerTask = asyncio.create_task(self._UpdateNextController())

    async def Close(self) -> None:
        await self._conductor.Close()
        if self._workerTask != None:
            self._workerTask.cancel()

    async def _UpdateNextController(self) -> None:
        while True:
            try:
                ticket: Ticket = self._conductor.TryObtainTicket()
                if ticket == None:
                    self._tracer.TraceInformation("Conductor closed")
                    return
                
                with ticket:
                    unit: ControllerUnit = self._controllerUnits[self._currentControllerIndex]
                    await unit.UpdateCurrentStatus()
                    self._currentControllerIndex += 1
                    if self._currentControllerIndex >= self._contecConfiguration.NumberOfControllers:
                        self._currentControllerIndex = 0
            except Exception as ex:
                self._tracer.TraceError(f"Failed to read controller {self._currentControllerIndex} status: {ex}")
            
            await asyncio.sleep(0.05)

