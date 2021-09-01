from otree.currency import Currency
from otree.views import Page, WaitPage

from typing import Tuple, List

from .models import Constants, Player, Group, Bid, Result, FinalResult


# PAGES
class IntroPage(Page):
    """Introduction page explaining auction mechanics."""

    def is_displayed(self):
        return self.subsession.round_number == 1


class ChatWaitPage(WaitPage):
    """Wait page to collect player before entering chats."""


class ChatPage(Page):
    """Pre-auction chat page for players to coordinate bidding."""

    timeout_seconds = 60
    timer_text = """Time left to chat with other players:"""

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Returns additional data to pass to page template."""

        return {
            'role_channel': player.get_role_channel(),
        }


class StartWaitPage(WaitPage):
    """Wait page before auction to determine auction start time."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Records server side start time of auction."""
        group.timer_start()


class AuctionPage(Page):
    """Main auction page with live updated of auction state."""

    @staticmethod
    def get_local_choices(player: Player) -> List[Tuple[int, List[Tuple[str, int, int, int]]]]:
        """Returns a list of names, start slots and bitfield values per row of choices in UI."""

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
                names = [str(s) for s in slots]

            # Determine bit field value of selection
            values = [sum([2**p for p in range(s, s + L)]) for s in slots]

            # Determine gap at end of row
            gap = (N - offset) % L

            # Strip currency wrapper to be able to use value in javascript
            valuations_float = [float(v) for v in valuations[offset]]

            # Zip together columns to rows and add to choices
            choices += [(offset, gap, list(zip(names, values, valuations_float)))]

        return choices

    @staticmethod
    def get_winners(group: Group):
        if Constants.use_static_result(group):
            return AuctionPage.get_winners_static(group)
        else:
            return AuctionPage.get_winners_dynamic(group)

    # TODO: Add NamedTupple and Typing
    @staticmethod
    def get_winners_static(group: Group):

        # Abbreviations to improve readability
        N = Constants.get_global_slot_count(group)
        L = Constants.get_local_slot_count(group)

        assert L == 1, "Static results can only be used when local slot count is one"

        # Retrieve highest bids for each possible combination of slots
        bid_global = Bid.highest(group, 2 ** N - 1)
        bids_local = [Bid.highest(group, 2 ** s) for s in range(N)]

        # Extract required data of highest bids
        highest = [(b.slots, b.bidder, str(b.price)) for b in bids_local if b]
        if bid_global:
            highest.append((bid_global.slots, bid_global.bidder, str(bid_global.price)))

        # Determine ranking and distance
        total_global = bid_global.price if bid_global else 0
        total_local = sum([b.price for b in bids_local if b])

        distance = int(total_global - total_local)

        return highest, distance

    @staticmethod
    def get_winners_dynamic(group: Group) -> Result.Table:
        """Retrieve winning bids and format them to be passed to frontend."""

        return Result(group).to_table()

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Returns additional data to pass to page template."""

        range_slots = range(1, Constants.get_global_slot_count(player) + 1)

        return {
            'static_result': Constants.use_static_result(player),
            'range_slots': range_slots,
            'global_value': Constants.get_global_value(player),
            'global_valuation': float(player.get_global_valuation()),
            'local_choices': AuctionPage.get_local_choices(player),
            'num_global_slots': Constants.get_global_slot_count(player),
            'num_local_slots': Constants.get_local_slot_count(player),
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
                payload = "Received malformed bid: {}".format(fatal)

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

        if not timeout_happened:
            # TODO: Make sure this is tracked
            print("Warning: Player ended auction before timeout!")


class EndWaitPage(WaitPage):
    """Wait page at end of auction to trigger result calculation."""

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Determine winner at end of page."""

        # TODO: Compute result only once?

        # Determine payoff based on randomly select round after last auction
        if group.subsession.round_number == Constants.num_rounds:

            reward_round = group.session.reward_round

            for p in group.get_players():
                reward_group = p.in_round(reward_round).group
                p.participant.payoff = FinalResult(reward_group).get_profit(p)


class ResultPage(Page):
    """Page to display results at end of auction."""

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Returns additional data to pass to page template."""

        num_global_slots = Constants.get_global_slot_count(player)
        range_global_slots = range(1, num_global_slots + 1)

        result = FinalResult(player.group)

        return {
            'num_global_slots': num_global_slots,
            'range_global_slots': range_global_slots,
            'has_result': result.has_winner(),
            'result': result.to_table(True),
            'profit': result.get_profit(player),
        }


class OutroPage(Page):
    """Final page displaying overall result."""

    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Returns additional data to pass to page template."""

        return {
            "round": player.session.reward_round,
            "reward": player.participant.payoff_plus_participation_fee()
        }
