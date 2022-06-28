"""Contains the Polkadot Academy Auction Experiment."""

from .models import Constants, Subsession, Group, Player
from .pages import page_sequence

import random


# Description in UI
doc = __doc__


# Session initialization
def creating_session(subsession: Subsession) -> None:
    """Intialize all random group and player values."""
    # Randomly choose length of candle auctions
    for g in subsession.get_groups():
        g.candle_duration = random.randint(
            Constants.candle_duration_min, Constants.candle_duration_max
        )
