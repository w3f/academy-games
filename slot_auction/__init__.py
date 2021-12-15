import random

from typing import List

from .models import Constants, Subsession, Player, Bid, FinalResult
from .pages import *


doc = """
Parachain Auction experiment
"""

# All treatments to consider (TODO: Use more consistently)
ALL_TREATMENTS = ["hard", "candle", "activity"]


# SESSION INITIALIZATION
def creating_session(subsession: Subsession) -> None:
    """Intialize all random group and player values."""

    N_hard = subsession.session.config.get('num_hard_participants', 0)
    N_candle = subsession.session.config.get('num_candle_participants', 0)
    N_activity = subsession.session.config.get('num_activity_participants', 0)

    N_group = Constants.players_per_group

    # Initial setup happens in first subsession of session
    if subsession.round_number == 1:
        N = subsession.session.num_participants

        # Check various conditions necessary for session setup
        assert N_hard + N_candle + N_activity == N, "Sum of participants across treatments has to match total number."
        assert N_hard % N_group == 0, "Number of participants for hard ending auction has to be multiple of group size"
        assert N_candle % N_group == 0, "Number of participants of candle auction has to be multiple of group size"
        assert N_activity % N_group == 0, "Number of participants of activity-rule auction has to be multiple of group size"

        # Helper function to create list of all treatment and role combinations
        def mkTreatment(name, total):
            return list(zip(
                [name] * total,
                ["global"] * (total // N_group) + ["local"] * (N_group - 1) * (total // N_group)
            ))

        # Assemble and shuffle all requested treatments
        treatments = mkTreatment("hard", N_hard) \
            + mkTreatment("candle", N_candle) \
            + mkTreatment("activity", N_activity)
        random.shuffle(treatments)

        # Assign final result to players
        for p, t in zip(subsession.get_players(), treatments):
            p.participant.treatment = t[0]
            p.participant.role = t[1]

        # Lastly determine round used to calculate participants reward
        subsession.session.reward_round = random.randint(1, Constants.num_rounds)

    # Shuffle groups by treatment
    players = subsession.get_players()
    players_by_treatment = {t: [p for p in players if p.treatment == t] for t in ALL_TREATMENTS}

    # TODO: Remove this sanity check
    assert len(players_by_treatment['hard']) == N_hard
    assert len(players_by_treatment['candle']) == N_candle
    assert len(players_by_treatment['activity']) == N_activity

    group_treatments = []
    group_matrix = []
    for name, subgroup in players_by_treatment.items():
        group_treatments += [name] * (len(subgroup) // N_group)

        players_global = [p for p in subgroup if p.role == "global"]
        players_local = [p for p in subgroup if p.role == "local"]
        random.shuffle(players_global)
        random.shuffle(players_local)

        players_local_matrix = [players_local[i:i+N_group-1] for i in range(0, len(players_local), N_group - 1)]

        group_matrix += [[g] + l for g, l in zip(players_global, players_local_matrix)]

    subsession.set_group_matrix(group_matrix)

    for g, t in zip(subsession.get_groups(), group_treatments):
        g.treatment = t

        # TODO: Check logic and remove this sanity check
        for p in g.get_players():
            assert p.treatment == t

    # Randomly choose length of (potential) candle auction
    for g in subsession.get_groups():
        g.candle_duration = random.randint(Constants.candle_duration_min, Constants.candle_duration_max)

    N_slots = Constants.get_global_slot_count(subsession)

    # Determine valuation based on role
    for p in subsession.get_players():
        if p.role == "global":
            p.valuations = random.randint(Constants.global_valuation_min, Constants.global_valuation_max)
        else:
            valued_slots = random.choices(range(N_slots), k=int(Constants.local_valuation_total))
            p.valuations = [valued_slots.count(i) for i in range(N_slots)]


# CUSTOM ADMIN PAGE
def vars_for_admin_report(subsession: Subsession):
    """Return template variables for admin report."""

    num_global_slots = Constants.get_global_slot_count(subsession)
    range_global_slots = range(1, num_global_slots + 1)

    result_by_group = []
    for group in subsession.get_groups():
        result = FinalResult(group)

        profits = [(i + 1, result.get_profit(p))
                   for i, p in enumerate(group.get_players())]

        result_by_group += [(
            group.id,
            Bid.count(group),
            result.has_winner(),
            result.to_table(True),
            profits,
        )]

    return {
        'num_global_slots': num_global_slots,
        'range_global_slots': range_global_slots,
        'result_by_group': result_by_group,
    }


# CUSTOM EXPORTER
def custom_export(all_players: List[Player]):
    """Custom exporter for auctions bids."""

    # Export header row
    yield [
        'session_code',
        'participant_code',
        'participant_role',
        'participant_treatment',
        'group_round',
        'group_id',
        'group_duration',
        'player_id',
        'player_valuations'
        'bid_timestamp',
        'bid_slots',
        'bid_price',
        'bid_valuation',
    ]
    for player in all_players:
        session = player.session
        participant = player.participant
        group = player.group

        # Export at least valuations...
        yield [
            session.code,
            participant.code,
            participant.role,
            participant.treatment,
            group.round_number,
            group.id,
            group.duration_final,
            player.id_in_group,
            player.valuations,
            None,  # bid.timestamp
            None,  # bid.slots
            None,  # bid.price
            None,  # bid.valuation
        ]

        # ... and all bids
        for bid in Bid.for_player(player):
            yield [
                session.code,
                participant.code,
                participant.role,
                participant.treatment,
                group.round_number,
                group.id,
                group.duration_final,
                player.id_in_group,
                player.valuations,
                bid.timestamp,
                bid.slots,
                bid.price,
                bid.valuation,
            ]


# OTHER CONSTANTS
page_sequence = [
    IntroPage,
    ChatWaitPage,
    ChatPage,
    StartWaitPage,
    AuctionPage,
    EndWaitPage,
    ResultPage,
    OutroPage
]
