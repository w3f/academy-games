import random

from .models import Constants, Subsession
from .pages import *


doc = """
Parachain Auction experiment
"""

# All treatments to consider (TODO: Use more consistently)
ALL_TREATMENTS = ["hard", "candle", "activity"]


def creating_session(subsession: Subsession) -> None:
    """Intialize all random group and player values."""

    N_hard = subsession.session.config.get('num_hard_participants', 0)
    N_candle = subsession.session.config.get('num_candle_participants', 0)
    N_activity = subsession.session.config.get('num_activity_participants', 0)

    N_group = Constants.players_per_group

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

        treatments = mkTreatment("hard", N_hard) \
            + mkTreatment("candle", N_candle) \
            + mkTreatment("activity", N_activity)
        random.shuffle(treatments)

        for p, t in zip(subsession.get_players(), treatments):
            p.participant.treatment = t[0]
            p.participant.role = t[1]

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

    # Determine valuation based on role
    for p in subsession.get_players():
        if p.role == "global":
            p.valuation = random.randint(Constants.global_valuation_min, Constants.global_valuation_max)
        else:
            p.valuation = random.randint(0, Constants.local_valuation_total)


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
