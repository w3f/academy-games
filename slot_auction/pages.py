"""Collection of all views."""

from otree.currency import Currency
from otree.views import Page, WaitPage

from typing import Tuple, List

from .models import Constants, Player, Group, Bid, Result, FinalResult
from .lexicon import Lexicon

from settings import LANGUAGE_CODE


def DEFAULT_TEMPLATE_VARS(page: str, player: Player) -> dict:
    """Return default template data used by most pages."""
    num_global_slots = Constants.get_global_slot_count(player)
    range_global_slots = range(1, num_global_slots + 1)

    return {
        'language': LANGUAGE_CODE,
        'lexicon': Lexicon.for_page_template(page),

        'num_rounds': Constants.get_num_rounds(player),
        'round': Constants.get_round_number(player),
        'id_in_group': player.id_in_group,

        'num_global_slots': num_global_slots,
        'range_global_slots': range_global_slots,
        'global_valuation': float(player.get_global_valuation()),
        'global_value': Constants.get_global_value(player),

        'num_local_slots': Constants.get_local_slot_count(player),
        'local_choices': AuctionPage.get_local_choices(player),
    }


# PAGES
class QuizPage(Page):
    """Quiz page checking the participants knowledge of auction mechanics."""

    form_model = "player"
    form_fields = [
        "quiz_player_per_group",
        "quiz_num_global_local",
        "quiz_role_shuffle",
    ]

    def is_displayed(self):
        """Display page only during the first round."""
        return self.subsession.round_number == 1

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        return {
            'lexicon': Lexicon.for_page_template("quiz"),
        }


def quiz_player_per_group_error_message(_: Player, value: int):
    """Check quiz answer to group size."""
    if value != Constants.players_per_group:
        return Lexicon.entry("quiz", 'error_message')


def quiz_num_global_local_error_message(_: Player, value: bool):
    """Check quiz answer to global/local player count."""
    if value:
        return Lexicon.entry("quiz", 'error_message')


def quiz_role_shuffle_error_message(_: Player, value: bool):
    """Check quiz answer to role shuffling."""
    if value:
        return Lexicon.entry("quiz", 'error_message')


class ValuationPage(Page):
    """Introduction page explaining auction mechanics."""

    timeout_seconds = 30
    timer_text = Lexicon.entry("valuation", 'timer')

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        return DEFAULT_TEMPLATE_VARS("valuation", player)


class ChatWaitPage(WaitPage):
    """Wait page to collect player before entering chats."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Record server side start time of auction."""
        group.chat_start()


class ChatPage(Page):
    """Pre-auction chat page for players to coordinate bidding."""

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        return {
            'lexicon': Lexicon.for_page_template("chat"),
            'num_rounds': Constants.get_num_rounds(player),
            'round': Constants.get_round_number(player),
            'role_channel': player.get_role_channel(),
            'player_nickname': "{} {}".format(
                Lexicon.entry('common', 'player'), player.id_in_group
            ),
        }

    @staticmethod
    def js_vars(player):
        """Return additional data to pass to js in page template."""
        return {
            'chat_duration': Constants.chat_duration,
            'chat_remaining_ms': player.group.chat_remaining_ms,
            'players_per_group': Constants.players_per_group,
        }

    @staticmethod
    def live_method(player: Player, data: dict) -> dict:
        """Receive ready signals from players."""
        # Check if group was locked already
        if player.group.chat_locked:
            return {player.id_in_group: (True, Constants.players_per_group)}

        # Try to parse data if provided
        update_all = False
        if data:
            try:
                ready = data['ready']

                if player.chat_skipped != ready:
                    player.chat_skipped = ready
                    update_all = True

            except Exception as fatal:
                print("Received: ", data)
                print("Exception: ", fatal)
                import traceback
                traceback.print_exc()

        # Check how many players are ready
        num_ready = sum([p.chat_skipped for p in player.group.get_players()])

        # Send out update to all players if required
        if update_all:
            # Lock chat if all player are ready
            if num_ready == Constants.players_per_group:
                player.group.chat_locked = True

            return {
                p.id_in_group: (p.chat_skipped, num_ready)
                for p in player.group.get_players()
            }

        # Otherwise just update sending player
        return {
            player.id_in_group: (player.chat_skipped, num_ready)
        }


class AuctionWaitPage(WaitPage):
    """Wait page before auction to determine auction start time."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Record server side start time of auction."""
        group.timer_start()


