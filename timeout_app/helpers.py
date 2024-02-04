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
    def get_template_names(self):
        return f'global/Stic.html'
    def get_timeout_seconds(self):
        import time
        if is_correct_treatment(self.player, 'BordaCount'):
            return self.player.start_time_Borda + self.player.timeout_Borda - time.time()
        elif is_correct_treatment(self.player, 'TTC'):
            return self.player.start_time_TTC + self.player.timeout_TTC - time.time()
        elif is_correct_treatment(self.player, 'VCG'):
            return self.player.start_time_VCG + self.player.timeout_VCG - time.time()
        else:
            return 0
    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened:
            return 'timeout_app'

def validate_test_answer(self, value, error_messages):
    if value in error_messages:
        self.player.number_of_tries += 1
        return error_messages[value]
    return None
