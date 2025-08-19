from abc import ABCMeta, abstractmethod

class ITracer:
    __metaclass__ = ABCMeta

    @abstractmethod
    def TraceVerbose(self, message: str) -> None: raise NotImplementedError

    @abstractmethod
    def TraceInformation(self, message: str) -> None: raise NotImplementedError

    @abstractmethod
    def TraceWarning(self, message: str) -> None: raise NotImplementedError

    @abstractmethod
    def TraceError(self, message: str) -> None: raise NotImplementedError

class ConsoleTracer(ITracer):
    def TraceVerbose(self, message: str) -> None:
        print(message)

    def TraceInformation(self, message: str) -> None:
        print(message)

    @abstractmethod
    def TraceWarning(self, message: str) -> None:
        print(message)

    @abstractmethod
    def TraceError(self, message: str) -> None:
        print(message)