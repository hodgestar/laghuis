""" A box of elements for getting input from a microphone.
"""

from .box import Box


class Mic(Box):
    def __init__(self, pipeline, name, mic):
        super(Mic, self).__init__(name, pipeline)
        self.add_sequence([
            'pulsesrc device=%d name=%s_pulsesrc_%d ' % (
                mic, name, mic),
            'equalizer-10bands ',
            'tee '
        ])
