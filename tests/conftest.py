# Module:   conftest
# Date:     6th December 2010
# Author:   James Mills, prologic at shortcircuit dot net dot au

"""py.test config"""

from time import sleep

import collections


def wait_event(m, channel, target=None, timeout=30.0):
    from circuits.core.manager import TIMEOUT

    flag = False

    def handler(evt, handler, retval):
        flag = True

    if target is None:
        target = m

    m.addHandler(handler, channel, target=target)

    for i in range(int(timeout / TIMEOUT)):
        if flag:
            return True
        sleep(TIMEOUT)


def wait_for(obj, attr, value=True, timeout=30.0):
    from circuits.core.manager import TIMEOUT
    for i in range(int(timeout / TIMEOUT)):
        if isinstance(value, collections.Callable):
            if value(obj, attr):
                return True
        elif getattr(obj, attr) == value:
            return True
        sleep(TIMEOUT)


def pytest_namespace():
    return dict((
        ("wait_event", wait_event),
        ("wait_for", wait_for),
    ))
