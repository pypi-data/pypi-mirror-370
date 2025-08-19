import argparse
import base64
import json
import tempfile
import traceback
from enum import Enum
from pathlib import Path
from rbt.cloud.v1alpha1.application.application_rbt import (
    Application,
    ConcurrentModificationError,
    InvalidInputError,
    Status,
)
from rbt.cloud.v1alpha1.auth.auth_rbt import APIKey
from rbt.cloud.v1alpha1.logs.logs_pb2 import Source
from rbt.v1alpha1.errors_pb2 import (
    PermissionDenied,
    StateAlreadyConstructed,
    StateNotConstructed,
    Unauthenticated,
    Unavailable,
)
from reboot.cli import terminal
from reboot.cli.commands import run_command
from reboot.cli.rc import ArgumentParser, SubcommandParser
from reboot.cloud.api_keys import (
    InvalidAPIKeyBearerToken,
    parse_api_key_bearer_token,
)
from reboot.naming import (
    QualifiedApplicationName,
    make_qualified_application_name_from_user_id_and_application_name,
)
from rebootdev.aio.aborted import Aborted
from rebootdev.aio.backoff import Backoff
from rebootdev.aio.external import ExternalContext
from rebootdev.aio.types import ApplicationId
from rebootdev.time import DateTimeWithTimeZone
from typing import Optional

DEFAULT_REBOOT_CLOUD_URL = "https://cloud.prod1.rbt.cloud:9991"

_API_KEY_FLAG = '--api-key'


class SourceType(Enum):
    CONSENSUS = 'consensus'
    CONFIG = 'config'
    ALL = 'all'


def add_cloud_options(subcommand: SubcommandParser, *, api_key_required: bool):
    """Add flags common to all `rbt` commands that interact with the cloud."""
    # TODO: Consider moving these to flags on the `cloud` subcommand using #3845

    subcommand.add_argument(
        '--cloud-url',
        type=str,
        help="the URL of the Reboot cloud API",
        default=DEFAULT_REBOOT_CLOUD_URL,
        non_empty_string=True,
    )
    # TODO: This should probably be read from a file by default.
    subcommand.add_argument(
        _API_KEY_FLAG,
        type=str,
        help="the API key to use to connect to the Reboot Cloud API",
        default=None,
        required=api_key_required,
        non_empty_string=True,
    )


def _application_url(application_id: ApplicationId, cloud_url: str) -> str:
    """
    Given a cloud URL (e.g. `https://cloud.prod1.rbt.cloud:9991`), returns the
    url for the given application (e.g. `https://a12345.prod1.rbt.cloud:9991`).
    """
    if not (
        cloud_url.startswith("https://") or cloud_url.startswith("http://")
    ):
        terminal.fail(
            f"Cloud URL '{cloud_url}' must have 'https://' or 'http://'."
        )
    protocol, hostname_port = cloud_url.split("://", maxsplit=1)
    if not hostname_port.startswith("cloud."):
        terminal.fail(
            f"Cloud host '{hostname_port}' is missing expected 'cloud.' prefix"
        )
    cell_hostname_port = hostname_port.removeprefix("cloud.")
    return f"{protocol}://{application_id}.{cell_hostname_port}"


def cloud_external_context(args) -> ExternalContext:
    api_key = args.api_key
    if api_key is None:
        terminal.fail(
            f"The {_API_KEY_FLAG} flag must be set in order to "
            "access the Reboot Cloud."
        )
    return ExternalContext(
        name="reboot-cli",
        bearer_token=api_key,
        url=args.cloud_url,
    )


