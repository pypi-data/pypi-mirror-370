GET_SETS_QUERY = """
query EventSets($eventId: ID!, $page: Int!, $perPage: Int!) {
  event(id: $eventId) {
    id
    sets(page: $page, perPage: $perPage, sortType: STANDARD) {
      nodes {
        id
        state
        winnerId

        games {
          id
          orderNum
          winnerId
          entrant1Score
          entrant2Score
          stage{
            name
          }
          selections {
            selectionValue
            character{
              name
            }
            entrant {
              id
            }
          }
        }

        slots {
          standing {
            stats {
              score {
                value
              }
            }
          }
          entrant {
            id
            participants {
              player {
                id
              }
            }
          }
        }

      }
    }
  }
}
"""

# Filter for the get_sets function
def get_sets_filter(response):
    if response['data'] is None:
        return None

    event_id = response['data']['event']['id']
    sets = response['data']['event']['sets']['nodes']
    return_sets = []
    return_games = []
    for s in sets:
        # No entrants in set
        if s['slots'][0]['entrant'] is None and s['slots'][1]['entrant'] is None:
            continue

        curr_set = {'id': s['id'], 'state': s['state'], 'eventId': event_id}

        if s['slots'][0]['entrant'] is None:
            curr_set['p1id'] = None
            curr_set['score1'] = 0
        else:
            p1 = s['slots'][0]['entrant']['participants'][0]['player']
            curr_set['p1id'] = p1['id']
            if s['slots'][0]['standing'] is not None:
                curr_set['score1'] = s['slots'][0]['standing']['stats']['score']['value']
            else:
                curr_set['score1'] = 0

        if s['slots'][1]['entrant'] is None:
            curr_set['p2id'] = None
            curr_set['score2'] = 0
        else:
            p2 = s['slots'][1]['entrant']['participants'][0]['player']
            curr_set['p2id'] = p2['id']
            if s['slots'][1]['standing'] is not None:
                curr_set['score2'] = s['slots'][1]['standing']['stats']['score']['value']
            else:
                curr_set['score2'] = 0

        curr_set['win1'] = curr_set['score1'] > curr_set['score2']
        curr_set['win2'] = curr_set['score1'] < curr_set['score2']
        curr_set['hasDQ'] = (curr_set['score1'] == -1) or (curr_set['score2'] == -1)

        return_sets.append(curr_set)

        if s['games'] is not None:
            games = s['games']
            for game in games:
                g = {
                    'id': game['id'],
                    'setId': s['id'],
                    'orderNum': game['orderNum'],
                    'score1': game['entrant1Score'],
                    'score2': game['entrant2Score'],
                    'stage': game['stage']['name'],
                    'character1': game['selections'][0]['character']['name'],
                    'character2': game['selections'][1]['character']['name'],
                }
                entrant1 = game['selections'][0]['entrant']['id']
                if entrant1 == s['slots'][0]['entrant']['id']:
                    g['p1id'] = curr_set['p1id']
                    g['p2id'] = curr_set['p2id']
                else:
                    g['p1id'] = curr_set['p2id']
                    g['p2id'] = curr_set['p1id']

                return_games.append(g)

    return return_sets, return_games

GET_PLACEMENTS_QUERY = '''
query EventStandings($eventId: ID!, $page: Int!, $perPage: Int!) {
  event(id: $eventId) {
    id
    name
    standings(query: {
      perPage: $perPage,
      page: $page}){
      nodes {
        placement
        entrant {
          initialSeedNum
          participants {
            player {
              id
            }
          }
        }
      }
    }
  }
}
'''

def get_placements_filter(response):
    if response['data'] is None:
        return None

    event_id = response['data']['event']['id']
    placements = response['data']['event']['standings']['nodes']
    return_placements = []
    for placement in placements:
        curr_ent = {
            'eventId': event_id,
            'playerId': placement['entrant']['participants'][0]['player']['id'],
            'placement': placement['placement'],
            'initialSeedNum': placement['entrant']['initialSeedNum']
        }
        return_placements.append(curr_ent)

    return return_placements

GET_PLAYERS_QUERY = """
query EventEntrants($eventId: ID!, $page: Int!, $perPage: Int!) {
  event(id: $eventId) {
    id
    entrants(query: {
      perPage: $perPage,
      page: $page}){
      nodes {
        participants {
          player {
            id
            prefix
            gamerTag
            user {
              id
              discriminator
              name
              genderPronoun
              location {
                country
                state
                city
              }
            }
          }
        }
      }
    }
  }
}
"""

def get_players_filter(response):
    if response['data'] is None:
        return None
    if response['data']['event'] is None:
        return None


    players = response['data']['event']['entrants']['nodes']
    return_players = []
    for player in players:
        p = player['participants'][0]['player']
        try:
            curr_player = {
                'id': p['id'],
                'prefix': p['prefix'],
                'gamerTag': p['gamerTag'],
                'discriminator': None,
                'name': None,
                'pronoun': None,
                'country': None,
                'state': None,
                'city': None,
            }
            if curr_player['prefix'] == '':
                curr_player['prefix'] = None

            # Deals with private users
            if p['user'] is not None:
                curr_player.update({
                    'discriminator': p['user']['discriminator'],
                    'name': p['user']['name'],
                    'pronoun': p['user']['genderPronoun'],
                })
                # Update if user has location
                if p['user']['location'] is not None:
                    curr_player.update({
                        'country': p['user']['location']['country'],
                        'state': p['user']['location']['state'],
                        'city': p['user']['location']['city'],
                    })

        except TypeError as err:
            print(player)
            raise err
        return_players.append(curr_player)

    return return_players



