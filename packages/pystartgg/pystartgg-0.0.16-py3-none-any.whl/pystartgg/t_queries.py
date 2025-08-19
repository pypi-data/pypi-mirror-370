# Queries for tournaments.py

GET_QUERY = """query ($tourneySlug: String!) {
  tournament(slug: $tourneySlug) {
    id
    name
    slug
    startAt
    endAt
    numAttendees
    countryCode
    addrState
    city
    state
    isOnline
    owner {
      id
    }
  }
}"""

# Filtering for the get function
def get_filter(response):
    if response['data']['tournament'] is None:
        return None

    tournament = response['data']['tournament']
    tournament['owner'] = tournament['owner']['id']
    states = {
        1: 'CREATED',
        2: 'ACTIVE',
        3: 'COMPLETED',
        4: 'READY',
        5: 'INVALID',
        6: 'CALLED',
        7: 'QUEUED',
    }
    tournament['state'] = states[tournament['state']]
    tournament['slug'] = tournament['slug'].split('/')[-1]

    return tournament

GET_INFO_QUERY = '''
query ($tourneyId: ID!) {
  tournament(id: $tourneyId) {
    id
    name
    slug
    startAt
    endAt
    numAttendees
    countryCode
    addrState
    city
    state
    isOnline
    owner {
      id
    }
  }
}
'''


def get_info_filter(response):
    if response['data'] is None:
        return None

    tournament = response['data']['tournament']
    tournament['owner'] = tournament['owner']['id']
    states = {
        1:'CREATED',
        2:'ACTIVE',
        3:'COMPLETED',
        4:'READY',
        5:'INVALID',
        6:'CALLED',
        7:'QUEUED',
    }
    tournament['state'] = states[tournament['state']]
    tournament['slug'] = tournament['slug'].split('/')[-1]

    return tournament

GET_EVENTS_QUERY = '''
    query ($tourneyId: ID!) {
      tournament(id: $tourneyId) {
        id
        events {
          id
          slug
          name
          videogame {
            id
          }
          teamRosterSize {
            maxPlayers
          }
          numEntrants
        }
      }
    }
'''

def get_events_filter(response):
    if response['data'] is None:
        return None

    tournament_id = response['data']['tournament']['id']
    events = response['data']['tournament']['events']
    for event in events:
        event['tournamentId'] = tournament_id
        event['videogame'] = event['videogame']['id']
        event['slug'] = event['slug'].split('/')[-1]
        if event['teamRosterSize'] is None:
            event['teamRosterSize'] = 1
        else:
            event['teamRosterSize'] = event['teamRosterSize']['maxPlayers']

    return events

GET_BETWEEN_DATES_FOR_GAME_QUERY = '''
query Tournaments($page: Int!, $videogameId: [ID!], $start: Timestamp!, $end: Timestamp!, $perPage: Int!) {
  tournaments(query: {
    perPage: $perPage
    page: $page
    sortBy: "startAt asc"
    filter: {
      videogameIds: $videogameId
      afterDate: $start
      beforeDate: $end
    }
  }) {
    nodes {
      id
      name
      slug
      startAt
      endAt
      numAttendees
      countryCode
      addrState
      city
      state
      isOnline
      owner {
        id
      }
      events {
        id
        slug
        name
        videogame {
          id
        }
        teamRosterSize {
          maxPlayers
        }
        numEntrants
      }
    }
  }
}
'''

def get_between_dates_for_game_filter(response):
    if response['data'] is None:
        return None

    return_tournaments = []
    return_events = []

    tournaments = response['data']['tournaments']['nodes']
    for tournament in tournaments:
        curr_tournament = {
            'id': tournament['id'],
            'name': tournament['name'],
            'slug': tournament['slug'].split('/')[-1],
            'startAt': tournament['startAt'],
            'endAt': tournament['endAt'],
            'numAttendees': tournament['numAttendees'],
            'countryCode': tournament['countryCode'],
            'addrState': tournament['addrState'],
            'city': tournament['city'],
            'state': tournament['state'],
            'isOnline': tournament['isOnline'],
            'owner': tournament['owner']['id']
        }
        return_tournaments.append(curr_tournament)

        events = tournament['events']
        for event in events:
            curr_event = {
                'id': event['id'],
                'slug': event['slug'].split('/')[-1],
                'name': event['name'],
                'videogame': event['videogame']['id'],
                'teamRosterSize': event['teamRosterSize'],
                'numEntrants': event['numEntrants'],
                'tournamentId': curr_tournament['id'],
            }

            if event['teamRosterSize'] is None:
                curr_event['teamRosterSize'] = 1
            else:
                curr_event['teamRosterSize'] = event['teamRosterSize']['maxPlayers']

            return_events.append(curr_event)

    return return_tournaments, return_events




