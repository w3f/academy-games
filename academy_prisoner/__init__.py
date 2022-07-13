"""Classic Prisoner's Dilemma game with chat for coordination."""

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.database import BooleanField

from otree.views import Page, WaitPage
from otree.forms import widgets


doc = __doc__


# MODELS
class C(BaseConstants):
    """App constants and configs."""

    NAME_IN_URL = 'academy_prisoner'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
    TITLE_PREFIX = "Lesson 2.2: "
    INSTRUCTIONS_TEMPLATE = 'academy_prisoner/instructions.html'
    PAYOFF_A = Currency(300)
    PAYOFF_B = Currency(200)
    PAYOFF_C = Currency(100)
    PAYOFF_D = Currency(0)


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Default base group."""

    pass


class Player(BasePlayer):
    """Tracks player choice and payoff."""

    cooperate = BooleanField(
        choices=[[True, 'Cooperate'], [False, 'Defect']],
        doc="""This player's decision""",
        widget=widgets.RadioSelect,
    )

    @property
    def choice(self) -> str:
        """Return players choice as string."""
        return self.field_display('cooperate')

    @property
    def opponent(self) -> "Player":
        """Return players opponent."""
        return self.get_others_in_group()[0]


# VIEWS
class Introduction(Page):
    """Display instructions to players."""

    timeout_seconds = 120

    @staticmethod
    def is_displayed(player: Player):
        """Only display instructions during first round."""
        return player.round_number == 1


class DecisionWait(WaitPage):
    """Wait for players to be ready."""

    pass


class Decision(Page):
    """Collect players decisions."""

    form_model = 'player'
    form_fields = ['cooperate']


class ResultsWait(WaitPage):
    """Wait for players and determine result."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Determine payoff of current round."""
        payoff_matrix = {
            (False, True): C.PAYOFF_A,
            (True, True): C.PAYOFF_B,
            (False, False): C.PAYOFF_C,
            (True, False): C.PAYOFF_D,
        }

        for player in group.get_players():
            player.payoff = payoff_matrix[
                (player.cooperate, player.opponent.cooperate)
            ]


class Results(Page):
    """Display result to player."""

    timeout_seconds = 45


page_sequence = [Introduction, DecisionWait, Decision, ResultsWait, Results]