def register_cloud(parser: ArgumentParser):
    """Register the 'cloud' subcommand with the given parser."""

    def _add_common_flags(subcommand: SubcommandParser):
        """Adds flags common to every `rbt cloud` subcommand."""

        add_cloud_options(subcommand, api_key_required=True)

        subcommand.add_argument(
            '--name',
            type=str,
            required=True,
            help="name of the application",
            non_empty_string=True,
        )

    up_subcommand = parser.subcommand('cloud up')
    _add_common_flags(up_subcommand)
    up_subcommand.add_argument(
        '--dockerfile',
        type=Path,
        help='the Dockerfile to build this application from',
        default='./Dockerfile',
    )
    up_subcommand.add_argument(
        '--docker-build-arg',
        type=str,
        repeatable=True,
        help='additional build arguments to pass to the Docker build command. '
        'Can be specified multiple times, e.g. '
        '`--docker-build-arg=key1=value1 --docker-build-arg=key2`',
    )

    down_subcommand = parser.subcommand('cloud down')
    _add_common_flags(down_subcommand)

    logs_subcommand = parser.subcommand('cloud logs')
    _add_common_flags(logs_subcommand)

    logs_subcommand.add_argument(
        '--follow',
        type=bool,
        default=False,
        help='if true, follows the logs as they are produced',
    )

    # Filters.
    logs_subcommand.add_argument(
        '--revision',
        type=int,
        default=None,
        help='the revision number to get logs for. If omitted: get logs for '
        ' all revisions',
    )
    logs_subcommand.add_argument(
        '--source',
        type=str,
        choices=[value.name.lower() for value in SourceType],
        # We default to `consensus` because, under normal circumstances,
        # developers don't care about the logs of their config runs. If a config
        # run fails, its `rbt cloud up` will already print those logs. If the
        # config run succeeds, its logs are mostly irrelevant.
        default=SourceType.CONSENSUS.name.lower(),
        help="which sources to show logs from; defaults to "
        f"'{SourceType.CONSENSUS.name.lower()}'",
    )
    logs_subcommand.add_argument(
        '--last',
        type=int,
        default=None,
        help='if set, only show the last N log lines. If not set, show all '
        'log lines.',
    )

    # Presentation.
    logs_subcommand.add_argument(
        '--show-revision',
        type=bool,
        default=None,
        help='if true, show the revision number of the log line in the logs. '
        'If false, never do so. If unset, will show revision numbers if there '
        'may be more than one revision in the logs.',
    )
    logs_subcommand.add_argument(
        '--show-source',
        type=bool,
        default=None,
        help='if true, show information about the source of the log '
        'line in the logs. If false, never do so. If unset, will show source '
        'information if there may be more than one type of source in the logs.',
    )
    logs_subcommand.add_argument(
        '--show-timestamp',
        type=bool,
        default=False,
        help='if true, includes timestamp in the logs',
    )


async def _user_id_from_api_key(api_key: str, cloud_url: str) -> str:
    try:
        api_key_id, api_key_secret = parse_api_key_bearer_token(token=api_key)
    except InvalidAPIKeyBearerToken:
        # Note that we do not log the API key contents; they are a secret, which
        # we don't want to output to a log file (if any).
        terminal.fail(
            "Invalid API key shape (expected: "
            "'XXXXXXXXXX-XXXXXXXXXXXXXXXXXXXX')"
        )

    context = ExternalContext(
        name="user-id-from-api-key",
        url=cloud_url,
        # TODO(rjh): once APIKey reads the bearer token for `Authenticate`, use
        #            that instead of passing `secret` in the proto below.
    )

    try:
        return (
            await APIKey.ref(api_key_id).Authenticate(
                context,
                secret=api_key_secret,
            )
        ).user_id
    except Aborted as aborted:
        match aborted.error:
            case StateNotConstructed(  # type: ignore[misc]
            ) | PermissionDenied(  # type: ignore[misc]
            ) | Unauthenticated():  # type: ignore[misc]
                # Note that we do not log the API key contents; they
                # are a secret, which we don't want to output to a log
                # file (if any).
                terminal.fail("Invalid API key")
            case _:
                terminal.fail(f"Unexpected error: {aborted}")


async def _maybe_create_application(
    qualified_application_name: QualifiedApplicationName,
    cloud_url: str,
    api_key: str,
) -> None:
    """
    Creates the Application with the given `qualified_application_name` if it
    doesn't exist yet.
    """
    # Use a separate context for `Create()`, since that call is allowed to fail
    # and will then leave its context unable to continue due to idempotency
    # uncertainty.
    context = ExternalContext(
        name="cloud-up-create-application",
        url=cloud_url,
        bearer_token=api_key,
    )
    try:
        await Application.Create(context, qualified_application_name)
    except Aborted as aborted:
        match aborted.error:
            case StateAlreadyConstructed():  # type: ignore[misc]
                # That's OK; we just want the application to exist!
                pass
            case _:
                # Unexpected error, propagate it.
                raise


async def _parse_common_cloud_args(
    args: argparse.Namespace
) -> tuple[str, str]:

    user_id = await _user_id_from_api_key(
        api_key=args.api_key,
        cloud_url=args.cloud_url,
    )

    qualified_application_name = make_qualified_application_name_from_user_id_and_application_name(
        user_id=user_id,
        application_name=args.name,
    )

    return user_id, qualified_application_name


