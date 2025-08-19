import asyncio
from asyncio import events
from threading import Lock

class Conductor:
    _liveTickets: list
    _closed: bool
    _lock: Lock
    _loop: events.AbstractEventLoop

    def __init__(self, loop: events.AbstractEventLoop = None) -> None:
        self._liveTickets = []
        self._closed = False
        self._lock = Lock()
        if loop is None:
            self._loop = events.get_event_loop()
        else:
            self._loop = loop

    def TryObtainTicket(self):
        self._lock.acquire()
        try:
            if self._closed:
                return
            newTicket = Ticket(self)
            self._liveTickets.append(newTicket)
            return newTicket
        finally:
            self._lock.release()

    def ObtainTicket(self):
        res = self.TryObtainTicket()
        if res == None:
            raise Exception("Conductor closed.")

        return res

    async def Close(self) -> None:
        self._closed = True
        self._lock.acquire()
        allLiveTasks = []
        try:
            for ticket in self._liveTickets:
                allLiveTasks.append(ticket.TicketTaskSource)
        finally:
            self._lock.release()
        
        if len(allLiveTasks) != 0:
            await asyncio.wait(allLiveTasks)

class Ticket:
    _parentConductor: Conductor

    def __init__(self, parentConductor: Conductor) -> None:
        self._parentConductor = parentConductor
        self.__TicketTaskSource = asyncio.Future(loop = parentConductor._loop)

    @property
    def TicketTaskSource(self)-> asyncio.Future:
        return self.__TicketTaskSource

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        self._parentConductor._loop.call_soon_threadsafe(self.TicketTaskSource.set_result, True)
        self._parentConductor._lock.acquire()
        try:
            self._parentConductor._liveTickets.remove(self)
        finally:
            self._parentConductor._lock.release()


async def Main():
    conductor = Conductor()
    with conductor.ObtainTicket():
        print("Inside")
    await conductor.Close()
    print("after")

if __name__ == "__main__":
    asyncio.run(Main())

