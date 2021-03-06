""" Main Laghuis script.
"""

from gi.repository import GObject, Gst as gst, GLib as glib

from .box import Box
from .twiddle import JackTwiddler


class LagJack(object):

    def __init__(self):
        GObject.threads_init()
        gst.init(None)

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

    def run(self):
        pipeline = gst.Pipeline()
        pipeline.bus.add_signal_watch()
        pipeline.bus.connect("message", self._on_bus_message)

        delay = int(2e9)
        max_delay = int(30e9)

        box = Box("laghuis", pipeline)
        box.add_sequence([
            'jackaudiosrc connect=none',
            'audiodynamic name=ad_expand mode=1 ratio=2.5 threshold=0.2',
            'equalizer-10bands name=eq band0=-2.0 band9=-2.0',
            'audiochebband lower-frequency=5 upper-frequency=3000',
            'audioamplify name=amp1 amplification=5.0',
            'audioecho name=echo_immediate'
            ' delay=%d max-delay=%d intensity=0.7 feedback=0.2' % (
                int(0.5e9), max_delay),
            'audioecho name=echo_fast'
            ' delay=%d max-delay=%d intensity=0.8 feedback=0.3' % (
                int(2e9), max_delay),
            'audioecho name=echo_slow'
            ' delay=%d max-delay=%d intensity=0.8 feedback=0.3' % (
                delay * 10, max_delay),
            'audioecho name=echo_super_slow'
            ' delay=%d max-delay=%d intensity=0.8 feedback=0.3' % (
                delay * 60, delay * 60),
            'audiodynamic name=ad_compress mode=0 ratio=0.3 threshold=8.0',
            'audioamplify name=amp2 amplification=5.0',
            'jackaudiosink connect=none',
        ])

        pipeline.set_state(gst.State.PLAYING)

        twiddler = JackTwiddler(
            pipeline=pipeline, box=box)
        glib.timeout_add_seconds(1, twiddler.safe_tic)

        mainloop = glib.MainLoop()
        try:
            mainloop.run()
        except KeyboardInterrupt:
            print "Quitting ..."


if __name__ == "__main__":
    l = LagJack()
    l.run()
