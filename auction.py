"""otree session and room config for auction experiment."""

# Shared defaults between all auction sessions
AUCTION_CONFIG_DEFAULTS = dict(
    app_sequence=['slot_auction'],
    real_world_currency_per_point=2.00, participation_fee=10.00,
    doc="Please ensure adjustment of participants per treatment in 'Configure session' section.",
    num_demo_participants=3,
    num_hard_participants=0, num_candle_participants=0, num_activity_participants=0,
    num_global_slots=2, num_local_slots=1,
    shuffle_groups=False,
)

SESSION_CONFIGS = [
    # Configs to run actual studies
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_custom',
        display_name="Auction Experiment",
    ),

    # Demo of auction treatments
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_hard',
        display_name="Demo - Hard Ending Auction",
        num_hard_participants=3,
    ),
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_candle',
        display_name="Demo - Candle Auction",
        num_candle_participants=3,
    ),
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_activity',
        display_name="Demo - Activity Rule Auction",
        num_activity_participants=3,
    ),

    # Demo of complex auction logic
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_more',
        display_name="Demo - Three Slot Auction",
        num_hard_participants=3,
        num_global_slots=3,
        num_local_slots=1,
    ),
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_complex',
        display_name="Demo - Overlapping Slot Auction",
        num_hard_participants=3,
        num_global_slots=9,
        num_local_slots=3,
    ),
]

ROOMS = []
