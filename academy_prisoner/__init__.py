"""Classic Prisoner's Dilemma game with chat for coordination."""

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.models_concrete import ChatMessage
from otree.database import BooleanField

from otree.views import Page, WaitPage
from otree.forms import widgets

from wallet import Wallet

import json


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
    def has_chosen(self) -> bool:
        return (self.field_maybe_none('cooperate') is not None)

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

    @staticmethod
    def live_method(player: Player, message):
        return {
            player.opponent.id_in_group: message
        }

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


def vars_for_admin_report(subsession):
    session = subsession.session

    # Compute cooperation ratios across rounds
    ratio = []
    for round in range(1, C.NUM_ROUNDS + 1):
        subsession = Subsession.objects_get(session=session, round_number=round)

        coop_yes = 0
        coop_no = 0
        for group in subsession.get_groups():
            c1, c2 = [p.field_maybe_none('cooperate') for p in group.get_players()]

            if c1 is not None and c2 is not None:
                if c1 and c2:
                    coop_yes += 1
                else:
                    coop_no += 1

        try:
            ratio += [100.0 * coop_yes / (coop_no + coop_yes)]
        except:
            ratio += [None]

    # Extract chat messages and outcome
    all_names = {}
    all_chats = {}

    for round in range(1, C.NUM_ROUNDS + 1):
        subsession = Subsession.objects_get(session=session, round_number=round)

        # For each group this round...
        for group in subsession.get_groups():
            [p1, p2] = group.get_players()

            channel = "{}-{}-{}".format(
                session.id, C.NAME_IN_URL, group.id
            )

            #print(channel)

            coop1 = p1.field_maybe_none("cooperate")
            coop2 = p2.field_maybe_none("cooperate")

            name1 = Wallet.current(p1.participant).public
            name2 = Wallet.current(p2.participant).public


            for msg in ChatMessage.objects_filter().order_by('timestamp'):
                print(msg.channel)

            # ... collect all message of group in round ...
            messages = []
            for msg in ChatMessage.objects_filter(channel=channel).order_by('timestamp'):

                print(msg)

                name = "Unknown"
                color = None

                if msg.participant == p1.participant:
                    name = name1
                    if coop1 is not None:
                        color = "success" if coop1 else "danger"

                elif msg.participant == p2.participant:
                    name = name2
                    if coop2 is not None:
                        color = "success" if coop2 else "danger"

                messages += [
                    (name, color, msg.body)
                ]

            # ... and collect them for each participant pair
            pp = p1.participant

            if pp not in all_chats:
                all_chats[pp] = []
                all_names[pp] = (name1, name2)

            all_chats[pp] += [(round, messages)]

    chat_combined = []

    for pp, messages in all_chats.items():
        name1, name2 = all_names[pp]
        chat_combined += [(name1, name2, messages)]

    return dict(
        coop=json.dumps(ratio),
        all_chats=chat_combined,
    )
