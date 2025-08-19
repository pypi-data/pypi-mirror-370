import pystartgg.tournaments as tournaments
import pystartgg.players as players
import pystartgg.events as events


class StartGG(object):
    def __init__(self, key, auto_retry=5):
        self.key = key
        self.header = {"Authorization": "Bearer " + key}
        self.auto_retry = auto_retry
        
    def set_key_and_header(self, new_key):
        self.key = new_key
        self.header = {"Authorization": "Bearer " + new_key}

    # Sets automatic retry, a variable that says if run_query retries if too many requests
    def set_auto_retry(self, t):
        self.auto_retry = t

    def print_key(self):
        print(self.key)

    def print_header(self):
        print(self.header)

    def print_auto_retry(self):
        print(self.header)

    @property
    def tournament(self):
        return tournaments.Tournament(self.key, self.header, self.auto_retry)

    @property
    def player(self):
        return players.Player(self.key, self.header, self.auto_retry)

    @property
    def event(self):
        return events.Event(self.key, self.header, self.auto_retry)

    # TODO: implement bracket. Could be relevant for majors with multiple waves
    #  or with unique formats (think Socal Star League). However, all the
    #  available endpoints appear to be covered by event and tournament for
    #  the purposes of this app.
    # @property
    # def bracket(self):
    #     return brackets.Bracket(self.key, self.header, self.auto_retry)

    # TODO: implement league. Not a priority
    # @property
    # def league(self):
    #     return leagues.League(self.key, self.header, self.auto_retry)