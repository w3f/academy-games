"""
Ultimatum game with two treatments: direct response and strategy method.
In the former, one player makes an offer and the other either accepts or rejects.
It comes in two flavors, with and without hypothetical questions about the second player's response to offers other than the one that is made.
In the latter treatment, the second player is given a list of all possible offers, and is asked which ones to accept or reject.
"""

from otree.constants import BaseConstants

from otree.currency import Currency, currency_range
from otree.api import models
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree.views import Page, WaitPage


doc = __doc__

# Models
class Constants(BaseConstants):
    name_in_url = 'academy_ultimatum'
    title_prefix = "Lesson 2.1: "
    players_per_group = 2
    num_rounds = 10

    instructions_template = 'academy_ultimatum/instructions.html'

    endowment = Currency(100)
    payoff_if_rejected = Currency(0)
    offer_increment = Currency(10)

    offer_choices = currency_range(0, endowment, offer_increment)
    num_offers = len(offer_choices)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    amount_offered = models.CurrencyField(choices=Constants.offer_choices)

    offer_accepted = models.BooleanField()

    def set_payoffs(self):
        p1, p2 = self.get_players()

        if self.offer_accepted:
            p1.payoff = Constants.endowment - self.amount_offered
            p2.payoff = self.amount_offered
        else:
            p1.payoff = Constants.payoff_if_rejected
            p2.payoff = Constants.payoff_if_rejected


class Player(BasePlayer):
    pass


# Pages
class PageWithInstructions(Page):
    """Abstract base page to provide instruction vars."""

    @staticmethod
    def vars_for_template(player: Player) -> dict:

        return {
            'offers': Constants.offer_choices,
            'reward': [Constants.endowment - o for o in Constants.offer_choices],
        }

class Introduction(PageWithInstructions):
    timeout_seconds = 60

    @staticmethod
    def is_displayed(player: Player):
        """Only displayed during first round."""
        return player.round_number == 1



class Offer(PageWithInstructions):
    form_model = 'group'
    form_fields = ['amount_offered']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


class WaitForProposer(WaitPage):
    pass


class Respond(PageWithInstructions):
    form_model = 'group'
    form_fields = ['offer_accepted']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(PageWithInstructions):
    pass


page_sequence = [
    Introduction,
    Offer,
    WaitForProposer,
    Respond,
    ResultsWaitPage,
    Results,
]
