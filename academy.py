"""otree session and room configs for blockchain academy."""

import importlib


# List of all game identifiers
ACADEMY_GAME_CONFIGS = {
    'wallet': dict(
        num_demo_participants=1,
        academy_game_name="Wallet App",
        academy_wallet_create=True,
        academy_endcard_reward=None,
    ),
    'ultimatum': dict(
        num_demo_participants=2,
        academy_game_name="Ultimatum Game",
    ),
    'cournot': dict(
        num_demo_participants=2,
        academy_game_name="Cournot Game",
    ),
    'guess': dict(
        num_demo_participants=2,
        academy_game_name="Guessing Game",
        academy_endcard_reward=200,
    ),
    'prisoner': dict(
        num_demo_participants=2,
        academy_game_name="Prisoner's Dilemma",
    ),
    'publicgood': dict(
        num_demo_participants=4,
        academy_game_name="Public Good Game",
    ),
    'auction': dict(
        num_demo_participants=4,
        academy_game_name="NFT Auction",
        academy_endcard_reward=None,
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
        else:
            return ['academy_wallet', self.name, 'academy_endcard']

    def session(self) -> dict:
        """Return game as otree session config."""
        return dict(
            name=self.name,
            display_name=self.display_name,
            app_sequence=self.app_sequence,
            academy_game_id=self.id,
            academy_wallet_open=True,
            academy_wallet_create=False,
            academy_endcard_reward=400,
        ) | self.config

    def room(self) -> dict:
        """Return game specific otree room config."""
        return dict(
            name=self.name,
            display_name=self.display_name,
        )


# Cache modules for each game
ACADEMY_GAMES = [AcademyGame.make(*kv) for kv in ACADEMY_GAME_CONFIGS.items()]

# Generate session config for each game
SESSION_CONFIGS = list(map(AcademyGame.session, ACADEMY_GAMES))

# Generate room config for each game
ROOMS = list(map(AcademyGame.room, ACADEMY_GAMES))
