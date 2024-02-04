# from collections import defaultdict
# from itertools import permutations, cycle
# import itertools
# import random
from otree.api import (
    models, BaseGroup, BasePlayer, BaseSubsession, BaseConstants, widgets
)
# from .helpers import get_strings

# def likert_field(label, verbose_name):
#     return models.IntegerField(
#         label=label,
#         verbose_name=verbose_name,
#         widget=widgets.RadioSelectHorizontal,
#         choices=[
#             [1, 'Strongly disagree'],
#             [2, 'Disagree'],
#             [3, 'Somewhat disagree'],
#             [4, 'Neither agree nor disagree'],
#             [5, 'Somewhat agree'],
#             [6, 'Agree'],
#             [7, 'Strongly agree']
#         ]
#     )
class C(BaseConstants):
    NAME_IN_URL = 'timeout_app'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1


class Player(BasePlayer):
    pass

class Group(BaseGroup):
    pass

class Subsession(BaseSubsession):
    pass

