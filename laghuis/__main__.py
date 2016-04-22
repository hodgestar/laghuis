""" Main Laghuis script.
"""

import time
from gi.repository import GObject, Gst as gst  # noqa

from .mic import Mic
from .speaker import Speakers
from .voices import EchoVoice, FileVoice


class Lag(object):

    def __init__(self):
        GObject.threads_init()
        gst.init(None)

    def run(self, debug):
        pipeline = gst.Pipeline()
        mics = [
            Mic(pipeline, 'MI', i) for i in (19,)
        ]

        voices = [
            EchoVoice(pipeline, "EV%d" % i, 2e9, 8e9, 0.8, 0.8) for i in (0,)
        ]
        file_voice = [
            FileVoice(pipeline, "FV", 'Ambient_C_Motion_2.mp3')
        ]

        speakers = [
            Speakers(pipeline, "SP%d" % i, i) for i in (9, )]

        print(len(mics))
        # mics[0].link(voices[0])
        file_voice[0].link(voices[0])
        voices[0].link(speakers[0])
        # voices[0].link(speakers[1])
        # voices[0].link(speakers[2])

        pipeline.set_state(gst.State.PLAYING)

        if debug:
            import pdb
            pdb.set_trace()
            return
        while 1:
            try:
                # for i in range(-10, 12):
                #     for j in range(10):
                #         setattr(b.equalizer_10bands, 'band%s' %j, i)
                #
                # for i in range(-10, 10):
                #     pan = float(i / 10.)
                #     p.audiopanorama.panorama = pan
                #     time.sleep(1)
                time.sleep(1)
            except:
                raise


if __name__ == "__main__":
    l = Lag()
    l.run(debug=False)
