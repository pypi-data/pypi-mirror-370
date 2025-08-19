# TODO: implement bracket. Could be relevant for majors with multiple waves
#  or with unique formats (think Socal Star League). However, all the
#  available endpoints appear to be covered by event and tournament for
#  the purposes of this app.

import pystartgg.b_queries as b_queries
from pystartgg.api import run_query

class Bracket:
    def __init__(self, key, header, auto_retry):
        self.key = key
        self.header = header
        self.auto_retry = auto_retry

    # Shows all the players in a bracket (aka phaseGroup)
    def show_entrants(self, bracket_id, page_num):
        variables = {"phaseGroupId": bracket_id, "page": page_num}
        response = run_query(b_queries.BRACKET_SHOW_ENTRANTS_QUERY, variables, self.header, self.auto_retry)
        data = b_queries.bracket_show_entrants_filter(response)
        return data

    # Shows all the players in a bracket
    def show_sets(self, bracket_id, page_num):
        variables = {"phaseGroupId": bracket_id, "page": page_num}
        response = run_query(b_queries.BRACKET_SHOW_SETS_QUERY, variables, self.header, self.auto_retry)
        data = b_queries.bracket_show_sets_filter(response)
        return data