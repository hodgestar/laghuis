""" Box for outputing to a pair of speakers.
"""

from .box import Box


class Speakers(Box):
    def __init__(self, pipeline, name, speaker):
        super(Speakers, self).__init__(name, pipeline)
        self.add_sequence([
            'audiomixer name=mixer',
            'audiopanorama name=pan',
            'pulsesink device=%d name=sink' %
            speaker
        ])
