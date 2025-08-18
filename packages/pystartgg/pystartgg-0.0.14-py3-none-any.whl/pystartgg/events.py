import pystartgg.e_queries as e_queries
from pystartgg.api import run_query, paginated

class Event:
    def __init__(self, key, header, auto_retry):
        self.key = key
        self.header = header
        self.auto_retry = auto_retry

    # Shows all the sets from an event
    def get_sets(self, event_id, page_num, per_page=32):
        variables = {"eventId": event_id, "page": page_num, "perPage": per_page}
        response = run_query(e_queries.GET_SETS_QUERY, variables, self.header, self.auto_retry)
        # print(response)
        data, data2 = e_queries.get_sets_filter(response)
        return data, data2

    def get_sets_all(self, event_id):
        func = paginated(self.get_sets, multi_return=True)
        return func(event_id)

    def get_placements(self, event_id, page_num, per_page=50):
        variables = {"eventId": event_id, "page": page_num, "perPage": per_page}
        response = run_query(e_queries.GET_PLACEMENTS_QUERY, variables, self.header, self.auto_retry)
        data = e_queries.get_placements_filter(response)
        return data

    def get_placements_all(self, event_id):
        func = paginated(self.get_placements)
        return func(event_id)

    def get_players(self, event_id, page_num, per_page=50):
        variables = {"eventId": event_id, "page": page_num, "perPage": per_page}
        response = run_query(e_queries.GET_PLAYERS_QUERY, variables, self.header, self.auto_retry)
        data = e_queries.get_players_filter(response)
        return data

    def get_players_all(self, event_id):
        func = paginated(self.get_players)
        return func(event_id)

    def get_player_ids(self, event_id):
        # Try using standings first
        players = self.get_players_all(event_id)
        if players is not None:
            return [p['id'] for p in players]

        # Use projected bracket if above does not return
        results = self.get_sets_all(event_id)
        if results is None or results == []:
            return []
        print(results)
        sets, games = results
        pids = set()
        for s in sets:
            for i in ('p1id', 'p2id'):
                if s[i] is not None:
                    pids.add(s[i])
        return list(pids)

    # ORIG
    # # Helper function to get entrantId at an event
    # def get_entrant_id(self, event_id, player_name):
    #     variables = {"eventId": event_id, "name": player_name}
    #     response = run_query(e_queries.ENTRANT_ID_QUERY, variables, self.header, self.auto_retry)
    #     data = response['data']['event']['entrants']['nodes'][0]['id']
    #     return data
    #
    # # Shows all the sets from an event
    # def show_sets(self, event_id, page_num):
    #     variables = {"eventId": event_id, "page": page_num}
    #     response = run_query(e_queries.SHOW_SETS_QUERY, variables, self.header, self.auto_retry)
    #     data = e_queries.show_sets_filter(response)
    #     return data
    #
    # # Shows all entrants from a specific event
    # def show_entrants(self, event_id, page_num):
    #     variables = {"eventId": event_id, "page": page_num}
    #     response = run_query(e_queries.SHOW_ENTRANTS_QUERY, variables, self.header, self.auto_retry)
    #     data = e_queries.show_entrants_filter(response)
    #     return data
    #
    # # Shows all entrant sets from a given event
    # def show_entrant_sets(self, event_id, entrant_name):
    #     entrant_id = self.get_entrant_id(event_id, entrant_name)
    #     variables = {"eventId": event_id, "entrantId": entrant_id, "page": 1}
    #     response = run_query(e_queries.SHOW_ENTRANT_SETS_QUERY, variables, self.header, self.auto_retry)
    #     data = e_queries.show_entrant_sets_filter(response)
    #     return data
    #
    # # Shows head to head at an event for two given entrants
    # def show_head_to_head(self, event_id, entrant1_name, entrant2_name):
    #     entrant1_id = self.get_entrant_id(event_id, entrant1_name)
    #     variables = {"eventId": event_id, "entrantId": entrant1_id, "page": 1}
    #     response = run_query(e_queries.SHOW_ENTRANT_SETS_QUERY, variables, self.header, self.auto_retry)
    #     data = e_queries.show_head_to_head_filter(response, entrant2_name)
    #     return data
    #
    # # Shows the results of an event with only entrant name, id, and placement
    # def show_lightweight_results(self, event_id, page_num):
    #     variables = {"eventId": event_id, "page": page_num}
    #     response = run_query(e_queries.SHOW_LIGHTWEIGHT_RESULTS_QUERY, variables, self.header, self.auto_retry)
    #     data = e_queries.show_lightweight_results_filter(response)
    #     return data