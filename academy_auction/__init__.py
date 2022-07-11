"""An adaption of our auction experiment for the academy."""

from .models import Constants, Subsession, Group, Player
from .pages import page_sequence

from typing import List

import random


# Description in UI
doc = __doc__


# Session initialization
def creating_session(subsession: Subsession) -> None:
    """Intialize group and player values in first subsession of session."""

    if subsession.round_number == 1:
        # Check various conditions necessary for session setup
        N_hard = subsession.session.config.get('num_groups_hard', 0)
        N_candle = subsession.session.config.get('num_groups_candle', 0)
        N_activity = subsession.session.config.get('num_groups_activity', 0)

        N = len(subsession.get_groups())

        assert N_hard + N_candle + N_activity == N, "Sum of groups across treatments has to match total number."

        # Shuffle and assignr requested treatments
        treatments = [0] * N_hard + [1] * N_candle + [2] * N_activity

        random.shuffle(treatments)

        for group, treatment in zip(subsession.get_groups(), treatments):
            group._treatment = treatment
    else:
        subsession.group_like_round(subsession.round_number - 1)

    # Randomly choose length of candle auctions
    for g in subsession.get_groups():
        if g.treatment == "candle":
            g.candle_duration = random.randint(
                Constants.candle_duration_min, Constants.candle_duration_max
            )


# CUSTOM EXPORTER
def custom_export(all_players: List[Player]):
    """Export auctions bids as custom exporter."""
    # Export header row
    yield [
        'session_code',
        'participant_code',
        'participant_treatment',
        'group_id',
        'group_duration',
        'player_id',
        'player_valuation',
        'bid_timestamp',
        'bid_price',
    ]

    for player in all_players:
        session_code = player.session.code
        participant = player.participant
        group = player.group

        for bid in Bid.for_player(player):
            yield [
                session_code,
                participant.code,
                participant.treatment,
                group.id_in_subsession,
                group.duration_final,
                player.id_in_group,
                player.valuation,
                bid.timestamp,
                bid.price,
            ]
