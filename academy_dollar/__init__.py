"""Classic dollar auction designed Martin Shubik"""

import time

from otree.constants import BaseConstants
from otree.currency import RealWorldCurrency
from otree.models import BaseSubsession, BaseGroup, BasePlayer
from otree.database import BooleanField, RealWorldCurrencyField, IntegerField

from otree.views import Page, WaitPage

from wallet import WalletPlayer


doc = __doc__


# MODELS
class C(BaseConstants):
    NAME_IN_URL = 'academy_dollar'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 1
    TITLE_PREFIX = "Lesson 2.3: "
    INSTRUCTIONS_TEMPLATE = 'academy_dollar/instructions.html'
    JACKPOT = RealWorldCurrency(1.00)
    INCREMENT = RealWorldCurrency(0.05)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    first_price = RealWorldCurrencyField(initial=0)
    first_player = IntegerField(initial=0)

    second_price = RealWorldCurrencyField(initial=0)
    second_player = IntegerField(initial=0)


class Player(WalletPlayer):

    # Players endowment, determines how high they can bid
    endowment = RealWorldCurrencyField()

    # Check otree's timer structure for time outs
    def has_timed_out(self):
        pp = self.participant

        return (
            pp._timeout_page_index == pp._index_in_pages
            and pp._timeout_expiration_time is not None
            and (pp._timeout_expiration_time < time.time())
        )


class Intro(Page):

    timeout_seconds = 45

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        """Determine available balance."""
        player.endowment = player.balance


class WaitToStart(WaitPage):
    pass


# PAGES
class Bid(Page):

    timeout_seconds = 90
    timer_text = "Time left till auction will end:"

    @staticmethod
    def js_vars(player: Player):
        return {
            'id_in_group': player.id_in_group,
            'increment': C.INCREMENT,
        }

    @staticmethod
    def live_method(player: Player, data):

        group = player.group

        # Return values
        status = "init"
        payload = None

        # Try to parse data if provided
        if data:
            price = RealWorldCurrency(data)

            if player.has_timed_out():
                # Bid was submitted after auction ended
                status = "error"
                payload = "Auction has ended."
            elif price > player.endowment:
                # Bid exceeds available funds
                status = "error"
                payload = "Price exceeds your available funds of {}".format(player.endowment)
            elif price <= group.first_price:
                # Bid is to low change outcome
                status = "error"
                payload = "Price has to exceed current highest bid of {}".format(group.first_price)
            elif group.first_player == player.id_in_group:
                # Player is already highest bidder
                status = "error"
                payload = "You are already the highest bidder."
            else:
                # Bid passed all checks and is highest bid
                status = "success"

                group.second_price = group.first_price
                group.second_player = group.first_player

                group.first_price = price
                group.first_player = player.id_in_group

        if not payload:
            # Return latest auction state by default
            next_price = group.first_price + C.INCREMENT;

            payload = (
                next_price, str(next_price),
                str(group.first_price), group.first_player,
                str(group.second_price), group.second_player
            )

        if status == "success":
            # Successful bids send updates to everybody
            return {
                pid: (status if pid == player.id_in_group else "update", payload)
                for pid in range(1, C.PLAYERS_PER_GROUP + 1)
            }

        # Any other request or outcome is only reported to the sender
        return {
            player.id_in_group: (status, payload)
        }


class ResultsWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        currency_ratio = group.session.config['real_world_currency_per_point']

        # Calculate first bidder payoff
        if group.first_player > 0:
            first_player = group.get_player_by_id(group.first_player)
            first_player.payoff = (C.JACKPOT - group.first_price) / currency_ratio

        # Calculate second bidder payoff
        if group.second_player > 0:
            second_player = group.get_player_by_id(group.second_player)
            second_player.payoff = -group.second_price / currency_ratio

        # Mark session as finished
        for player in group.get_players():
            player.participant.finished = True


class Results(Page):
    pass

page_sequence = [Intro, WaitToStart, Bid, ResultsWaitPage, Results]


# CUSTOM ADMIN REPORT
def vars_for_admin_report(subsession):
    prices = []

    for group in subsession.get_groups():
        if group.first_player:
            prices += [ group.first_price ]

    if prices:
        return dict(
            price_highest=max(prices),
            price_average=sum(prices) / len(prices),
            price_lowest=min(prices),
        )
    else:
        return dict(
            price_highest="-",
            price_average="-",
            price_lowest="-",
       )
