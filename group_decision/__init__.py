from itertools import permutations, cycle
import random
from otree.api import *
from .pages import *
from .helpers import get_strings
class C(BaseConstants):
    NAME_IN_URL = 'random_task_order'
    PLAYERS_PER_GROUP = 3
    TREATEMENTS = ['VCG', 'BordaCount', 'TTC']
    NUM_ROUNDS = 3 
    strings = get_strings()

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    treatment_order = models.StringField()

class Player(BasePlayer):
    start_time_VCG = models.IntegerField(initial=0)
    start_time_TTC = models.IntegerField(initial=0)
    start_time_Borda = models.IntegerField(initial=0)

    timeout_VCG = models.IntegerField(initial=720)
    timeout_TTC = models.IntegerField(initial=720)
    timeout_Borda = models.IntegerField(initial=720)


def creating_session(subsession: Subsession):
    treatment_orderings = cycle(permutations(C.TREATEMENTS))
    
    if subsession.round_number == 1:
        for group in subsession.get_groups():
            treatment_order = next(treatment_orderings)
            group.treatment_order = ','.join(treatment_order)
            
            for p in group.get_players():
                round_numbers = list(range(1, C.NUM_ROUNDS + 1))
                treatment_order = dict(zip(treatment_order, round_numbers))
                
                p.participant.TREATEMENT_ORDER = treatment_order

                for round_number, treatment in enumerate(treatment_order, start=1):
                    p.participant.vars[f'treatment_round_{round_number}'] = treatment



class Introduction(Page):
    def is_displayed(self):
        return self.round_number == 1
    
    def vars_for_template(self):
        return {
            'strings': C.strings,
        }

    def before_next_page(self: Player, timeout_happened):
        import time
        if is_correct_treatment(self, 'BordaCount'):
            self.start_time_Borda = int(time.time())
        elif is_correct_treatment(self, 'TTC'):
            self.start_time_TTC = int(time.time())
        elif is_correct_treatment(self, 'VCG'):
            self.start_time_VCG = int(time.time())
        else:
            return 0
        
page_sequence = [Introduction, VCG, InfoVCG, BordaCount1, BordaCount2, TTC]