"""An adaption of our auction experiment for the academy."""

from .models import Constants, Subsession, Group, Player, Bid
from .pages import page_sequence

from wallet import Wallet

from typing import Any, List, Set

import random

import operator
import functools

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


# CUSTOM ADMIN REPORT
def vars_for_admin_report(subsession):
    count_all = []
    highest_all = []
    winning_all = []

    count_hard = []
    highest_hard = []
    winning_hard = []

    count_activity = []
    highest_activity = []
    winning_activity = []

    count_candle = []
    highest_candle = []
    winning_candle = []

    for group in subsession.get_groups():
        count = Bid.count(group)
        count_all += [ count ]

        highest = Bid.highest(group)
        if highest:
            highest_all += [ highest.price ]

        winning = Bid.result(group)
        if winning:
            winning_all += [ winning.price ]

        if group.treatment == "hard":
            count_hard += [ count ]

            if winning:
                winning_hard += [ winning.price ]
            if highest:
                highest_hard += [ highest.price]

        elif group.treatment == "candle":
            count_candle += [ count ]

            if winning:
                winning_candle += [ winning.price ]
            if highest:
                highest_candle += [ highest.price ]

        elif group.treatment == "activity":
            count_activity += [ count ]

            if winning:
                winning_activity += [ winning.price ]
            if highest:
                highest_activity += [ highest.price ]

    def average(xs):
        return sum(xs) / len(xs) if xs else "-"

    def average_and_round(xs):
        return round(sum(xs) / len(xs), 2) if xs else "-"

    return dict(
        count_all=average_and_round(count_all),
        highest_all=average(highest_all),
        winning_all=average(winning_all),

        count_hard=average_and_round(count_hard),
        highest_hard=average(highest_hard),
        winning_hard=average(winning_hard),

        count_candle=average_and_round(count_candle),
        highest_candle=average(highest_candle),
        winning_candle=average(winning_candle),

        count_activity=average_and_round(count_activity),
        highest_activity=average(highest_activity),
        winning_activity=average(winning_activity),
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
                group.treatment,
                group.id_in_subsession,
                group.duration_final,
                player.id_in_group,
                player.valuation,
                bid.timestamp,
                bid.price,
            ]

    yield []

    yield [
        'wallet_public',
        'wallet_balance',
        'wallet_games',
        'wallet_bids',
        'wallet_winner',
        'wallet_price',
    ]

    for player in all_players:
        bid = Bid.result(player.group)

        winner = (bid.player == player) if bid else False
        price = bid.price if winner else ""

        wallet = player.wallet

        if wallet:
            yield [
                wallet.public,
                wallet.balance,
                len(wallet.games),
                len(Bid.for_player(player)),
                winner,
                price,
            ]

    yield []

    yield [
        'wallet_public',
        'wallet_balance',
        'wallet_games',
        'wallet_auction',
    ]

    def flatset(data: List[List[Any]]) -> Set[Any]:
        return functools.reduce(operator.or_, map(set, data), set())

    all_sessions = flatset([p.wallet.sessions for p in all_players if player.wallet])
    all_participants = flatset([s.pp_set for s in all_sessions])
    all_privates = set([Wallet.current(p)._private for p in all_participants if Wallet.current(p)])
    all_wallets = [Wallet.objects_first(_private=p) for p in all_privates]

    for wallet in all_wallets:
        games = [w.game_id for w in wallet.wallet_set if w.is_game]

        yield [
            wallet.public,
            wallet.balance,
            len(games),
            "auction" in games,
        ]
