from . import pages
from . import Constants

class PlayerBot(Bot):

    def play_round(self):
        yield (pages.Introduction)
        if self.player.id_in_group == 1:
            yield (pages.Offer, {'amount_offered': int(10)})
        else:
            yield (pages.Respond, {'offer_accepted': True})
        yield (pages.Results)



