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
            'seconds': {
                'en': "seconds",
                'de': "Sekunden",
            },
            'no_bids': {
                'en': "No bids were received...",
                'de': "Es wurden keine Gebote abgegeben...",
            },
            'player': {
                'en': "Bidder",
                'de': "Bieter",
            },
            'player_me': {
                'en': "Me",
                'de': "Ich",
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
        },
        'quiz': {
            'title': {
                'en': "Quiz",
                'de': "Quiz",
            },
            'text': {
                'en': "Please answer the following questions to make sure you understood the rules of the game correctly.",
                'de': "Bitte beantworten Sie die folgenden Fragen um sicherzustellen, dass Sie die Regel verstanden haben.",
            },
            'error_message': {
                'en': "Your answer is not correct.",
                'de': "Ihre Antwort ist falsch.",
            },
            'player_per_group': {
                'en': "How many bidders (incl. you) participate in the auction?",
                'de': "Wie viele Teilnehmer befinden sich (inkl. Ihnen) in einer Auktion?",
            },
            'num_global_local': {
                'en': "There are always one local and two global bidders in an auction.",
                'de': "Es gibt immer einen lokalen Bieter und zwei globale Bieter in einer Auktion.",
            },
            'role_shuffle': {
                'en': "The bidders role changes every round.",
                'de': "Die Rolle eines Spielers wechselt jede Runde.",
            },
        },
        'valuation': {
            'title': {
                'en': "Valuation for Round",
                'de': "Wertschätzung für Runde",
            },
            'timer': {
                'en': "Time left to prepare for round:",
                'de': "Verbleibende Zeit zum Vorbereiten:",
            },
            'role_global': {
                'en': "You are a <b>global</b> bidder.",
                'de': "Sie sind ein <b>globaler</b> Bieter.",
            },
            'role_local': {
                'en': "You are a <b>local</b> bidder.",
                'de': "Sie sind ein <b>lokaler</b> Bieter.",
            },
            'treatment_hard': {
                'en': "You are participating in an auction with a known ending time.",
                'de': "Sie nehmen an einer Auktion mit festem Ende teil.",
            },
            'treatment_candle': {
                'en': "You are participating in an auction with unkown ending time.",
                'de': "Sie nehmen an einer Auktion mit unbekanntem Ende teil.",
            },
            'treatment_activity': {
                'en': "You are participating in an auction with activity-rule.",
                'de': "Sie nehmen an einer Auktion mit Aktivitätsregel teil.",
            },
        },
        'chat': {
            'title': {
                'en': "Phase 1: Chat",
                'de': "Phase 1: Chat",
            },
            'timer': {
                'en': "Time left to chat with other players",
                'de': "Verbleibende Zeit zum Kommunizieren mit anderen Bietern",
            },
            'subtitle_global': {
                'en': "Chat with all players:",
                'de': "Alle Bieter:",
            },
            'subtitle_local': {
                'en': "Chat only with local players:",
                'de': "Nur lokale Bieter:",
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
                'en': "Phase 2: Auction",
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
            'total': {
                'en': "Total",
                'de': "Summe",
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
            'target_select': {
                'en': "Please select a period to begin bidding.",
                'de': "Bitte wählen Sie eine Periode um mit dem Bieten anzufangen.",
            },
            'target_some': {
                'en': "Minimum bid to win this period",
                'de': "Minimalgebot um diese Periode zu gewinnen",
            },
            'target_none': {
                'en': "You are currently winning this period.",
                'de': "Sie gewinnen momentan diese Periode.",
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
            'status_unknown': {
                'en': "Unknown status returned",
                'de': "Unbekannter Status empfangen",
            },
            'slots_zero': {
                'en': "No period on which to bid selected.",
                'de': "Keine Periode für ein Gebot ausgewählt.",
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
        'reward': {
            'title': {
                'en': "Final Result and Payout",
                'de': "Endergebnis und Bezahlung",
            },
            'thanks': {
                'en': "Thank you for your participation.",
                'de': "Vielen Dank für Ihre Teilnahme.",
            },
            'reward_round': {
                'en': "Your payout will be based on the outcome in round",
                'de': "Ihre Bezahlung basiert auf dem Ergebnis in Runde",
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
