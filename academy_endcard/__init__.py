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
    def get_reward(model: MixinSessionFK) -> RealWorldCurrency:
        """Return if app should allow user to create new wallets."""
        return RealWorldCurrency(model.session.config.get('academy_endcard_reward', 0))


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
            points = [p.payoff for p in participants]
            points_min = min(points)
            points_offset = 0

            if points_min < 0:
                points_offset = -points_min

                for p in subsession.get_players():
                    p.payoff = points_offset

            points_total = sum(points) + len(points) * points_offset
            reward_per_point = float(reward) / float(points_total)

            logger.info(f"reward: '{subsession.session.code}' payoff ratio is {reward_per_point}")

            config = subsession.session.config.copy()
            config['real_world_currency_per_point'] = reward_per_point
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
