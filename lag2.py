import gi
import time
import click

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst as gst  # noqa


class Lag(object):

    def __init__(self):
        GObject.threads_init()
        gst.init(None)

    def run(self, debug, delay=2.0, max_delay=8.0, feedback=0.5, intensity=0.9, panorama=0.0):
        result = [
            # Reverb effect (i.e. short delay)
            # 'audioecho'
            # ' delay=50000000 feedback=0.3 intensity=0.3',
            'audioecho'
            ' delay=%d max-delay=%d'
            ' feedback=%g intensity=%g'
            % (delay * 1e9, max_delay * 1e9, feedback, intensity),
            'audiopanorama panorama=%g' % (panorama),
        ]



        pipe = ' ! '.join([
            'audiomixer name=in'
            #' pulsesrc ! in.'
            # ' pulsesrc device=2 ! in.'
            # ' pulsesrc device=3 ! in.'
            # ' pulsesrc device=4 ! in.'
            ' in.'
        ] + result + [
            'tee name=out'
            ' out. ! queue ! pulsesink'
            # ' out. ! queue ! pulsesink device=1'
            # ' out. ! queue ! pulsesink device=2'
            # ' out. ! queue ! pulsesink device=3'
        ])

        pipe = \
            ' filesrc location=Ambient_C_Motion_2.mp3 ! decodebin ! ' \
            'audioconvert ! audioresample ! equalizer-10bands name=eq ! autoaudiosink'

        # pipe = \
        #     ' filesrc location=Ambient_C_Motion_2.mp3 ! decodebin ! ' \
        #     'audioconvert ! audioresample ! ' + result[0] + ' ! autoaudiosink'

        click.echo(pipe)
        pipeline = gst.parse_launch(pipe)
        pipeline.set_state(gst.State.PLAYING)
        if debug:
            import pdb
            pdb.set_trace()
            return
        while 1:
            try:
                eq = pipeline.get_child_by_name('eq')
                time.sleep(1.0)
                eq.props.band0 = 0.0
                eq.props.band1 = 0.0
                eq.props.band2 = 0.0
                eq.props.band3 = 0.0
                eq.props.band4 = 0.0
                eq.props.band5 = 0.0
                eq.props.band6 = 0.0
                eq.props.band7 = 0.0
                eq.props.band8 = 0.0
                eq.props.band9 = 0.0


                time.sleep(1.0)
                eq.props.band0 = -12.0
                eq.props.band1 = -12.0
                eq.props.band2 = -12.0
                eq.props.band3 = -12.0
                eq.props.band4 = -12.0
                eq.props.band5 = -12.0
                eq.props.band6 = -12.0
                eq.props.band7 = -12.0
                eq.props.band8 = -12.0
                eq.props.band9 = -12.0

            except:
                break


if __name__ == "__main__":
    l = Lag()
    l.run(debug=False)
