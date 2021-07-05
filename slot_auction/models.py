from otree.api import *

from typing import Tuple, List, Optional

import math
import time
import json

# HELPERS
def now() -> int:
    """Return a monotonic timestamp in milliseconds."""

    return int(time.monotonic() * 1000)


# DEFAULT MODELS
class Constants(BaseConstants):
    name_in_url = 'slot_auction'
    players_per_group = 3
    num_rounds = 15

    # Default slots config (overridden by session)
    _num_global_slots = 2
    _num_local_slots = 1

    # Valuation config
    global_valuation_min = cu(90)
    global_valuation_max = cu(110)

    local_valuation_total = cu(80)

    # Duration config
    hard_duration = 60

    candle_duration_max = 90
    candle_duration_min = 45

    activity_duration = 30

    @staticmethod
    def use_static_result(model: models.MixinSessionFK):
        """Return true if static result UI can be used."""

        return Constants.get_local_slot_count(model) <= 1

    @staticmethod
    def get_global_slot_count(model: models.MixinSessionFK):
        """Return total number of slots for auction."""

        return model.session.config.get('num_global_slots', Constants._num_global_slots)

    @staticmethod
    def get_local_slot_count(model: models.MixinSessionFK):
        """Return number of slots in local players bid."""

        return model.session.config.get('num_local_slots', Constants._num_local_slots)

    @staticmethod
    def get_global_value(model: models.MixinSessionFK):
        """Return value equivalent to bidding on all slots."""
        return 2 ** Constants.get_global_slot_count(model) - 1

    @staticmethod
    def get_local_choices(model: models.MixinSessionFK) -> List[int]:
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
    def get_local_rows(model: models.MixinSessionFK) -> List[int]:
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
    treatment = models.StringField()
    candle_duration = models.IntegerField()

    timestamp_start = models.IntegerField()
    timestamp_reset = models.IntegerField()

    result_json = models.LongStringField()

    def timer_start(self):
        """Start auction timer of group."""

        self.timestamp_start = now()
        self.timestamp_reset = self.timestamp_start

    def timer_reset(self):
        """Reset auction timer of group."""

        self.timestamp_reset = now()

    def timestamp(self) -> int:
        """Get timestamp in ms relative to start of auction."""

        return now() - self.timestamp_start

    @property
    def timeout_total(self) -> int:
        """Return the initial page timeout in ms based on auction format."""

        if self.treatment == "hard":
            return Constants.hard_duration * 1000
        elif self.treatment == "candle":
            return Constants.candle_duration_max * 1000
        elif self.treatment == "activity":
            return Constants.activity_duration * 1000
        else:
            raise Exception("Unknown treatment: ", self.treatment)

    @property
    def timeout_remaining(self) -> int:
        """Return remaining timeout in ms since last reset or start."""

        return self.timestamp_reset + self.timeout_total - now()

    @property
    def result(self) -> any:
        """Return decode result."""

        return json.loads(self.result_json)

    @result.setter
    def result(self, value):
        """Encode result before setting it."""
        self.result_json = json.dumps(value)


class Player(BasePlayer):
    valuation = models.CurrencyField()

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

    def get_global_valuation(self) -> int:
        """Return player valuations for all slots."""

        if self.role == 'global':
            return self.valuation
        else:
            return Constants.local_valuation_total

    def get_local_valuations(self) -> List[List[int]]:
        """Return players valuation for each of the local choices."""

        rows = Constants.get_local_rows(self)
        valuations = [[0] * n for n in rows]

        if self.role == 'local':
            # FIXME: Only values the first two options, so does not work for num_slots > 2
            valuations[0][0] = int(self.valuation)
            valuations[0][1] = int(Constants.local_valuation_total - self.valuation)

        return valuations


# EXTRA MODELS
class Bid(ExtraModel):
    group = models.Link(Group)
    player = models.Link(Player)
    slots = models.IntegerField()
    price = models.CurrencyField()
    timestamp = models.IntegerField()

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

    @staticmethod
    def for_slots(group: Group, slots: int, timestamp: Optional[int] = None) -> List["Bid"]:
        """Return all bids for a certain group, slots and optionally until a certain timestamp."""

        if timestamp:
            return Bid.objects_filter(Bid.timestamp <= timestamp, group=group, slots=slots).order_by('timestamp').all()
        else:
            return Bid.objects_filter(group=group, slots=slots).order_by('timestamp').all()

    @staticmethod
    def highest(group: Group, slots: int, timestamp: Optional[int] = None) -> List["Bid"]:
        """Return highest bid for a certain group, slots and optionally until a certain timestamp."""

        result = None
        for bid in Bid.for_slots(group, slots, timestamp):
            if not result or result.price < bid.price:
                result = bid

        return result

    # TODO: Improve readability by using named tuples
    @staticmethod
    def get_winners(group: Group, timestamp: Optional[int] = None) -> List[Tuple[float, int, List["Bid"]]]:
        """Return the winnner for each slot of the auction, optionally until a certain timestamp."""

        # Get the highest local slots bids
        highest = [Bid.highest(group, slots, timestamp) for slots in Constants.get_local_choices(group)]

        result = [(float(b.price), b.slots, [b]) for b in highest if b]

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
            result += [(float(global_highest.price), global_highest.slots, [global_highest])]

        # Sort all bids and combination by highest price
        result.sort(reverse=True, key=(lambda e: int(e[0])))

        return result
