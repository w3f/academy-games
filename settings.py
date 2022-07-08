"""otree main config."""

# Project-specific subconfigs
import academy
import auction

from os import environ


# Combine all session configs
SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.00, participation_fee=0.00,
    num_demo_participants=0,
)

SESSION_CONFIGS = academy.SESSION_CONFIGS + auction.SESSION_CONFIGS

# Fields used across apps
PARTICIPANT_FIELDS = ['role', 'treatment', 'finished']
SESSION_FIELDS = ['reward_round']

# ISO-639 code
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """<h4>Polkadot Experiments Platform</h4>"""

SECRET_KEY = '3685133242197'

# Combine all room configs
ROOMS = [
    # Default room for testing
    dict(
        name='testing',
        display_name='Testing & Development',
    ),
] + academy.ROOMS + auction.ROOMS
