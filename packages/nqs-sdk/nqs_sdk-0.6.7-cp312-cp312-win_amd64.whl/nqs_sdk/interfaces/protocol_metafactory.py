from abc import ABC, abstractmethod

from nqs_sdk.bindings.protocols.protocol_infos import ProtocolInfos
from nqs_sdk.interfaces.protocol_factory import ProtocolFactory


class ProtocolMetaFactory(ABC):
    @abstractmethod
    def id(self) -> str:
        pass

    @abstractmethod
    def get_config(self) -> dict:
        pass

    @abstractmethod
    def get_factories(self) -> list[ProtocolFactory]:
        pass

    @abstractmethod
    def register_protocol(self, protocol: ProtocolInfos) -> None:
        pass
