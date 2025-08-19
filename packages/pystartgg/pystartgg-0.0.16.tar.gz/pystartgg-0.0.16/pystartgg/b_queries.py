# TODO: implement bracket. Could be relevant for majors with multiple waves
#  or with unique formats (think Socal Star League). However, all the
#  available endpoints appear to be covered by event and tournament for
#  the purposes of this app.

# Queries for brackets.py

BRACKET_SHOW_ENTRANTS_QUERY = """query ($phaseGroupId: ID!, $page: Int!) {
  phaseGroup(id: $phaseGroupId) {
    id
    seeds (query: {page: $page, perPage: 32}) {
      nodes {
        seedNum
        placement
        entrant {
          id
          name
          participants {
            player {
              id
              gamerTag
            }
          }
        }
      }
    }
  }
}"""


# Filter for the show_entrants function
def bracket_show_entrants_filter(response):
    if response['data']['phaseGroup'] is None:
        return None

    if response['data']['phaseGroup']['seeds']['nodes'] is None:
        return None

    entrants = []  # Need for return at the end

    for node in response['data']['phaseGroup']['seeds']['nodes']:
        cur_entrant = {
            'entrantId': node['entrant']['id'],
            'tag': node['entrant']['name'],
            'finalPlacement': node['placement'],
            'seed': node['seedNum']
        }

        players = []
        for user in node['entrant']['participants']:
            cur_player = {
                'playerId': user['player']['id'],
                'playerTag': user['player']['gamerTag']
            }
            players.append(cur_player)
        cur_entrant['entrantPlayers'] = players

        entrants.append(cur_entrant)

    return entrants

BRACKET_SHOW_SETS_QUERY = """query PhaseGroupSets($phaseGroupId: ID!, $page:Int!){
  phaseGroup(id:$phaseGroupId){
    phase {
      name
    }
    sets(
      page: $page
      perPage: 32
    ){
      nodes{
        id
        slots{
          entrant{
            id
            name
            participants {
              player {
                id
                gamerTag
              }
            }
          }
          standing {
            placement
            stats {
              score {
                value
              }
            }
          }
        }
      }
    }
  }
}"""

# Filter for the show_sets function
def bracket_show_sets_filter(response):
    if response['data']['phaseGroup'] is None:
        return None

    if response['data']['phaseGroup']['sets']['nodes'] is None:
        return None

    bracket_name = response['data']['phaseGroup']['phase']['name']
    sets = []  # Need for return at the end

    for node in response['data']['phaseGroup']['sets']['nodes']:
        cur_set = {
            'id': node['id'],
            'entrant1Id': node['slots'][0]['entrant']['id'],
            'entrant2Id': node['slots'][1]['entrant']['id'],
            'entrant1Name': node['slots'][0]['entrant']['name'],
            'entrant2Name': node['slots'][1]['entrant']['name']
        }

        # Next 2 if/else blocks make sure there's a result in, sometimes DQs are weird
        match_done = True
        if node['slots'][0]['standing'] is None:
            cur_set['entrant1Score'] = -1
            match_done = False
        elif node['slots'][0]['standing']['stats']['score']['value'] is not None:
            cur_set['entrant1Score'] = node['slots'][0]['standing']['stats']['score']['value']
        else:
            cur_set['entrant1Score'] = -1

        if node['slots'][0]['standing'] is None:
            cur_set['entrant2Score'] = -1
            match_done = False
        elif node['slots'][1]['standing']['stats']['score']['value'] is not None:
            cur_set['entrant2Score'] = node['slots'][1]['standing']['stats']['score']['value']
        else:
            cur_set['entrant2Score'] = -1

        # Determining winner/loser (elif because sometimes smashgg won't give us one)
        if match_done:
            cur_set['completed'] = True
            if node['slots'][0]['standing']['placement'] == 1:
                cur_set['winnerId'] = cur_set['entrant1Id']
                cur_set['loserId'] = cur_set['entrant2Id']
                cur_set['winnerName'] = cur_set['entrant1Name']
                cur_set['loserName'] = cur_set['entrant2Name']
            elif node['slots'][0]['standing']['placement'] == 2:
                cur_set['winnerId'] = cur_set['entrant2Id']
                cur_set['loserId'] = cur_set['entrant1Id']
                cur_set['winnerName'] = cur_set['entrant2Name']
                cur_set['loserName'] = cur_set['entrant1Name']
        else:
            cur_set['completed'] = False

        cur_set['bracketName'] = bracket_name

        for j in range(0, 2):
            players = []
            for user in node['slots'][j]['entrant']['participants']:
                cur_player = {'playerId': user['player']['id'], 'playerTag': user['player']['gamerTag']}
                players.append(cur_player)

            cur_set['entrant' + str(j + 1) + 'Players'] = players

        sets.append(cur_set)  # Adding that specific set onto the large list of sets

    return sets