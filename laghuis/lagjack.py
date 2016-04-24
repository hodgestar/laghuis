""" Main Laghuis script.
"""

from gi.repository import GObject, Gst as gst, GLib as glib

from .box import Box
from .twiddle import PrintTwiddler


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

        box = Box(pipeline, "laghuis")
        box.add_sequence([
            'jackaudiosrc connect=none',
            'audioecho delay=%d max-delay=%d intensity=0.6 feedback=0.5' % (
                delay, max_delay),
            'jackaudiosink connect=none',
        ])

        pipeline.set_state(gst.State.PLAYING)

        twiddler = PrintTwiddler(
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
