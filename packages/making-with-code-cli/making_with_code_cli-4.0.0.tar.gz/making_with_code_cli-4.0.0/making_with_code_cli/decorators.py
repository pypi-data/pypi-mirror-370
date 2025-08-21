from functools import update_wrapper
import click
import sys
from making_with_code_cli.styles import error
from making_with_code_cli.errors import MWCError


def handle_mwc_errors(f):
    """Decorator declaring a click command. 
    Wraps execution in a try/catch block, so that MWCErrors can be handled with 
    graceful output.
    """
    def command(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except MWCError as e:
            click.echo(error(str(e), preformatted=True), err=True)
            sys.exit(1)
    return update_wrapper(command, f)
