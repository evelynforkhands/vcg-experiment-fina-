from itertools import permutations, cycle
from otree.api import (
    models, BaseGroup, BasePlayer, BaseSubsession, BaseConstants
)
from .helpers import get_strings

class C(BaseConstants):
    NAME_IN_URL = 'random_task_order'
    PLAYERS_PER_GROUP = 3
    TREATEMENTS = ['VCG', 'BordaCount', 'TTC']
    NUM_ROUNDS = 3 
    strings = get_strings()

class Group(BaseGroup):
    treatment_order = models.StringField()

class Player(BasePlayer):
    start_time_VCG = models.IntegerField(initial=0)
    start_time_TTC = models.IntegerField(initial=0)
    start_time_Borda = models.IntegerField(initial=0)

    timeout_VCG = models.IntegerField(initial=720)
    timeout_TTC = models.IntegerField(initial=720)
    timeout_Borda = models.IntegerField(initial=720)

class Subsession(BaseSubsession):

    def creating_session(self):
        treatment_orderings = cycle(permutations(C.TREATEMENTS))
        
        if self.round_number == 1:
            for group in self.get_groups():
                treatment_order = next(treatment_orderings)
                group.treatment_order = ','.join(treatment_order)
                
                for p in group.get_players():
                    round_numbers = list(range(1, C.NUM_ROUNDS + 1))
                    treatment_order = dict(zip(treatment_order, round_numbers))
                    
                    p.participant.TREATEMENT_ORDER = treatment_order

                    for round_number, treatment in enumerate(treatment_order, start=1):
                        p.participant.vars[f'treatment_round_{round_number}'] = treatment