async def cloud_up(args: argparse.Namespace) -> int:
    """Implementation of the 'cloud up' subcommand."""

    user_id, qualified_application_name = await _parse_common_cloud_args(args)

    context = ExternalContext(
        name="cloud-up",
        url=args.cloud_url,
        bearer_token=args.api_key,
    )

    try:
        terminal.info("[😇] checking permissions...", end=" ")
        await _maybe_create_application(
            qualified_application_name=qualified_application_name,
            cloud_url=args.cloud_url,
            api_key=args.api_key,
        )
        application = Application.ref(qualified_application_name)

        pushinfo_response = await application.PushInfo(context)
        terminal.info("✅")

        registry_endpoint = (
            pushinfo_response.registry_url
            # Regardless of whether the prefix is "https" or "http", we must
            # remove it; the Docker client will decide for itself whether it
            # believes the registry is "secure" or "insecure". We hope it
            # guesses right, otherwise the requests will fail.
            .removeprefix("https://").removeprefix("http://")
        )
        docker_tag = f"{registry_endpoint}/{pushinfo_response.repository}:{pushinfo_response.tag}"

        digest = await _docker_build_and_push(
            dockerfile=args.dockerfile,
            tag=docker_tag,
            registry_endpoint=registry_endpoint,
            registry_username=pushinfo_response.username,
            registry_password=pushinfo_response.password,
            docker_build_args=args.docker_build_arg,
        )

        terminal.info("[🚀] deploying...", end=" ")
        up_response = await application.idempotently().Up(
            context, digest=digest
        )

    except Aborted as aborted:
        if isinstance(aborted.error, InvalidInputError):
            terminal.fail("🛑 failed:\n"
                          f"  {aborted.error.reason}")
        elif isinstance(aborted.error, ConcurrentModificationError):
            terminal.fail(
                "🛑 failed:\n"
                "  The application is already being `up`ped or `down`ed. "
                "Please wait until that operation completes."
            )
        else:
            # Note that `PermissionDenied` shouldn't happen, since the
            # application we're attempting to `Up()` is by definition owned by
            # the user.
            print(f"🛑 unexpected error: {aborted}")
            traceback.print_exc()
            terminal.fail("Please report this bug to the maintainers")

    async for status_response in application.reactively().RevisionStatus(
        context, revision_number=up_response.revision_number
    ):
        revision = status_response.revision
        if revision.status == Status.UPPING:
            # Keep waiting.
            continue

        if revision.status == Status.UP:
            terminal.info(
                f"✅\n"
                "\n"
                f"  '{args.name}' revision {revision.number} is available at: {_application_url(ApplicationId(up_response.application_id), args.cloud_url)}"
                "\n"
            )
            return 0

        if revision.status == Status.FAILED:
            terminal.error(
                "🛑 failed:\n"
                f"Could not deploy revision {revision.number}:\n"
                f"  {revision.failure_reason}\n"
                "\n"
                f"### Logs for revision {revision.number} ###"
            )
            await _cloud_logs(
                user_id=user_id,
                qualified_application_name=qualified_application_name,
                source=SourceType.CONFIG,
                name=args.name,
                cloud_url=args.cloud_url,
                api_key=args.api_key,
                revision=revision.number,
                last=None,  # Show all logs for this revision.
                show_revision=False,
                show_source=False,
                show_timestamp=False,
                follow=False,
            )
            terminal.error(
                f"### End of logs for revision {revision.number} ###\n"
                "Please correct the issue and try again."
            )
            # ISSUE(https://github.com/reboot-dev/mono/issues/4501): don't exit
            # with `sys.exit(1)` here; it causes an unexplained stack trace.
            # Simply return the error code instead and do a `sys.exit()` in the
            # caller, when the `asyncio.run()` is done.
            return 1

        if revision.status == Status.DOWNING or revision.status == Status.DOWN:
            terminal.fail(
                "🛑 failed:\n"
                "  The application is being `down`ed. Please wait until that "
                "operation completes."
            )

        # A revision that we `Up()`ed will never be in the `DOWNING` or `DOWN`
        # state. Those only appear for revisions created by calling `Down()`.
        raise ValueError(
            f"Application reached an unexpected status: '{revision.status}'. "
            "Please report this bug to the maintainers."
        )

    # Should be unreachable, but need for the type checking.
    return 1


