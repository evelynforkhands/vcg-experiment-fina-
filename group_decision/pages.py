
from otree.api import Page

from .VCG.VCG_pages import InfoVCG
from .helpers import is_correct_treatment

class VCG(Page):
    def is_displayed(self):
        return is_correct_treatment(self, 'VCG')


class BordaCount1(Page):
    def is_displayed(self):
        return is_correct_treatment(self, 'BordaCount')

class BordaCount2(Page):
    def is_displayed(self):
        return is_correct_treatment(self, 'BordaCount')

class TTC(Page):
    def is_displayed(self):
        return is_correct_treatment(self, 'TTC')


