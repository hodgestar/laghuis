""" Things for dynamically twiddling pipeline values.
"""


class Twiddler(object):
    def __init__(self, **kw):
        self.count = 0
        for k, v in kw.items():
            setattr(self, k, v)

    def safe_tic(self):
        # wrapper around .tic() to ensure that we always
        # return True which ensures that .tic() gets called again
        # later even if an exception is raised.
        try:
            self.tic()
        except Exception as err:
            print err
        self.count += 1
        return True

    def tic(self):
        pass


class PrintTwiddler(Twiddler):
    def tic(self):
        print "Tic"


class JackTwiddler(Twiddler):

    def tic(self):
        band = self.count % 10
        prev_band = (self.count - 1) % 10
        setattr(self.box.eq, "band%d" % band, 10)
        setattr(self.box.eq, "band%d" % prev_band, -23)