# # ORIG
# PLAYER_ID_QUERY = """query EventEntrants($eventId: ID!, $name: String!) {
#     event(id: $eventId) {
#     entrants(query: {
#       page: 1
#       perPage: 32
#       filter: {name: $name}
#     }) {
#       nodes {
#         participants {
#           gamerTag
#           player {
#             id
#           }
#         }
#       }
#     }
#     }
#     }"""
#
# # Filtering for the player_id function
# def player_id_filter(response, player_name):
#     if response['data']['event']['entrants']['nodes'] is None:
#         return None
#
#     for node in response['data']['event']['entrants']['nodes'][0]['participants']:
#         if node['gamerTag'].lower() == player_name.lower():
#             player_id = node['player']['id']
#         elif (node['participants'][0]['gamerTag'].split("|")[-1]).lower() == player_name.lower():
#             player_id = node['player']['id']
#
#     return player_id
#
# EVENT_ID_QUERY = """query ($tourneySlug: String!) {
#   tournament(slug: $tourneySlug) {
#     events {
#       id
#       slug
#     }
#   }
# }"""
#
# # Filter for the event_id function
# def event_id_filter(response, event_name):
#     if response['data']['tournament'] is None:
#         return None
#
#     for event in response['data']['tournament']['events']:
#         if event['slug'].split("/")[-1] == event_name:
#             return event['id']
#
#     return None
#
# ENTRANT_ID_QUERY = """query EventEntrants($eventId: ID!, $name: String!) {
#     event(id: $eventId) {
#     entrants(query: {
#       page: 1
#       perPage: 32
#       filter: {
#         name: $name
#       }
#     }) {
#       nodes {
#         id
#         name
#       }
#     }
#     }
#     }"""
#
#
#
# GET_WITH_BRACKETS_QUERY = """query ($tourneySlug: String!) {
#   tournament(slug: $tourneySlug) {
#     id
#     name
#     countryCode
#     addrState
#     city
#     startAt
#     endAt
#     numAttendees
#     events {
#       id
#       name
#       slug
#       phaseGroups {
#         id
#       }
#     }
#   }
# }"""
#
# # Filtering for the get_with_brackets function
# def get_with_brackets_filter(response, event_name):
#     if response['data']['tournament'] is None:
#         return None
#
#     data = {
#         'id': response['data']['tournament']['id'],
#         'name': response['data']['tournament']['name'],
#         'country': response['data']['tournament']['countryCode'],
#         'state': response['data']['tournament']['addrState'],
#         'city': response['data']['tournament']['city'],
#         'startTimestamp': response['data']['tournament']['startAt'],
#         'endTimestamp': response['data']['tournament']['endAt'],
#         'entrants': response['data']['tournament']['numAttendees']
#     }
#
#     for event in response['data']['tournament']['events']:
#         if event['slug'].split("/")[-1] == event_name:
#             data['eventId'] = event['id']
#             data['eventName'] = event['name']
#             data['eventSlug'] = event['slug'].split('/')[-1]
#             bracket_ids = []
#             if event['phaseGroups'] is not None:
#                 for node in event['phaseGroups']:
#                     bracket_ids.append(node['id'])
#             data['bracketIds'] = bracket_ids
#
#             break
#
#     return data
#
# # Filtering for the get_with_brackets_all function
# def get_with_brackets_all_filter(response):
#     if response['data']['tournament'] is None:
#         return None
#
#     data = {
#         'id': response['data']['tournament']['id'],
#         'name': response['data']['tournament']['name'],
#         'country': response['data']['tournament']['countryCode'],
#         'state': response['data']['tournament']['addrState'],
#         'city': response['data']['tournament']['city'],
#         'startTimestamp': response['data']['tournament']['startAt'],
#         'endTimestamp': response['data']['tournament']['endAt'],
#         'entrants': response['data']['tournament']['numAttendees']
#     }
#
#     for event in response['data']['tournament']['events']:
#         bracket_ids = []
#         if event['phaseGroups'] is not None:
#             for node in event['phaseGroups']:
#                 bracket_ids.append(node['id'])
#
#         del event['phaseGroups']
#         event['bracketIds'] = bracket_ids
#
#     data['events'] = response['data']['tournament']['events']
#
#     return data
#
# # GET_EVENTS_QUERY = """query ($tourneySlug: String!) {
# #   tournament(slug: $tourneySlug) {
# #     events {
# #       id
# #       name
# #       slug
# #       numEntrants
# #     }
# #   }
# # }"""
#
# # # Filter for the get_events function
# # def get_events_filter(response):
# #     if response['data']['tournament'] is None:
# #         return None
# #
# #     event_list = []
# #     for event in response['data']['tournament']['events']:
# #         cur_event = {
# #             'id': event['id'],
# #             'name': event['name'],
# #             'slug': event['slug'].split('/')[-1],
# #             'entrants': event['numEntrants']
# #         }
# #
# #         event_list.append(cur_event)
# #
# #     return event_list
#
#
#
#
# # # Filter for the get_sets function
# # def get_sets_filter(response):
# #     if 'data' not in response:
# #         return None
# #     if response['data']['event'] is None:
# #         return None
# #
# #     if response['data']['event']['sets']['nodes'] is None:
# #         return None
# #
# #     sets = []  # Need for return at the end
# #
# #     for node in response['data']['event']['sets']['nodes']:
# #         # TODO: these catch when a set has less than two competitors,
# #         #  which does not work for tournaments which have not started yet.
# #         #  Need to modify to allow for NULL competitors.
# #         if len(node['slots']) < 2:
# #             continue  # This fixes a bug where player doesn't have an opponent
# #         if (node['slots'][0]['entrant'] is None) or (node['slots'][1]['entrant'] is None):
# #             continue  # This fixes a bug when tournament ends early
# #
# #         cur_set = {
# #             'id': node['id'],
# #             'entrant1Id': node['slots'][0]['entrant']['id'],
# #             'entrant2Id': node['slots'][1]['entrant']['id'],
# #             'entrant1Name': node['slots'][0]['entrant']['name'],
# #             'entrant2Name': node['slots'][1]['entrant']['name']
# #         }
# #
# #         if node['games'] is not None:
# #             entrant1_chars = []
# #             entrant2_chars = []
# #             game_winners_ids = []
# #             for game in node['games']:
# #                 if (game[
# #                     'selections'] is None):  # This fixes an issue with selections being none while games are reported
# #                     continue
# #                 elif (node['slots'][0]['entrant']['id'] == game['selections'][0]['entrant']['id']):
# #                     entrant1_chars.append(game['selections'][0]['selectionValue'])
# #                     if len(game['selections']) > 1:
# #                         entrant2_chars.append(game['selections'][1]['selectionValue'])
# #                 else:
# #                     entrant2_chars.append(game['selections'][0]['selectionValue'])
# #                     if len(game['selections']) > 1:
# #                         entrant1_chars.append(game['selections'][1]['selectionValue'])
# #
# #                 game_winners_ids.append(game['winnerId'])
# #
# #             cur_set['entrant1Chars'] = entrant1_chars
# #             cur_set['entrant2Chars'] = entrant2_chars
# #             cur_set['gameWinners'] = game_winners_ids
# #
# #         # Next 2 if/else blocks make sure there's a result in, sometimes DQs are weird
# #         # there also could be ongoing matches
# #         match_done = True
# #         if node['slots'][0]['standing'] is None:
# #             cur_set['entrant1Score'] = -1
# #             match_done = False
# #         elif node['slots'][0]['standing']['stats']['score']['value'] is not None:
# #             cur_set['entrant1Score'] = node['slots'][0]['standing']['stats']['score']['value']
# #         else:
# #             cur_set['entrant1Score'] = -1
# #
# #         if node['slots'][1]['standing'] is None:
# #             cur_set['entrant2Score'] = -1
# #             match_done = False
# #         elif node['slots'][1]['standing']['stats']['score']['value'] is not None:
# #             cur_set['entrant2Score'] = node['slots'][1]['standing']['stats']['score']['value']
# #         else:
# #             cur_set['entrant2Score'] = -1
# #
# #         # Determining winner/loser (elif because sometimes startgg won't give us one)
# #         if match_done:
# #             cur_set['completed'] = True
# #             if node['slots'][0]['standing']['placement'] == 1:
# #                 cur_set['winnerId'] = cur_set['entrant1Id']
# #                 cur_set['loserId'] = cur_set['entrant2Id']
# #                 cur_set['winnerName'] = cur_set['entrant1Name']
# #                 cur_set['loserName'] = cur_set['entrant2Name']
# #             elif node['slots'][0]['standing']['placement'] == 2:
# #                 cur_set['winnerId'] = cur_set['entrant2Id']
# #                 cur_set['loserId'] = cur_set['entrant1Id']
# #                 cur_set['winnerName'] = cur_set['entrant2Name']
# #                 cur_set['loserName'] = cur_set['entrant1Name']
# #         else:
# #             cur_set['completed'] = False
# #
# #         cur_set['fullRoundText'] = node['fullRoundText']
# #
# #         if node['phaseGroup'] is not None:
# #             cur_set['bracketName'] = node['phaseGroup']['phase']['name']
# #             cur_set['bracketId'] = node['phaseGroup']['id']
# #         else:
# #             cur_set['bracketName'] = None
# #             cur_set['bracketId'] = None
# #
# #         # This gives player_ids, but it also is made to work with team events
# #         for j in range(0, 2):
# #             players = []
# #             for user in node['slots'][j]['entrant']['participants']:
# #                 cur_player = {}
# #                 if user['player'] is not None:
# #                     cur_player['playerId'] = user['player']['id']
# #                     cur_player['playerTag'] = user['player']['gamerTag']
# #                     if user['entrants'] is not None:
# #                         cur_player['entrantId'] = user['entrants'][0]['id']
# #                     else:
# #                         cur_player['entrantId'] = node['slots'][j]['entrant']['id']
# #                     players.append(cur_player)
# #                 else:
# #                     cur_player['playerId'] = None
# #                     cur_player['playerTag'] = None
# #                     cur_player['entrantId'] = node['slots'][j]['entrant']['id']
# #
# #             cur_set['entrant' + str(j + 1) + 'Players'] = players
# #
# #         sets.append(cur_set)  # Adding that specific set onto the large list of sets
# #
# #     return sets
#
#
# GET_ENTRANTS_QUERY = """query EventStandings($eventId: ID!, $page: Int!) {
#   event(id: $eventId) {
#     id
#     name
#     standings(query: {
#       perPage: 25,
#       page: $page}){
#       nodes {
#         placement
#         entrant {
#           id
#           name
#           participants {
#             player {
#               id
#               gamerTag
#             }
#           }
#           seeds {
#             seedNum
#           }
#         }
#       }
#     }
#   }
# }"""
#
#
# # Filters for the get_players function
# def get_entrants_filter(response):
#     if response['data']['event'] is None:
#         return None
#
#     if response['data']['event']['standings']['nodes'] is None:
#         return None
#
#     entrants = []  # Need for return at the end
#
#     for node in response['data']['event']['standings']['nodes']:
#         cur_entrant = {
#             'entrantId': node['entrant']['id'],
#             'tag': node['entrant']['name'],
#             'finalPlacement': node['placement']
#         }
#         if node['entrant']['seeds'] is None:
#             cur_entrant['seed'] = -1
#         else:
#             cur_entrant['seed'] = node['entrant']['seeds'][0]['seedNum']
#
#         players = []
#         for user in node['entrant']['participants']:
#             cur_player = {}
#             if user['player']['id'] is not None:
#                 cur_player['playerId'] = user['player']['id']
#             else:
#                 cur_player['playerId'] = "None"
#             cur_player['playerTag'] = user['player']['gamerTag']
#             players.append(cur_player)
#         cur_entrant['entrantPlayers'] = players
#
#         entrants.append(cur_entrant)
#
#     return entrants
#
# GET_EVENT_BRACKETS_QUERY = """query ($tourneySlug: String!) {
#   tournament(slug: $tourneySlug) {
#     events {
#       name
#       slug
#       phaseGroups {
#         id
#       }
#     }
#   }
# }"""
#
# # Filter for the get_events_brackets function
# def get_events_brackets_filter(response, event_name):
#     if response['data']['tournament'] is None:
#         return None
#
#     brackets = {}
#
#     for event in response['data']['tournament']['events']:
#         if event['slug'].split('/')[-1] == event_name:
#             bracket_ids = []
#             for node in event['phaseGroups']:
#                 bracket_ids.append(node['id'])
#
#             brackets['eventName'] = event['name']
#             brackets['slug'] = event['slug']
#             brackets['bracketIds'] = bracket_ids
#
#     return brackets
#
# # Filter for the get_all_event_brackets function
# def get_all_event_brackets_filter(response):
#     if response['data']['tournament'] is None:
#         return None
#
#     brackets = []
#     for event in response['data']['tournament']['events']:
#         cur_bracket = {}
#         bracket_ids = []
#         if event['phaseGroups'] is not None:
#             for node in event['phaseGroups']:
#                 bracket_ids.append(node['id'])
#
#         cur_bracket['eventName'] = event['name']
#         cur_bracket['slug'] = event['slug']
#         cur_bracket['bracketIds'] = bracket_ids
#
#         brackets.append(cur_bracket)
#
#     return brackets
#
# GET_ENTRANT_SETS_QUERY = """query EventSets($eventId: ID!, $entrantId: ID!, $page: Int!) {
#   event(id: $eventId) {
#     sets(
#       page: $page
#       perPage: 16
#       filters: {
#         entrantIds: [$entrantId]
#       }
#     ) {
#       nodes {
#         id
#         fullRoundText
#         slots {
#           standing {
#             placement
#             stats {
#               score {
#                 value
#               }
#             }
#           }
#           entrant {
#             id
#             name
#           }
#         }
#         phaseGroup {
#           id
#         }
#       }
#     }
#   }
# }"""
#
#
# # Filter for the get_player_sets function
# def get_entrant_sets_filter(response):
#     if response['data']['event'] is None:
#         return None
#
#     if response['data']['event']['sets']['nodes'] is None:
#         return None
#
#     sets = []  # Need for return at the end
#
#     for node in response['data']['event']['sets']['nodes']:
#         cur_set = {
#             'id': node['id'],
#             'entrant1Id': node['slots'][0]['entrant']['id'],
#             'entrant2Id': node['slots'][1]['entrant']['id'],
#             'entrant1Name': node['slots'][0]['entrant']['name'],
#             'entrant2Name': node['slots'][1]['entrant']['name']
#         }
#
#         # Next 2 if/else blocks make sure there's a result in, sometimes DQs are weird
#         match_done = True
#         if node['slots'][0]['standing'] is None:
#             cur_set['entrant1Score'] = -1
#             match_done = False
#         elif node['slots'][0]['standing']['stats']['score']['value'] is not None:
#             cur_set['entrant1Score'] = node['slots'][0]['standing']['stats']['score']['value']
#         else:
#             cur_set['entrant1Score'] = -1
#
#         if node['slots'][1]['standing'] is None:
#             cur_set['entrant2Score'] = -1
#             match_done = False
#         elif node['slots'][1]['standing']['stats']['score']['value'] is not None:
#             cur_set['entrant2Score'] = node['slots'][1]['standing']['stats']['score']['value']
#         else:
#             cur_set['entrant2Score'] = -1
#
#         # Determining winner/loser (elif because sometimes startgg won't give us one)
#         if match_done:
#             cur_set['completed'] = True
#             if node['slots'][0]['standing']['placement'] == 1:
#                 cur_set['winnerId'] = cur_set['entrant1Id']
#                 cur_set['loserId'] = cur_set['entrant2Id']
#                 cur_set['winnerName'] = cur_set['entrant1Name']
#                 cur_set['loserName'] = cur_set['entrant2Name']
#             elif node['slots'][0]['standing']['placement'] == 2:
#                 cur_set['winnerId'] = cur_set['entrant2Id']
#                 cur_set['loserId'] = cur_set['entrant1Id']
#                 cur_set['winnerName'] = cur_set['entrant2Name']
#                 cur_set['loserName'] = cur_set['entrant1Name']
#         else:
#             cur_set['completed'] = False
#
#         cur_set['setRound'] = node['fullRoundText']
#         cur_set['bracketId'] = node['phaseGroup']['id']
#
#         sets.append(cur_set)  # Adding that specific set onto the large list of sets
#
#     return sets
#
#
# # Filter for the get_head_to_head function
# def get_head_to_head_filter(response, player2_name):
#     if response['data']['event'] is None:
#         return None
#
#     if response['data']['event']['sets']['nodes'] is None:
#         return None
#
#     sets = []
#
#     for node in response['data']['event']['sets']['nodes']:
#         # Yes, the if statement needs to be this long to account for all cases
#         # I don't want to run another query, smash.gg's API can be trash sometimes
#         if ((node['slots'][0]['entrant']['name'].split('|')[-1]).lower() == player2_name.lower()
#                 or node['slots'][0]['entrant']['name'].lower() == player2_name.lower()
#                 or (node['slots'][1]['entrant']['name'].split('|')[-1]).lower() == player2_name.lower()
#                 or node['slots'][1]['entrant']['name'].lower() == player2_name.lower()):
#             cur_set = {
#                 'id': node['id'],
#                 'entrant1Id': node['slots'][0]['entrant']['id'],
#                 'entrant2Id': node['slots'][1]['entrant']['id'],
#                 'entrant1Name': node['slots'][0]['entrant']['name'],
#                 'entrant2Name': node['slots'][1]['entrant']['name']
#             }
#
#             # Next 2 if/else blocks make sure there's a result in, sometimes DQs are weird
#             match_done = True
#             if node['slots'][0]['standing'] is None:
#                 cur_set['entrant1Score'] = -1
#                 match_done = False
#             elif node['slots'][0]['standing']['stats']['score']['value'] is not None:
#                 cur_set['entrant1Score'] = node['slots'][0]['standing']['stats']['score']['value']
#             else:
#                 cur_set['entrant1Score'] = -1
#
#             if node['slots'][1]['standing'] is None:
#                 cur_set['entrant2Score'] = -1
#                 match_done = False
#             elif node['slots'][1]['standing']['stats']['score']['value'] is not None:
#                 cur_set['entrant2Score'] = node['slots'][1]['standing']['stats']['score']['value']
#             else:
#                 cur_set['entrant2Score'] = -1
#
#             # Determining winner/loser (elif because sometimes startgg won't give us one)
#             if match_done:
#                 cur_set['completed'] = True
#                 if node['slots'][0]['standing']['placement'] == 1:
#                     cur_set['winnerId'] = cur_set['entrant1Id']
#                     cur_set['loserId'] = cur_set['entrant2Id']
#                     cur_set['winnerName'] = cur_set['entrant1Name']
#                     cur_set['loserName'] = cur_set['entrant2Name']
#                 elif node['slots'][0]['standing']['placement'] == 2:
#                     cur_set['winnerId'] = cur_set['entrant2Id']
#                     cur_set['loserId'] = cur_set['entrant1Id']
#                     cur_set['winnerName'] = cur_set['entrant2Name']
#                     cur_set['loserName'] = cur_set['entrant1Name']
#             else:
#                 cur_set['completed'] = False
#
#             cur_set['setRound'] = node['fullRoundText']
#             cur_set['bracketId'] = node['phaseGroup']['id']
#
#             sets.append(cur_set)
#
#     return sets
#
# GET_EVENT_BY_GAME_SIZE_DATED_QUERY = """query TournamentsByVideogame($page: Int!, $videogameId: [ID!], $after: Timestamp!, $before: Timestamp!) {
#   tournaments(query: {
#     perPage: 32
#     page: $page
#     sortBy: "startAt asc"
#     filter: {
#       past: false
#       videogameIds: $videogameId
#       afterDate: $after
#       beforeDate: $before
#     }
#   }) {
#     nodes {
#       name
#       id
#       slug
#       isOnline
#       startAt
#       endAt
#       events {
#         name
#         id
#         numEntrants
#         videogame {
#           id
#         }
#       }
#     }
#   }
# }"""
#
# # Filter for the get_event_by_game_size_dated function
# def get_event_by_game_size_dated_filter(response, size, videogame_id):
#     if response['data'] is None:
#         return None
#
#     if response['data']['tournaments'] is None:
#         return None
#
#     if response['data']['tournaments']['nodes'] is None:
#         return None
#
#     events = []
#
#     for node in response['data']['tournaments']['nodes']:
#         for event in node['events']:
#             if (event['numEntrants'] is None) or (event['videogame']['id'] is None):
#                 continue
#             elif event['videogame']['id'] == videogame_id and event['numEntrants'] >= size:
#                 cur_event = {
#                     'tournamentName': node['name'],
#                     'tournamentSlug': node['slug'].split('/')[-1],
#                     'tournamentId': node['id'],
#                     'online': node['isOnline'],
#                     'startAt': node['startAt'],
#                     'endAt': node['endAt'],
#                     'eventName': event['name'],
#                     'eventId': event['id'],
#                     'numEntrants': event['numEntrants']
#                 }
#
#                 events.append(cur_event)
#
#     return events
#
# GET_LIGHTWEIGHT_RESULTS_QUERY = """query EventStandings($eventId: ID!, $page: Int!,) {
#   event(id: $eventId) {
#     standings(query: {
#       perPage: 64,
#       page: $page
#     }){
#       nodes {
#         placement
#         entrant {
#           name
#           id
#         }
#       }
#     }
#   }
# }"""
#
# # Filter for the get_lightweight_results function
# def get_lightweight_results_filter(response):
#     if response['data']['event'] is None:
#         return None
#     if response['data']['event']['standings']['nodes'] is None:
#         return None
#
#     entrants = []
#
#     for node in response['data']['event']['standings']['nodes']:
#         cur_entrant = {
#             'placement': node['placement'],
#             'name': node['entrant']['name'].split(' | ')[-1],
#             'id': node['entrant']['id']
#         }
#
#         entrants.append(cur_entrant)
#
#     return entrants
#
# GET_BY_COUNTRY_QUERY = """query TournamentsByCountry($countryCode: String!, $page: Int!) {
#   tournaments(query: {
#     perPage: 32,
#     page: $page,
#     sortBy: "startAt desc"
#     filter: {
#       countryCode: $countryCode
#     }
#   }) {
#     nodes {
#       id
#       name
#       slug
#       numAttendees
#       addrState
#       city
#       startAt
#       endAt
#       state
#     }
#   }
# }"""
#
# # Filter for the get_by_country function
# def get_by_country_filter(response):
#     if response['data']['tournaments'] is None:
#         return None
#
#     if response['data']['tournaments']['nodes'] is None:
#         return None
#
#     tournaments = []
#
#     for node in response['data']['tournaments']['nodes']:
#         cur_tournament = {
#             'id': node['id'],
#             'name': node['name'],
#             'slug': node['slug'].split('/')[-1],
#             'entrants': node['numAttendees'],
#             'state': node['addrState'], 'city': node['city'],
#             'startTimestamp': node['startAt'],
#             'endTimestamp': node['endAt']
#         }
#         # TODO: IMPLEMENT THIS ONCE I ACTUALLY UNDERSTAND HOW STATE WORKS
#         # if node['state'] == 3:
#         #     cur_tournament['completed'] = True
#         # else:
#         #     cur_tournament['completed'] = False
#
#         tournaments.append(cur_tournament)
#
#     return tournaments
#
# GET_BY_STATE_QUERY = """query TournamentsByState($state: String!, $page: Int!) {
#   tournaments(query: {
#     perPage: 32
#     page: $page
#     filter: {
#       addrState: $state
#     }
#   }) {
#     nodes {
#       id
#       name
#       slug
#       numAttendees
#       city
#       startAt
#       endAt
#       state
#     }
#   }
# }"""
#
# # Filter for the get_by_state function
# def get_by_state_filter(response):
#     if response['data']['tournaments'] is None:
#         return None
#
#     if response['data']['tournaments']['nodes'] is None:
#         return None
#
#     tournaments = []
#
#     for node in response['data']['tournaments']['nodes']:
#         cur_tournament = {
#             'id': node['id'],
#             'name': node['name'],
#             'slug': node['slug'].split('/')[-1],
#             'entrants': node['numAttendees'],
#             'city': node['city'],
#             'startTimestamp': node['startAt'],
#             'endTimestamp': node['endAt']
#         }
#         # TODO: IMPLEMENT THIS ONCE I ACTUALLY UNDERSTAND HOW STATE WORKS
#         # if node['state'] == 3:
#         #     cur_tournament['completed'] = True
#         # else:
#         #     cur_tournament['completed'] = False
#
#         tournaments.append(cur_tournament)
#
#     return tournaments
#
# GET_BY_RADIUS_QUERY = """query ($page: Int, $coordinates: String!, $radius: String!) {
#   tournaments(query: {
#     page: $page
#     perPage: 32
#     filter: {
#       location: {
#         distanceFrom: $coordinates,
#         distance: $radius
#       }
#     }
#   }) {
#     nodes {
#       id
#       name
#       slug
#       numAttendees
#       countryCode
#       addrState
#       city
#       startAt
#       endAt
#       state
#     }
#   }
# }"""
#
# def get_by_radius_filter(response):
#     if response['data']['tournaments'] is None:
#         return None
#
#     if response['data']['tournaments']['nodes'] is None:
#         return None
#
#     tournaments = []
#
#     for node in response['data']['tournaments']['nodes']:
#         cur_tournament = {
#             'id': node['id'],
#             'name': node['name'],
#             'slug': node['slug'].split('/')[-1],
#             'entrants': node['numAttendees'],
#             'country': node['countryCode'],
#             'state': node['addrState'],
#             'city': node['city'],
#             'startTimestamp': node['startAt'],
#             'endTimestamp': node['endAt']
#         }
#
#         tournaments.append(cur_tournament)
#
#     return tournaments
#
# GET_PLAYERS_BY_SPONSOR = """query ($slug:String!, $sponsor: String!) {
#   tournament(slug: $slug) {
#     participants(query: {
#       filter: {
#         search: {
#           fieldsToSearch: ["prefix"],
#           searchString: $sponsor
#         }
#       }
#     }) {
#       nodes {
#         id
#         gamerTag
#         user {
#           name
#           location {
#             country
#             state
#             city
#           }
#           player {
#             id
#           }
#         }
#       }
#     }
#   }
# }"""
#
# def get_players_by_sponsor_filter(response):
#     if response['data']['tournament'] is None:
#         return None
#
#     if response['data']['tournament']['participants']['nodes'] is None:
#         return None
#
#     players = []
#
#     for node in response['data']['tournament']['participants']['nodes']:
#         cur_player = {'tag': node['gamerTag']}
#         if node['user'] is not None:
#             cur_player['playerId'] = response['user']['player']['id']
#             cur_player['name'] = response['user']['name']
#             cur_player['country'] = response['user']['location']['country']
#             cur_player['state'] = response['user']['location']['state']
#             cur_player['city'] = response['user']['location']['city']
#
#         players.append(cur_player)
#
#     return players
#
# GET_BY_OWNER_QUERY = """query TournamentsByOwner($ownerId: ID!, $page: Int!) {
#     tournaments(query: {
#       perPage: 25,
#       page: $page,
#       filter: { ownerId: $ownerId }
#     }) {
#     nodes {
#       id
#       name
#       slug
# 	  numAttendees
#       countryCode
#       addrState
#       city
#       startAt
#       endAt
#       state
#     }
#   }
# }
# """
#
# def get_by_owner_filter(response):
#     if response['data']['tournaments'] is None:
#         return None
#
#     if response['data']['tournaments']['nodes'] is None:
#         return None
#
#     tournaments = []
#
#     for node in response['data']['tournaments']['nodes']:
#         cur_tournament = {
#             'id': node['id'],
#             'name': node['name'],
#             'slug': node['slug'].split('/')[-1],
#             'entrants': node['numAttendees'],
#             'country': node['countryCode'],
#             'state': node['addrState'],
#             'city': node['city'],
#             'startTimestamp': node['startAt'],
#             'endTimestamp': node['endAt']
#         }
#
#         tournaments.append(cur_tournament)
#
#     return tournaments