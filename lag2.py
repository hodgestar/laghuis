import gi
import re
import time
from collections import OrderedDict

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst as gst  # noqa


class ElementProxy(object):
    def __init__(self, elem):
        self.__dict__['_elem'] = elem

    def __getattr__(self, name):
        return getattr(self._elem.props, name)

    def __setattr__(self, name, value):
        return setattr(self._elem.props, name, value)


class Box(object):
    def __init__(self, name, pipeline):
        self.name = name
        self.pipeline = pipeline
        self.elements = {}
        self._prev = None
        self.first = []
        self.last = None
        self.box_before = []
        self.box_after = []

    def __getattr__(self, name):
        if name in self.elements:
            return ElementProxy(self.elements[name])
        raise AttributeError("Unknown element %r" % (name,))

    def _set_elem_name(self, elem_def):
        name_re = re.compile("name=([^ ]*)")
        name = name_re.search(elem_def)
        if name is None:
            name = elem_def.split()[0]
            name = name.replace('-', '_')
            return "%s name=%s_%s" % (elem_def, self.name, name)
        else:
            name = "name=%s_%s" % (self.name, name.group(1))
            return name_re.sub(name, elem_def)

    def _get_elem_name(self, elem):
        return elem.name[len(self.name) + 1:]

    def add_element_series(self, elem_def):
        elem_def = self._set_elem_name(elem_def)
        elem = gst.parse_launch(elem_def)
        self.elements[self._get_elem_name(elem)] = elem
        self.pipeline.add(elem)
        if self._prev:
            self._prev.link(elem)
        if not self.first:
            self.first.append(elem)
        self.last = elem
        self._prev = elem

    def add_element_parallel(self, elem_def):
        elem_def = self._set_elem_name(elem_def)
        elem = gst.parse_launch(elem_def)
        self.elements[self._get_elem_name(elem)] = elem
        self.pipeline.add(elem)
        if self._prev:
            self._prev.link(elem)
        self.first.append(elem)
        self.last = elem
        self._prev = elem

    def add_sequence(self, element_defs):
        for elem_def in element_defs:
            self.add_element_series(elem_def)

    def add_sequence_parallel(self, element_defs):
        self._prev = None
        self.add_element_parallel(element_defs[0])
        if len(element_defs) > 1:
            self.add_sequence(element_defs[1:])

    def link(self, other_box):
        for item in other_box.first:
            print('link: %s >>> %s ' %
                  (str(self.last.name), str(item.name)))
            self.last.link(item)
            print(item.name)
        self.box_after = other_box
        other_box.set_box_before(self)
        # print(gst.get_static_pad(other_box, 'src'))

    def set_box_before(self, other_box):
        self.box_before = other_box

    def unlink(self):
        self.add_sequence()


class Microphone(Box):
    def __init__(self, pipeline, name, microphones):
        super(Microphone, self).__init__(name, pipeline)
        for mike in microphones:
            self.add_sequence_parallel([
                'pulsesrc device=%d name=%s_pulsesrc_%d ' %
                (mike, name, mike)
            ])


class FileInput(Box):
    def __init__(self, pipeline, location, name):
        super(FileInput, self).__init__(name, pipeline)
        self.add_sequence([
            'filesrc location=%s ' % location,
            'decodebin ',
            'audioconvert ',
            'audioresample '
        ])
        self.elements['decodebin'].connect("pad-added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        print("OnDynamicPad Called!")
        pad.link(self.elements['audioconvert'].sinkpads[0])


class Equalizer(Box):
    def __init__(self, pipeline, name):
        super(Equalizer, self).__init__(name, pipeline)
        self.add_sequence([
            'equalizer-10bands ',
            'tee '
        ])


class AudioEcho(Box):
    def __init__(self, pipeline, name, delay, max_delay, feedback, intensity):
        super(AudioEcho, self).__init__(name, pipeline)
        self.add_sequence([
            'audioecho delay=%d max-delay=%d feedback=%g intensity=%g ' %
            (delay, max_delay, feedback, intensity)
        ])


class AudioPanorama(Box):
    def __init__(self, pipeline, name):
        super(AudioPanorama, self).__init__(name, pipeline)
        self.add_sequence([
            'audiopanorama '
        ])


class Speakers(Box):
    def __init__(self, pipeline, name, speakers=(0,)):
        super(Speakers, self).__init__(name, pipeline)
        for speaker in speakers:
            self.add_sequence_parallel([
                'queue name=queue_%d ' % speaker,
                'pulsesink device=%d name=%s_speaker_%d ' %
                (speaker, name, speaker)
            ])


class Debug(Box):
    def __init__(self, pipeline, name):
        super(Debug, self).__init__(name, pipeline)
        self.add_sequence([
            'GST_DEBUG '
        ])


class Lag(object):

    def __init__(self):
        GObject.threads_init()
        gst.init(None)

    def run(self, debug):
        pipeline = gst.Pipeline()
        mike = Microphone(pipeline, 'MI', [3])
        # f = FileInput(pipeline, 'Ambient_C_Motion_2.mp3', 'FI')
        b = Equalizer(pipeline, 'EQ')

        p = AudioPanorama(pipeline, 'AP')
        ae = AudioEcho(pipeline, 'AE', 2e9, 8e9, 0.8, 0.8)
        s0 = Speakers(pipeline, "SP0", [0, 1, 2, 4])
        # d = Debug(pipeline, 'DB')

        mike.link(p)
        # f.link(p)
        p.link(ae)
        ae.link(b)
        b.link(s0)
        # p.link(s0)
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

        # result = [
        #     # Reverb effect (i.e. short delay)
        #     # 'audioecho'
        #     # ' delay=50000000 feedback=0.3 intensity=0.3',
        #     'audioecho'
        #     ' delay=%d max-delay=%d'
        #     ' feedback=%g intensity=%g'
        #     % (delay * 1e9, max_delay * 1e9, feedback, intensity),
        #     'audiopanorama panorama=%g' % (panorama),
        # ]
        #
        # pipe = ' ! '.join([
        #     'audiomixer name=in'
        #     #' pulsesrc ! in.'
        #     # ' pulsesrc device=2 ! in.'
        #     # ' pulsesrc device=3 ! in.'
        #     # ' pulsesrc device=4 ! in.'
        #     ' in.'
        # ] + result + [
        #     'tee name=out'
        #     ' out. ! queue ! pulsesink'
        #     # ' out. ! queue ! pulsesink device=1'
        #     # ' out. ! queue ! pulsesink device=2'
        #     # ' out. ! queue ! pulsesink device=3'
        # ])
        # pipe = \
        #     ' filesrc location=Ambient_C_Motion_2.mp3 ! decodebin ! ' \
        #     'audioconvert ! audioresample ! ' + result[0] + ' ! autoaudiosink'

