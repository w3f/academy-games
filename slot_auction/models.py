from otree.constants import BaseConstants
from otree.currency import Currency
from otree.database import (
    ExtraModel,
    Link,
    IntegerField,
    FloatField,
    CurrencyField,
    StringField,
    LongStringField,
    MixinSessionFK,
)
from otree.models import BaseSubsession, BaseGroup, BasePlayer

from typing import Tuple, List, Union, Optional

import math
import time
import json

# GENERAL TYPE ALIASES
Slots = int

# DEFAULT MODELS
class Constants(BaseConstants):
    name_in_url = 'slot_auction'
    players_per_group = 3
    num_rounds = 15

    # Default slots config (overridden by session)
    _num_global_slots = 2
    _num_local_slots = 1

    # Valuation config
    global_valuation_min = Currency(90)
    global_valuation_max = Currency(110)

    local_valuation_total = Currency(80)

    # Duration config
    hard_duration = 60.0

    candle_duration_max = 90
    candle_duration_min = 45

    activity_duration = 30.0

    @staticmethod
    def use_static_result(model: MixinSessionFK) -> bool:
        """Return true if static result UI can be used."""

        return Constants.get_local_slot_count(model) <= 1

    @staticmethod
    def get_global_slot_count(model: MixinSessionFK) -> int:
        """Return total number of slots for auction."""

        return model.session.config.get('num_global_slots', Constants._num_global_slots)

    @staticmethod
    def get_local_slot_count(model: MixinSessionFK) -> int:
        """Return number of slots in local players bid."""

        return model.session.config.get('num_local_slots', Constants._num_local_slots)

    @staticmethod
    def get_global_value(model: MixinSessionFK) -> Slots:
        """Return value equivalent to bidding on all slots."""
        return 2 ** Constants.get_global_slot_count(model) - 1

    @staticmethod
    def get_local_values(model: MixinSessionFK) -> List[Slots]:
        """Return slot values of available local choices."""

        # Abbreviations to improve readability
        N = Constants.get_global_slot_count(model)
        L = Constants.get_local_slot_count(model)

        values = []
        for offset in range(L):
            slots = [s for s in range(offset, N, L) if s + L <= N]
            values += [sum([2**p for p in range(s, s + L)]) for s in slots]

        return values

    @staticmethod
    def get_valid_values(model: MixinSessionFK) -> List[Slots]:
        """Return all valid global and local slot values."""

        return [Constants.get_global_value(model)] + Constants.get_local_values(model)

    @staticmethod
    def get_local_rows(model: MixinSessionFK) -> List[int]:
        """Returns number of choices per row in UI."""

        # Abbreviations to improve readability
        N = Constants.get_global_slot_count(model)
        L = Constants.get_local_slot_count(model)

        return [(N - offset) // L for offset in range(L)]

    # Basic sanity checks
    assert _num_global_slots > _num_local_slots
    assert global_valuation_max >= global_valuation_min


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = StringField()
    candle_duration = IntegerField()

    timestamp_start = FloatField()
    timestamp_reset = FloatField()

    result_json = LongStringField()

    def timer_start(self) -> None:
        """Start auction timer of group."""

        self.timestamp_start = time.monotonic()
        self.timestamp_reset = self.timestamp_start

    def timer_reset(self) -> None:
        """Reset auction timer of group."""

        self.timestamp_reset = time.monotonic()

    def timestamp(self) -> float:
        """Get timestamp in s relative to start of auction."""

        return time.monotonic() - self.timestamp_start

    @property
    def timeout_total(self) -> float:
        """Return the initial page timeout in s based on auction format."""

        if self.treatment == "hard":
            return Constants.hard_duration
        elif self.treatment == "candle":
            return float(Constants.candle_duration_max)
        elif self.treatment == "activity":
            return Constants.activity_duration
        else:
            raise Exception("Unknown treatment: ", self.treatment)

    @property
    def timeout_total_ms(self) -> int:
        """Return the initial page timeout in ms based on auction format."""

        return int(self.timeout_total * 1000)

    @property
    def timeout_remaining(self) -> float:
        """Return remaining timeout in s since last reset or start."""

        return self.timestamp_reset + self.timeout_total - time.monotonic()

    @property
    def timeout_remaining_ms(self) -> int:
        """Return remaining timeout in ms since last reset or start."""

        return int(self.timeout_remaining * 1000)

    @property
    def duration(self) -> float:
        """Return total auction length taking into account timer resets."""

        return self.timestamp_reset - self.timestamp_start + self.timeout_total

    def is_valid_timestamp(self, timestamp: float) -> bool:
        """Check if provided timestamp falls within the auction period."""

        return 0 < timestamp <= self.duration

    @property
    def result(self) -> any:
        """Return decode result."""

        return json.loads(self.result_json)

    @result.setter
    def result(self, value):
        """Encode result before setting it."""

        self.result_json = json.dumps(value)


class Player(BasePlayer):
    valuation = CurrencyField()

    @property
    def role(self) -> str:
        """Return role from underlying participant"""

        return self.participant.role

    @property
    def treatment(self) -> str:
        """Return treatment from underlying participant"""

        return self.participant.treatment

    def get_role_channel(self) -> str:
        """Return name of role specific chat channel."""

        return '{}-{}'.format(self.group.id, self.role)

    def get_valuation(self, slots: Slots) -> Currency:
        """Return valuation of a specific slot."""

        if Constants.get_global_value(self) == slots:
            return self.get_global_valuation()
        elif self.role == 'local':
            values = Constants.get_local_values(self)

            # FIXME: Only values the first two options, so does not work for num_slots > 2
            if slots == values[0]:
                return self.valuation
            elif slots == values[1]:
                return Constants.local_valuation_total - self.valuation

        return Currency(0)

    def get_global_valuation(self) -> Currency:
        """Return player valuations for all slots."""

        if self.role == 'global':
            return self.valuation
        else:
            return Constants.local_valuation_total

    def get_local_valuations(self) -> List[List[Currency]]:
        """Return players valuation for each of the local choices."""

        rows = Constants.get_local_rows(self)
        valuations = [[0] * n for n in rows]

        if self.role == 'local':
            # FIXME: Only values the first two options, so does not work for num_slots > 2
            valuations[0][0] = self.valuation
            valuations[0][1] = Constants.local_valuation_total - self.valuation

        return valuations


# EXTRA MODELS
class Bid(ExtraModel):
    group = Link(Group)
    player = Link(Player)
    slots = IntegerField()
    price = CurrencyField()
    timestamp = FloatField()

    @property
    def bidder(self):
        """Return unique bidder id within his bidding group."""

        return self.player.id_in_group

    @property
    def first_slot(self):
        """Return first slot of bid."""

        low = (self.slots & -self.slots)
        lowBit = -1

        while (low):
            low >>= 1
            lowBit += 1

        return lowBit

    @property
    def last_slot(self):
        """Return last slot of bid."""

        return math.floor(math.log(self.slots, 2))

    @property
    def num_slots(self):
        """Return number of slots selected in bid."""

        slots = self.slots

        count = 0
        while (slots):
            count += slots & 1
            slots >>= 1

        return count

    def get_profit(self):
        """Return difference between valuation and price of bid."""

        valuation = self.player.get_valuation(self.slots)

        if valuation == 0:
            print("WARNING: no valuation for {} bid".format(self.price))

        return valuation - self.price

    class SubmissionFailure(Exception):
        """Failure to create valid bid with supplied data."""
        pass

    @staticmethod
    def submit(player: Player, slots: Slots, price: Currency, timestamp: float) -> None:
        """Check and submit bid to database"""

        # Some simple sanity checks
        if not 0 < slots < 2 ** Constants.get_global_slot_count(player):
            raise Bid.SubmissionFailure("No or invalid slots selected")

        if not price > 0:
            raise Bid.SubmissionFailure("Price must be larger then zero")

        # Check timestamp
        if not player.group.is_valid_timestamp(timestamp):
            raise Bid.SubmissionFailure("Auction time has run out")

        # Check if bid is a valid choice
        if slots not in Constants.get_valid_values(player):
            raise Bid.SubmissionFailure("Invalid combination of slots selected")

        # Check if bid is within valuation
        valuation = player.get_valuation(slots)
        if price > valuation:
            raise Bid.SubmissionFailure(
                "Price must not exceed valuation of {}".format(valuation)
            )

        # Check that bid is higher for selection
        highest = Bid.highest(player.group, slots)
        if highest and highest.price >= price:
            raise Bid.SubmissionFailure(
                "Price must exceed current best bid at {}".format(highest.price)
            )

        Bid.create(
            group=player.group,
            player=player,
            slots=slots,
            price=price,
            timestamp=timestamp
        )

        # Reset auction time if activity rule is used
        if player.group.treatment == "activity":
            player.group.timer_reset()

    @staticmethod
    def for_slots(group: Group, slots: Slots, timestamp: Optional[float] = None) -> List["Bid"]:
        """Return all bids for a certain group, slots and optionally until a certain timestamp."""

        if timestamp:
            return Bid.objects_filter(Bid.timestamp <= timestamp, group=group, slots=slots).order_by('timestamp').all()
        else:
            return Bid.objects_filter(group=group, slots=slots).order_by('timestamp').all()

    @staticmethod
    def highest(group: Group, slots: Slots, timestamp: Optional[float] = None) -> Optional["Bid"]:
        """Return highest bid for a certain group, slots and optionally until a certain timestamp."""

        result = None
        for bid in Bid.for_slots(group, slots, timestamp):
            if not result or result.price < bid.price:
                result = bid

        return result

    # Type helpers
    CombinedBids = Tuple[Currency, Slots, List["Bid"]]  # = (total, slots, bids)

    @staticmethod
    def get_winners(group: Group, timestamp: Optional[float] = None) -> List[CombinedBids]:
        """Return the winnner for each slot of the auction, optionally until a certain timestamp."""

        # Get the highest local slots bids
        highest = [Bid.highest(group, slots, timestamp)
                   for slots in Constants.get_local_values(group)]

        result = [(b.price, b.slots, [b]) for b in highest if b]

        # Try to combine highest bids in all ways possible
        i = 0
        while i < len(result):
            a = result[i]

            k = i + 1
            while k < len(result):
                b = result[k]

                if not(a[1] & b[1]):
                    combined = (a[0] + b[0], a[1] | b[1], a[2] + b[2])
                    result.insert(k + 1, combined)

                k += 1

            i += 1

        # Add highest global bid
        global_highest = Bid.highest(group, Constants.get_global_value(group), timestamp)
        if global_highest:
            result += [(global_highest.price, global_highest.slots, [global_highest])]

        # Sort all bids and combination by highest price
        result.sort(reverse=True, key=(lambda e: e[0]))

        # Filter out duplicates with lower totals
        filtered = []
        included = set()
        for entry in result:
            _, _, bids = entry
            if not included.issuperset(bids):
                filtered.append(entry)
                included.update(bids)

        return filtered


class Result:

    def __init__(self, group: Group, timestamp: Optional[float] = None):
        self.winners = Bid.get_winners(group, timestamp)
        self.N = Constants.get_global_slot_count(group)

    def has_winner(self):
        return len(self.winners) > 0

    # Type alias to improve readability
    LayoutedBid = Tuple[int, int, Currency]  # = (width, player, price)

    Row = Tuple[List[LayoutedBid], Currency]
    RankedRow = Tuple[int, List[LayoutedBid], Currency]

    Table = Union[List[Row], List[RankedRow]]

    def to_table(self, with_rank: bool = False) -> Table:
        """Turn result into table layout."""

        table = []  # = (layout, total)
        for rank, (total, _, bids) in enumerate(self.winners):
            # Sort bids by slot
            sorted(bids, key=lambda b: b.slots)

            # Figure out row layout for bids
            layout = []  # = (width, player, price)
            next = 0
            for b in bids:
                first = b.first_slot

                # Add gap entry if bids do not touch
                gap = first - next
                if gap > 0:
                    layout += [(gap, 0, 0)]

                # Add bid itself
                next = b.last_slot + 1
                layout += [(next - first, b.bidder, b.price)]

            # Check and add gap at the end
            gap = self.N - next
            if gap > 0:
                layout += [(gap, 0, 0)]

            # Add resulting row to table
            if with_rank:
                table += [(rank + 1, layout, total)]
            else:
                table += [(layout, total)]

        return table

    def get_profit(self, player: Player) -> Currency:
        """Determine a player's profit in the auction."""

        if self.has_winner():
            winning_bids = self.winners[0][2]

            return sum([bid.get_profit() for bid in winning_bids
                        if bid.player == player],
                       start=Currency(0))

        return Currency(0)
