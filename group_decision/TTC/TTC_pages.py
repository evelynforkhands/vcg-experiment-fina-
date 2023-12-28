from group_decision.helpers import PageWithTimeout, is_correct_treatment

def is_displayed_TTC(self):
        if not PageWithTimeout.is_displayed(self):
            return False
        return is_correct_treatment(self, 'TTC')

class TTCPage(PageWithTimeout):
    @property
    def template_name(self):
        return f'group_decision/TTC/{self.__class__.__name__}.html'
    is_displayed = is_displayed_TTC
