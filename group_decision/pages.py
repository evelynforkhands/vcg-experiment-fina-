
from otree.api import Page

from .VCG.VCG_pages import *
from .helpers import PageWithTimeout, is_correct_treatment, get_strings
from .models import Player, C


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

class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1
    
    def vars_for_template(self):
        return {
            'strings': C.strings,
        }

    def before_next_page(self):
        import time
        if is_correct_treatment(self.player, 'BordaCount'):
            self.player.start_time_Borda = int(time.time())
        elif is_correct_treatment(self.player, 'TTC'):
            self.player.start_time_TTC = int(time.time())
        elif is_correct_treatment(self.player, 'VCG'):
            self.player.start_time_VCG = int(time.time())
        else:
            return 0
        

class TaskIntro(Page):

    def vars_for_template(self):
        return {
            'order': self.group.round_number,
            'strings': C.strings
        }
    
    def before_next_page(self):
        import time
        if is_correct_treatment(self.player, 'BordaCount'):
            self.player.start_time_Borda = int(time.time())
        elif is_correct_treatment(self.player, 'TTC'):
            self.player.start_time_TTC = int(time.time())
        elif is_correct_treatment(self.player, 'VCG'):
            self.player.start_time_VCG = int(time.time())
        else:
            return 0


page_sequence = [Introduction, TaskIntro, InfoVCG, TestVCG_1, TestVCG_2, DecisionVCG, WaitForOtherToVoteVCG, BordaCount1, BordaCount2, TTC]