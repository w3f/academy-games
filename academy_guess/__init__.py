"""Try to guess 2/3 of the average number chosen, i.e. Keynesian beauty contest."""

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.database import BooleanField, FloatField, IntegerField
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree.views import Page, WaitPage

from typing import List


doc = __doc__


# MODELS
class C(BaseConstants):
    """Constants used across the app."""

    NAME_IN_URL = 'academy_guess'
    PLAYERS_PER_GROUP = 4
    NUM_ROUNDS = 10
    TITLE_PREFIX = "Lesson 2.2: "
    JACKPOT = Currency(100)
    GUESS_MAX = 100
    INSTRUCTIONS_TEMPLATE = 'academy_guess/instructions.html'


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Group keeps track of average and best guesses."""

    two_thirds_avg = FloatField()
    best_guess = IntegerField()
    num_winners = IntegerField()

    @property
    def guesses(self) -> List[int]:
        """Retrieve and sort all guesses from players."""
        return sorted(p.guess for p in self.get_players())

    @property
    def history(self) -> List[float]:
        """Retrieve history of previous averages."""
        return [g.two_thirds_avg for g in self.in_previous_rounds()]


class Player(BasePlayer):
    """Player keeps track of guess and if won."""

    guess = IntegerField(
        min=0, max=C.GUESS_MAX, label="Please pick a number from 0 to 100:"
    )
    is_winner = BooleanField(initial=False)


# PAGES
class Introduction(Page):
    """Display introduction to players."""

    timeout_seconds = 120

    @staticmethod
    def is_displayed(player: Player):
        """Only display standalone intro page in first round."""
        return player.round_number == 1


class Guess(Page):
    """Collect player's guesses."""

    form_model = 'player'
    form_fields = ['guess']


class ResultsWaitPage(WaitPage):
    """Wait for group and compute result."""

    def after_all_players_arrive(group: Group) -> None:
        """Determine payoff for round."""
        players = group.get_players()
        guesses = [p.guess for p in players]
        two_thirds_avg = (2 / 3) * sum(guesses) / len(players)
        group.two_thirds_avg = round(two_thirds_avg, 2)
        group.best_guess = min(guesses, key=lambda guess: abs(guess - group.two_thirds_avg))
        winners = [p for p in players if p.guess == group.best_guess]
        group.num_winners = len(winners)
        for p in winners:
            p.is_winner = True
            p.payoff = C.JACKPOT / group.num_winners


class Results(Page):
    """Display result to players."""

    pass


page_sequence = [Introduction, Guess, ResultsWaitPage, Results]
