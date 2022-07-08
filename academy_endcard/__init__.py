"""End-of-session app that displays participants progress."""

from otree.constants import BaseConstants
from otree.currency import RealWorldCurrency
from otree.models import BaseSubsession, BaseGroup
from otree.database import db, MixinSessionFK
from otree.views import Page, WaitPage

from wallet import WalletPlayer

import logging


logger = logging.getLogger('academy')

doc = __doc__


class C(BaseConstants):
    """Constants for a simple single player app."""

    NAME_IN_URL = 'academy_endcard'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    @staticmethod
    def get_reward(model: MixinSessionFK) -> bool:
        """Return if app should allow user to create new wallets."""
        return model.session.config.get('academy_endcard_reward', None)


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Default base group."""

    pass


class Player(WalletPlayer):
    """Default wallet-associated player."""

    pass


# Pages
class EndWaitPage(WaitPage):
    """Session wide wait page to distribute any reward."""

    body_text = "Waiting for remaining players to calculate reward..."

    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: BaseSubsession):
        """Trigger real currency payout based on total reward."""
        reward = C.get_reward(subsession)

        if reward:
            participants = [p.participant for p in subsession.get_players()]
            total = sum(p.payoff for p in participants)

            config = subsession.session.config.copy()
            config['real_world_currency_per_point'] = reward / total
            subsession.session.config = config

            payoff_total = RealWorldCurrency(0)
            for p in subsession.get_players():
                participant = p.participant
                participant.finished = True

                payoff_points = participant.payoff
                payoff_real = participant.payoff_in_real_world_currency()
                payoff_total += payoff_real

                logger.info(f"reward: '{participant.code}' receives {payoff_real} ({payoff_points})")

            logger.info(f"reward: '{subsession.session.code}' total payoff is {payoff_total}")


class EndCard(Page):
    """Single page to display current status."""

    pass


page_sequence = [EndWaitPage, EndCard]
