"""Try to guess 2/3 of the average number chosen, i.e. Keynesian beauty contest."""

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.database import BooleanField, FloatField, IntegerField
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from otree.views import Page, WaitPage

from typing import List, Optional

import math
import json

doc = __doc__


# MODELS
class C(BaseConstants):
    """Constants used across the app."""

    NAME_IN_URL = 'academy_guess'
    PLAYERS_PER_GROUP = None
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
    def size(self) -> int:
        return len(self.get_players())

    @property
    def guesses(self) -> List[int]:
        """Retrieve and sort all valid guesses from players."""
        # Use list comprehension to filter out None values
        valid_guesses = [p.field_maybe_none('guess') for p in self.get_players() if p.field_maybe_none('guess') is not None]
        return sorted(valid_guesses)

    @property
    def history(self) -> List[Optional[float]]:
        """Retrieve history of previous averages."""
        return [g.field_maybe_none('two_thirds_avg') for g in self.in_previous_rounds()]


class Player(BasePlayer):
    """Player keeps track of guess and if won."""

    guess = IntegerField(
        min=0, max=C.GUESS_MAX, label="Please pick a number from 0 to 100:",
        blank=True,
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

    timeout_seconds = 30

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        if timeout_happened:
            player.guess = None


class ResultsWaitPage(WaitPage):
    """Wait for group and compute result."""

    def after_all_players_arrive(group: Group) -> None:
        """Determine payoff for round."""
        players = group.get_players()

        # Filter out players whose guess is None
        players_with_guess = [p for p in players if p.field_maybe_none('guess') is not None]

        # Proceed only if there are players who made a guess
        if players_with_guess:
            # Calculate two_thirds_avg with players who made a guess
            guesses = [p.field_maybe_none('guess') for p in players_with_guess]
            two_thirds_avg = (2 / 3) * sum(guesses) / len(guesses)
            group.two_thirds_avg = round(two_thirds_avg, 2)

            # Find the best guess
            group.best_guess = min(guesses, key=lambda guess: abs(guess - group.two_thirds_avg))

            # Determine winners
            winners = [p for p in players_with_guess if p.guess == group.best_guess]
            group.num_winners = len(winners)
            for p in winners:
                p.is_winner = True
                p.payoff = C.JACKPOT / group.num_winners
        else:
            # Handle the case where no players made a guess
            group.two_thirds_avg = None
            group.best_guess = None
            group.num_winners = 0


class Results(Page):
    """Display result to players."""

    timeout_seconds = 20


def creating_session(subsession):
    if subsession.round_number == 1:
        players = subsession.get_players()

        factor = math.floor(len(players) / 6)

        group_1 = factor * 3 + len(players) % 6
        if factor > 1:
            group_2 = factor * 2

            if factor > 2:
                group_3 = factor
            else:
                group_3 = 0
                group_1 += factor
        else:
            group_2 = 0
            group_3 = 0
            group_1 += factor * 3

        matrix = [list(range(1, group_1 + 1))]
        if group_2:
            matrix += [list(range(group_1 + 1, group_1 + group_2 + 1))]

            if group_3:
                matrix += [list(range(group_1 + group_2 + 1, group_1 + group_2 + group_3 + 1))]

        subsession.set_group_matrix(matrix)
    else:
        subsession.group_like_round(1)


page_sequence = [Introduction, Guess, ResultsWaitPage, Results]


def vars_for_admin_report(subsession):
    session = subsession.session

    group_sizes = [g.size for g in subsession.get_groups()]

    group1_size = group_sizes[0]
    group2_size = group_sizes[1] if len(group_sizes) > 1 else 0
    group3_size = group_sizes[2] if len(group_sizes) > 2 else 0

    group1_best = [None] * C.NUM_ROUNDS
    group2_best = [None] * C.NUM_ROUNDS
    group3_best = [None] * C.NUM_ROUNDS

    for round in range(1, C.NUM_ROUNDS + 1):
        subsession = Subsession.objects_get(session=session, round_number=round)

        best = [g.field_maybe_none('best_guess') for g in subsession.get_groups()]

        i = round - 1
        group1_best[i] = best[0]
        group2_best[i] = best[1] if group2_size else None
        group3_best[i] = best[2] if group3_size else None

    return dict(
        group1_size=group1_size,
        group2_size=group2_size,
        group3_size=group3_size,

        group1_best=json.dumps(group1_best),
        group2_best=json.dumps(group2_best),
        group3_best=json.dumps(group3_best),
    )
