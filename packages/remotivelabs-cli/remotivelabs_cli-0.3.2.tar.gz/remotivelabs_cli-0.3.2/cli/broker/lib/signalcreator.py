from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence, TypeVar

import remotivelabs.broker._generated.common_pb2 as common
import remotivelabs.broker._generated.network_api_pb2 as network_api
import remotivelabs.broker._generated.system_api_pb2_grpc as system_api_grpc

T = TypeVar("T")

_logger = logging.getLogger("remotivelabs.SignalCreator")
_MSG_DUPLICATE = "Warning duplicated (namespace.signal): {}, to avoid" + 'ambiguity set "short_names": false in your interfaces.json on {}'


class MetaGetter:
    def __init__(self, proto_message: Any):
        self.meta = proto_message

    def _getDefault(self, field: T, default: Optional[T]) -> T:  # noqa: N802
        if field is not None:
            return field

        if default:
            return default

        raise Exception("Failed to retrieve meta data field")

    def getDescription(self, default: Optional[str] = None) -> str:  # noqa: N802
        """Get protobuffer MetaData field description"""
        return self._getDefault(self.meta.description, default)  # type: ignore

    def getUnit(self, default: Optional[str] = None) -> str:  # noqa: N802
        """Get protobuffer MetaData field unit"""
        return self._getDefault(self.meta.unit, default)  # type: ignore

    def getMax(self, default: Optional[float] = None) -> float:  # noqa: N802
        """Get protobuffer MetaData field max"""
        return self._getDefault(self.meta.max, default)  # type: ignore

    def getMin(self, default: Optional[float] = None) -> float:  # noqa: N802
        """Get protobuffer MetaData field min"""
        return self._getDefault(self.meta.min, default)  # type: ignore

    def getSize(self, default: Optional[int] = None) -> int:  # noqa: N802
        """Get protobuffer MetaData field size"""
        return self._getDefault(self.meta.size, default)  # type: ignore

    def getIsRaw(self, default: Optional[bool] = None) -> bool:  # noqa: N802
        """Get protobuffer MetaData field isRaw"""
        return self._getDefault(self.meta.isRaw, default)  # type: ignore

    def getFactor(self, default: Optional[float] = None) -> float:  # noqa: N802
        """Get protobuffer MetaData field factor"""
        return self._getDefault(self.meta.factor, default)  # type: ignore

    def getOffset(self, default: Optional[float] = None) -> float:  # noqa: N802
        """Get protobuffer MetaData field offset"""
        return self._getDefault(self.meta.offset, default)  # type: ignore

    def getSenders(self, default: Optional[Sequence[str]] = None) -> Sequence[str]:  # noqa: N802
        """Get protobuffer MetaData field sender"""
        return self._getDefault(self.meta.sender, default)

    def getReceivers(self, default: Optional[Sequence[str]] = None) -> Sequence[str]:  # noqa: N802
        """Get protobuffer MetaData field receiver"""
        return self._getDefault(self.meta.receiver, default)

    def getCycleTime(self, default: Optional[float] = None) -> float:  # noqa: N802
        """Get protobuffer MetaData field cycleTime"""
        return self._getDefault(self.meta.cycleTime, default)  # type: ignore

    def getStartValue(self, default: Optional[float] = None) -> float:  # noqa: N802
        """Get protobuffer MetaData field startValue"""
        return self._getDefault(self.meta.startValue, default)  # type: ignore


