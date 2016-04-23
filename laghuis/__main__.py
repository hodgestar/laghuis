""" Main Laghuis script.
"""

from gi.repository import GObject, Gst as gst, GLib as glib

from .mic import AlsaMic, PulseMic
from .speaker import AlsaSpeakers, PulseSpeakers
from .voices import EchoVoice, FileVoice


class Lag(object):

    ALSA = "alsa"
    PULSE = "pulse"

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
        elif mtype == gst.MessageType.STATE_CHANGED:
            old, new, pending = msg.parse_state_changed()
            print "%s -> %s (src: %s)" % (
                old.value_name, new.value_name, msg.src)
            if pending != gst.State.VOID_PENDING:
                print "  PENDING: %s" % (pending.value_name,)

    def run(self, audio_type=ALSA):
        assert audio_type in (self.ALSA, self.PULSE)
        self.pipeline = pipeline = gst.Pipeline()
        pipeline.bus.add_signal_watch()
        pipeline.bus.connect("message", self._on_bus_message)

        if audio_type == self.ALSA:
            mic_cls = AlsaMic
            speaker_cls = AlsaSpeakers
        else:
            mic_cls = PulseMic
            speaker_cls = PulseSpeakers

        mics = mic_cls.all(pipeline)
        speakers = speaker_cls.all(pipeline)

        voices = [
            EchoVoice(pipeline, "echo%d" % i, 2e9, 8e9, 0.8, 0.8)
            for i in range(len(speakers))
        ]

        file_voice = FileVoice(
            pipeline, "file_ambient", 'Ambient_C_Motion_2.mp3')

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
    l.run(Lag.PULSE)
