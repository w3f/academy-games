"""Cross-session participant wallet to track and encourage progress."""

from otree.constants import BaseConstants
from otree.currency import Currency
from otree.database import (
    IntegerField,
    StringField,
    MixinSessionFK,
)
from otree.models import BaseSubsession, BaseGroup
from otree.room import ROOM_DICT
from otree.views import Page

from wallet import Wallet, WalletError, WalletPlayer

from typing import List, Optional

import logging


logger = logging.getLogger('wallet')

doc = __doc__


class C(BaseConstants):
    """Single player app, use config to control provided functionalities."""

    NAME_IN_URL = 'academy_wallet'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    TITLE_PREFIX = "Lesson 2: "

    WALLET_CREATE = 0

    @staticmethod
    def get_wallet_create(model: MixinSessionFK) -> bool:
        """Return if app should allow user to create new wallets."""
        return model.session.config.get('academy_wallet_create', False)

    WALLET_PHRASE = 1

    @staticmethod
    def get_wallet_phrase(model: MixinSessionFK) -> bool:
        """Return if app should allow users to open existing wallets."""
        return model.session.config.get('academy_wallet_phrase', False)

    WALLET_CODE = 2

    @staticmethod
    def get_wallet_code(model: MixinSessionFK) -> bool:
        """Return if app should determine wallet based on room membership."""
        return model.session.config.get('academy_wallet_code', False)

    WALLET_PUBKEY = 3

    @staticmethod
    def get_wallet_signin(model: MixinSessionFK) -> bool:
        """Return if app is able to get a valid signature from the user authenticating them"""
        return model.session.config.get('academy_wallet_pubkey', False)


class Subsession(BaseSubsession):
    """Default base subsession."""

    pass


class Group(BaseGroup):
    """Default base group."""

    pass


# Constants to improve readability

class Player(WalletPlayer):
    """Authentication via form input, with optional phrase if not enrollment."""

    source = IntegerField(
        choices=[
            [C.WALLET_CREATE, 'create'],
            [C.WALLET_PHRASE, 'phrase'],
            [C.WALLET_CODE, 'code'],
            [C.WALLET_PUBKEY, 'pubkey'],
        ]
    )

    phrase = StringField(blank=True)

    code = StringField(blank=True)

    pubkey = StringField(blank=True)

# PAGES
class Authenticate(Page):

    form_model = 'player'
    form_fields = ['source', 'phrase', 'code', 'pubkey'] # TODO: How to add another field here?

    def inner_dispatch(self, request):
        """Intercept request data to access cookies for wallet."""
        if C.get_wallet_code(self.participant):
            # Default value if wallet missing
            self.wallet_template_vars = dict(wallet=None)

            # Check academy wallet room cookie
            room = ROOM_DICT.get("academy_wallet")
            if room and room.has_session():
                cookie = f"session_{room.get_session().code}_participant"
                code = request.session.get(cookie)
                if code:
                    wallet = Wallet.current_by_code(code)
                    if wallet:
                        # Provide details to templates
                        self.wallet_template_vars['wallet'] = dict(
                            public=wallet.public,
                            code=code,
                        )
                        logger.info(f"Room-based association succeeded: '{wallet.public}'")

        return super().inner_dispatch(request)

    def get_context_data(self, **context):
        """Intercept context data to add wallet details to template."""
        if C.get_wallet_code(self.participant):
            context.update(self.wallet_template_vars)

        return super().get_context_data(**context)

    @staticmethod
    def error_message(player, values) -> Optional[str]:
        """Enroll with priority, otherwise try to open wallet."""
        try:
            print("Got to this try block")
            print(f"values['source']: {values['source']} values['pubkey']: {values['pubkey']} ")
            if values['source'] == C.WALLET_CREATE and C.get_wallet_create(player):
                Wallet.generate(player.participant)
            elif values['source'] == C.WALLET_PHRASE and C.get_wallet_phrase(player) and values['phrase']:
                Wallet.open(player.participant, values['phrase'])
            elif values['source'] == C.WALLET_PUBKEY and C.get_wallet_signin(player) and values['pubkey']:
                print("Hey I got the Hashed Pubkey")
                Wallet.test_open(player.participant, values['pubkey'])
            elif values['source'] == C.WALLET_CODE and C.get_wallet_code(player) and values['code']:
                Wallet.open_with_code(player.participant, values['code'])
            elif values['source'] == C.WALLET_CODE and C.get_wallet_signin(player) and values['code']:
                Wallet.test_open_with_code(player.participant, values['code'])
            else:
                # print(f"values source == {values['source']} values pubkey == {values['pubkey']}")
                return 'Please enter a valid phrase to open a wallet.'
        except WalletError as err:
            return str(err)

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        return {
            'wallet_code': C.get_wallet_code(player),
            'wallet_create': C.get_wallet_create(player),
            'wallet_phrase': C.get_wallet_phrase(player),
            'wallet_pubkey': C.get_wallet_signin(player),
        }

    @staticmethod
    def before_next_page(player: Player, timeout_happened: bool):
        """Make sure authentication was successful."""
        wallet = player.wallet

        if not wallet:
            logger.error("Failed to associate participant '{{player.participant}}' with wallet.")
        elif player.source == C.WALLET_CREATE:
            # Add phrase to database for new wallets
            player.phrase = wallet.private
        elif player.source == C.WALLET_CODE:
            # Add phrase to database for code-based wallets
            player.phrase = wallet.private


class Profile(Page):
    """Display content of current wallet."""

    @staticmethod
    def vars_for_template(player: Player) -> dict:
        """Return additional data to pass to page template."""
        return dict(
            wallet_private=player.source != C.WALLET_CODE,
        )


# App authenticates and displays result
page_sequence = [Authenticate, Profile]


# CUSTOM EXPORTER
def custom_export(all_players: List[Player]):
    """Export all wallet transactions and their details."""
    # Export header row
    yield [
        'wallet_session',
        'wallet_name',
        'wallet_participant',
        'wallet_public',
        'wallet_private',
        'wallet_payoff'
    ]
    for player in all_players:
        session = player.session
        participant = player.participant
        wallet = Wallet.current(participant)

        yield [
            session.code,
            session.config.get('academy_game_name'),
            participant.code,
            wallet.public if wallet else None,
            wallet.private if wallet else None,
            participant.payoff_plus_participation_fee(),
        ]
