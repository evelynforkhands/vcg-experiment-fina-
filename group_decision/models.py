from itertools import permutations, cycle
from otree.api import (
    models, BaseGroup, BasePlayer, BaseSubsession, BaseConstants, widgets
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


    vcg_comprehension_1 = models.StringField(
        choices=[
            [1,
             'The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised.'],
            [2,
             'The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is minimised.'],
            [3, 'The app randomly matches tenants to rooms.'],
            [4, 'The app matches tenants to rooms based on the highest individual bid.'],
        ],
        widget=widgets.RadioSelect,
        verbose_name='How does the app match tenants to rooms?',
        blank=False
    )

    vcg_comprehension_2 = models.StringField(
        choices=[
            [1,
             'Decisive influence means that if a tenant had not participated in the bidding, other tenants would have been matched to rooms they like more. '],
            [2,
             'Decisive influence means that a tenant is not interested in any of the rooms.'],
            [3,
             'Decisive influence means that a tenant is interested in all of the rooms equally.'],
            [4,
             'Decisive influence means that a tenant\'s bid determines the final matching of a room.']
        ],
        widget=widgets.RadioSelect,
        verbose_name='What does it mean for a tenant to have a decisive influence on the final matching?',
        blank=False
    )

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
