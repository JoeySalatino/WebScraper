#!/usr/bin/env python3
"""Pulls the current point spread and over/under for every game on
ESPN's scoreboard for each league asked for.
"""

import concurrent.futures
import itertools
import sys
import time

import requests

URL = 'https://site.api.espn.com/apis/site/v2/sports/{}/scoreboard'

leagues = {
    'nfl':   'football/nfl',
    'ncaaf': 'football/college-football',
    'nba':   'basketball/nba',
    'ncaab': 'basketball/mens-college-basketball',
    'nhl':   'hockey/nhl',
    'mlb':   'baseball/mlb',
}


def fetch_league(league):
    ''' Download the scoreboard for one league and return league, events. '''
    response = requests.get(URL.format(leagues[league]), timeout=10)
    response.raise_for_status()
    return league, response.json().get('events', [])


def parse_event(league, event):
    ''' Turn one ESPN event into a dict with the betting info. '''
    competition = event['competitions'][0]
    odds = (competition.get('odds') or [{}])[0]
    return {
        'league':     league.upper(),
        'game':       event.get('shortName', '?'),
        'line':       odds.get('details', 'N/A'),
        'over_under': odds.get('overUnder', 'N/A'),
    }


def parse_league(result):
    ''' Parse every event in a league, events pair. '''
    league, events = result
    return map(lambda event: parse_event(league, event), events)


def has_odds(game):
    return game['line'] != 'N/A'


def format_game(game):
    return f"{game['league']:<6} {game['game']:<14} {game['line']:<14} {game['over_under']}"


def scrape(leagues, workers):
    ''' Fetch leagues concurrently and return a list of games with odds. '''
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(fetch_league, leagues)
        games   = itertools.chain.from_iterable(map(parse_league, results))
        return list(filter(has_odds, games))


def usage(status=0):
    print(f'''Usage: {sys.argv[0]} [-w WORKERS] [leagues...]

    -w WORKERS  Number of concurrent workers (default: 1)

Leagues: {', '.join(leagues)} (default: all)''')
    sys.exit(status)


def main():
    arguments = sys.argv[1:]
    workers   = 1
    leagues_list   = []

    while arguments:
        argument = arguments.pop(0)
        if argument == '-w':
            workers = int(arguments.pop(0))
        elif argument == '-h':
            usage(0)
        elif argument in LEAGUES:
            leagues.append(argument)
        else:
            usage(1)

    leagues_list = leagues or list(leagues)

    start = time.time()
    games = scrape(leagues_list, workers)
    elapsed = time.time() - start

    print(f"{'LEAGUE':<6} {'GAME':<14} {'LINE':<14} O/U")
    print('\n'.join(map(format_game, games)))
    print(f'\n{len(games)} games with odds: {workers} worker(s): {elapsed:.2f}s',
          file=sys.stderr)


if __name__ == '__main__':
    main()
