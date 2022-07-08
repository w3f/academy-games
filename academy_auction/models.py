"""Collection of all database models."""

from otree.constants import BaseConstants
from otree.currency import RealWorldCurrency
from otree.database import (
    ExtraModel,
    Link,
    BooleanField,
    IntegerField,
    FloatField,
    CurrencyField,
)
from otree.models import BaseSubsession, BaseGroup
from wallet import WalletPlayer

from typing import List, Optional

import time


# MODELS
class Constants(BaseConstants):
    """Collection of configuration constants."""

    name_in_url = 'academy_auction'
    players_per_group = 4
    num_rounds = 1
    TITLE_PREFIX = "Lesson 2.3: "

    # Duration config
    candle_duration_max = 120
    candle_duration_min = 60


class Subsession(BaseSubsession):
    """One round of auction."""

    pass


class Group(BaseGroup):
    """Group of players in the same auction."""

    candle_duration = IntegerField()
    timestamp_start = FloatField()

    def timer_start(self) -> None:
        """Start auction timer of group."""
        self.timestamp_start = time.monotonic()

    def timestamp(self) -> float:
        """Get timestamp in s relative to start of auction."""
        return time.monotonic() - self.timestamp_start

    @property
    def timeout_total(self) -> float:
        """Return the initial page timeout in s based on auction format."""
        return float(Constants.candle_duration_max)

    @property
    def timeout_total_ms(self) -> int:
        """Return the initial page timeout in ms based on auction format."""
        return int(self.timeout_total * 1000)

    @property
    def timeout_final(self) -> float:
        """Return the final auction timeout in s based on auction format."""
        return float(self.candle_duration)

    @property
    def timeout_remaining(self) -> float:
        """Return remaining timeout in s since last reset or start."""
        return self.timestamp_start + self.timeout_total - time.monotonic()

    @property
    def timeout_remaining_ms(self) -> int:
        """Return remaining timeout in ms since last reset or start."""
        return int(self.timeout_remaining * 1000)

    @property
    def duration_max(self) -> float:
        """Return maximum auction length considering max candle ending and timer resets."""
        return self.timeout_total

    @property
    def duration_final(self) -> float:
        """Return auction length considering actual candle ending and timer resets."""
        return self.timeout_final

    def is_valid_timestamp(self, timestamp: float) -> bool:
        """Check if provided timestamp falls within the auction period."""
        return 0 < timestamp <= self.duration_max


class Player(WalletPlayer):
    """Bidder in an auction."""

    # Players valuations, determines how high they can bid
    valuation = CurrencyField()

    # Track if player left page of the auction before its end
    auction_skipped = BooleanField(initial=False)


# EXTRA MODELS
class Bid(ExtraModel):
    """Additional model to track and process all bids."""

    # Useful index
    group = Link(Group)
    # Who bid?
    player = Link(Player)
    # How much?
    price = CurrencyField()
    # And when?
    timestamp = FloatField()

    @property
    def bidder(self) -> int:
        """Return unique bidder id within his bidding group."""
        return self.player.id_in_group

    @property
    def valuation(self) -> RealWorldCurrency:
        """Return how bidder valuates this bid."""
        return self.player.valuation

    @property
    def profit(self) -> RealWorldCurrency:
        """Return difference between valuation and price of bid."""
        valuation = self.valuation

        # TODO: Check if this warning is necessary
        if valuation == 0:
            print("WARNING: no valuation for {} bid".format(self.price))

        return valuation - self.price

    class SubmissionFailure(Exception):
        """Failure to create valid bid with supplied data."""

        @classmethod
        def from_format(cls, templ: str, *args, **kwargs) -> "Bid.SubmissionFailure":
            """Create error message from formatted string."""
            return cls(templ.format(*args, **kwargs))

    @staticmethod
    def submit(player: Player, price: RealWorldCurrency, timestamp: float) -> None:
        """Check and submit bid to database."""
        # Some simple sanity checks
        if not price > 0:
            raise Bid.SubmissionFailure("Price needs to be larger than zero.")

        # Check timestamp
        if not player.group.is_valid_timestamp(timestamp):
            raise Bid.SubmissionFailure("Auction has already ended.")

        # Check if bid is within valuation
        if price > player.valuation:
            raise Bid.SubmissionFailure.from_format(
                "Price exceeds available funds of {}", player.valuation
            )

        # Check that bid is higher for selection
        highest = Bid.highest(player.group)
        if highest and highest.price >= price:
            raise Bid.SubmissionFailure.from_format(
                "Price below current highest bid of {}", highest.price
            )

        Bid.create(
            group=player.group,
            player=player,
            price=price,
            timestamp=timestamp
        )

    @staticmethod
    def count(group: Group) -> int:
        """Return number of bids in group."""
        return Bid.objects_filter(group=group).count()

    @staticmethod
    def for_player(player: Player) -> List["Bid"]:
        """Return all bids of a certain player."""
        return Bid.objects_filter(group=player.group, player=player).order_by('timestamp').all()

    @staticmethod
    def for_group(group: Group, timestamp: Optional[float] = None) -> List["Bid"]:
        """Return all bids for a certain group and optionally until a certain timestamp."""
        if timestamp:
            return Bid.objects_filter(Bid.timestamp <= timestamp, group=group).order_by('timestamp').all()
        else:
            return Bid.objects_filter(group=group).order_by('timestamp').all()

    @staticmethod
    def highest(group: Group, timestamp: Optional[float] = None) -> Optional["Bid"]:
        """Return highest bid for a certain group and optionally until a certain timestamp."""
        result = None
        for bid in Bid.for_group(group, timestamp):
            if not result or result.price < bid.price:
                result = bid

        return result

    @staticmethod
    def result(group: Group) -> Optional["Bid"]:
        """Return highest bid for a certain group based on candle duration."""
        timestamp = float(group.candle_duration)
        return Bid.highest(group, timestamp)
