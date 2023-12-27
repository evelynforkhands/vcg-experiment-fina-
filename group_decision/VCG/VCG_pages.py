from ..helpers import PageWithTimeout, is_correct_treatment, get_strings
from ..models import Player, C

def is_displayed_VCG(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'VCG')

class InfoVCG(PageWithTimeout):
    form_model = 'player'
    template_name = 'group_decision/VCG/InfoVCG.html'

    is_displayed = is_displayed_VCG

    def vars_for_template(self):
        return {
            'order': self.group.round_number,
            'strings': C.strings,
        }

class TestVCG_1(PageWithTimeout):
    form_model = 'player'
    form_fields = ['vcg_comprehension_1']
    template_name = 'group_decision/VCG/TestVCG_1.html'

    is_displayed = is_displayed_VCG

    def error_message(self: Player, values):
        if values['vcg_comprehension_1'] == '2':
            self.number_of_tries_vcg += 1
            return "This answer is incorrect. The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised. Remember, the higher a tenant's bid for a room, the more they like that room."
        elif values['vcg_comprehension_1'] == '3':
            self.number_of_tries_vcg += 1
            return "This answer is incorrect. The matching is not random. The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised. Remember, the higher a tenant's bid for a room, the more they like that room."
        elif values['vcg_comprehension_1'] == '4':
            self.number_of_tries_vcg += 1
            return "This answer is incorrect. The highest individual bid does not determine the matching. The app takes into account all the bids, and matches tenants to rooms in such a way that the sum of all their bids is maximised.  "

    def is_displayed(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'VCG')



class TestVCG_2(PageWithTimeout):
    form_model = 'player'
    form_fields = ['vcg_comprehension_2']
    template_name = 'group_decision/VCG/TestVCG_2.html'
    is_displayed = is_displayed_VCG

    def error_message(self, values):
        if values['vcg_comprehension_2'] == '2':
            self.number_of_tries_vcg += 1
            return f"This answer is incorrect. Decisive influence means that if a tenant had not participated in the bidding, other tenants would have been matched to rooms they like more. "
        elif values['vcg_comprehension_2'] == '3':
            self.number_of_tries_vcg += 1
            return f"This answer is incorrect. Decisive influence means that if a tenant had not participated in the bidding, other tenants would have been matched to rooms they like more. "
        elif values['vcg_comprehension_2'] == '4':
            self.number_of_tries_vcg += 1
            return f"This answer is incorrect. Decisive influence means that if a tenant had not participated in the bidding, other tenants would have been matched to rooms they like more. "
