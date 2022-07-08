"""Cross-session participant wallet to track and encourage progress."""

from otree.constants import BaseConstants
from otree.database import (
    BooleanField,
    StringField,
    MixinSessionFK,
)
from otree.models import BaseSubsession, BaseGroup
from otree.views import Page

from wallet import Wallet, WalletError, WalletPlayer

from typing import Optional


doc = __doc__


class C(BaseConstants):
    """Single player app, use config to control provided functionalities."""

    NAME_IN_URL = 'academy_wallet'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    @staticmethod
    def get_wallet_create(model: MixinSessionFK) -> bool:
        """Return if app should allow user to create new wallets."""
        return model.session.config.get('academy_wallet_create', True)

    @staticmethod
    def get_wallet_open(model: MixinSessionFK) -> bool:
        """Return if app should allow users to open existing wallets."""
        return model.session.config.get('academy_wallet_open', True)


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Default base group."""

    pass


class Player(WalletPlayer):
    """Authentication via form input, with optional phrase if not enrollment."""

    enroll = BooleanField()

    phrase = StringField(blank=True)


# PAGES
class Authenticate(Page):

    form_model = 'player'
    form_fields = ['enroll', 'phrase']

    @staticmethod
    def error_message(player, values) -> Optional[str]:
        """Enroll with priority, otherwise try to open wallet."""
        try:
            if values['enroll'] and C.get_wallet_create(player):
                Wallet.generate(player.participant)
            elif values['phrase'] and C.get_wallet_open(player):
                Wallet.open(player.participant, values['phrase'])
            else:
                return 'Please enter a valid phrase to open a wallet.'
        except WalletError as err:
            return str(err)

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        return {
            'wallet_create': C.get_wallet_create(player),
            'wallet_open': C.get_wallet_open(player),
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        """Make sure authentication was successful."""
        wallet = Wallet.current(player.participant)

        if not wallet:
            # TODO: Handle or fail!
            print("Failure: Player is not associated with wallet!")
        elif player.enroll:
            # Add phrase to database for new enrolled
            player.phrase = wallet.phrase


class Profile(Page):
    """Display content of current wallet."""

    pass


# App authenticates and displays result
page_sequence = [Authenticate, Profile]
