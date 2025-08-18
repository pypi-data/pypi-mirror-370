# TODO: implement league. Not a priority

import pystartgg.l_queries as l_queries
from pystartgg.api import run_query

class League:
    def __init__(self, key, header, auto_retry):
        self.key = key
        self.header = header
        self.auto_retry = auto_retry

    # Shows metadata for a league
    def show(self, league_name):
        variables = {"slug": league_name}
        response = run_query(l_queries.SHOW_QUERY, variables, self.header, self.auto_retry)
        data = l_queries.league_show_filter(response)
        return data

    # Shows schedule for a league
    def show_schedule(self, league_name, page_num):
        variables = {"slug": league_name, "page": page_num}
        response = run_query(l_queries.SHOW_SCHEDULE_QUERY, variables, self.header, self.auto_retry)
        data = l_queries.league_show_schedule_filter(response)
        return data

    # Shows standings for a league
    def show_standings(self, league_name, page_num):
        variables = {"slug": league_name, "page": page_num}
        response = run_query(l_queries.SHOW_STANDINGS_QUERY, variables, self.header, self.auto_retry)
        data = l_queries.league_show_standings_filter(response)
        return data