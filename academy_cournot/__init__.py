"""A Cournot competition where unit sell price depends on total units produced."""

from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.database import CurrencyField, IntegerField

from otree.views import Page, WaitPage

doc = __doc__


# MODELS
class C(BaseConstants):
    """Default app constants."""

    NAME_IN_URL = 'academy_cournot'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 2
    TITLE_PREFIX = "Session I: "
    INSTRUCTIONS_TEMPLATE = 'academy_cournot/instructions.html'
    # Total production capacity of all players
    TOTAL_CAPACITY = 60
    MAX_UNITS_PER_PLAYER = int(TOTAL_CAPACITY / PLAYERS_PER_GROUP)


class Subsession(BaseSubsession):
    """Plain default subsession."""

    pass


class Group(BaseGroup):
    """Default group tracking overall price and production."""

    unit_price = CurrencyField()
    total_units = IntegerField(doc="""Total units produced by all players""")


class Player(BasePlayer):
    """Default player tracking units produced."""

    units = IntegerField(
        min=0,
        max=C.MAX_UNITS_PER_PLAYER,
        doc="""Quantity of units to produce""",
        label="How many units will you produce (from 0 to 30)?",
    )

    def get_other_units(self) -> int:
        """Return sum of all units of other players in group."""
        return self.group.total_units - self.units


# VIEWS
class IntroPage(Page):
    """Into page displaying introduction."""

    timeout_seconds = 30

    def is_displayed(self):
        """Display page on during the first round."""
        return self.subsession.round_number == 1


class DecisionPage(Page):
    """Page to collect units produced by player."""

    form_model = 'player'
    form_fields = ['units']


class ResultWaitPage(WaitPage):
    """Page to collect all players and calculate result."""

    body_text = "Waiting for the other participant to decide."

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Calculate result after all player are ready."""
        players = group.get_players()

        group.total_units = sum(p.units for p in players)
        group.unit_price = C.TOTAL_CAPACITY - group.total_units

        for p in players:
            p.payoff = group.unit_price * p.units


class ResultPage(Page):
    """Page to display result to players."""

    @staticmethod
    def vars_for_template(player: Player):
        """Return additional data for page template."""
        return dict(other_player_units=player.get_other_units())


page_sequence = [IntroPage, DecisionPage, ResultWaitPage, ResultPage]
