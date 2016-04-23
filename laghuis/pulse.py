""" Utilities for dealing with Pulse Audio.
"""

import subprocess
import re

ELEM_RES = {
    "sources": re.compile(r"^Source #(?P<device>\d+)$"),
    "sinks": re.compile(r"^Sink #(?P<device>\d+)$"),
}
USB_SND_DESC = "Description: CM108 Audio"


def _find_pulse_elements(elem_type, elem_desc=USB_SND_DESC):
    """ Find sound sources or sinks that match a description.

    :param elem_type: Either "sources" or "sinks".
    :param elem_desc: Element description to filter on.
    """
    elem_re = ELEM_RES[elem_type]
    elems = []
    current_device = None
    output = subprocess.check_output(["pactl", "list", elem_type])
    for line in output.splitlines():
        match = elem_re.match(line)
        if match is not None:
            current_device = int(match.group('device'))
            continue
        if elem_desc in line and current_device is not None:
            elems.append(current_device)
    return elems


def find_pulse_srcs(elem_desc=USB_SND_DESC):
    """ Find sound sources. """
    return _find_pulse_elements("sources", elem_desc=elem_desc)


def find_pulse_sinks(elem_desc=USB_SND_DESC):
    """ Find sound sinks. """
    return _find_pulse_elements("sinks", elem_desc=elem_desc)
