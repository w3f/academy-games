"""Ultimatum game with direct response: one player makes an offer and the other either accepts or rejects."""

from otree.constants import BaseConstants

from otree.currency import Currency, currency_range
from otree.api import models
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree.views import Page, WaitPage

import json


doc = __doc__

# Models
class Constants(BaseConstants):
    """Various base constants used throughout."""
    name_in_url = 'academy_ultimatum'
    title_prefix = "Lesson 2.1: "
    players_per_group = 2
    num_rounds = 1

    instructions_template = 'academy_ultimatum/instructions.html'

    endowment = Currency(100)
    payoff_if_rejected = Currency(0)
    offer_increment = Currency(10)

    offer_choices = currency_range(0, endowment, offer_increment)
    num_offers = len(offer_choices)


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Track offers and responses during round."""

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
    """Default base player."""

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
    """Display intructions to users."""

    timeout_seconds = 120

    @staticmethod
    def is_displayed(player: Player):
        """Only displayed during first round."""
        return player.round_number == 1


class Offer(PageWithInstructions):
    """Collect offer from first player."""

    form_model = 'group'
    form_fields = ['amount_offered']

    @staticmethod
    def is_displayed(player: Player):
        """Only display response page second player."""
        return player.id_in_group == 1


class WaitForProposer(WaitPage):
    pass


class Respond(PageWithInstructions):
    """Collect responds to offer from second player."""

    form_model = 'group'
    form_fields = ['offer_accepted']

    @staticmethod
    def is_displayed(player: Player):
        """Only display response page second player."""
        return player.id_in_group == 2


class ResultsWaitPage(WaitPage):
    """Display result to players."""

    def after_all_players_arrive(self):
        """Trigger payoff calculation at end of round."""
        self.group.set_payoffs()


class Results(PageWithInstructions):
    """Display result to players."""

    timeout_seconds = 45


page_sequence = [
    Introduction,
    Offer,
    WaitForProposer,
    Respond,
    ResultsWaitPage,
    Results,
]


def vars_for_admin_report(subsession):
    accept = [0] * Constants.num_offers
    reject = [0] * Constants.num_offers

    for group in subsession.get_groups():
        offer = group.field_maybe_none("amount_offered")
        accepted = group.field_maybe_none("offer_accepted")

        if offer is None or accepted is None:
            continue

        index = int(offer / Constants.offer_increment)

        if accepted:
            accept[index] += 1
        else:
            reject[index] += 1

    return dict(
        accept=json.dumps(accept),
        reject=json.dumps(reject),
    )
