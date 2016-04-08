import gi
import time
import click

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst as gst  # noqa
GObject.threads_init()
gst.init(None)


@click.group()
@click.option(
    '--src', default='pulsesrc',
    help='Also try autoaudiosrc.')
@click.option(
    '--sink', default='pulsesink',
    help='Also try autoaudiosink.')
@click.option(
    '--pdb/--no-pdb', default=False,
    help='Enable PDB to allow fiddling.')
def cli(src, sink, pdb):
    pass


@cli.resultcallback()
def run_gst_pipeline(result, src, sink, pdb):
    pipe = ' ! '.join([
        'audiomixer name=in'
        ' pulsesrc device=2 ! in.'
        ' pulsesrc device=3 ! in.'
        ' pulsesrc device=4 ! in.'
        ' in.'
    ] + result + [
        'tee name=out'
        ' out. ! queue ! pulsesink device=1'
        ' out. ! queue ! pulsesink device=2'
        ' out. ! queue ! pulsesink device=3'
    ])
    click.echo(pipe)
    pipeline = gst.parse_launch(pipe)
    pipeline.set_state(gst.State.PLAYING)
    if pdb:
        import pdb
        pdb.set_trace()
        return
    while 1:
        try:
            time.sleep(1.0)
        except:
            break


@cli.command()
def passthru():
    return ['audioconvert', 'audioresample']


@cli.command()
def queue_delay():
    return [
        'queue max-size-buffers=0 max-size-time=0 max-size-bytes=0'
        ' min-threshold-time=2000000000',
    ]


@cli.command()
@click.option(
    '-d', '--delay', default=2.0,
    help="Delay in seconds.")
@click.option(
    '-m', '--max-delay', default=8.0,
    help="Maximum delay in seconds.")
@click.option(
    '-f', '--feedback', default=0.5,
    help="Amount of feedback (0.0 - 1.0)")
@click.option(
    '-i', '--intensity', default=0.9,
    help="Intensity of echo (0.0 - 1.0)")
@click.option(
    '-p', '--panorama', default=0.0,
    help="Pan from -1.0 (left) to 1.0 (right)."
)
def audioecho(**kw):
    kw['delay'] = int(kw['delay'] * 1e9)
    kw['max_delay'] = int(kw['max_delay'] * 1e9)
    return [
        # Reverb effect (i.e. short delay)
        # 'audioecho'
        # ' delay=50000000 feedback=0.3 intensity=0.3',
        'audioecho'
        ' delay=%(delay)d max-delay=%(max_delay)d'
        ' feedback=%(feedback)g intensity=%(intensity)g'
        % kw,
        'audiopanorama panorama=%(panorama)g' % kw,
    ]


if __name__ == "__main__":
    cli()
