from group_decision.helpers import PageWithTimeout, is_correct_treatment, validate_test_answer
from ..models import Player, C
from otree.api import WaitPage

def is_displayed_BordaCount(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'BordaCount')

class BordaCountPage(PageWithTimeout):
    @property
    def template_name(self):
        return f'group_decision/BordaCount/{self.__class__.__name__}.html'
    is_displayed = is_displayed_BordaCount

class InfoBordaCount(BordaCountPage):
    form_model = 'player'
    def vars_for_template(self):
        return {
            'order': self.group.round_number,
            'strings': C.strings,
        }
class TestBordaCount_1(BordaCountPage):
    form_model = 'player'
    form_fields = ['borda_comprehension_1']
    def error_message(self: Player, values):
        error_messages = {
            '2': "This answer is incorrect. The app does not ensure no tenant ever gets the room they assigned the least number of points to. It is possible for a tenant to get a room they assigned the least number of points to.",
            '3': "This answer is incorrect. No matter what the specific points tenants assigned to rooms, it is possible for a tenant to get a room they assigned the least number of points to.",
            '4': "This answer is incorrect. The app accounts for all the rooms, including the room that a tenants assigns the least number of points to. It is possible for a tenant to get a room they assigned the least number of points to."
        }
        return validate_test_answer(self, values['borda_comprehension_1'], error_messages)

class TestBordaCount_2(BordaCountPage):
    form_model = 'player'
    form_fields = ['borda_comprehension_2']
    def error_message(self, values):

        error_messages = {
            '2': "This answer is incorrect. The order in which tenants submit points does not affect the matching. In case of a tie, the app performs a random match.",
            '3': "This answer is incorrect. The app does not match the room to the tenant with the next highest points for the room. In case of a tie, the app performs a random match.",
            '4': "This answer is incorrect. The tenants must not re-rank their choices. In case of a tie, the app performs a random match."
        }
        return validate_test_answer(self, values['borda_comprehension_2'], error_messages)
    
class DecisionBordaCount(BordaCountPage):
    form_model = 'player'
    form_fields = ['borda_count_room_X', 'borda_count_room_Y', 'borda_count_room_Z']

    def error_message(self, values):
        rankings = [
            values['borda_count_room_X'],
            values['borda_count_room_Y'],
            values['borda_count_room_Z']
        ]
        if len(rankings) != len(set(rankings)):
            return "You must give a unique ranking to each room."

    def vars_for_template(self):
        return {
            'strings': C.strings,
        }
    
    def before_next_page(self):
        self.player.participant.vars['reached_wait_page'] = True



class OutcomeBordaCount(BordaCountPage):
    form_model = 'player'
    
    def vars_for_template(self):
        rank = self.player.field_maybe_none('assigned_room_rank')

        rank_to_magnitude = {1: "most", 2: "second-most", 3: "least"}
        liked_magnitude = rank_to_magnitude.get(rank, "None")

        return {
            'order': self.group.round_number,
            'strings': C.strings,
            'assigned_room': self.player.field_maybe_none('assigned_room'),
            'assigned_room_points': 4 - rank,
            'assigned_room_rank': self.player.field_maybe_none('assigned_room_rank'),
            'liked_magnitude': liked_magnitude,
            'points': self.player.field_maybe_none('points'),
            'strings': C.strings,
        }
    
    def before_next_page(self):
        self.player.participant.vars['reached_wait_page'] = False

class WaitForBordaCount(WaitPage):
    form_model = 'player'
    body_text = "Please wait for other participants to assign points to available rooms."
    def is_displayed(self):
        return is_correct_treatment(self, 'BordaCount')
    
    
    def after_all_players_arrive(self):
        self.group.assign_rooms_borda()
    