async def cloud_down(args: argparse.Namespace) -> None:
    """Implementation of the 'cloud down' subcommand."""

    user_id, qualified_application_name = await _parse_common_cloud_args(args)

    context = ExternalContext(
        name="cloud-down",
        url=args.cloud_url,
        bearer_token=args.api_key,
    )

    try:
        response = await Application.ref(qualified_application_name
                                        ).Down(context)

        if response.status == Status.DOWNING:
            # TODO(rjh): once the CLoud waits to resolve
            #            `down_response.down_task_id` until the application has
            #            terminated, await the completion of
            #            `down_response.down_task_id` here, and tell the user
            #            when their application has in fact terminated.

            terminal.info(
                f"Your application '{args.name}' is being terminated..."
            )
        elif response.status == Status.DOWN:
            terminal.info(
                f"Your application '{args.name}' is already terminated."
            )
    except Aborted as aborted:
        match aborted.error:
            case StateNotConstructed():  # type: ignore[misc]
                terminal.fail(
                    f"User '{user_id}' does not have an application named "
                    f"'{args.name}'"
                )
            case _:
                # There are no other expected errors for
                # `Down()`. Most notably, `PermissionDenied` can't
                # happen, since the application we're attempting to
                # `Down()` is by definition owned by the user.
                terminal.fail(f"Unexpected error: {aborted}")


async def cloud_logs(args: argparse.Namespace) -> None:
    """Implementation of the 'cloud logs' subcommand"""
    user_id, qualified_application_name = await _parse_common_cloud_args(args)
    source = SourceType[args.source.upper()]
    await _cloud_logs(
        user_id=user_id,
        qualified_application_name=qualified_application_name,
        source=source,
        name=args.name,
        cloud_url=args.cloud_url,
        api_key=args.api_key,
        revision=args.revision,
        last=args.last,
        show_revision=args.show_revision,
        show_source=args.show_source,
        show_timestamp=args.show_timestamp,
        follow=args.follow,
    )


async def _cloud_logs(
    user_id: str,
    qualified_application_name: str,
    source: SourceType,
    name: str,
    cloud_url: str,
    api_key: str,
    revision: Optional[int],
    last: Optional[int],
    show_revision: Optional[bool],
    show_source: Optional[bool],
    show_timestamp: bool,
    follow: bool,
) -> None:
    context = ExternalContext(
        name="cloud-logs",
        url=cloud_url,
        bearer_token=api_key,
    )

    application = Application.ref(qualified_application_name)

    revision_numbers = [revision] if revision is not None else None
    show_revision = (
        # Obey explicit user instructions.
        show_revision if show_revision is not None
        # If there are no explicit instructions, show revision numbers if we
        # request logs for more than one revision.
        else revision_numbers is None or len(revision_numbers) != 1
    )
    show_source = (
        # Obey explicit user instructions.
        show_source if show_source is not None
        # If there are no explicit instructions, show sources if we request
        # logs from multiple source types
        else source == SourceType.ALL
    )

    proto_sources = (
        [Source.CONSENSUS] if source == SourceType.CONSENSUS else
        ([Source.CONFIG_RUN] if source == SourceType.CONFIG else [])
    )

    # If the user specified `--follow`, we assume that they only want
    # the last few lines of old logs before the new logs start. They can
    # manually override this by specifying `--last` to get more lines.
    if follow and last is None:
        last = 20

    # We'll retry in the event of `Unavailable` after a backoff, but
    # not if we've already gotten some logs because then we want to
    # exit so the logs don't show up weirdly.
    #
    # ISSUE(https://github.com/reboot-dev/mono/issues/4599): retry even
    # after the first logs have been delivered, e.g. during `--follow`.
    started = False
    backoff = Backoff()
    while not started:
        try:
            printed_lines = 0
            async for response in application.Logs(
                context,
                follow=follow,
                revision_numbers=revision_numbers,
                last=last,
                sources=proto_sources,
            ):
                started = True
                for record in response.records:
                    printed_lines += 1

                    extra_info: list[str] = []
                    if show_timestamp:
                        # Print the timestamp in the local timezone.
                        timestamp = DateTimeWithTimeZone.from_protobuf_timestamp(
                            record.timestamp
                        )
                        extra_info.append(f"{timestamp.astimezone()}")
                    if show_source:
                        # Print the source of the log line.
                        if record.WhichOneof("source") == "consensus_id":
                            # The consensus ID is in fully-qualified format,
                            # including the application ID (e.g.
                            # 'a12345678-c000001'). The application ID isn't
                            # interesting here; strip it.
                            consensus_id = record.consensus_id.split("-")[-1]
                            extra_info.append(f"consensus={consensus_id}")
                        elif record.WhichOneof("source") == "config_run_id":
                            config_run_id = record.config_run_id.removeprefix(
                                "config-run-"
                            )
                            # Add two spaces of padding after the config run ID
                            # to make the text the same length as when we show
                            # a consensus ID.
                            extra_info.append(f"config={config_run_id}")
                        else:
                            extra_info.append("source=???")
                    if show_revision:
                        extra_info.append(f"revision={record.revision_number}")

                    line = ""
                    if extra_info:
                        line = f"[{', '.join(extra_info)}] "

                    line += record.text
                    print(line)
            if source == SourceType.CONSENSUS and printed_lines == 0:
                # The user isn't seeing any output, and it's possible
                # that we filtered out some log lines. Print a message
                # to that effect.
                terminal.warn(
                    "Serving consensuses had no logs matching the requested "
                    "filters. Lines from non-serving sources were filtered "
                    "out; use `--source=all` to see them."
                )
            break

        except Aborted as aborted:
            match aborted.error:
                case StateNotConstructed():  # type: ignore[misc]
                    terminal.fail(
                        f"User '{user_id}' does not have an application named "
                        f"'{name}'"
                    )
                case Unavailable():  # type: ignore[misc]
                    if started:
                        terminal.fail(
                            "\n... connection interrupted, please try again"
                        )
                    await backoff()
                    continue
                case _:
                    # There are no other expected errors for
                    # `Logs()`. Most notably, `PermissionDenied` can't
                    # happen, since the application we're attempting
                    # to call `Logs()` on is by definition owned by
                    # the user.
                    terminal.fail(f"\nUnexpected error: {aborted}")


