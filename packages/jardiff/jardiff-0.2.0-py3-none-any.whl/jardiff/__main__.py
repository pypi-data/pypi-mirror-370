"""Entry point when executing ``python -m jardiff``.

This module simply imports the ``main`` function from :mod:`jardiff.cli`
and invokes it.  It is needed so that the package can be executed as
a module using the ``-m`` switch.
"""

from .cli import main


if __name__ == "__main__":
    # Delegate execution to the CLI's main entry point
    main()
