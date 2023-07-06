"""Minimal otree cross-session wallet implementation."""

from otree.currency import RealWorldCurrency
from otree.database import (
    ExtraModel,
    OTreeColumn,
    IntegerField,
    StringField,
    st,
    ForeignKey
)
from otree.models import BasePlayer, Participant, Session

from hashlib import sha256
from typing import List, Optional, Tuple

import sr25519
import binascii
from substrateinterface.base import ss58_decode, is_valid_ss58_address
from hashlib import blake2b

HASH_PASS = "Chalet-In-Valais"

class WalletError(Exception):
    """Default exception type for wallet runtime errors."""

    pass

# Quick lookup index for wallet associations
class Wallet(ExtraModel):
    """Cross-session tracker of participant progress."""

    id = OTreeColumn(st.Integer, ForeignKey('otree_participant.id'), primary_key=True)

    # TODO: Add owner link to participant

    _public = StringField()
    _private = IntegerField()

    @classmethod
    def create(cls, owner: Participant, public: str) -> "Wallet":

        wallet = cls.current(owner)
        if wallet:
            # Participant should not exist no duplicates
            raise WalletError("Participant can only have one wallet.")

        # Check that wallet has not be claimed for this session
        for other in owner.session.pp_set:
            if cls.objects_exists(id=other.id, _public=public):
                # This should never happen do we need?
                raise WalletError("Wallet already assosciated with other session participant")

        super().create(id=owner.id, _public=public, _private=0)

    @staticmethod
    def open(owner: Participant, payload: str) -> "Wallet":
        ## The payload coming from client has a specific format which is:
        ## payload = "address{}signature"
        if payload.count("{}") != 1:
                raise WalletError("Incorrect format of sign-in message")

        pieces = payload.split("{}")
        address = pieces[0]
        signature = pieces[1]
        signature_encoded = binascii.unhexlify(signature[2:])

        if not is_valid_ss58_address(address):
            raise WalletError("Not a valid ss58 address")

        address_decoded = ss58_decode(address)
        address_bytes = binascii.unhexlify(address_decoded)

        message = "<Bytes>participantId is {}".format(owner.id) + "</Bytes>"

        if not sr25519.verify(signature_encoded, message.encode('utf-8'), address_bytes):
            raise WalletError(
                f"Couldn't verify signature with sig: {signature}, "
                f"message: {message}, "
                f"address: {address}"
                f"participant.id: {owner.id}",
            )

        ## We want to hash the ss58 encoded address in order to preserve the persons annonymity in the database
        hashed_address = blake2b(address.encode('utf-8') + HASH_PASS.encode('utf-8')).digest()
        hashed_address_hex = binascii.hexlify(hashed_address).decode('utf-8')

        return Wallet.create(owner, hashed_address_hex)

    @staticmethod
    def open_with_code(owner: Participant, code: str) -> "Wallet":
        """Associate a participant with the wallet of a certain participant."""
        other = Participant.objects_first(code=code)
        if not other:
            raise WalletError("No participant associated with code.")

        wallet = Wallet.current(other)
        if not wallet:
            raise WalletError("No wallet associated with code.")

        return Wallet.create(owner, wallet._public)

    @staticmethod
    def current(owner: Participant) -> Optional["Wallet"]:
        """Get wallet associated with certain participant."""
        return Wallet.objects_first(id=owner.id)

    @staticmethod
    def current_by_code(code: str) -> Optional["Wallet"]:
        """Get wallet associated with certain code."""
        owner = Participant.objects_first(code=code)
        return Wallet.current(owner) if owner else None

    # Shorthand properties mostly for readable logic and templates
    @property
    def public(self) -> str:
        """Generate mnemonic phrase from wallet seed."""
        return self._public

    @property
    def owner(self) -> Participant:
        """Return associated participant."""
        return Participant.objects_get(id=self.id)

    @property
    def game_id(self):
        """Return session display name of current association."""
        return self.owner.session.config['academy_game_id']

    @property
    def game_name(self):
        """Return session display name of current association."""
        return self.owner.session.config['academy_game_name']

    @property
    def is_game(self) -> bool:
        """Return true if association is a game, i.e. not a wallet."""
        return self.game_id != "wallet"

    @property
    def value(self) -> RealWorldCurrency:
        """Return the value of an association."""
        self.owner.payoff_plus_participation_fee()

    @property
    def code(self) -> str:
        """Return participant code of current association."""
        return self.owner.code

    @property
    def wallet_set(self):
        """Return set of all wallet associated with seed."""
        return Wallet.objects_filter(_public=self._public)

    @property
    def participants(self) -> List[Participant]:
        """Return all participants associated with wallet."""
        return [w.owner for w in self.wallet_set]

    @property
    def games(self) -> List[Participant]:
        """List all endowments on account."""
        return [w.owner for w in self.wallet_set if w.is_game]

    @property
    def endowments(self) -> List[Participant]:
        """List all endowments on account."""
        return [w.owner for w in self.wallet_set if not w.is_game]

    @property
    def sessions(self) -> List[Session]:
        """Return all game session in which the wallet participated."""
        return [p.session for p in self.games]

    @property
    def balance(self) -> RealWorldCurrency:
        """Sum of all payoffs associated with wallet."""
        return sum([
            p.payoff_plus_participation_fee() for p in self.participants
        ], start=RealWorldCurrency(0))

    Transaction = Tuple[str, RealWorldCurrency, bool]

    @property
    def transactions(self) -> List[Transaction]:
        """List of all sessions and payouts associated with wallet."""
        values = [(p, p.payoff_plus_participation_fee()) for p in self.endowments]
        endowments = [(("Endowment" if v > 0 else "Debt"), v, p._get_finished()) for p, v in values if v != 0]

        games = [(p.session.config['academy_game_name'] + (" (current)" if p.id == self.id else ""),
                  p.payoff_plus_participation_fee(),
                  p._get_finished()
                  ) for p in self.games]

        return endowments + games

class WalletPlayer(BasePlayer):
    """BasePlayer but with direct access to wallet via property."""

    __abstract__ = True

    @property
    def wallet(self) -> Optional[Wallet]:
        """Retrieve wallet associated with participant."""
        return Wallet.current(self.participant)

    @property
    def balance(self) -> RealWorldCurrency:
        """Return current balance in wallet."""
        return self.wallet.balance if self.wallet else RealWorldCurrency(0)
