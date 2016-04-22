""" Utilities for dealing with ALSA.
"""

import subprocess
import re

CARD_REGEX = re.compile(
    r"^card (?P<card_no>\d+):"
    r" (?P<device_code>[^ ]*)"
    r" \[(?P<device_name>[^\]]*)\], .*$")
USB_SND_CARD = "USB PnP Sound Device"


def find_snd_cards(device_name=USB_SND_CARD, card_re=CARD_REGEX):
    """ Find sounds devices using aplay -l.
    """
    # Our USB sound cards appear as lines line:
    #
    # card 1: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
    #   Subdevices: 0/1
    #   Subdevice #0: subdevice #0
    output = subprocess.check_output(["aplay", "-l"])
    snd_cards = set()
    for line in output.splitlines():
        card = card_re.match(line)
        if card is None:
            continue
        if card.group('device_name') == device_name:
            snd_cards.add("hw:%s" % card.group('card_no'))
    return sorted(snd_cards)
