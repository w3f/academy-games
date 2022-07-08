"""Public goods with punishment, roughly based on Fehr & Gaechter 2000."""

from settings import REAL_WORLD_CURRENCY_CODE, USE_POINTS
import settings

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.database import CurrencyField, IntegerField

from otree.views import Page, WaitPage

from otree.i18n import CURRENCY_SYMBOLS

from typing import List


doc = __doc__


# Global helper functions, mostly work-arounds otrees inflexibility and lack of API
def GET_CURRENCY_SYMBOL():
    """Determine current currency symbol."""
    if settings.USE_POINTS:
        return getattr(settings, 'POINTS_CUSTOM_NAME', "points")
    else:
        code = REAL_WORLD_CURRENCY_CODE
        return CURRENCY_SYMBOLS.get(code, code)


def PUNISHMENT_COST_FUNCTION(points: int) -> Currency:
    """Return cost of punishment, model by a quartered quadratic function."""
    return Currency(round(0.25 * (points + 1)**2))


PERCENT_PER_PUNISHMENT = 10


# Models
class C(BaseConstants):
    """Cournot game constants."""

    NAME_IN_URL = 'academy_publicgood'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 10
    TITLE_PREFIX = "Lesson 2.2: "
    INSTRUCTIONS_TEMPLATE = 'academy_publicgood/instructions.html'
    ENDOWMENT = Currency(20)
    MULTIPLIER = 1.6
    MAX_PUNISHMENT = 10
    PERCENT_PER_PUNISHMENT = PERCENT_PER_PUNISHMENT

    cost = staticmethod(PUNISHMENT_COST_FUNCTION)
    COST_TABLE = {
        'columns': MAX_PUNISHMENT + 2,
        'points': range(MAX_PUNISHMENT + 1),
        'percentage': ["{}%".format(p * PERCENT_PER_PUNISHMENT) for p in range(MAX_PUNISHMENT + 1)],
        'cost': [int(PUNISHMENT_COST_FUNCTION(p)) for p in range(MAX_PUNISHMENT + 1)],
    }
    CURRENCY_SYMBOL = GET_CURRENCY_SYMBOL()


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Track total contributions and its distribution."""

    total_contribution = CurrencyField()
    individual_share = CurrencyField()


def PunishmentField(id_in_group):
    """Create player id specific punishment fields."""
    return IntegerField(
        min=0, max=C.MAX_PUNISHMENT,
        label="Punishment for Player {}".format(id_in_group)
    )


class Player(BasePlayer):
    """Tracks contribution and punishments chosen by players."""

    # Track common good contribution
    contribution = CurrencyField(
        min=0, max=C.ENDOWMENT, label="How much will you contribute?"
    )

    # Track punishments between players
    punishment_player1 = PunishmentField(1)
    punishment_player2 = PunishmentField(2)
    punishment_player3 = PunishmentField(3)
    punishment_player4 = PunishmentField(4)

    punishment_received = IntegerField()

    # Track loss/cost of punishment received and sent
    punishment_loss = CurrencyField()
    punishment_cost = CurrencyField()

    @property
    def punishment_field(self) -> str:
        """Return name of field containing player's punishment."""
        return f"punishment_player{self.id_in_group}"

    def punishment_for(self, player: "Player") -> int:
        """Return punishment directed at specific player."""
        return getattr(self, player.punishment_field)


# PAGES
class Introduction(Page):
    """Display introduction to players."""

    timeout_seconds = 120

    @staticmethod
    def is_displayed(player: Player):
        """Only displayed during first round."""
        return player.round_number == 1


class Contribute(Page):
    """Collect contributions from players."""

    form_model = 'player'
    form_fields = ['contribution']


class ContributeWait(WaitPage):
    """Wait for all players to choose contribution."""

    @staticmethod
    def after_all_players_arrive(group: Group) -> None:
        """Determine individual shares based on contributions."""
        group.total_contribution = sum(p.contribution for p in group.get_players())
        group.individual_share = (
            group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
        )


class Punish(Page):
    """Collect punishments from players."""

    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player) -> List[str]:
        """Exclude players own punishment field."""
        return [p.punishment_field for p in player.get_others_in_group()]

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Provide other players and punishment schedule."""
        return dict(
            other_players=player.get_others_in_group(),
        )


class PunishWait(WaitPage):
    """Wait for all players to choose punishments."""

    def after_all_players_arrive(group: Group) -> None:
        """Determine reward based on punishment."""
        for player in group.get_players():
            payoff_base = C.ENDOWMENT - player.contribution + group.individual_share

            others = player.get_others_in_group()

            player.punishment_received = sum(
                [o.punishment_for(player) for o in others]
            )

            percentage = min(player.punishment_received, C.MAX_PUNISHMENT) * C.PERCENT_PER_PUNISHMENT
            player.punishment_loss = payoff_base * (percentage / 100.0)

            player.punishment_cost = sum(
                [C.cost(player.punishment_for(o)) for o in others]
            )

            player.payoff = payoff_base - player.punishment_loss - player.punishment_cost


class Results(Page):
    """Display result to players."""

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Provide other players and punishment schedule."""
        percentage = min(player.punishment_received, C.MAX_PUNISHMENT) * C.PERCENT_PER_PUNISHMENT
        return dict(
            percentage=percentage,
        )


page_sequence = [
    Introduction,
    Contribute,
    ContributeWait,
    Punish,
    PunishWait,
    Results,
]
