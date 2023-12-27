from otree.api import Page
import json

def get_strings():
    with open('./_static/global/strings.json') as f:
        strings = json.load(f)
    return strings

def is_correct_treatment(player, treatment):
    current_round_treatment = player.participant.vars.get(f'treatment_round_{player.round_number}')
    return treatment == current_round_treatment

class PageWithTimeout(Page):
    timer_text = 'Time left to complete this part:'
    def get_timeout_seconds(player):
        import time
        if is_correct_treatment(player, 'BordaCount'):
            return player.start_time_Borda + player.timeout_Borda - time.time()
        elif is_correct_treatment(player, 'TTC'):
            return player.start_time_TTC + player.timeout_TTC - time.time()
        elif is_correct_treatment(player, 'VCG'):
            return player.start_time_VCG + player.timeout_VCG - time.time()
        else:
            return 0
