import asyncio
import logging
import psutil
import tempfile
from google.protobuf.descriptor_pb2 import FileDescriptorSet
from log.log import get_logger
from pathlib import Path
from reboot.consensus.local_envoy import LocalEnvoy
from rebootdev.aio.types import ApplicationId
from typing import Optional

logger = get_logger(__name__)
logger.setLevel(logging.WARNING)


class ExecutableLocalEnvoy(LocalEnvoy):

    def __init__(
        self,
        *,
        listener_port: int,
        application_id: ApplicationId,
        file_descriptor_set: FileDescriptorSet,
        use_tls: bool,
        certificate: Optional[Path],
        key: Optional[Path],
        debug_mode: bool,
    ):
        self._requested_listener_port = listener_port
        self._listener_port = 0
        self._admin_port = 0
        self._container_id: Optional[str] = None
        self._debug_mode = debug_mode
        if self._debug_mode:
            # TODO(rjh): it's not elegant that we're setting this for the whole
            #            module, although in practice it's not a big deal.
            logger.setLevel(logging.DEBUG)

        # Generate envoy config and write it to temporary files that get
        # cleaned up on .stop(). We copy all files without their metadata
        # to ensure that they are readable by the envoy user.
        self._tmp_envoy_dir = tempfile.TemporaryDirectory()

        # Envoy as a local executable observes the same filesystem that this
        # code does, so the output dir and observed dir are the same.
        self._envoy_dir_path = Path(self._tmp_envoy_dir.name)

        super().__init__(
            # The admin port is for debugging, so limit it to localhost.
            admin_listen_host='127.0.0.1',
            # Since there may be multiple Envoys running on this same host, we
            # must pick the admin port dynamically to avoid conflicts.
            admin_port=0,
            # Envoy will run on the same host as this code, so the xDS server
            # only needs to listen on localhost.
            xds_listen_host='127.0.0.1',
            xds_connect_host='127.0.0.1',
            # The port we run Envoy on is the port the user has requested to
            # send traffic to.
            envoy_port=self._requested_listener_port,
            application_id=application_id,
            file_descriptor_set=file_descriptor_set,
            use_tls=use_tls,
            observed_dir=Path(self._tmp_envoy_dir.name),
        )

        self._envoy_config_path = self._write_envoy_dir(
            # A local executable has the same view of the filesystem as this
            # code does, so the output dir and observed dir are the same.
            output_dir=Path(self._tmp_envoy_dir.name),
            certificate=certificate,
            key=key,
        )

        self._process: Optional[asyncio.subprocess.Process] = None

    @property
    def port(self) -> int:
        """Returns the port of the Envoy proxy.
        """
        if self._listener_port == 0:
            raise ValueError(
                'ExecutableLocalEnvoy.start() must be called before you can get the port'
            )
        return self._listener_port

    async def _start(self):
        command = [
            'envoy',
            '-c',
            str(self._envoy_config_path),
            # We need to disable hot restarts in order to run multiple
            # proxies at the same time otherwise they will clash
            # trying to create a domain socket. See
            # https://www.envoyproxy.io/docs/envoy/latest/operations/cli#cmdoption-base-id
            # for more details.
            '--disable-hot-restart',
            '--log-path',
            f'/tmp/envoy.{self._requested_listener_port}.log',
        ]

        if self._debug_mode:
            command.extend([
                '--log-level',
                'debug',
            ])

        logger.debug(f"Envoy command:\n```\n{' '.join(command)}\n```")
        logger.debug(
            f"Envoy config:\n```\n{self._envoy_config_path.read_text()}\n```"
        )

        self._process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.STDOUT,
            stdout=asyncio.subprocess.PIPE,
            # Envoy must have its configuration directory as its working dir to
            # let our Lua code find the libraries that we've copied into that
            # directory.
            cwd=self._tmp_envoy_dir.name,
        )
        assert self._process.stdout is not None

        # We must now determine the listener port and the admin port that Envoy
        # has come up on (since it picked them both dynamically). There are two
        # ways we could do this:
        #
        # 1. Tail envoy's log file, look for a line that says "admin address",
        #    and parse the port from that line. Then call the admin endpoint's
        #    `/listeners` API and parse the listener port from the response.
        # 2. Use `psutil` to look at the network connections that Envoy has
        #    open, and find the ports that it's listening on that way.
        #
        # The second approach is easier and faster, so we'll use that. The only
        # downside is that the necessary `net_connections()` method is not
        # supported for non-root users on AIX... But we don't support AIX.
        found_admin_port = False
        found_listener_port = False
        while not found_listener_port or not found_admin_port:
            for connection in psutil.Process(self._process.pid
                                            ).net_connections():
                # We're only interested in ports Envoy is listening on.
                if connection.status != "LISTEN":
                    continue

                # The only connection that Envoy will serve on 0.0.0.0 is the
                # listener port.
                if connection.laddr.ip == "0.0.0.0":
                    found_listener_port = True
                    self._listener_port = connection.laddr.port
                else:
                    # The only connection that Envoy will serve NOT on 0.0.0.0
                    # is the admin port.
                    found_admin_port = True
                    self._admin_port = connection.laddr.port

            # The listener port hasn't been opened yet. Give it a moment
            # before looking for it again.
            await asyncio.sleep(0.01)

        logger.info(f"Envoy admin port: {self._admin_port}")
        logger.info(f"Envoy listener port: {self._listener_port}")

        async def _output_logs():

            async def read_stdout():
                assert self._process is not None
                assert self._process.stdout is not None
                while not self._process.stdout.at_eof():
                    yield await self._process.stdout.readline()

            async for line in read_stdout():
                decoded_line = line.decode()

                if self._debug_mode:
                    print(decoded_line)

        self._output_logs_task = asyncio.create_task(
            _output_logs(),
            name=f'_output_logs() in {__name__}',
        )

    async def _stop(self):
        assert self._process is not None
        try:
            self._process.terminate()
            # Wait for the process to terminate, but don't wait too long.
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                # The process still hasn't gracefully terminated. Kill the
                # process. There's no way to ignore that signal, so we can
                # safely do a non-timeout-based `await` for it to finish.
                self._process.kill()
                await self._process.wait()
        except ProcessLookupError:
            # The process already exited. That's fine.
            pass
