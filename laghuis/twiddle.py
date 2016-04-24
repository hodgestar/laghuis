""" Things for dynamically twiddling pipeline values.
"""


class Twiddler(object):
    def __init__(self, pipeline, **kw):
        self.pipeline = pipeline
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
        return True

    def tic(self):
        pass


class PrintTwiddler(Twiddler):
    def tic(self):
        print "Tic"
