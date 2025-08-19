from abc import ABCMeta, abstractmethod

class IControllerUnit:
    __metaclass__ = ABCMeta

    @abstractmethod
    async def SetRegisterValue(self, registerNumber: int, value: int) -> None: raise NotImplementedError

    @abstractmethod
    async def ChangeActivationRegister(self, mask: int, shouldTurnOn: bool) -> None: raise NotImplementedError

    @property
    def UnitId(self) -> int:
        raise NotImplementedError