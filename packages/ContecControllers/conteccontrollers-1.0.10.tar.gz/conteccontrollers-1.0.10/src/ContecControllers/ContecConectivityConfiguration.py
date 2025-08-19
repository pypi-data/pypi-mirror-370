class ContecConectivityConfiguration:

    def __init__(self, numberOfControllers: int, controllerIp: str, controllerPort: int) -> None:
        self.__NumberOfControllers = numberOfControllers
        self.__ControllerIp = controllerIp
        self.__ControllerPort = controllerPort

    @property
    def NumberOfControllers(self)-> int:
        return self.__NumberOfControllers

    @property
    def ControllerIp(self)-> str:
        return self.__ControllerIp

    @property
    def ControllerPort(self)-> int:
        return self.__ControllerPort