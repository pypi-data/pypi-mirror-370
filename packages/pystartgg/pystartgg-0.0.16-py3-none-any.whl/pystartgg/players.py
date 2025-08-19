import pystartgg.p_queries as p_queries
from pystartgg.api import run_query

class Player:
    def __init__(self, key, header, auto_retry):
        self.key = key
        self.header = header
        self.auto_retry = auto_retry

    # Shows info for a player
    def get_info(self, player_id):
        variables = {"playerId": player_id}
        response = run_query(p_queries.PLAYER_GET_INFO_QUERY, variables, self.header, self.auto_retry)
        data = p_queries.player_get_info_filter(response)
        return data

    # ORIG
    # # Shows tournament attended by a player
    # def show_tournaments(self, player_id, page_num):
    #     variables = {"playerId": player_id, "page": page_num}
    #     response = run_query(p_queries.PLAYER_SHOW_TOURNAMENTS_QUERY, variables, self.header, self.auto_retry)
    #     data = p_queries.player_show_tournaments_filter(response)
    #     return data
    #
    # # Shows tournaments attended by a player for a certain game
    # # This is SUPER janky code but I don't know how to get it to work otherwise
    # def show_tournaments_for_game(self, player_id, player_name, videogame_id, page_num):
    #     variables = {"playerId": player_id, "playerName": player_name, "videogameId": videogame_id, "page": page_num}
    #     response = run_query(p_queries.PLAYER_SHOW_TOURNAMENTS_FOR_GAME_QUERY, variables, self.header, self.auto_retry)
    #     data = p_queries.player_show_tournaments_for_game(response, videogame_id)
    #     return data

