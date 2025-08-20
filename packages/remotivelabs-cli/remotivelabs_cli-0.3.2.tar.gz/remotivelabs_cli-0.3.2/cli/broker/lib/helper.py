from __future__ import annotations

import hashlib
import itertools
import ntpath
import os
import posixpath
from glob import glob
from logging import getLogger
from typing import Any, BinaryIO, Callable, Generator, Optional, Sequence
from urllib.parse import urlparse

import grpc
import remotivelabs.broker._generated.common_pb2 as common
import remotivelabs.broker._generated.network_api_pb2 as network_api
import remotivelabs.broker._generated.network_api_pb2_grpc as network_api_grpc
import remotivelabs.broker._generated.system_api_pb2 as system_api
import remotivelabs.broker._generated.system_api_pb2_grpc as system_api_grpc
from grpc_interceptor import ClientCallDetails, ClientInterceptor

from cli.utils.console import print_generic_error

log = getLogger(__name__)


class HeaderInterceptor(ClientInterceptor):
    def __init__(self, header_dict: dict[str, str]):
        self.header_dict = header_dict

    def intercept(
        self,
        method: Callable[[Any, ClientCallDetails], Any],
        request_or_iterator: Any,
        call_details: grpc.ClientCallDetails,
    ) -> Any:
        new_details = ClientCallDetails(
            call_details.method,
            call_details.timeout,
            self.header_dict.items(),  # type: ignore[arg-type]
            call_details.credentials,
            call_details.wait_for_ready,
            call_details.compression,
        )

        return method(request_or_iterator, new_details)


def create_channel(url: str, x_api_key: Optional[str] = None, authorization_token: Optional[str] = None) -> grpc.Channel:
    """
    Create communication channels for gRPC calls.
    """

    parsed_url = urlparse(url)
    if parsed_url.hostname is None:
        msg = f"invalid url {url}, missing hostname"
        raise ValueError(msg)

    if parsed_url.scheme == "https":
        creds = grpc.ssl_channel_credentials(root_certificates=None, private_key=None, certificate_chain=None)
        channel = grpc.secure_channel(parsed_url.hostname + ":" + str(parsed_url.port or "443"), creds)
    else:
        addr = parsed_url.hostname + ":" + str(parsed_url.port or "50051")
        channel = grpc.insecure_channel(addr)

    if x_api_key is None and authorization_token is None:
        return channel

    if x_api_key is not None:
        return grpc.intercept_channel(channel, HeaderInterceptor({"x-api-key": x_api_key}))

    # Adding both x-api-key (old) and authorization header for compatibility
    return grpc.intercept_channel(
        channel,
        HeaderInterceptor(
            {
                "x-api-key": authorization_token,  # type: ignore
                "authorization": f"Bearer {authorization_token}",
            }
        ),
    )


def publish_signals(
    client_id: common.ClientId,
    stub: network_api_grpc.NetworkServiceStub,
    signals_with_payload: Sequence[network_api.Signal],
    frequency: int = 0,
) -> None:
    """
    Publish array of values for signals
    """

    publisher_info = network_api.PublisherConfig(
        clientId=client_id,
        signals=network_api.Signals(signal=signals_with_payload),
        frequency=frequency,
    )

    try:
        stub.PublishSignals(publisher_info)
    except grpc._channel._Rendezvous as err:  # type:ignore[attr-defined]
        log.error(err)


def printer(signals: Sequence[common.SignalId]) -> None:
    """
    Debug printing of received array of signal with values.
    """

    for signal in signals:
        log.info(f"{signal} {signal.namespace.name}")


def get_sha256(path: str) -> str:
    """
    Calculate SHA256 for a file.
    """

    with open(path, "rb") as f:
        b = f.read()  # read entire file as bytes
        return hashlib.sha256(b).hexdigest()


def generate_data(file: BinaryIO, dest_path: str, chunk_size: int, sha256: str) -> Generator[system_api.FileUploadRequest, None, None]:
    for x in itertools.count(start=0):
        if x == 0:
            file_description = system_api.FileDescription(sha256=sha256, path=dest_path)
            yield system_api.FileUploadRequest(fileDescription=file_description)
        else:
            buf = file.read(chunk_size)
            if not buf:
                break
            yield system_api.FileUploadRequest(chunk=buf)


