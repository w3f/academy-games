"""Public goods with punishment, roughly based on Fehr & Gaechter 2000."""

from settings import REAL_WORLD_CURRENCY_CODE, USE_POINTS
import settings

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.database import db, CurrencyField, IntegerField

from otree.views import Page, WaitPage

from otree.i18n import CURRENCY_SYMBOLS

from typing import List, Optional

import json


doc = __doc__


# Global helper functions, mostly work-arounds otrees inflexibility and lack of API
def GET_CURRENCY_SYMBOL():
    """Determine current currency symbol."""
    if settings.USE_POINTS:
        return getattr(settings, 'POINTS_CUSTOM_NAME', "points")
    else:
        code = REAL_WORLD_CURRENCY_CODE
        return CURRENCY_SYMBOLS.get(code, code)


def PUNISHMENT_COST_FUNCTION(percentage: int) -> Currency:
    """Return cost of punishment, model by a quartered quadratic function."""
    return Currency(round(0.25 * ((percentage / 10) + 1)**2))


# Models
class C(BaseConstants):
    """Cournot game constants."""

    NAME_IN_URL = 'academy_publicgood'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 10
    TITLE_PREFIX = "Lesson 2.2: "
    INSTRUCTIONS_TEMPLATE = 'academy_publicgood/instructions.html'
    ENDOWMENT_INITIAL = Currency(80)
    ENDOWMENT_ROUND = Currency(20)
    MULTIPLIER = 1.6
    PUNISHMENT_STEP = 10
    PUNISHMENT_MAX = 100

    cost = staticmethod(PUNISHMENT_COST_FUNCTION)
    COST_TABLE = {
        'columns': PUNISHMENT_MAX / PUNISHMENT_STEP + 2,
        'percentage': [f"{p}%" for p in range(0, PUNISHMENT_MAX + 1, PUNISHMENT_STEP)],
        'cost': [int(PUNISHMENT_COST_FUNCTION(p)) for p in range(0, PUNISHMENT_MAX + 1, PUNISHMENT_STEP)],
    }
    CURRENCY_SYMBOL = GET_CURRENCY_SYMBOL()


class Subsession(BaseSubsession):
    """Default base subsession."""

    def __init__(self, round_number, session):
        session._set_admin_report_app_names()
        super().__init__(round_number=round_number, session=session)

        db.commit()

class Group(BaseGroup):
    """Track total contributions and its distribution."""

    total_contribution = CurrencyField()
    individual_share = CurrencyField()

    @property
    def total_public_good(self) -> int:
        """Return total contribution after multiplier was applied."""
        return self.total_contribution * C.MULTIPLIER


def PunishmentField(id_in_group):
    """Create player id specific punishment fields."""
    return IntegerField(
        min=0, max=C.PUNISHMENT_MAX,
        label="Punishment for Player {}".format(id_in_group)
    )


class Player(BasePlayer):
    """Tracks contribution and punishments chosen by players."""

    # Track balance at the begging of round
    total = CurrencyField()

    # Track common good contribution
    contribution = CurrencyField(
        min=0, max=C.ENDOWMENT_ROUND, label="How much will you contribute?"
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
    def remainder(self) -> int:
        return C.ENDOWMENT_ROUND - self.contribution

    @property
    def punishment_field(self) -> str:
        """Return name of field containing player's punishment."""
        return f"punishment_player{self.id_in_group}"

    @property
    def punishment_budget(self) -> int:
        """Return the points available for punishment."""
        return self.total + self.punishment_base

    @property
    def punishment_base(self) -> int:
        """Return base point used to compute punishment."""
        return C.ENDOWMENT_ROUND - self.contribution + self.group.individual_share

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

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        """Provide participant with initial endowment."""
        player.participant.payoff = C.ENDOWMENT_INITIAL


class Contribute(Page):
    """Collect contributions from players."""

    timeout_seconds = 35

    form_model = 'player'
    form_fields = ['contribution']

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Provide endowment details."""
        return dict(
            balance_before=player.participant.payoff + C.ENDOWMENT_ROUND,
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if timeout_happened:
            player.contribution = C.ENDOWMENT_ROUND


class ContributeWait(WaitPage):
    """Wait for all players to choose contribution."""

    @staticmethod
    def after_all_players_arrive(group: Group) -> None:
        """Determine endowment and individual shares based on contributions."""
        for p in group.get_players():
            p.total = p.participant.payoff

        group.total_contribution = sum(p.contribution for p in group.get_players())
        group.individual_share = (
            group.total_contribution * C.MULTIPLIER / C.PLAYERS_PER_GROUP
        )


class Punish(Page):
    """Collect punishments from players."""

    form_model = 'player'

    timeout_seconds = 45

    @staticmethod
    def get_form_fields(player: Player) -> List[str]:
        """Exclude players own punishment field."""
        return [p.punishment_field for p in player.get_others_in_group()]

    @staticmethod
    def error_message(player: Player, values: dict) -> Optional[str]:
        punishments = [values[field] for field in Punish.get_form_fields(player)]
        cost = sum(C.cost(p) for p in punishments)
        budget = player.punishment_budget

        if cost and cost > budget:
            return f"Total cost of punishment ({cost}) exceeds available funds ({budget})."


    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Provide other players and punishment schedule."""
        return dict(
            other_players=player.get_others_in_group(),
        )

    @staticmethod
    def js_vars(player: Player) -> dict:
        """Return player ids and punishment bases for js calculation."""
        return dict(
            player_ids=[p.id_in_group for p in player.get_others_in_group()],
            punishment_bases=[p.punishment_base for p in player.get_others_in_group()],
        )

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if timeout_happened:
            for p in player.get_others_in_group():
                setattr(player, p.punishment_field, 0)


class PunishWait(WaitPage):
    """Wait for all players to choose punishments."""

    def after_all_players_arrive(group: Group) -> None:
        """Determine reward based on punishment."""
        for player in group.get_players():
            others = player.get_others_in_group()

            player.punishment_received = sum(
                [o.punishment_for(player) for o in others]
            )

            percentage = min(player.punishment_received, C.PUNISHMENT_MAX)
            player.punishment_loss = round(player.punishment_base * (percentage / 100.0))

            player.punishment_cost = sum(
                [C.cost(player.punishment_for(o)) for o in others]
            )

            player.payoff = player.punishment_base - player.punishment_loss - player.punishment_cost


class Results(Page):
    """Display result to players."""

    timeout_seconds = 45

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Provide other players and punishment schedule."""
        percentage = min(player.punishment_received, C.PUNISHMENT_MAX)

        return dict(percentage=percentage)


page_sequence = [
    Introduction,
    Contribute,
    ContributeWait,
    Punish,
    PunishWait,
    Results,
]


def vars_for_admin_report(subsession):
    session = subsession.session

    contribute_avg = [None] * C.NUM_ROUNDS
    punish_avg = [None] * C.NUM_ROUNDS

    for round in range(1, C.NUM_ROUNDS + 1):

        subsession = Subsession.objects_get(session=session, round_number=round)

        contribute = [p.field_maybe_none('contribution') for p in subsession.get_players()]
        contribute = [c for c in contribute if c is not None]

        if contribute:
            contribute_avg[round - 1] = float(sum(contribute) / len(contribute))

        punish = [p.field_maybe_none('punishment_received') for p in subsession.get_players()]
        punish = [p / 3 for p in punish if p is not None]

        if punish:
            punish_avg[round - 1] = sum(punish) / len(punish)

    return dict(
        contribute=json.dumps(contribute_avg),
        punish=json.dumps(punish_avg),
    )
