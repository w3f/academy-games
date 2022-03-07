

class Lexicon(dict):
    data = {
        'common': {
            'player_id': {
                'en': "You are Player",
                'de': "Sie sind Bieter",
            },
            'alert_practice': {
                'en': "This is a practice round!",
                'de': "Sie befinden sich in einer Proberunde!"
            },
            'title_valuation': {
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
    }

    @classmethod
    def for_page(cls, page: str, lang: str):
        """Create lexicon for specified page and language."""
        return { k: v[lang] for k, v in cls.data.get('common').items() } \
             | { k: v[lang] for k, v in cls.data.get(page, {}).items() }
