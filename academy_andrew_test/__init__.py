from otree.constants import BaseConstants
from otree.currency import Currency
from otree.database import (
    IntegerField,
    StringField,
    MixinSessionFK,
)
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.room import ROOM_DICT
from otree.views import Page

from typing import List, Optional

doc = __doc__


class C(BaseConstants):
    NAME_IN_URL = 'academy_andrew_test'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    TITLE_PREFIX = "Lesson 42: "
    ANDREWS_VARIABLE = 50

class Subsession(BaseSubsession):
    """Default base subsession"""

    pass

class Group(BaseGroup):
    """Default base group"""

    pass

class Player(BasePlayer):
    """Default player"""
    my_var = IntegerField(blank=True)

class Andrew(Page):

    form_model = 'player'
    form_fields = ['my_var']

    @staticmethod
    def display_player_var(player: Player):
        return player.my_var

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return some data for Andrews variable to page template"""
        return {
            "andrews_data": C.ANDREWS_VARIABLE,
            "num_rounds": C.NUM_ROUNDS
        }

page_sequence = [Andrew]