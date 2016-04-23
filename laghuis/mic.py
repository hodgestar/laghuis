""" A box of elements for getting input from a microphone.
"""

from .box import Box


class Mic(Box):

    SRC_TEMPLATE = None

    def __init__(self, pipeline, name, device):
        super(Mic, self).__init__(name, pipeline)
        self.add_sequence([
            self.SRC_TEMPLATE % {
                "name": "src",
                "device": device,
            },
            'equalizer-10bands',
            'tee',
        ])

    @classmethod
    def _create_many(cls, pipeline, srcs):
        return [
            cls(pipeline, 'mic%d' % i, device)
            for i, device in enumerate(srcs)
        ]

    @classmethod
    def all(self):
        raise NotImplementedError("Please implement. :)")


class AlsaMic(Mic):
    SRC_TEMPLATE = "alsasrc name=%(name)s device=%(device)s"

    @classmethod
    def all(cls, pipeline):
        from .alsa import find_alsa_cards
        return cls._create_many(pipeline, find_alsa_cards())


class PulseMic(Mic):
    SRC_TEMPLATE = "pulsesrc name=%(name)s device=%(device)d"

    @classmethod
    def all(cls, pipeline):
        from .pulse import find_pulse_srcs
        return cls._create_many(pipeline, find_pulse_srcs())
