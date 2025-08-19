import logging

import click


def global_options(f):
    """Common decorator to add global options to command groups"""
    from .debug import setup_file_logging

    def debug_callback(ctx, param, value):
        if value:
            setup_file_logging(level=logging._nameToLevel[value])
        return value

    return click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
        help="Enable debug logging to file",
        callback=debug_callback,
        expose_value=False,
        is_eager=True,
        hidden=True,
    )(f)