class AuctionPage(Page):
    """Main auction page with live updated of auction state."""

    @staticmethod
    def get_local_choices(player: Player) -> List[Tuple[int, List[Tuple[str, int, int, int]]]]:
        """Return a list of names, start slots and bitfield values per row of choices in UI."""
        # Abbreviations to improve readability
        N = Constants.get_global_slot_count(player)
        L = Constants.get_local_slot_count(player)

        # Get player specific valuations
        valuations = player.get_local_valuations()

        # There is a row for each offset in the choice table
        choices = []
        for offset in range(L):
            # Compute start slots
            slots = [s for s in range(offset, N, L) if s + L <= N]

            # Determine name of selection
            if L > 1:
                names = ["{} - {}".format(s + 1, s + L) for s in slots]
            else:
                names = [str(s + 1) for s in slots]

            # Determine bit field value of selection
            values = [sum([2**p for p in range(s, s + L)]) for s in slots]

            # Determine gap at end of row
            gap = (N - offset) % L

            # Strip currency wrapper to be able to use value in javascript
            valuations_float = [float(valuations.pop(0)) for _ in range(len(slots))]

            # Zip together columns to rows and add to choices
            choices += [(offset, gap, list(zip(names, values, valuations_float)))]

        return choices

    @staticmethod
    def get_winners(group: Group):
        """Retrieve winning bids and format them to be passed to frontend."""
        if Constants.use_static_result(group):
            return AuctionPage.get_winners_static(group)
        else:
            return AuctionPage.get_winners_dynamic(group)

    # TODO: Add NamedTupple and Typing
    @staticmethod
    def get_winners_static(group: Group):
        """Provide current winning bids for a static view."""
        # Abbreviations to improve readability
        N = Constants.get_global_slot_count(group)
        L = Constants.get_local_slot_count(group)

        assert L == 1, "Static results can only be used when local slot count is one"

        # Retrieve highest bids for each possible combination of slots
        bid_global = Bid.highest(group, 2 ** N - 1)
        bids_local = list(filter(None, [Bid.highest(group, 2 ** s) for s in range(N)]))

        # Extract required data of highest bids
        highest = [(b.slots, b.bidder, str(b.price)) for b in bids_local]
        if bid_global:
            highest.append((bid_global.slots, bid_global.bidder, str(bid_global.price)))

        # Determine ranking and distance
        total_global = bid_global.price if bid_global else 0
        total_local = sum([b.price for b in bids_local])

        distance = float(total_global - total_local)

        # Resolve tie based on timestamps
        winner = "none"
        if distance > 0:
            winner = "global"
        elif distance < 0:
            winner = "local"
        elif bid_global and bids_local:
            if bid_global.timestamp < max([b.timestamp for b in bids_local]):
                winner = "global"
            else:
                winner = "local"

        distance = abs(distance)

        return highest, winner, distance

    @staticmethod
    def get_winners_dynamic(group: Group) -> Result.Table:
        """Provide current winning bids for a static dynamic view."""
        return Result(group).to_table()

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        candle_percentage_normal = 100.0 * Constants.candle_duration_min / Constants.candle_duration_max

        return DEFAULT_TEMPLATE_VARS("auction", player) | {
            'use_static_result': Constants.use_static_result(player),
            'candle_percentage_ending': 100.0 - candle_percentage_normal,
            'candle_percentage_normal': candle_percentage_normal,
        }

    @staticmethod
    def js_vars(player: Player):
        """Return additional data to pass to js in page template."""
        group = player.group

        candle_percentage = 100.0 * (1.0 - Constants.candle_duration_min / Constants.candle_duration_max)

        return {
            'id_in_group': player.id_in_group,

            'timeout_remaining_ms': group.timeout_remaining_ms,
            'timeout_total_ms': group.timeout_total_ms,
            'timeout_total': group.timeout_total,

            'candle_percentage': candle_percentage,
        }

    @staticmethod
    def live_method(player: Player, data: dict) -> dict:
        """Receive players bids and act accordingly."""
        # Save time of reception
        timestamp = player.group.timestamp()

        # Return values
        status = "init"
        payload = None

        # Try to parse data if provided
        if data:
            try:
                price = Currency(data['price'])
                slots = int(data['slots'])

                Bid.submit(player, slots, price, timestamp)

                status = "success"
            except Bid.SubmissionFailure as error:
                status = "error"
                payload = str(error)
            except Exception as fatal:
                status = "error"
                payload = "{}: {}".format(
                    Lexicon.entry("auction", "result_malformed"), fatal
                )

                print("Received: ", data)
                print("Exception: ", fatal)
                import traceback
                traceback.print_exc()

        if not payload:
            # Return latest auction state by default
            payload = AuctionPage.get_winners(player.group)

        if status == "success":
            # Successful bids send updates to everybody
            return {
                pid: (status if pid == player.id_in_group else "update", payload)
                for pid in range(1, Constants.players_per_group + 1)
            }

        # Any other request or outcome is only reported to the sender
        return {
            player.id_in_group: (status, payload)
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        """Make sure page was submitted by timeout."""
        if timeout_happened: # Logic seems to be inverted for some reason
            player.auction_skipped = True
            print("Warning: Player ended auction before timeout!")


class ResultWaitPage(WaitPage):
    """Wait page at end of auction to trigger result calculation."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Determine winner after auction ends."""
        # TODO: Compute result only once?

        # Determine payoff based on randomly select round after last auction
        if group.subsession.round_number == Constants.num_rounds:

            reward_round = group.session.reward_round

            for p in group.get_players():
                player = p.in_round(reward_round)
                p.participant.payoff = FinalResult(player.group).get_profit(player)
                p.participant.finished = True


class ResultPage(Page):
    """Page to display results at end of auction."""

    timeout_seconds = 30
    timer_text = Lexicon.entry("result", 'timer')

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        result = FinalResult(player.group)

        return DEFAULT_TEMPLATE_VARS("result", player) | {
            'has_result': result.has_winner(),
            'result': result.to_table(True),
            'profit': result.get_profit(player),
        }


class RewardPage(Page):
    """Final page displaying overall result."""

    def is_displayed(self):
        """Display page on during the last round."""
        return self.subsession.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        reward_round = player.session.reward_round
        result = FinalResult(player.in_round(reward_round).group)

        return DEFAULT_TEMPLATE_VARS("reward", player) | {
            'reward_round': reward_round,
            'has_result': result.has_winner(),
            'result': result.to_table(True),
            'profit': result.get_profit(player),
            'reward': player.participant.payoff_plus_participation_fee()
        }
