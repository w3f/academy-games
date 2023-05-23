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

import secrets
from hashlib import sha256
from typing import List, Optional, Tuple

from bip39 import INDEX_TO_WORD_TABLE, WORD_TO_INDEX_TABLE

class WalletError(Exception):
    """Default exception type for wallet runtime errors."""

    pass


# Quick and dirty 32-bit signed seed to/from three word mnemonic phrase (32bit + 1bit CS)
# Uses signed ints to work with otree IntegerColumn on PostgesSQL
def random_seed32() -> int:
    """Generate a random 32-bit signed seed."""
    unsigned = secrets.randbits(32)
    return int.from_bytes(unsigned.to_bytes(4, 'big'), 'big', signed=True)


def seed_to_checksum32(seed: int):
    """Compute 1-bit checksum of 32-bit signed seed."""
    bytes = seed.to_bytes(4, byteorder='big', signed=True)
    return sha256(bytes).digest()[0] >> 7


def seed_to_phrase32(seed: int) -> str:
    """Turn a 32-bit signed seed into a three word mnemonic phrase."""
    # Checksum is first bit of sha256
    checksum = seed_to_checksum32(seed)

    # TODO: Check if this is necessary or make it work on signed ints
    unsigned = int.from_bytes(seed.to_bytes(4, 'big', signed=True), 'big')

    # Append checksum to seed
    raw = (unsigned << 1) | checksum

    # Convert each 11 bit chunk into a word.
    words: List[str] = []
    for _ in range(3):
        words.append(INDEX_TO_WORD_TABLE[raw & 0b111_1111_1111])
        raw >>= 11

    words.reverse()
    return " ".join(words)


def phrase_to_seed32(phrase: str) -> int:
    """Parse a mnemonic three-words phrase to retrieve its 32-bit seed."""
    # Avoid dealing with weird characters
    if not all(c in " abcdefghijklmnopqrstuvwxyz" for c in phrase):
        raise WalletError("Phrase contains an invalid character.")

    # Split phrase and check length
    words = phrase.split()
    if len(words) != 3:
        raise WalletError("Phrase should be three words.")

    # Convert words into bytes
    raw = 0
    for word in words:
        raw <<= 11
        try:
            raw |= WORD_TO_INDEX_TABLE[word]
        except KeyError:
            raise WalletError("Phrase contains unknown word '{}'.".format(word))

    # Retrieve and check checksum
    seed = int.from_bytes((raw >> 1).to_bytes(4, 'big'), 'big', signed=True)
    checksum = raw & 0x1

    if checksum != seed_to_checksum32(seed):
        raise WalletError("Phrase has invalid checksum.")

    return seed


# Quick lookup index for wallet associations
class Wallet(ExtraModel):
    """Cross-session tracker of participant progress."""

    id = OTreeColumn(st.Integer, ForeignKey('otree_participant.id'), primary_key=True)

    # TODO: Add owner link to participant

    _public = IntegerField()
    _private = IntegerField()

    _test_public = StringField()

    @classmethod
    def test_create(cls, owner: Participant, public: str) -> "Wallet":

        wallet = cls.current(owner)
        if wallet:
            # Participant should not exist no duplicates
            raise WalletError("Participant can only have one wallet.")

        # Check that wallet has not be claimed for this session
        for other in owner.session.pp_set:
            if cls.objects_exists(id=other.id, _test_public=public):
                # This should never happen do we need?
                raise WalletError("Wallet already assosciated with other session participant")

        super().create(id=owner.id, _test_public=public, _public=0, _private=0)

    # Static user-facing API to control wallet associations
    @classmethod
    def create(cls, owner: Participant, public: int, private: int) -> "Wallet":

        wallet = cls.current(owner)
        if wallet:
                # Different/Incorrect phrase
                raise WalletError("Participant can only have one wallet.")

        # Check that wallet has not been claimed for this session
        for other in owner.session.pp_set:
            if cls.objects_exists(id=other.id, _private=private):
                raise WalletError("Wallet already associated with other session participant.")

        super().create(id=owner.id, _public=public, _private=private)

    @staticmethod
    def generate(owner: Participant) -> str:
        """Generate a new wallet associate with participant."""

        # Collision avoidacance ;-)
        while True:
            public = random_seed32()

            if Wallet.objects_exists(_public=public):
                continue
            if Wallet.objects_exists(_private=public):
                continue
            break

        while True:
            private = random_seed32()

            if Wallet.objects_exists(_public=private):
                continue
            if Wallet.objects_exists(_private=private):
                continue
            break

        return Wallet.create(owner, public, private)

    @staticmethod
    def test_open(owner: Participant, public: str) -> "Wallet":

        # Check that wallet exists at all
        # wallet = Wallet.objects_first(_test_public=public)
        # if not wallet:
        #     raise WalletError("No wallet associated with phrase.")

        return Wallet.test_create(owner, public)

    @staticmethod
    def open(owner: Participant, phrase: str) -> "Wallet":
        """Associate a participant with a certain wallet."""
        private = phrase_to_seed32(phrase)

        # Check that wallet exists at all
        wallet = Wallet.objects_first(_private=private)
        if not wallet:
            raise WalletError("No wallet associated with phrase.")

        # Register the existing wallet with the current participant
        return Wallet.create(owner, wallet._public, private)

    @staticmethod
    def open_with_code(owner: Participant, code: str) -> "Wallet":
        """Associate a participant with the wallet of a certain participant."""
        other = Participant.objects_first(code=code)
        if not other:
            raise WalletError("No participant associated with code.")

        wallet = Wallet.current(other)
        if not wallet:
            raise WalletError("No wallet associated with code.")

        return Wallet.create(owner, wallet._public, wallet._private)

    @staticmethod
    def test_open_with_code(owner: Participant, code: str) -> "Wallet":
        """Associate a participant with the wallet of a certain participant."""
        other = Participant.objects_first(code=code)
        if not other:
            raise WalletError("No participant associated with code.")

        wallet = Wallet.current(other)
        if not wallet:
            raise WalletError("No wallet associated with code.")

        return Wallet.test_create(owner, wallet._test_public)

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
        return "0x{:04x}".format(int.from_bytes(self._public.to_bytes(4, 'big', signed=True), 'big'))

    @property
    def test_public(self) -> str:
        return self._test_public

    @property
    def private(self) -> str:
        """Generate mnemonic phrase from wallet seed."""
        return seed_to_phrase32(self._private)

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
        return Wallet.objects_filter(_private=self._private)

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
