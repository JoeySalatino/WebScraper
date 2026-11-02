Sports Betting Odds Scraper

This is a python scraper that pulls the current point spread and over/under for every game on ESPN's scoreboard website across many different leagues (NFL, College Football, NBA, College Basketball, NHL, MLB).


Usage

In order to scrape every league with one worker run:
	./scrape.py
In order to scrape every league with 6 concurrent workers run:
	./scrape.py -w 6
In order to scrape a/multiple specific leagues run:
	./scrape.py nfl nba -w 2
The options:
	Usage: ./scraper.py [-w WORKERS] [LEAGUES...]
 
        -w WORKERS  Number of concurrent workers (default: 1)
 
    	Leagues: nfl, ncaaf, nba, ncaab, nhl, mlb (default: all)

Example output:
 
    LEAGUE GAME           LINE           O/U
    NFL    DAL @ NYG      DAL -3.5       44.5
    NBA    BOS @ MIA      BOS -6.5       214.5
    ...
    14 games with odds | 6 worker(s) | 0.41s


Performance:

Workers: 1
Time(s): 0.42

Workers: 6
Time(s); 0.10


concurrent.futures:

Each league is a seperate HTTP request, and most of the time is spent waiting on the network. With one worker, each request happens one after another, so the total time is all six added up. With a ThreadPoolExecutor and six workers, all six requests are working at the same time, so the total time is the slowest request. Thats why the 6 worker run is much faster. 


Functional Programming:
By itself, functional programming doesnt make the scraper any faster; map and filter are about the same as a regular loop. The benefit is that each step is its own pure function with no shared states. This makes concurrency easy: no thread is ever touching anything that another thread is also touching. Since map and filter are iterators this is lazy, so nothing is copied into the lists until the very end. 
