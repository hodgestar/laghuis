""" Voices for the Laghuis.
"""

from .box import Box


class FileVoice(Box):
    def __init__(self, pipeline, location, name):
        super(FileVoice, self).__init__(name, pipeline)
        self.add_sequence([
            'filesrc location=%s ' % location,
            'decodebin ',
            'audioconvert ',
            'audioresample '
        ])
        self.elements['decodebin'].connect(
            "pad-added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        print("OnDynamicPad Called!")
        pad.link(self.elements['audioconvert'].sinkpads[0])


class EchoVoice(Box):
    def __init__(self, pipeline, name, delay, max_delay, feedback, intensity):
        super(EchoVoice, self).__init__(name, pipeline)
        self.add_sequence([
            'audioecho delay=%d max-delay=%d feedback=%g intensity=%g ' %
            (delay, max_delay, feedback, intensity)
        ])
