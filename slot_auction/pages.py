from otree.currency import Currency
from otree.database import MixinSessionFK
from otree.views import Page, WaitPage

from typing import Tuple, List

from .models import Constants, Player, Group, Bid


# HELPERS
def bids2row(model: MixinSessionFK, bids: List[Bid]) -> List[Tuple[int, int, Currency]]:
    """Generate row layout from list of non-overlapping bids."""

    N = Constants.get_global_slot_count(model)

    sorted(bids, key=lambda b: b.slots)

    layout = []  # contains (width, player, price)
    next = 0
    for b in bids:
        first = b.first_slot

        gap = first - next
        if gap > 0:
            layout += [(gap, 0, 0)]

        next = b.last_slot + 1
        layout += [(next - first, b.bidder, b.price)]

    gap = N - next
    if gap > 0:
        layout += [(gap, 0, 0)]

    return layout


def result2table(model, result) -> List[Tuple[List[Tuple[int, int, Currency]], Currency]]:
    """Turn result into table layout."""

    table = []  # (bids, total)
    returned = set()
    for total, _, bids in result:
        if not returned.issuperset(bids):
            table += [(bids2row(model, bids), total)]
            returned.update(bids)

    return table


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

            # Zip together columns to rows and add to choices
            choices += [(offset, gap, list(zip(names, values, valuations[offset])))]

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
    def get_winners_dynamic(group: Group) -> List[Tuple[int, List[Tuple[int, Currency]], Currency]]:
        """Retrieve winning bids and format them to be passed to frontend."""

        return result2table(group, Bid.get_winners(group))

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Returns additional data to pass to page template."""

        range_slots = range(1, Constants.get_global_slot_count(player) + 1)

        return {
            'static_result': Constants.use_static_result(player),
            'range_slots': range_slots,
            'global_value': Constants.get_global_value(player),
            'global_valuation': int(player.get_global_valuation()),
            'local_choices': AuctionPage.get_local_choices(player),
            'num_global_slots': Constants.get_global_slot_count(player),
            'num_local_slots': Constants.get_local_slot_count(player),
        }

    @staticmethod
    def live_method(player: Player, data: dict) -> dict:
        """Receive players bids and act accordingly."""

        # Save time of reception
        timestamp = player.group.timestamp()

        # Try and parse bid data if provided
        if data:
            try:
                price = data['price']
                slots = data['slot']

                # FIXME: Needs checks and better feedback

                # Check timestamp

                # Check if bid is a valid choice

                # Check if bid is within valuation

                # Check that bid is higher

                # Check activity rule if necessary

                Bid.create(
                    group=player.group,
                    player=player,
                    slots=slots,
                    price=Currency(price),
                    timestamp=timestamp
                )

                # Reset auction time if activity rule is used
                if player.group.treatment == "activity":
                    player.group.timer_reset()

            except Exception as ex:
                print('Exception: ', ex)
                print('Data: ', data)
                return

        # Always return current state
        return {0: AuctionPage.get_winners(player.group)}

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

        timestamp = None
        if group.treatment == "candle":
            timestamp = float(group.candle_duration)

        # FIXME: Compute result only once
        #group.result = Bid.get_winners(group, timestamp)


class ResultPage(Page):
    """Page to display results at end of auction."""

    @staticmethod
    def get_result_table(group: Group):

        timestamp = None
        if group.treatment == "candle":
            timestamp = float(group.candle_duration)

        return result2table(group, Bid.get_winners(group, timestamp))

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Returns additional data to pass to page template."""

        unranked_table = ResultPage.get_result_table(player.group)

        range_slots = range(1, Constants.get_global_slot_count(player) + 1)
        result = zip(range(1, len(unranked_table) + 1), *zip(*unranked_table))

        return {
            'range_slots': range_slots,
            'result': result
        }


class OutroPage(Page):
    """Final page displaying overall result."""

    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds
