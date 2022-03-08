"""
Provides localization support for custom text.

Return language is configure in otree, i.e. the LANGUAGE_CODE setting.
"""

from settings import LANGUAGE_CODE


class Lexicon:
    """Thin wrapper around a locals dict to easily create lexicons."""

    # Nested dict organized into pages, identifiers and languages
    _locals = {
        # Share dictionary used by most page templates and shared templates
        'common': {
            'rank': {
                'en': "Rank",
                'de': "Rang",
            },
            'slot': {
                'en': "Period",
                'de': "Periode",
            },
            'total': {
                'en': "Total",
                'de': "Summe",
            },
            'player': {
                'en': "Bidder",
                'de': "Bieter",
            },
            'seconds': {
                'en': "seconds",
                'de': "Sekunden",
            },
            'no_bids': {
                'en': "No bids were received...",
                'de': "Es wurden keine Gebote abgegeben...",
            },
            'player_is': {
                'en': "You are Bidder",
                'de': "Sie sind Bieter",
            },
            'player_earn': {
                'en': "You earned",
                'de': "Sie verdienen",
            },
            'alert_practice': {
                'en': "This is a practice round!",
                'de': "Sie befinden sich in einer Proberunde!"
            },
            'subtitle_result': {
                'en': "Result of Round",
                'de': "Ergebnis der Runde",
            },
            'subtitle_valuation': {
                'en': "Your Valuation",
                'de': "Ihre Wertschätzung",
            },
            'next_button': {
                'en': "Please press the button below once you are ready.",
                'de': "Bitte klicken Sie auf <i>Weiter</i> sobald Sie bereit sind.",
            },
        },
        'intro': {
            'title': {
                'en': "Start of Round",
                'de': "Beginn der Runde",
            },
            'timer': {
                'en': "Time left to prepare for round:",
                'de': "Verbleibende Zeit zum Vorbereiten:",
            },
            'timer': {
                'en': "Time left to prepare for round:",
                'de': "Verbleibende Zeit zum Vorbereiten:",
            },
            'subtitle': {
                'en': "Introduction",
                'de': "Einführung",
            },
            'role_global': {
                'en': "You are a <b>global</b> bidder.",
                'de': "Sie sind <b>Bieter B</b>.",
            },
            'role_local': {
                'en': "You are a <b>local</b> bidder.",
                'de': "Sie sind <b>Bieter A</b>.",
            },
            'treatment_hard': {
                'en': "You are participating in an auction with hard ending.",
                'de': "Sie nehmen an einer Auktion mit festem Ende teil.",
            },
            'treatment_candle': {
                'en': "You are participating in a candle auction.",
                'de': "Sie nehmen an einer Auktion mit unbekanntem Ende teil.",
            },
            'treatment_activity': {
                'en': "You are participating in an activity-rule auction.",
                'de': "Sie nehmen an einer Auktion mit Aktivitätsregel teil.",
            },
        },
        'chat': {
            'title': {
                'en': "Pre-Auction Chat",
                'de': "Phase 1: Kommunizieren",
            },
            'timer': {
                'en': "Time left to chat with other players",
                'de': "Verbleibende Zeit zum Kommunizieren mit anderen Bietern",
            },
            'subtitle_global': {
                'en': "Chat will all players:",
                'de': "Alle Bieter:",
            },
            'subtitle_local': {
                'en': "Chat only with local players:",
                'de': "Nur Bieter A:",
            },
            'button_off': {
                'en': "End communication",
                'de': "Kommunikation beenden",
            },
            'button_on': {
                'en': "Waiting for other players...",
                'de': "Warte auf andere Bieter...",
            },
        },
        'auction': {
            'title': {
                'en': "Auction",
                'de': "Phase 2: Auktion",
            },
            'timer': {
                'en': "Time left in auction",
                'de': "Verbleibende Zeit bis zum Ende der Auktion",
            },
            'subtitle_result': {
                'en': "Current result",
                'de': "Aktuelle Ergebnisse",
            },
            'distance': {
                'en': "Distance",
                'de': "Distanz",
            },
            'no_bidder': {
                'en': "No bidder",
                'de': "Kein Bieter",
            },
            'waiting': {
                'en': "Waiting for bids...",
                'de': "Warte auf Gebote...",
            },
            'subtitle_input': {
                'en': "Participate in Auction",
                'de': "Teilnehmen an der Auktion",
            },
            'all_slots': {
                'en': "All periods",
                'de': "Alle Perioden",
            },
            'label_price': {
                'en': "Amount",
                'de': "Anzahl",
            },
            'button_bid': {
                'en': "Send Bid",
                'de': "Bieten",
            },
            'result_success': {
                'en': "Bid was successfully submitted.",
                'de': "Gebot wurde angenommen.",
            },
            'result_malformed': {
                'en': "Received malformed bid",
                'de': "Unbekanntes Gebotsformat",
            },
            'player_me': {
                'en': "Me",
                'de': "Ich",
            },
            'status_unknown': {
                'en': "Unknown status returned",
                'de': "Unbekannter Status empfangen",
            },
        },
        'result': {
            'title': {
                'en': "End of Round",
                'de': "Ende der Runde",
            },
            'timer': {
                'en': "Time left to view result:",
                'de': "Verbleibende Zeit zum Betrachten des Ergebnisses:",
            },
            'duration_is': {
                'en': "The auction ended after",
                'de': "Die Auktion endete nach",
            },
        },
        'outro': {
            'title': {
                'en': "Final Result and Payout",
                'de': "Endergebnis und Bezahlung",
            },
            'thanks': {
                'en': "Thank you for your participation.",
                'de': "Vielen Dank für Ihre Teilnahme.",
            },
            'reward_round': {
                'en': "Your payout will be based on your perfomance in round",
                'de': "Ihre Bezahlung basiert auf Ihre Leistung in Runde",
            },
            'player_payout': {
                'en': "Your total payout will be",
                'de': "In Summe erhalten Sie als Bezahlung",
            },
        },
        'bid': {
            'slots_invalid': {
                'en': "No or invalid period selected.",
                'de': "Keine oder ungültige Periode ausgewählt.",
            },
            'price_negative': {
                'en': "Amount must be larger then zero.",
                'de': "Die gebotene Menge muss positive sein.",
            },
            'auction_timeout': {
                'en': "Auction time has run out.",
                'de': "Die Auktion wurde beendet.",
            },
            'slots_mismatch': {
                'en': "Invalid combination of periods selected.",
                'de': "Ungültige Kombination von Perioden.",
            },
            'price_too_high': {
                'en': "Amount must not exceed valuation of",
                'de': "Menge übersteigt die Wertschätzung von",
            },
            'price_too_low': {
                'en': "Amount must exceed current best bid at",
                'de': "Menge übersteigt nicht Höchstgebot von",
            },
        },
    }

    @classmethod
    def for_page_template(cls, page: str):
        """Create lexicon to be used in full page context (incl. common)."""
        return cls.page("common") | cls.page(page)

    @classmethod
    def page(cls, page: str):
        """Return lexicon for a single page."""
        return {
            k: v.get(LANGUAGE_CODE, "")
            for k, v in cls._locals.get(page, {}).items()
        }

    @classmethod
    def entry(cls, page: str, identity: str):
        """Return a specific lexicon entry."""
        return cls._locals.get(page, {}).get(identity, {}).get(LANGUAGE_CODE, "")