# ORIG

# # Queries for events.py
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
# SHOW_SETS_QUERY = """query EventSets($eventId: ID!, $page: Int!) {
#   event(id: $eventId) {
#     tournament {
#       id
#       name
#     }
#     name
#     sets(page: $page, perPage: 18, sortType: STANDARD) {
#       nodes {
#         fullRoundText
#         games {
#           winnerId
#           selections {
#             selectionValue
#             entrant {
#               id
#             }
#           }
#         }
#         id
#         slots {
#           standing {
#             id
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
#             participants {
#               entrants {
#                 id
#               }
#               player {
#                 id
#                 gamerTag
#
#               }
#             }
#           }
#         }
#         phaseGroup {
#           id
#           phase {
#             name
#           }
#         }
#       }
#     }
#   }
# }"""
#
#
# def show_sets_filter(response):
#     if 'data' not in response:
#         return None
#     if response['data']['event'] is None:
#         return None
#
#     if response['data']['event']['sets']['nodes'] is None:
#         return None
#
#     sets = []  # Need for return at the end
#
#     for node in response['data']['event']['sets']['nodes']:
#         if len(node['slots']) < 2:
#             continue  # This fixes a bug where player doesn't have an opponent
#         if (node['slots'][0]['entrant'] is None) or (node['slots'][1]['entrant'] is None):
#             continue  # This fixes a bug when tournament ends early
#
#         cur_set = {
#             'id': node['id'],
#             'entrant1Id': node['slots'][0]['entrant']['id'],
#             'entrant2Id': node['slots'][1]['entrant']['id'],
#             'entrant1Name': node['slots'][0]['entrant']['name'],
#             'entrant2Name': node['slots'][1]['entrant']['name']
#         }
#
#         if node['games'] is not None:
#             entrant1_chars = []
#             entrant2_chars = []
#             game_winners_ids = []
#             for game in node['games']:
#                 if game['selections'] is None:  # This fixes an issue with selections being none while games are reported
#                     continue
#                 elif node['slots'][0]['entrant']['id'] == game['selections'][0]['entrant']['id']:
#                     entrant1_chars.append(game['selections'][0]['selectionValue'])
#                     if len(game['selections']) > 1:
#                         entrant2_chars.append(game['selections'][1]['selectionValue'])
#                 else:
#                     entrant2_chars.append(game['selections'][0]['selectionValue'])
#                     if len(game['selections']) > 1:
#                         entrant1_chars.append(game['selections'][1]['selectionValue'])
#
#                 game_winners_ids.append(game['winnerId'])
#
#             cur_set['entrant1Chars'] = entrant1_chars
#             cur_set['entrant2Chars'] = entrant2_chars
#             cur_set['gameWinners'] = game_winners_ids
#
#         # Next 2 if/else blocks make sure there's a result in, sometimes DQs are weird
#         # there also could be ongoing matches
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
#         # Determining winner/loser (elif because sometimes smashgg won't give us one)
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
#         cur_set['fullRoundText'] = node['fullRoundText']
#
#         if node['phaseGroup'] is not None:
#             cur_set['bracketName'] = node['phaseGroup']['phase']['name']
#             cur_set['bracketId'] = node['phaseGroup']['id']
#         else:
#             cur_set['bracketName'] = None
#             cur_set['bracketId'] = None
#
#         # This gives player_ids, but it also is made to work with team events
#         for j in range(0, 2):
#             players = []
#             for user in node['slots'][j]['entrant']['participants']:
#                 cur_player = {}
#                 if user['player'] is not None:
#                     cur_player['playerId'] = user['player']['id']
#                     cur_player['playerTag'] = user['player']['gamerTag']
#                     if user['entrants'] is not None:
#                         cur_player['entrantId'] = user['entrants'][0]['id']
#                     else:
#                         cur_player['entrantId'] = node['slots'][j]['entrant']['id']
#                     players.append(cur_player)
#                 else:
#                     cur_player['playerId'] = None
#                     cur_player['playerTag'] = None
#                     cur_player['entrantId'] = node['slots'][j]['entrant']['id']
#
#             cur_set['entrant' + str(j + 1) + 'Players'] = players
#
#         sets.append(cur_set)  # Adding that specific set onto the large list of sets
#
#     return sets
#
#
# SHOW_ENTRANTS_QUERY = """query EventStandings($eventId: ID!, $page: Int!) {
#   event(id: $eventId) {
#     id
#     name
#     standings(query: {
#       perPage: 24,
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
# # Filters for the show_players function
# def show_entrants_filter(response):
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
# SHOW_ENTRANT_SETS_QUERY = """query EventSets($eventId: ID!, $entrantId: ID!, $page: Int!) {
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
# # Filter for the show_player_sets function
# def show_entrant_sets_filter(response):
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
#         # Determining winner/loser (elif because sometimes smashgg won't give us one)
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
# # Filter for the show_head_to_head function
# def show_head_to_head_filter(response, player2_name):
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
#             # Determining winner/loser (elif because sometimes smashgg won't give us one)
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
# SHOW_LIGHTWEIGHT_RESULTS_QUERY = """query EventStandings($eventId: ID!, $page: Int!,) {
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
# # Filter for the show_lightweight_results function
# def show_lightweight_results_filter(response):
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