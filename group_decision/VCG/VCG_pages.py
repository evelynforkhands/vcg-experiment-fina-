from ..helpers import PageWithTimeout, is_correct_treatment, validate_test_answer
from ..models import Player, C
from otree.api import WaitPage

def is_displayed_VCG(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'VCG')

class VCGPage(PageWithTimeout):
    @property
    def template_name(self):
        return f'group_decision/VCG/{self.__class__.__name__}.html'
    is_displayed = is_displayed_VCG



class InfoVCG(VCGPage):
    form_model = 'player'
    def vars_for_template(self):
        return {
            'order': self.group.round_number,
            'strings': C.strings,
        }

class TestVCG_1(VCGPage):
    form_model = 'player'
    form_fields = ['vcg_comprehension_1']

    def error_message(self: Player, values):
        error_messages = {
            '2': "This answer is incorrect. The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised. Remember, the higher a tenant's bid for a room, the more they like that room.",
            '3': "This answer is incorrect. The matching is not random. The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised. Remember, the higher a tenant's bid for a room, the more they like that room.",
            '4': "This answer is incorrect. The highest individual bid does not determine the matching. The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised.  "
        }
        return validate_test_answer(self, values['vcg_comprehension_1'], error_messages)
    
    def is_displayed(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'VCG')


class TestVCG_2(VCGPage):
    form_model = 'player'
    form_fields = ['vcg_comprehension_2']

    def error_message(self, values):
        if values['vcg_comprehension_2'] in ['2', '3', '4']:
            self.player.number_of_tries += 1
            return "This answer is incorrect. Decisive influence means that if a tenant had not participated in the bidding, other tenants would have been matched to rooms they like more."
        return None

class DecisionVCG(VCGPage):
    form_model = 'player'
    form_fields = ['bid_room_X', 'bid_room_Y', 'bid_room_Z']


    def vars_for_template(self):
        return {
            'strings': C.strings,
        }
    
    def before_next_page(self):
        #set reached_wait_page to True for the player
        self.player.participant.vars['reached_wait_page'] = True


class WaitForVCG(WaitPage):
    form_model = 'player'
    body_text = "Please wait for other participants to bid on available rooms."
    def is_displayed(self):
        return is_correct_treatment(self, 'VCG')
    
    def after_all_players_arrive(self):
        self.group.vcg_allocation()
    
    
class OutcomeVCG(VCGPage):
    def vars_for_template(self):
        return {
            'assigned_room_vcg': self.player.assigned_room,
            'pivotal': self.player.field_maybe_none('pivotal'),
            'payment': self.player.field_maybe_none('payment_vcg'),
            'points': self.player.field_maybe_none('points'),
            'strings': C.strings,
            'bids': self.player.get_sorted_bids(),
        }