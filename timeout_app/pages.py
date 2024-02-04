
from otree.api import Page


class TimeOutPage(Page):
    def vars_for_template(self):
        round = int(self.participant.vars.get('round_number'))
        return {
            'payoff': 3 if round == 1 else 5
        }


page_sequence = [TimeOutPage]