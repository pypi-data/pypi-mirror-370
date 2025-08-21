from abc import ABC, abstractmethod


class ProtocolInfos(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def factory_id(self) -> str: ...

    @abstractmethod
    def get_token_infos(self) -> dict[str, int]: ...
