# TODO: implement league. Not a priority

# Queries for leagues.py
SHOW_QUERY = """query ($slug: String!){
  league(slug: $slug) {
    id
    name
    startAt
    endAt
    videogames {
      displayName
      id
    }
  }
}"""

# Filter for the show function
def league_show_filter(response):
    if response['data']['league'] is None:
        return None

    data = {
        'id': response['data']['league']['id'],
        'name': response['data']['league']['name'],
        'startTimestamp': response['data']['league']['startAt'],
        'endTimestamp': response['data']['league']['endAt'],
        'games': response['data']['league']['videogames']
    }

    return data

SHOW_SCHEDULE_QUERY = """query LeagueSchedule ($slug: String!, $page: Int!){
  league(slug: $slug) {
    id
    name
    events(query: {
      page: $page,
      perPage: 20
    }) {
      nodes {
        id
        name
        slug
        startAt
        numEntrants
        tournament {
          id
          name
          slug
        }
      }
    }
  }
}"""


# Filter for the show_schedule function
def league_show_schedule_filter(response):
    if response['data']['league'] is None:
        return None

    if response['data']['league']['events']['nodes'] is None:
        return None

    events = []

    for node in response['data']['league']['events']['nodes']:
        cur_event = {
            'eventId': node['id'],
            'eventName': node['name'],
            'eventSlug': node['slug'].split('/')[-1],
            'eventStartTimestamp': node['startAt'],
            'eventEntrants': node['numEntrants'],
            'tournamentId': node['tournament']['id'],
            'tournamentName': node['tournament']['name'],
            'tournamentSlug': node['tournament']['slug'].split('/')[-1]
        }

        events.append(cur_event)

    return events

SHOW_STANDINGS_QUERY = """query LeagueStandings ($slug: String!, $page: Int!){
  league(slug: $slug) {
    standings (query: {
      page: $page,
      perPage: 25
    }) {
      nodes {
        id
        placement
        player {
          id
          gamerTag
        }
      }
    }
  }
}"""

# Filter for the show_standings function
def league_show_standings_filter(response):
    if response['data']['league'] is None:
        return None

    if response['data']['league']['standings']['nodes'] is None:
        return None

    players = []

    for node in response['data']['league']['standings']['nodes']:
        cur_player = {'id': node['id'], 'standing': node['placement']}
        if node['player'] is not None: # Smashgg is weird sometimes
            cur_player['name'] = node['player']['gamerTag']
            cur_player['playerId'] = node['player']['id']
        else:
            cur_player['name'] = "smashgg has a bug, ignore this one and playerId please -- very sorry"
            cur_player['playerId'] = None
        players.append(cur_player)

    return players