def upload_file(system_stub: system_api_grpc.SystemServiceStub, path: str, dest_path: str) -> None:
    """
    Upload single file to internal storage on broker.
    """

    sha256 = get_sha256(path)
    log.debug(f"SHA256 for file {path}: {sha256}")
    with open(path, "rb") as file:
        # make sure path is unix style (necessary for windows, and does no harm om
        # linux)
        upload_iterator = generate_data(file, dest_path.replace(ntpath.sep, posixpath.sep), 1000000, sha256)
        response = system_stub.UploadFile(upload_iterator, compression=grpc.Compression.Gzip)
        log.debug(f"Uploaded {path} with response {response}")


def download_file(system_stub: system_api_grpc.SystemServiceStub, path: str, dest_path: str) -> None:
    """
    Download file from Broker remote storage.
    """

    with open(dest_path, "wb") as file:
        for response in system_stub.BatchDownloadFiles(
            system_api.FileDescriptions(fileDescriptions=[system_api.FileDescription(path=path.replace(ntpath.sep, posixpath.sep))])
        ):
            assert not response.HasField("errorMessage"), f"Error uploading file, message is: {response.errorMessage}"
            file.write(response.chunk)


def upload_folder(system_stub: system_api_grpc.SystemServiceStub, folder: str) -> None:
    """
    Upload directory and its content to Broker remote storage.
    """

    files = [y for x in os.walk(folder) for y in glob(os.path.join(x[0], "*")) if not os.path.isdir(y)]
    assert len(files) != 0, "Specified upload folder is empty or does not exist"
    for file in files:
        upload_file(system_stub, file, file.replace(folder, ""))


def reload_configuration(
    system_stub: system_api_grpc.SystemServiceStub,
) -> None:
    """
    Trigger reload of configuration on Broker.
    """

    request = common.Empty()
    response = system_stub.ReloadConfiguration(request, timeout=60000)
    log.debug(f"Reload configuration with response {response}")


def check_license(
    system_stub: system_api_grpc.SystemServiceStub,
) -> None:
    """
    Check license to Broker. Throws exception if failure.
    """
    status = system_stub.GetLicenseInfo(common.Empty()).status
    assert status == system_api.LicenseStatus.VALID, f"Check your license, status is: {status}"


def act_on_signal(  # noqa: PLR0913
    client_id: common.ClientId,
    network_stub: network_api_grpc.NetworkServiceStub,
    sub_signals: Sequence[common.SignalId],
    on_change: bool,
    fun: Callable[[Sequence[network_api.Signal]], None],
    on_subscribed: Optional[Callable[..., None]] = None,
) -> None:
    """
    Bind callback to be triggered when receiving any of the specified signals.
    """

    log.debug("Subscription started")

    sub_info = network_api.SubscriberConfig(
        clientId=client_id,
        signals=network_api.SignalIds(signalId=sub_signals),
        onChange=on_change,
    )
    try:
        subscripton = network_stub.SubscribeToSignals(sub_info, timeout=None)
        if on_subscribed:
            on_subscribed(subscripton)
        log.debug("Waiting for signal...")
        for subs_counter in subscripton:
            fun(subs_counter.signal)

    except grpc.RpcError as e:
        # Only try to cancel if cancel was not already attempted
        if e.code() != grpc.StatusCode.CANCELLED:
            try:
                subscripton.cancel()
                print_generic_error("A gRPC error occurred:")
                print_generic_error(str(e))
            except grpc.RpcError:
                pass
    except grpc._channel._Rendezvous as err:  # type:ignore[attr-defined]
        log.error(err)
    # reload, alternatively non-existing signal
    log.debug("Subscription terminated")


def act_on_scripted_signal(  # noqa: PLR0913
    client_id: common.ClientId,
    network_stub: network_api_grpc.NetworkServiceStub,
    script: bytes,
    on_change: bool,
    fun: Callable[[Sequence[network_api.Signal]], None],
    on_subscribed: Optional[Callable[..., None]] = None,
) -> None:
    """
    Bind callback to be triggered when receiving any of the specified signals.
    """

    log.debug("Subscription with mapping code started...")

    sub_info = network_api.SubscriberWithScriptConfig(
        clientId=client_id,
        script=script,
        onChange=on_change,
    )
    try:
        subscription = network_stub.SubscribeToSignalWithScript(sub_info, timeout=None)
        if on_subscribed:
            on_subscribed(subscription)
        log.debug("Waiting for signal...")
        for subs_counter in subscription:
            fun(subs_counter.signal)

    except grpc.RpcError as e:
        try:
            subscription.cancel()
            print_generic_error("A gRPC error occurred:")
            print_generic_error(str(e))
        except grpc.RpcError:
            pass

    except grpc._channel._Rendezvous as err:  # type:ignore[attr-defined]
        log.error(err)
    # reload, alternatively non-existing signal
    log.debug("Subscription terminated")
