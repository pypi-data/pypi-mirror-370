import pystartgg.t_queries as t_queries
from pystartgg.api import run_query, paginated

# HELPER FUNCTIONS
class Tournament:
    def __init__(self, key, header, auto_retry):
        self.key = key
        self.header = header
        self.auto_retry = auto_retry

    # Metadata for a tournament
    def get(self, tournament_name):
        variables = {"tourneySlug": tournament_name}
        response = run_query(t_queries.GET_QUERY, variables, self.header, self.auto_retry)
        data = t_queries.get_filter(response)
        return data

    def get_info(self, tournament_id):
        variables = {"tourneyId": tournament_id}
        response = run_query(t_queries.GET_INFO_QUERY, variables, self.header, self.auto_retry)
        data = t_queries.get_info_filter(response)
        return data

    def get_events(self, tournament_id):
        variables = {"tourneyId": tournament_id}
        response = run_query(t_queries.GET_EVENTS_QUERY, variables, self.header, self.auto_retry)
        data = t_queries.get_events_filter(response)
        return data

    def get_between_dates_for_game(self, start, end, videogameId, page_num, per_page=50):
        variables = {
            "start": start,
            "end": end,
            "videogameId": videogameId,
            "page": page_num,
            "perPage": per_page
        }
        response = run_query(t_queries.GET_BETWEEN_DATES_FOR_GAME_QUERY, variables, self.header, self.auto_retry)
        data1, data2 = t_queries.get_between_dates_for_game_filter(response)
        return data1, data2

    def get_between_dates_for_game_all(self, start, end, videogameId):
        func = paginated(self.get_between_dates_for_game, multi_return=True)
        return func(start, end, videogameId)


    #ORIG
    # # Helper function to get playerId at an event
    # def get_player_id(self, event_id, player_name):
    #     variables = {"eventId": event_id, "name": player_name}
    #     response = run_query(t_queries.PLAYER_ID_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.player_id_filter(response, player_name)
    #     return data
    #
    # # Helper function to get entrantId at an event
    # def get_entrant_id(self, event_id, player_name):
    #     variables = {"eventId": event_id, "name": player_name}
    #     response = run_query(t_queries.ENTRANT_ID_QUERY, variables, self.header, self.auto_retry)
    #     data = response['data']['event']['entrants']['nodes'][0]['id']
    #     return data
    #
    # # Helper function to get an eventId from a tournament
    # def get_event_id(self, tournament_name, event_name):
    #     variables = {"tourneySlug": tournament_name}
    #     response = run_query(t_queries.EVENT_ID_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.event_id_filter(response, event_name)
    #     return data
    #
    # # ACTUAL FUNCTIONS
    #
    #
    # # Metadata for a tournament with a specific brackets
    # def get_with_brackets(self, tournament_name, event_name):
    #     variables = {"tourneySlug": tournament_name}
    #     response = run_query(t_queries.GET_WITH_BRACKETS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_with_brackets_filter(response, event_name)
    #     return data
    #
    # # Metadata for a tournament with all brackets
    # def get_with_brackets_all(self, tournament_name):
    #     variables = {"tourneySlug": tournament_name}
    #     response = run_query(t_queries.GET_WITH_BRACKETS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_with_brackets_all_filter(response)
    #     return data
    #
    # # # Shows all events from a tournaments
    # # def get_events(self, tournament_name):
    # #     variables = {"tourneySlug": tournament_name}
    # #     response = run_query(t_queries.GET_EVENTS_QUERY, variables, self.header, self.auto_retry)
    # #     data = t_queries.get_events_filter(response)
    # #     return data
    #
    #
    #
    # # Shows all entrants from a specific event
    # def get_entrants(self, tournament_name, event_name, page_num):
    #     event_id = self.get_event_id(tournament_name, event_name)
    #     variables = {"eventId": event_id, "page": page_num}
    #     response = run_query(t_queries.GET_ENTRANTS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_entrants_filter(response)
    #     return data
    #
    # # Shows all the event bracket IDs as well as the name and slug of the event
    # def get_event_brackets(self, tournament_name, event_name):
    #     variables = {"tourneySlug": tournament_name}
    #     response = run_query(t_queries.GET_EVENT_BRACKETS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_events_brackets_filter(response, event_name)
    #     return data
    #
    # # Same as get_events_brackets but for all events at a tournament
    # def get_all_event_brackets(self, tournament_name):
    #     variables = {"tourneySlug": tournament_name}
    #     response = run_query(t_queries.GET_EVENT_BRACKETS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_all_event_brackets_filter(response)
    #     return data
    #
    # # Shows all entrant sets from a given event
    # def get_entrant_sets(self, tournament_name, event_name, entrant_name):
    #     event_id = self.get_event_id(tournament_name, event_name)
    #     entrant_id = self.get_entrant_id(event_id, entrant_name)
    #     variables = {"eventId": event_id, "entrantId": entrant_id, "page": 1}
    #     response = run_query(t_queries.GET_ENTRANT_SETS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_entrant_sets_filter(response)
    #     return data
    #
    # # Shows head to head at an event for two given entrants
    # def get_head_to_head(self, tournament_name, event_name, entrant1_name, entrant2_name):
    #     event_id = self.get_event_id(tournament_name, event_name)
    #     entrant1_id = self.get_entrant_id(event_id, entrant1_name)
    #     variables = {"eventId": event_id, "entrantId": entrant1_id, "page": 1}
    #     response = run_query(t_queries.GET_ENTRANT_SETS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_head_to_head_filter(response, entrant2_name)
    #     return data
    #
    # # Shows all events (of a certain game) of a minimum size in between two unix timestamps
    # def get_event_by_game_size_dated(self, num_entrants, videogame_id, after, before, page_num):
    #     variables = {"videogameId": videogame_id, "after": after, "before": before, "page": page_num}
    #     response = run_query(t_queries.GET_EVENT_BY_GAME_SIZE_DATED_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_event_by_game_size_dated_filter(response, num_entrants, videogame_id)
    #     return data
    #
    # # Shows the results of an event with only entrant name, id, and placement
    # def get_lightweight_results(self, tournament_name, event_name, page_num):
    #     event_id = self.get_event_id(tournament_name, event_name)
    #     variables = {"eventId": event_id, "page": page_num}
    #     response = run_query(t_queries.GET_LIGHTWEIGHT_RESULTS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_lightweight_results_filter(response)
    #     return data
    #
    # # Shows a list of tournaments by country
    # def get_by_country(self, country_code, page_num):
    #     variables = {"countryCode": country_code, "page": page_num}
    #     response = run_query(t_queries.GET_BY_COUNTRY_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_by_country_filter(response)
    #     return data
    #
    # # Shows a list of tournaments by US State
    # def get_by_state(self, state_code, page_num):
    #     variables = {"state": state_code, "page": page_num}
    #     response = run_query(t_queries.GET_BY_STATE_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_by_state_filter(response)
    #     return data
    #
    # # Shows a list of tournaments from a certain point within a radius
    # def get_by_radius(self, coordinates, radius, page_num):
    #     variables = {"coordinates": coordinates, "radius": radius, "page": page_num}
    #     response = run_query(t_queries.GET_BY_RADIUS_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_by_radius_filter(response)
    #     return data
    #
    # # Shows a list of players at a tournament by their sponsor
    # def get_players_by_sponsor(self, tournament_name, sponsor):
    #     variables = {"slug": tournament_name, "sponsor": sponsor}
    #     response = run_query(t_queries.GET_PLAYERS_BY_SPONSOR, variables, self.header, self.auto_retry)
    #     data = t_queries.get_players_by_sponsor_filter(response)
    #     return data
    #
    # def get_by_owner(self, owner, page_num):
    #     variables = {"ownerId": owner, "page": page_num}
    #     response = run_query(t_queries.GET_BY_OWNER_QUERY, variables, self.header, self.auto_retry)
    #     data = t_queries.get_by_owner_filter(response)
    #     return data