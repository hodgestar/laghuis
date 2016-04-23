""" A box of elements for getting input from a microphone.
"""

from .box import Box


class Mic(Box):
    def __init__(self, pipeline, name, device):
        super(Mic, self).__init__(name, pipeline)
        self.add_sequence([
            'pulsesrc name=src device=%d' % (device,),
            'equalizer-10bands',
            'tee',
        ])
