"""Minimal otree cross-session wallet implementation."""

from otree.currency import RealWorldCurrency
from otree.database import (
    ExtraModel,
    OTreeColumn,
    IntegerField,
    st,
    ForeignKey
)
from otree.models import BasePlayer, Participant

import secrets
from hashlib import sha256
from typing import List, Optional, Tuple

from bip39 import INDEX_TO_WORD_TABLE, WORD_TO_INDEX_TABLE


class WalletError(Exception):
    """Default exception type for wallet runtime errors."""

    pass


# Quick and dirty 32-bit seed <->three word mnemonic phrase (32bit + 1bit CS)
def seed_to_checksum32(seed: int):
    """Compute 1-bit checksum of 32-bit seed."""
    bytes = seed.to_bytes(4, byteorder='big')
    return sha256(bytes).digest()[0] >> 7


def seed_to_phrase32(seed: int) -> str:
    """Turn a 32-bit seed into a three word mnemonic phrase."""
    # Checksum is first bit of sha256
    checksum = seed_to_checksum32(seed)

    # Append checksum to seed
    raw = (seed << 1) | checksum

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
    seed = raw >> 1
    checksum = raw & 0x1

    if checksum != seed_to_checksum32(seed):
        raise WalletError("Phrase has invalid checksum.")

    return seed


def to_unsigned32(value: int) -> int:
    """Convert signed to unsigned int."""
    return int.from_bytes(value.to_bytes(4, 'big', signed=True), 'big')


def to_signed32(value: int) -> int:
    """Convert unsigned to signed int."""
    return int.from_bytes(value.to_bytes(4, 'big'), 'big', signed=True)


# Quick lookup index for wallet associations
class Wallet(ExtraModel):
    """Cross-session tracker of participant progress."""

    id = OTreeColumn(st.Integer, ForeignKey('otree_participant.id'), primary_key=True)

    _seed = IntegerField()

    @property
    def seed(self) -> int:
        """Return seed by converting it back to unsigned."""
        return to_unsigned32(self._seed)

    @seed.setter
    def seed(self, value) -> None:
        """Encode seed as signed integer, for improved SQL compliance."""
        self._seed = to_signed32(value)

    # Static user-facing API to control wallet associations

    @staticmethod
    def generate(owner: Participant) -> str:
        """Generate a new wallet associate with participant."""
        if Wallet.objects_exists(id=owner.id):
            raise WalletError("Participant is already associated with wallet.")

        seed = secrets.randbits(32)

        return Wallet.create(
            id=owner.id,
            _seed=to_signed32(seed),
        )

    @staticmethod
    def open(owner: Participant, phrase: str) -> "Wallet":
        """Associate a participant with a certain wallet."""
        seed = phrase_to_seed32(phrase)

        wallet = Wallet.current(owner)
        if wallet:
            if wallet.seed == seed:
                # Reopen existing association
                raise WalletError("Participant has opened wallet already.")
            else:
                # Different/Incorrect phrase
                raise WalletError("Participant can only have one wallet.")

        seed_sql = to_signed32(seed)

        # Check that wallet exists at all
        if not Wallet.objects_filter(_seed=seed_sql).count():
            raise WalletError("No wallet associated with phrase.")

        # Check that wallet has not been claimed for this session
        for other in owner.session.pp_set:
            if Wallet.objects_exists(id=other.id, _seed=seed_sql):
                raise WalletError("Wallet already associated with other session participant.")

        # Register the existing wallet with the current participant
        return Wallet.create(id=owner.id, _seed=seed_sql)

    @staticmethod
    def current(owner: Participant) -> Optional["Wallet"]:
        """Get wallet associated with certain participant."""
        return Wallet.objects_first(id=owner.id)

    # Shorthand properties mostly for readable logic and templates

    @property
    def phrase(self) -> str:
        """Generate mnemonic phrase from wallet seed."""
        return seed_to_phrase32(self.seed)

    @property
    def is_game(self) -> bool:
        """Return true if association is a game, i.e. not a wallet."""
        return self.owner.session.config['academy_game_id'] != "wallet"

    @property
    def owner(self) -> Participant:
        """Return associated participant."""
        return Participant.objects_get(id=self.id)

    @property
    def code(self) -> str:
        """Return participant code of current association."""
        return self.owner.code

    @property
    def game_name(self):
        """Return session display name of current association."""
        return self.owner.session.config['academy_game_name']

    @property
    def participants(self) -> List[Participant]:
        """Return all participants associated with wallet."""
        return [w.owner for w in Wallet.objects_filter(_seed=self._seed) if w.is_game]

    @property
    def balance(self) -> RealWorldCurrency:
        """Sum of all payoffs associated with wallet."""
        return sum([
            p.payoff_plus_participation_fee() for p in self.participants
        ], start=RealWorldCurrency(0))

    @property
    def transactions(self) -> List[Tuple[str, RealWorldCurrency, bool]]:
        """List of all sessions and payouts associated with wallet."""
        return [(p.session.config['academy_game_name'] + (" (current)" if p.id == self.id else ""),
                 p.payoff_plus_participation_fee(),
                 p._get_finished()
                 ) for p in self.participants]


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
