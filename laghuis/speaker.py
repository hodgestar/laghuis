""" Box for outputing to a pair of speakers.
"""

from .box import Box


class Speakers(Box):

    SINK_TEMPLATE = None

    def __init__(self, pipeline, name, device):
        super(Speakers, self).__init__(name, pipeline)
        self.add_sequence([
            'audiomixer name=mixer',
            'audiopanorama name=pan',
            self.SINK_TEMPLATE % {
                "name": "sink",
                "device": device,
            },
        ])

    @classmethod
    def _create_many(cls, pipeline, srcs):
        return [
            cls(pipeline, 'spk%d' % i, device)
            for i, device in enumerate(srcs)
        ]

    @classmethod
    def all(self):
        raise NotImplementedError("Please implement. :)")


class AlsaSpeakers(Speakers):
    SINK_TEMPLATE = 'alsasink name=%(name)s device=%(device)s'

    @classmethod
    def all(cls, pipeline):
        from .alsa import find_alsa_cards
        return cls._create_many(pipeline, find_alsa_cards())


class PulseSpeakers(Speakers):
    SINK_TEMPLATE = 'pulsesink name=%(name)s device=%(device)d'

    @classmethod
    def all(cls, pipeline):
        from .pulse import find_pulse_sinks
        return cls._create_many(pipeline, find_pulse_sinks())
