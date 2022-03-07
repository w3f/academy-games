class Lexicon(dict):
    """Thin wrapper around a dict to easily create lexicons."""
    data = {
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
                'de': "In Summe ist die Bezahlung",
            },
        },
    }

    @classmethod
    def for_page(cls, page: str, lang: str):
        """Create lexicon for specified page and language."""
        return { k: v[lang] for k, v in cls.data.get('common').items() } \
             | { k: v[lang] for k, v in cls.data.get(page, {}).items() }
