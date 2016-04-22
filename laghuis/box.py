""" Base classes for boxes of Gst pipeline elements.
"""

import re
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

    def set_box_before(self, other_box):
        self.box_before = other_box

    def unlink(self):
        self.add_sequence()
