from itertools import permutations, cycle
import random
from otree.api import *
from .pages import *

class C(BaseConstants):
    NAME_IN_URL = 'random_task_order'
    PLAYERS_PER_GROUP = 3
    TREATEMENTS = ['VCG', 'BordaCount', 'TTC']
    NUM_ROUNDS = 3 

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    treatment_order = models.StringField()

class Player(BasePlayer):
    pass

def creating_session(subsession: Subsession):
    treatment_orderings = cycle(permutations(C.TREATEMENTS))
    
    if subsession.round_number == 1:
        for group in subsession.get_groups():
            treatment_order = next(treatment_orderings)
            group.treatment_order = ','.join(treatment_order)
            
            for p in group.get_players():
                round_numbers = list(range(1, C.NUM_ROUNDS + 1))
                treatment_order = dict(zip(treatment_order, round_numbers))
                
                print('player', p.id_in_subsession)
                print('treatment_order is', treatment_order)
                p.participant.TREATEMENT_ORDER = treatment_order

                for round_number, treatment in enumerate(treatment_order, start=1):
                    p.participant.vars[f'treatment_round_{round_number}'] = treatment



