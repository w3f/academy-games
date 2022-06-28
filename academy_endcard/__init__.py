"""Cross session and app wallet to track particopant progress."""

from otree.constants import BaseConstants
from otree.models import BaseSubsession, BaseGroup
from wallet import WalletPlayer

from otree.views import Page


doc = __doc__


class C(BaseConstants):
    """Constants for a simple single player app."""

    NAME_IN_URL = 'academy_endcard'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Default base group."""

    pass


class Player(WalletPlayer):
    """Default wallet-associated player."""

    pass


class EndCard(Page):
    """Single page to display current status."""

    pass


page_sequence = [EndCard]
