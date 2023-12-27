from ..helpers import PageWithTimeout, is_correct_treatment, get_strings
# from ..__init__ import C
strings = get_strings()
# load template from current directory InfoVCG.html

class InfoVCG(PageWithTimeout):
    form_model = 'player'
    template_name = 'group_decision/VCG/InfoVCG.html'

    def is_displayed(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'VCG')

    def vars_for_template(self):
        return {
            'order': self.group.round_number,
            'strings': strings,
        }

