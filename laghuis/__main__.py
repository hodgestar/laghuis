""" Main Laghuis script.
"""

from gi.repository import GObject, Gst as gst, GLib as glib

from .mic import Mic
from .pulse import find_pulse_srcs, find_pulse_sinks
from .speaker import Speakers
from .voices import EchoVoice, FileVoice


class Lag(object):

    def __init__(self):
        GObject.threads_init()
        gst.init(None)
        self.pipeline = None

    def _on_bus_message(self, bus, msg):
        mtype = msg.type
        if mtype == gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print "Error: %s" % err, debug
            self.pipeline.set_state(gst.State.NULL)
        elif mtype == gst.MessageType.EOS:
            print "Done (EOS)."
            self.pipeline.set_state(gst.State.NULL)

    def run(self):
        self.pipeline = pipeline = gst.Pipeline()
        pipeline.bus.add_signal_watch()
        pipeline.bus.connect("message", self._on_bus_message)

        srcs = find_pulse_srcs()
        sinks = find_pulse_sinks()

        mics = [
            Mic(pipeline, 'mic%d' % i, device)
            for i, device in enumerate(srcs)
        ]

        speakers = [
            Speakers(pipeline, 'spk%d' % i, device)
            for i, device in enumerate(sinks)
        ]

        voices = [
            EchoVoice(pipeline, "echo%d" % i, 2e9, 8e9, 0.8, 0.8)
            for i in range(len(speakers))
        ]

        file_voice = FileVoice(
            pipeline, "file%d" % i, 'Ambient_C_Motion_2.mp3')

        print "Mics:"
        print mics

        print "Speakers:"
        print speakers

        print "Terminating mics ..."
        for mic in mics:
            mic.terminate()

        print "Linking file voices ..."
        for i in range(len(speakers)):
            file_voice.link(voices[i])
            voices[i].link(speakers[i])

        pipeline.set_state(gst.State.PLAYING)

        mainloop = glib.MainLoop()
        try:
            mainloop.run()
        except KeyboardInterrupt:
            print "Quitting ..."


if __name__ == "__main__":
    l = Lag()
    l.run()
