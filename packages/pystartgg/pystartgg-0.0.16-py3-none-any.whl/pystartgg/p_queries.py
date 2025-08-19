# Queries for players.py
PLAYER_GET_INFO_QUERY = """query ($playerId: ID!) {
  player(id: $playerId) {
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
} """

# Filter for the get_info function
def player_get_info_filter(response):
    if response['data']['player'] is None:
        return None
    if response['data']['player']['user'] is None:
        return None

    p = response['data']['player']
    player = {
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
    if player['prefix'] == '':
        player['prefix'] = None

    # Deals with private users
    if p['user'] is not None:
        player.update({
            'discriminator': p['user']['discriminator'],
            'name': p['user']['name'],
            'pronoun': p['user']['genderPronoun'],
        })
        # Update if user has location
        if p['user']['location'] is not None:
            player.update({
                'country': p['user']['location']['country'],
                'state': p['user']['location']['state'],
                'city': p['user']['location']['city'],
            })
    return player

# ORIG

# PLAYER_SHOW_TOURNAMENTS_QUERY = """query ($playerId: ID!, $page: Int!) {
#   player (id: $playerId) {
#     user {
#       tournaments (query: {perPage: 64, page: $page}) {
#         nodes {
#           name
#           slug
#           id
#           numAttendees
#           countryCode
#           startAt
#         }
#       }
#     }
#   }
# }"""
#
# # Filter for the get_tournaments function
# def player_show_tournaments_filter(response):
#     if response['data']['player'] is None:
#         return None
#     if response['data']['player']['user']['tournaments']['nodes'] is None:
#         return None
#
#     tournaments = []
#
#     for node in response['data']['player']['user']['tournaments']['nodes']:
#         cur_tournament = {
#             'name': node['name'],
#             'slug': node['slug'].split('/')[-1],
#             'id': node['id'],
#             'attendees': node['numAttendees'],
#             'country': node['countryCode'],
#             'unixTimestamp': node['startAt']
#         }
#
#         tournaments.append(cur_tournament)
#
#     return tournaments
#
# PLAYER_SHOW_TOURNAMENTS_FOR_GAME_QUERY = """query ($playerId: ID!, $playerName: String!, $videogameId: [ID!], $page: Int!) {
#   player (id: $playerId) {
#     user {
#       tournaments (query: {perPage: 25, page: $page, filter: {videogameId: $videogameId}}) {
#         nodes {
#           name
#           slug
#           id
#           numAttendees
#           countryCode
#           startAt
#           events {
#             name
#             id
#             slug
#             numEntrants
#             videogame {
#               id
#             }
#             entrants (query: {filter: {name: $playerName}}) {
#               nodes {
#                 id
#               }
#             }
#           }
#         }
#       }
#     }
#   }
# }"""
#
# # Filter for the show_tournaments_for_game function
# def player_show_tournaments_for_game(response, videogame_id):
#     if response['data']['player'] is None:
#         return None
#     if response['data']['player']['user']['tournaments']['nodes'] is None:
#         return None
#
#     tournaments = []
#
#     # This is really janky code because of the really janky query
#     # that I had to submit, but it works! Looking for a better way to make this query still
#     for node in response['data']['player']['user']['tournaments']['nodes']:
#         for event in node['events']:
#             if event['videogame']['id'] == videogame_id and event['entrants']['nodes'] is not None:
#                 cur_tournament = {
#                     'name': node['name'],
#                     'slug': node['slug'].split('/')[-1],
#                     'id': node['id'],
#                     'attendees': node['numAttendees'],
#                     'country': node['countryCode'],
#                     'startTimestamp': node['startAt'],
#                     'eventName': event['name'],
#                     'eventSlug': event['slug'].split('/')[-1],
#                     'eventId': event['id'],
#                     'eventEntrants': event['numEntrants']
#                 }
#
#                 tournaments.append(cur_tournament)
#
#     return tournaments