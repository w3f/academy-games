from os import environ

SESSION_CONFIGS = [
    dict(
        name='hard_auction',
        display_name="Hard Ending Auction",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_hard_participants=3,
    ),
    dict(
        name='candle_auction',
        display_name="Candle Auction",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_candle_participants=3,
    ),
    dict(
        name='activity_auction',
        display_name="Activity Rule Auction",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_activity_participants=3,
    ),

    dict(
        name='hard_auction_4',
        display_name="Hard Ending Auction (4 Slots)",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_hard_participants=3,
        num_global_slots=4,
        num_local_slots=2
    ),
    dict(
        name='candle_auction_4',
        display_name="Candle Auction (4 Slots)",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_candle_participants=3,
        num_global_slots=4,
        num_local_slots=2
    ),
    dict(
        name='activity_auction_4',
        display_name="Activity Rule Auction (4 Slots)",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_activity_participants=3,
        num_global_slots=4,
        num_local_slots=2
    ),

    dict(
        name='hard_auction_6',
        display_name="Hard Ending Auction (6 Slots)",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_hard_participants=3,
        num_global_slots=6,
        num_local_slots=1
    ),
    dict(
        name='hard_auction_9',
        display_name="Hard Ending Auction (9 Slots)",
        app_sequence=['slot_auction'],
        num_demo_participants=3,
        num_hard_participants=3,
        num_global_slots=9,
        num_local_slots=3
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00,
    doc="Please ensure adjustment of participants per treatment in 'Configure session' section.",
    num_global_slots=2, num_local_slots=1,
    num_hard_participants=0, num_candle_participants=0, num_activity_participants=0
)

PARTICIPANT_FIELDS = ['role', 'treatment']
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """<h4>Polkadot Experiments Platform</h4>"""

SECRET_KEY = '3685133242197'
