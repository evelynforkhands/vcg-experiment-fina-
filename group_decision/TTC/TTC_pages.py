from group_decision.helpers import PageWithTimeout, is_correct_treatment, validate_test_answer
from ..models import Player, C
from otree.api import WaitPage

def is_displayed_TTC(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'TTC')

class TTCPage(PageWithTimeout):
    @property
    def template_name(self):
        return f'group_decision/TTC/{self.__class__.__name__}.html'
    is_displayed = is_displayed_TTC

class InfoTTC(TTCPage):
    def vars_for_template(self):
        return {
            'order': self.player.group.round_number,
            'strings': C.strings,
        }
    
class TestTTC_1(TTCPage):
    form_fields = ['ttc_comprehension_1']
    form_model = 'player'
    def error_message(self: Player, values):
        error_messages = {
            '2': "This answer is incorrect. The app does not note the order of preference submission when matching tenants to rooms. Tenants rank rooms from the room they like most (1st choice) to the room they like least (3rd choice). The app matches rooms to tenants in 5 steps.<br><br>. Step 1. Each tenant ranks the available rooms from the room they like most (1st choice) to the room they like least (3rd choice).<br>Step 2. The app assigns a random number to each tenant, from 1 to 3.<br>Step 3. For each room, the app notes which tenants liked it most.<br>Step 4. If more than one tenant liked a room best, the app performs a random match based on the tenant number assigned in Step 2.<br>Step 5. The tenant and room matched in Step 4 are taken out of the process.<br> The app repeats Steps 3 to 5 with the remaining tenants and rooms until all rooms are matched to tenants.",
            '3': "This answer is incorrect. The app does not only note the tenants' last choices. Tenants rank rooms from the room they like most (1st choice) to the room they like least (3rd choice). The app matches rooms to tenants in 5 steps.<br><br>. Step 1. Each tenant ranks the available rooms from the room they like most (1st choice) to the room they like least (3rd choice).<br>Step 2. The app assigns a random number to each tenant, from 1 to 3.<br>Step 3. For each room, the app notes which tenants liked it most.<br>Step 4. If more than one tenant liked a room best, the app performs a random match based on the tenant number assigned in Step 2.<br>Step 5. The tenant and room matched in Step 4 are taken out of the process.<br> The app repeats Steps 3 to 5 with the remaining tenants and rooms until all rooms are matched to tenants.",
            '4': "This answer is incorrect. The app does not only note the tenants' group numbers, but also who liked each room most. Tenants rank rooms from the room they like most (1st choice) to the room they like least (3rd choice). The app matches rooms to tenants in 5 steps.<br><br>. Step 1. Each tenant ranks the available rooms from the room they like most (1st choice) to the room they like least (3rd choice).<br>Step 2. The app assigns a random number to each tenant, from 1 to 3.<br>Step 3. For each room, the app notes which tenants liked it most.<br>Step 4. If more than one tenant liked a room best, the app performs a random match based on the tenant number assigned in Step 2.<br>Step 5. The tenant and room matched in Step 4 are taken out of the process.<br> The app repeats Steps 3 to 5 with the remaining tenants and rooms until all rooms are matched to tenants."
        }

        return validate_test_answer(self, values['ttc_comprehension_1'], error_messages)
      
class TestTTC_2(TTCPage):
    form_fields = ['ttc_comprehension_2']
    form_model = 'player'
    def error_message(self: Player, values):
        error_messages = {
            '2': "This answer is incorrect. The app does not automatically assign the room to the tenant with the lowest assigned number. If more than one tenant liked a room best, the app performs a random match based on the tenant number assigned to them.",
            '3': "This answer is incorrect. The app does not favor tenants who ranked the room as their second choice. If more than one tenant liked a room best, the app performs a random match based on the tenant number assigned to them.",
            '4': "This answer is incorrect. The order in which tenants submit rankings does not affect the matching. If more than one tenant liked a room best, the app performs a random match based on the tenant number assigned to them."
        }

        return validate_test_answer(self, values['ttc_comprehension_2'], error_messages)
     
class DecisionTTC(TTCPage):
    form_model = 'player'
    form_fields = ['ttc_room_X', 'ttc_room_Y', 'ttc_room_Z']

    def error_message(self, values):
        rankings = [values['ttc_room_X'], values['ttc_room_Y'], values['ttc_room_Z']]
        if len(set(rankings)) != len(rankings):
            return "You must give a unique ranking to each room."

    def vars_for_template(self):
        return {
            'strings': C.strings,
        }
    
class WaitForTTC(WaitPage):
    form_model = 'player'
    body_text = "Please wait for other participants to rank the available rooms."

    def is_displayed(self):
        return is_correct_treatment(self, 'TTC')
    
    def after_all_players_arrive(self):
        self.group.assign_rooms_ttc()

class OutComeTTC(TTCPage):
    def vars_for_template(self):
        return {
            'assigned_room_ttc': self.player.assigned_room,
            'assigned_room_rank': self.player.field_maybe_none('assigned_room_rank'),
            'points': self.player.field_maybe_none('points'),
            'strings': C.strings,
        }

