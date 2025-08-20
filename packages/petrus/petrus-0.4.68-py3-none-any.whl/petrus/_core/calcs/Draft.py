import importlib.resources

from petrus._core.calcs.Calc import Calc


class Draft(Calc):
    def _calc(self, name):
        return importlib.resources.read_text("petrus.drafts", "%s.txt" % name)
