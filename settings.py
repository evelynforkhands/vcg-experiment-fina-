from os import environ

from itertools import permutations

PARTICIPANT_FIELDS = ['task_rounds']
SESSION_CONFIGS = [
    {
        'name': 'vcg',
        'display_name': "Experiment",
        'num_demo_participants': 3,
        'players_per_group': 3,
        'app_sequence': ['group_decision'],
        'wait_for_all_groups': False,
    },
]


SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point= 0.05, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['TREATEMENT_ORDER']
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'

REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = environ.get('OTREE_ADMIN_USERNAME')
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = environ.get('OTREE_SECRET_KEY')