async def _docker_build_and_push(
    dockerfile: Path,
    tag: str,
    registry_endpoint: str,
    registry_username: str,
    registry_password: str,
    docker_build_args: Optional[list[str]] = None,
) -> str:
    """
    Builds and pushes an image with the given `tag` from the `dockerfile`.

    Returns the digest of the pushed image.
    """
    assert dockerfile.is_absolute()
    if not dockerfile.exists() or not dockerfile.is_file():
        terminal.fail(f"🛑 Could not find Dockerfile '{dockerfile}'")

    dockerfile_pretty = str(dockerfile)
    try:
        dockerfile_pretty = str(dockerfile.relative_to(Path.cwd()))
        if not dockerfile_pretty.startswith("."):
            dockerfile_pretty = f"./{dockerfile_pretty}"
    except ValueError:
        # This means the Dockerfile is not in the current working directory.
        # That's OK, we'll simply use the absolute path.
        pass

    await run_command(
        command=[
            "docker",
            "buildx",
            "build",
            # Reboot Cloud runs on AMD64, so its images must be built for that
            # platform.
            "--platform",
            "linux/amd64",
            "--file",
            str(dockerfile),
            "--tag",
            tag,
        ] + [f"--build-arg={arg}" for arg in docker_build_args or []] + [
            ".",
        ],
        cwd=str(dockerfile.parent),
        icon="🐳",
        command_name="build",
        explanation=f"building container from '{dockerfile_pretty}'",
        capture_output=False,
    )

    try:
        # The push step we do with config from a temporary directory, which
        # allows us to use a one-time Docker `config.json`. That avoids
        # permanently storing the user's credentials in their normal
        # `~/.docker/config.json`.
        with tempfile.TemporaryDirectory() as tempdir:
            # Create a temporary Docker configuration file.
            docker_config = Path(tempdir) / "config.json"
            docker_config.write_text(
                json.dumps(
                    {
                        "auths":
                            {
                                registry_endpoint:
                                    {
                                        "auth":
                                            base64.b64encode(
                                                f"{registry_username}:{registry_password}"
                                                .encode()
                                            ).decode(),
                                    }
                            }
                    }
                )
            )

            # Push the image with the temporary Docker configuration.
            await run_command(
                command=[
                    "docker",
                    "--config",
                    str(tempdir),
                    "push",
                    tag,
                ],
                icon="🚛",
                command_name="push",
                explanation="pushing container",
                capture_output=False,
            )

        # Obtain the image digest.
        digest = (
            await run_command(
                command=[
                    "docker",
                    "inspect",
                    "--format",
                    "{{index .RepoDigests 0}}",
                    tag,
                ],
                icon="👀",
                command_name="inspect",
                explanation="inspecting container",
                capture_output=True,
                only_show_if_verbose=True,
            )
        ).rsplit("@", 1)[-1]

        return digest

    finally:
        # Remove the tag from the local Docker daemon so that it doesn't pollute the
        # user's list of images.
        await run_command(
            command=[
                "docker",
                "image",
                "remove",
                tag,
            ],
            icon="🧹",
            command_name="cleanup",
            explanation="cleaning up",
            capture_output=False,
            only_show_if_verbose=True,
        )