class SignalCreator:
    """
    Class for prepearing and writing signals via gRPC.
    """

    def __init__(self, system_stub: system_api_grpc.SystemServiceStub, namespaces: List[str] | None = None):
        self._sinfos: Dict[Any, Any] = {}
        self._virtual: List[Any] = []
        self._networks: Dict[Any, Any] = {}
        nss: List[common.NameSpace] = []
        if namespaces is None:
            conf = system_stub.GetConfiguration(common.Empty())
            for ninfo in conf.networkInfo:
                nss.append(ninfo.namespace)
                if ninfo.type == "virtual":
                    self._virtual.append(ninfo.namespace.name)
        else:
            nss = list(map(lambda namespace: common.NameSpace(name=namespace), namespaces))

        for namespace in nss:
            res = system_stub.ListSignals(namespace)
            self._addframes(namespace, res)
            for finfo in res.frame:
                self._add(finfo.signalInfo)
                for sinfo in finfo.childInfo:
                    self._add(sinfo)

    def _addframes(self, namespace: common.NameSpace, res: common.Frames) -> None:
        self._networks[namespace.name] = res

    def _add(self, sinfo: common.SignalInfo) -> None:
        k = (sinfo.id.namespace.name, sinfo.id.name)
        if k in self._sinfos:
            msg = _MSG_DUPLICATE.format(k, sinfo.id.namespace)
            _logger.warning(msg)
        self._sinfos[k] = MetaGetter(sinfo.metaData)

    def get_meta(self, name: str, namespace_name: str) -> MetaGetter:
        """
        Get meta fields for signal or frame
        """

        k = (namespace_name, name)
        if (k not in self._sinfos) and (namespace_name not in self._virtual):
            raise Exception(f"signal not declared (namespace, signal): {k}")
        return self._sinfos[k]  # type: ignore

    def signal(self, name: str, namespace_name: str) -> common.SignalId:
        """
        Create object for signal.
        """

        self.get_meta(name, namespace_name)  # Checks if the signal is present
        return common.SignalId(name=name, namespace=common.NameSpace(name=namespace_name))

    def frames(self, namespace_name: str) -> Sequence[common.SignalId]:
        """
        Get all frames in given namespace
        """

        all_frames = []
        for finfo in self._networks[namespace_name].frame:
            all_frames.append(self.signal(finfo.signalInfo.id.name, namespace_name))
        return all_frames

    def frame_by_signal(self, name: str, namespace_name: str) -> common.SignalId:
        """
        Get frame for the given signal.
        """

        for finfo in self._networks[namespace_name].frame:
            for sinfo in finfo.childInfo:
                if sinfo.id.name == name:
                    return self.signal(finfo.signalInfo.id.name, namespace_name)
        raise Exception(f"signal not declared (namespace, signal): {namespace_name} {name}")

    def signals_in_frame(self, name: str, namespace_name: str) -> Sequence[common.SignalId]:
        """
        Get all signals residing in the frame.
        """

        all_signals = []
        frame = None
        for finfo in self._networks[namespace_name].frame:
            if finfo.signalInfo.id.name == name:
                frame = finfo
                for sinfo in finfo.childInfo:
                    all_signals.append(self.signal(sinfo.id.name, namespace_name))
        assert frame is not None, f"frame {name} does not exist in namespace {namespace_name}"
        return all_signals

    def signal_with_payload(
        self, name: str, namespace_name: str, value_pair: tuple[str, Any], allow_malformed: bool = False
    ) -> network_api.Signal:
        """
        Create value with signal for writing.
        """

        signal = self.signal(name, namespace_name)
        meta = self.get_meta(name, namespace_name)

        key, value = value_pair
        types = ["integer", "double", "raw", "arbitration"]
        if key not in types:
            raise Exception(f"type must be one of: {types}")
        if key == "raw" and allow_malformed is False:
            expected = meta.getSize()
            assert len(value) * 8 == expected, f"payload size missmatch, expected {expected / 8} bytes"
        elif key != "raw":
            # Check bounds if any
            check_min = meta.getMin()
            if (check_min is not None) and (value < check_min):
                _logger.warning(f'Value below minimum value of {check_min} for signal "{name}"')
            check_max = meta.getMax()
            if (check_max is not None) and (value > check_max):
                _logger.warning(f'Value above maximum value of {check_max} for signal "{name}"')

        params = {"id": signal, key: value}
        return network_api.Signal(**params)
