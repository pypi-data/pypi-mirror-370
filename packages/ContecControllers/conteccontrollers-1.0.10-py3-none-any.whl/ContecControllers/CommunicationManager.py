from asyncio import events
from threading import Lock, Thread
from .Conductor import Conductor
from typing import Callable
from pymodbus.client import ModbusTcpClient
import asyncio
from queue import Queue
from pymodbus.exceptions import ModbusIOException
import time
import _thread
from .ITracer import ConsoleTracer, ITracer

class TaskToExecute:
    def __init__(self, functionToPerforme: Callable[[], any]):
        self.__FunctionToPerforme = functionToPerforme
        self.__loop = events.get_event_loop()
        self.__TaskToComplete = asyncio.Future()

    @property
    def FunctionToPerforme(self) -> Callable[[], any]:
        return self.__FunctionToPerforme

    @property
    def Loop(self) -> events.AbstractEventLoop:
        return self.__loop

    @property
    def TaskToComplete(self) -> asyncio.Future:
        return self.__TaskToComplete

class CommunicationManager:
    _tracer: ITracer
    _pendingTasks = Queue
    _controllersIp: str
    _controllersPort: int
    _modbusTcpClient: ModbusTcpClient
    _conductor: Conductor
    _lock: Lock
    _currentExecutingTask: TaskToExecute
    _communicationThread: Thread

    def __init__(self, tracer: ITracer, controllersIp: str, controllersPort: int) -> None:
        self._tracer = tracer
        self.__IsConnected = False
        self._controllersIp = controllersIp
        self._controllersPort = controllersPort
        self._modbusTcpClient = ModbusTcpClient(self._controllersIp, port=self._controllersPort, timeout=0.75)
        self._conductor = Conductor()
        self._pendingTasks = Queue()
        self._lock = Lock()
        self._currentExecutingTask = None
    
    @property
    def IsConnected(self)-> bool:
        return self.__IsConnected

    def StartListening(self) -> None:
        self._communicationThread = Thread(target=self._ExecutePendingCommand, name="ContecCommunication")
        self._communicationThread.start()

    async def ReadInputRegistersAsync(self, slaveAddress: int, startAddress: int, numberOfPoints: int) -> list[int]:
        result = [None]
        func = lambda: self._ReadInputRegisters(slaveAddress, startAddress, numberOfPoints, result)
        taskToExecute = TaskToExecute(func)
        self._lock.acquire()
        try:
            self._pendingTasks.put(taskToExecute)
        finally:
            self._lock.release()
        await taskToExecute.TaskToComplete
        return result[0]
    
    async def WriteSingleRegisterAsync(self, slaveAddress, regAddress, newRegValue) -> None:
        func = lambda: self._WriteSingleRegisterAsync(slaveAddress, regAddress, newRegValue)
        taskToExecute = TaskToExecute(func)
        self._lock.acquire()
        try:
            self._pendingTasks.put(taskToExecute)
        finally:
            self._lock.release()
        await taskToExecute.TaskToComplete

    async def CloseAsync(self) -> None:
        self._tracer.TraceInformation("Closing communication manager.")
        await self._conductor.Close()
        self._communicationThread.join()
        if self._modbusTcpClient.is_socket_open():
            self._modbusTcpClient.close()

        cancelMessage: str = "Communication closed"
        while not self._pendingTasks.empty:
            taskToExecute: TaskToExecute = self._pendingTasks.get()
            taskToExecute.TaskToComplete.cancel(cancelMessage)
        
        if self._currentExecutingTask != None:
            self._currentExecutingTask.TaskToComplete.cancel(cancelMessage)
        
        self._tracer.TraceInformation("Communication manager closed.")

    def _ReadInputRegisters(self, slaveAddress: int, startAddress: int, numberOfPoints: int, result: list) -> None:
        res = self._modbusTcpClient.read_holding_registers(startAddress, count=numberOfPoints, device_id=(slaveAddress + 1))
        if type(res) is ModbusIOException:
            raise res
        result[0] = res.registers

    def _WriteSingleRegisterAsync(self, slaveAddress, regAddress, newRegValue) -> None:
        res = self._modbusTcpClient.write_register(regAddress, newRegValue, device_id=(slaveAddress + 1))
        if type(res) is ModbusIOException:
            raise res

    def _ExecutePendingCommand(self) -> None:
        numberOfFailures: int = 0
        while True:
            try:
                time.sleep(0.03) # 30 ms
                ticket = self._conductor.TryObtainTicket()
                if ticket == None:
                    self._tracer.TraceInformation("Communication manager got not ticker from Conductor. Stop listening...")
                    return
                with ticket:
                    self._lock.acquire()
                    try:
                        self._currentExecutingTask = self._pendingTasks.get_nowait()
                    finally:
                        self._lock.release()
                    if self._currentExecutingTask == None:
                        continue
                    while not self._modbusTcpClient.is_socket_open():
                        self.__IsConnected = False
                        if self.IsClosed():
                            return
                        if not self._modbusTcpClient.connect():
                            self._tracer.TraceError("Failed to connect to Contec controllers")
                            time.sleep(1)
                        else:
                            self._tracer.TraceInformation("connected to Contec controllers")
                            time.sleep(0.2)

                    self.__IsConnected = True
                    try:
                        self._currentExecutingTask.FunctionToPerforme()
                        self._currentExecutingTask.Loop.call_soon_threadsafe(
                            self._currentExecutingTask.TaskToComplete.set_result, True
                        )
                        numberOfFailures = 0
                    except Exception as e: 
                        if (type(e).__name__ == 'ConnectionResetError'):
                            self._modbusTcpClient.close()

                        numberOfFailures += 1
                        if (numberOfFailures > 3):
                            self._tracer.TraceError(f"Task failed with exception: {e}")                        
                        self._lock.acquire()
                        try:
                            self._pendingTasks.put(self._currentExecutingTask)
                        finally:
                            self._lock.release()
                    finally:
                        self._currentExecutingTask = None
            except Exception as e:
                pass
    
    def IsClosed(self):
        ticket = self._conductor.TryObtainTicket()
        if ticket == None:
            return True
        with ticket:
            return False

async def Main():
    communicationManager = CommunicationManager(ConsoleTracer(), '127.0.0.1', 1234)
    communicationManager.StartListening()
    for i in range(1000):
        await communicationManager.WriteSingleRegisterAsync(1, 26, i % 10)
        res = await communicationManager.ReadInputRegistersAsync(1, 26, 3)
        print(f"got result {i} - {res}")
        time.sleep(1)
    await communicationManager.CloseAsync()
    print("Done")
    await asyncio.sleep(5)
    print("Done5")

if __name__ == "__main__":
    asyncio.run(Main())