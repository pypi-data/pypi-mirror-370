from pathlib import Path
from reboot.cli import terminal
from reboot.cli.cloud import add_cloud_options, cloud_external_context
from reboot.cli.rc import ArgumentParser
from reboot.cloud.client import client


def register_secret(parser: ArgumentParser):

    def add_common_args(subcommand):
        add_cloud_options(subcommand, api_key_required=True)
        subcommand.add_argument(
            '--secret-name',
            type=str,
            required=True,
            help="name of the secret",
        )

    secret_write = parser.subcommand('cloud secret write')
    add_common_args(secret_write)
    # TODO: These two options should be a mutually exclusive group, but that
    # facility is not exposed by `rc.py`.
    secret_write.add_argument(
        '--secret-value',
        type=str,
        help=
        "the secret value to store; the value will be UTF8 encoded for storage",
    )
    secret_write.add_argument(
        '--secret-value-file',
        type=Path,
        help="a file containing a secret value to store",
    )

    add_common_args(parser.subcommand('cloud secret delete'))


async def secret_write(args) -> None:
    """Implementation of the 'cloud secret write' subcommand."""

    # TODO: These should be mutually exclusive, but cannot be: see `register_secret`.
    secret_value: bytes
    if args.secret_value is not None:
        if args.secret_value_file is not None:
            terminal.fail(
                "Only one of `--secret-value` and `--secret-value-file` may be set."
            )
        secret_value = args.secret_value.encode()
    else:
        if args.secret_value_file is None:
            terminal.fail(
                "At least one of `--secret-value` and `--secret-value-file` must be set."
            )
        secret_value = args.secret_value_file.read_bytes()

    context = cloud_external_context(args)
    user_id = await client.user_id(context, args.api_key)
    try:
        await client.secret_write(
            context, user_id, args.secret_name, secret_value
        )
    except Exception as e:
        terminal.fail(
            f"Failed to write secret: {e}\n\nPlease report this issue to the maintainers."
        )

    terminal.info(f"Wrote secret: {args.secret_name}")


async def secret_delete(args) -> None:
    """Implementation of the 'cloud secret delete' subcommand."""

    context = cloud_external_context(args)
    user_id = await client.user_id(context, args.api_key)
    try:
        await client.secret_delete(context, user_id, args.secret_name)
    except Exception as e:
        terminal.fail(
            f"Failed to delete secret: {e}\n\nPlease report this issue to the maintainers."
        )

    terminal.info(f"Deleted secret: {args.secret_name}")
