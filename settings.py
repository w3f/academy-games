"""otree session and room configs for blockchain academy."""

from os import environ

# Determine and configure demo mode
IN_DEMO_MODE = (environ.get('OTREE_AUTH_LEVEL') == "DEMO")

# Default config for all games
ACADEMY_GAME_DEFAULTS = dict(
    academy_wallet_code=False,
    academy_endcard_reward=0,
)

# Default config for all auctions
ACADEMY_AUCTION_DEFAULTS = dict(
    num_demo_participants=3,
    academy_game_name="NFT Auction",
    academy_wallet_code=True,
    academy_wallet_pubkey=True,
    real_world_currency_per_point=0.01,
    num_groups_hard=0,
    num_groups_candle=0,
    num_groups_activity=0,
)

# List of auction varients
ACADEMY_AUCTION_TREATMENTS = [ 'hard', 'candle', 'activity' ]

# List of all game identifiers
ACADEMY_GAME_CONFIGS = {
    'wallet': dict(
        num_demo_participants=1,
        academy_game_name="Wallet App",
        academy_wallet_pubkey=True,
    ),
    'ultimatum': dict(
        num_demo_participants=2,
        academy_game_name="Ultimatum Game",
        academy_wallet_code=True,
        academy_wallet_pubkey=True,
        academy_endcard_reward=500,
    ),
    'cournot': dict(
        num_demo_participants=2,
        academy_game_name="Cournot Game",
        academy_wallet_code=True,
        academy_wallet_pubkey=True,
        academy_endcard_reward=500,
    ),
    'guess': dict(
        num_demo_participants=2,
        academy_game_name="Guessing Game",
        academy_wallet_code=True,
        academy_wallet_pubkey=True,
        academy_endcard_reward=250,
    ),
    'prisoner': dict(
        num_demo_participants=2,
        academy_game_name="Prisoner's Dilemma",
        academy_wallet_code=True,
        academy_wallet_pubkey=True,
        academy_endcard_reward=500,
    ),
    'publicgood': dict(
        num_demo_participants=4,
        academy_game_name="Public Good Game",
        academy_wallet_code=True,
        academy_wallet_pubkey=True,
        academy_endcard_reward=500,
    ),
    'dollar': dict(
        num_demo_participants=5,
        academy_game_name="Dollar Auction",
        academy_wallet_code=True,
        academy_wallet_pubkey=True,
        real_world_currency_per_point = 0.01,
    ),
    'auction' : ACADEMY_AUCTION_DEFAULTS | dict(
        num_groups_candle=1,
    ),
}


# Helper class to generate session from config
class AcademyGame:
    """Caches metadata to generate otree configs."""

    def __init__(self, identifier: str, config: dict):
        """Load and cache game app module by identifier."""
        self.id = identifier
        self.name = f"academy_{identifier}"
        self.config = config

    @staticmethod
    def make(identifier: str, config: dict) -> "AcademyGame":
        """Construct game via identifier."""
        return AcademyGame(identifier, config)

    @property
    def display_name(self) -> str:
        """Fetch display name from config."""
        return f"Academy Games - {self.game_name}"

    @property
    def game_name(self) -> str:
        """Fetch game name from config."""
        return self.config['academy_game_name']

    @property
    def app_sequence(self) -> list[str]:
        """Determine app sequence of game."""
        if self.id == "wallet":
            return [self.name, "academy_endcard"]
        elif self.id == "auction":
            return ['academy_wallet', self.name]
        else:
            return ['academy_wallet', self.name, 'academy_endcard']

    def session(self) -> dict:
        """Return game as otree session config."""
        return ACADEMY_GAME_DEFAULTS | dict(
            name=self.name,
            display_name=self.display_name,
            app_sequence=self.app_sequence,
            academy_game_id=self.id,
        ) | self.config

    def room(self) -> dict:
        """Return game specific otree room config."""
        return dict(
            name=self.name,
            display_name=self.display_name,
        )


def MAKE_AUCTION_SESSION(treatment: str) -> dict:
    """Alter default config for specific treatment."""
    # Generate session for treatment
    config = ACADEMY_AUCTION_DEFAULTS | { f"num_groups_{treatment}": 1 }
    session = AcademyGame("auction", config).session()

    # Extend default names of session
    name = f"{session['name']}_{treatment}"
    display_name = f"{session['display_name']} - {treatment.capitalize()} Ending"

    return session | dict(name=name, display_name=display_name)


# Cache modules for each game
ACADEMY_GAMES = [AcademyGame.make(*kv) for kv in ACADEMY_GAME_CONFIGS.items()]

# Configs for treatment specific auctions
ACADEMY_AUCTIONS = list(map(MAKE_AUCTION_SESSION, ACADEMY_AUCTION_TREATMENTS))

# Default session config
SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.00, participation_fee=0.00,
    num_demo_participants=0,
)

# Generate session config for each game
SESSION_CONFIGS = list(map(AcademyGame.session, ACADEMY_GAMES)) + ACADEMY_AUCTIONS

# Fields used across apps
PARTICIPANT_FIELDS = ['role', 'treatment', 'finished']
SESSION_FIELDS = ['reward_round']

# ISO-639 code
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """<h4>Polkadot Academy Games</h4>"""

SECRET_KEY = '5192012476463'

# Generate room config for each game
ROOMS = list(map(AcademyGame.room, ACADEMY_GAMES))
