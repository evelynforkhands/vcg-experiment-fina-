
from otree.api import Page

def is_correct_treatment(player, treatment):
    current_round_treatment = player.participant.vars.get(f'treatment_round_{player.round_number}')
    return treatment == current_round_treatment

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

page_sequence = [VCG, BordaCount1, BordaCount2, TTC]
