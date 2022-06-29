from os import environ


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

# Shared defaults to improve UI when creating academy sessions
ACADEMY_CONFIG_DEFAULTS = dict(
    academy_wallet_open=True,
    academy_wallet_create=True,
)

SESSION_CONFIGS = [

    # Configs to run actual studies
    AUCTION_CONFIG_DEFAULTS | dict(
        name='auction_custom',
        display_name="Auction Experiment",
    ),

    # Configs used to run academy sessions
    ACADEMY_CONFIG_DEFAULTS | dict(
        name='academy_one',
        display_name="Academy Day 1",
        app_sequence=[
            'academy_wallet',
            'academy_cournot',
            'academy_endcard',
        ],
        num_demo_participants=2,
        academy_wallet_open=False
    ),

    ACADEMY_CONFIG_DEFAULTS | dict(
        name='academy_two',
        display_name="Academy Day 2",
        app_sequence=[
            'academy_wallet',
            'academy_guess',
            'academy_prisoner',
            'academy_punishment',
            'academy_endcard',
        ],
        num_demo_participants=4,
    ),

    ACADEMY_CONFIG_DEFAULTS | dict(
        name='academy_final',
        display_name="Academy Auction Final",
        app_sequence=[
            'academy_wallet',
            'academy_auction',
        ],
        real_world_currency_per_point=0.01,
        num_demo_participants=4,
        academy_wallet_create=False
    ),

    # Demos of academy games
    dict(
        name='cournot_demo',
        app_sequence=['academy_cournot'],
        display_name="Demo - Cournot Game",
        num_demo_participants=2,
    ),
    dict(
        name='guess_demo',
        app_sequence=['academy_guess'],
        display_name="Demo - Guess 2/3 Average",
        num_demo_participants=4,
    ),
    dict(
        name='prisoner_demo',
        app_sequence=['academy_prisoner'],
        display_name="Demo - Prisoner's Dilemma",
        num_demo_participants=2,
    ),
    dict(
        name='punishment_demo',
        app_sequence=['academy_punishment'],
        display_name="Demo - Common Goods with Punishment",
        num_demo_participants=4,
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

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.00, participation_fee=0.00, num_demo_participants=0,
)

PARTICIPANT_FIELDS = ['role', 'treatment', 'finished']
SESSION_FIELDS = ['reward_round']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """<h4>Polkadot Experiments Platform</h4>"""

SECRET_KEY = '3685133242197'

ROOMS = [
    dict(
        name='testing',
        display_name='Testing & Development',
    ),
    dict(
        name='academy',
        display_name='Blockchain Academy 2022',
    ),
]
