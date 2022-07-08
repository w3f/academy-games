"""Collection of all views."""

from otree.currency import RealWorldCurrency
from otree.views import Page, WaitPage

from typing import Tuple

from .models import Constants, Player, Group, Bid


class IntroPage(Page):
    """Introduction page explaining auction mechanics."""

    timeout_seconds = 120

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        """Determine valuation and reconcile player that can not participate."""
        player.valuation = player.balance

        if player.valuation <= 0:
            player.payoff = RealWorldCurrency(0)
            player.participant.finished = True


class AuctionWaitPage(WaitPage):
    """Wait page before auction to determine auction start time."""

    @staticmethod
    def is_displayed(player: Player):
        """Force wait only if you participated in auction."""
        return player.valuation > 0

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Determine start time of auction."""
        # Record server side start time
        group.timer_start()


class AuctionPage(Page):
    """Main auction page with live updated of auction state."""

    @staticmethod
    def is_displayed(player: Player):
        """Display auction only if you have points with which to bid."""
        return player.valuation > 0

    @staticmethod
    def get_highest(group: Group) -> Tuple[int, RealWorldCurrency]:
        """Retrieve winning bid to be passed to frontend."""
        highest = Bid.highest(group)
        if highest:
            return highest.bidder, str(highest.price)

        return 0, str(RealWorldCurrency(0))

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        candle_percentage_normal = 100.0 * Constants.candle_duration_min / Constants.candle_duration_max

        return {
            'valuation': int(player.valuation),
            'id_in_group': player.id_in_group,
            'image_url': "academy/item_{:02d}.jpg".format(player.group.id % 10),
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
                price = RealWorldCurrency(data['price'])
                Bid.submit(player, price, timestamp)
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
            payload = AuctionPage.get_highest(player.group)

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
    def is_displayed(player: Player):
        """Force wait only if you participated in auction."""
        return player.valuation > 0

    @staticmethod
    def after_all_players_arrive(group: Group):
        """Determine valuations and start time of auction."""
        best = Bid.result(group)

        for player in group.get_players():
            if best and best.player == player:
                player.payoff = -best.price
            else:
                player.payoff = RealWorldCurrency(0)


class ResultPage(Page):
    """Page to display results at end of auction."""

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        best = Bid.result(player.group) if player.valuation > 0 else None

        reward = player.participant.payoff_plus_participation_fee()

        return {
            'id_in_group': player.id_in_group,
            'best': best,
            'reward': reward,
        }


page_sequence = [
    IntroPage,
    AuctionWaitPage,
    AuctionPage,
    ResultWaitPage,
    ResultPage,
]
