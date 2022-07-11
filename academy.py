"""otree session and room configs for blockchain academy."""

import importlib

# Default config for all games
ACADEMY_GAME_DEFAULTS = dict(
    academy_wallet_create=False,
    academy_wallet_phrase=False,
    academy_wallet_code=False,
    academy_wallet_endowment=0,
    academy_endcard_reward=0,
)

# Default config for all auctions
ACADEMY_AUCTION_DEFAULTS = dict(
    num_demo_participants=3,
    academy_game_name="NFT Auction",
    academy_wallet_phrase=True,
    academy_wallet_code=True,
    num_hard_participants=0,
    num_candle_participants=0,
    num_activity_participants=0,
)

# List of auction varients
ACADEMY_AUCTION_TREATMENTS = [ 'hard', 'candle', 'activity' ]

# List of all game identifiers
ACADEMY_GAME_CONFIGS = {
    'wallet': dict(
        num_demo_participants=1,
        academy_game_name="Wallet App",
        academy_wallet_create=True,
    ),
    'ultimatum': dict(
        num_demo_participants=2,
        academy_game_name="Ultimatum Game",
        academy_wallet_phrase=True,
        academy_wallet_code=True,
        academy_endcard_reward=400,
    ),
    'cournot': dict(
        num_demo_participants=2,
        academy_game_name="Cournot Game",
        academy_wallet_code=True,
        academy_wallet_phrase=True,
        academy_endcard_reward=400,
    ),
    'guess': dict(
        num_demo_participants=2,
        academy_game_name="Guessing Game",
        academy_wallet_phrase=True,
        academy_wallet_code=True,
        academy_endcard_reward=200,
    ),
    'prisoner': dict(
        num_demo_participants=2,
        academy_game_name="Prisoner's Dilemma",
        academy_wallet_phrase=True,
        academy_wallet_code=True,
        academy_endcard_reward=400,
    ),
    'publicgood': dict(
        num_demo_participants=4,
        academy_game_name="Public Good Game",
        academy_wallet_phrase=True,
        academy_wallet_code=True,
        academy_endcard_reward=400,
    ),
    'auction' : ACADEMY_AUCTION_DEFAULTS | dict(
        num_candle_participants=3,
    ),
}

# Helper class
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
    num_key = f"num_{treatment}_participants"
    num_value = ACADEMY_AUCTION_DEFAULTS['num_demo_participants']

    config = ACADEMY_AUCTION_DEFAULTS | { num_key: num_value }

    session = AcademyGame("auction", config).session()

    name = f"academy_auction_{treatment}"

    suffix = f" - {treatment.capitalize()} Ending"
    display_name = session['display_name'] + suffix

    return session | {
        "name": name,
        "display_name": display_name,
    }

# Cache modules for each game
ACADEMY_GAMES = [AcademyGame.make(*kv) for kv in ACADEMY_GAME_CONFIGS.items()]

# Configs for treatment specific auctions
ACADEMY_AUCTIONS = list(map(MAKE_AUCTION_SESSION, ACADEMY_AUCTION_TREATMENTS))

# Generate session config for each game
SESSION_CONFIGS = list(map(AcademyGame.session, ACADEMY_GAMES)) + ACADEMY_AUCTIONS

# Generate room config for each game
ROOMS = list(map(AcademyGame.room, ACADEMY_GAMES))
