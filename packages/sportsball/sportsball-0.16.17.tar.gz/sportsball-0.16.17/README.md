# sportsball

<a href="https://pypi.org/project/sportsball/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/sportsball">
</a>

A library for pulling in and normalising sports stats.

<p align="center">
    <img src="sportsball.png" alt="sportsball" width="200"/>
</p>

## Dependencies :globe_with_meridians:

Python 3.11.6:

- [pandas](https://pandas.pydata.org/)
- [requests](https://requests.readthedocs.io/en/latest/)
- [requests-cache](https://requests-cache.readthedocs.io/en/stable/)
- [python-dateutil](https://github.com/dateutil/dateutil)
- [tqdm](https://github.com/tqdm/tqdm)
- [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/)
- [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
- [joblib](https://joblib.readthedocs.io/en/stable/)
- [pyarrow](https://arrow.apache.org/docs/python/index.html)
- [ipython](https://ipython.org/)
- [pytz](https://pythonhosted.org/pytz/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [geocoder](https://geocoder.readthedocs.io/)
- [retry-requests](https://github.com/bustawin/retry-requests)
- [timezonefinder](https://timezonefinder.michelfe.it/gui)
- [nba_api](https://github.com/swar/nba_api)
- [pydantic](https://docs.pydantic.dev/latest/)
- [flatten_json](https://github.com/amirziai/flatten)
- [pygooglenews](https://github.com/kotartemiy/pygooglenews)
- [extruct](https://github.com/scrapinghub/extruct)
- [wikipedia-api](https://github.com/martin-majlis/Wikipedia-API)
- [tweepy](https://www.tweepy.org/)
- [pytest-is-running](https://github.com/adamchainz/pytest-is-running)
- [PySocks](https://github.com/Anorov/PySocks)
- [func-timeout](https://github.com/kata198/func_timeout)
- [tenacity](https://github.com/jd/tenacity)
- [random_user_agent](https://github.com/Luqman-Ud-Din/random_user_agent)
- [wayback](https://github.com/edgi-govdata-archiving/wayback)
- [cryptography](https://cryptography.io/en/latest/)
- [feedparser](https://github.com/kurtmckee/feedparser)
- [dateparser](https://dateparser.readthedocs.io/en/latest/)
- [playwright](https://playwright.dev/)
- [cchardet](https://github.com/PyYoshi/cChardet)
- [lxml](https://lxml.de/)
- [gender-guesser](https://github.com/lead-ratings/gender-guesser)
- [scrapesession](https://github.com/8W9aG/scrapesession)
- [pyhigh](https://github.com/sgherbst/pyhigh)
- [datefinder](https://github.com/akoumjian/datefinder)

## Raison D'être :thought_balloon:

`sportsball` aims to be a library for pulling in historical information about previous sporting games in a standardised fashion for easy data processing.
The models it uses are designed to be used for many different types of sports.

The supported leagues are:

* 🏉 [AFL](https://www.afl.com.au/)
* 🎾 [ATP](https://www.atptour.com/en)
* ⚽ [EPL](https://www.premierleague.com/ens)
* ⚽ [FIFA](https://www.fifa.com/en)
* 🐎 [HKJC](https://www.hkjc.com/home/english/index.aspx)
* 🏏 [IPL](https://www.iplt20.com/)
* ⚾ [MLB](https://www.mlb.com/)
* 🏀 [NBA](https://www.nba.com/)
* 🏀 [NCAAB](https://www.ncaa.com/sports/basketball-men/d1)
* 🏈 [NCAAF](https://www.ncaa.com/sports/football/fbs)
* 🏈 [NFL](https://www.nfl.com/)
* 🏒 [NHL](https://www.nhl.com/)

## Architecture :triangular_ruler:

`sportsball` is an object orientated library. The entities are organised like so:

* **Game**: A game within a season.
    * **Team**: The team within the game. Note that in games with individual players a team exists as a wrapper.
        * **Player**: A player within the team.
            * **Address**: The address information of a players birth.
            * **Owner**: The owner of the player.
            * **Venue**: The college of the player.
        * **Odds**: The odds for the team to win the game.
            * **Bookie**: The bookie publishing the odds.
        * **News**: News about the team the day before the game.
        * **Social**: Social posts from the team the day before the game.
        * **Coach**: A coach for the team.
    * **Venue**: The venue the game was played in.
        * **Address**: The address information of a venue.
            * **Weather**: The weather at the address.
    * **Dividend**: The dividends the game pays out.
    * **Umpire**: The umpires adjudicating the game.

### Objects

A list of the attributes on each object.

#### Game

A representation of the game within a season.

* **dt**: The timezone aware date/time of the game start.
* **week**: The round of the game within the season.
* **game_number**: The index of the game within the round.
* **venue**: The venue the game took place at.
* **teams**: A list of teams within the game.
* **home_team**: The team representing the home team.
* **away_team**: The ream representing the away team.
* **end_dt**: The timzone aware date/time of the game end.
* **attendance**: How many people attended the game.
* **league**: The league the game belongs to.
* **year** The year the game was in.
* **season_type**: The type of the season the game was played in.
* **postponed**: Whether the game was postponed.
* **playoff**: Whether the game was a playoff game.
* **distance**: The distance the game was played over.
* **version**: The version of the game model.

#### Team

A representation of a team within a game.

* **identifier**: The unique identifier for the team.
* **name**: The name of the team.
* **location**: The home location of the team.
* **players**: A list of players with the team for the game.
* **odds**: A list of odds for the team on the game to win.
* **points**: The amount of points scored by this team on the game.
* **ladder_rank**: The ladder rank of the team at the beginning of the round of the game.
* **kicks**: The number of kicks a team produced.
* **news**: News articles about the team a day from the game.
* **social**: Social media posts from the team a day from the game.
* **field_goals**: The sum of the field goals made by the team in the game.
* **field_goals_attempted**: The sum of the field goals attempted by the team in the game.
* **offensive_rebounds**: The number of rebounds during offense by the team in the game.
* **assists**: The number of times the player on the team made a pass that resulted in a field goal in the game.
* **turnovers**: The number of times a player on the team loses possession of the ball in the game.
* **marks**: The number of times a player on the team marks the ball in the game.
* **handballs**: The number of times a player on the team handballs the ball in the game.
* **disposals**: The number of times a player on the team disposes of the ball in the game.
* **goals**: The number of times a player on the team scored a goal in the game.
* **behinds**: The number of times a player on the team scored a behind in the game.
* **hit_outs**: The number of times a player on the team hit out the ball in the game.
* **tackles**: The number of times a player on the team tackled another player in the game.
* **rebounds**: The number of times a player on the team gets a rebound in the game.
* **insides**: The number of times a player on the team kicks a ball inside 50 in the game.
* **clearances**: The number of times a player on the team performs a clearance in the game.
* **clangers**: The number of times a player on the team performs a clanger in the game.
* **free_kicks_for**: The number of times a player on the team was rewarded a free kick in the game.
* **free_kicks_against**: The number of times a player on the team gave a player on the other team a free kick in the game.
* **brownlow_votes**: The number of times a player on the team was given a brownlow vote in the game.
* **contested_possessions**: The number of times a player on the team got a contested posession in the game.
* **uncontested_possessions**: The number of times a player on the team got an uncontested posession in the game.
* **contested_marks**: The number of times a player on the team got a contested mark in the game.
* **marks_inside**: The number of times a player on the team got a mark inside 50 in the game.
* **one_percenters**: The number of times a player on the team performs a "one-percenter" in the game.
* **bounces**: The number of times a player on the team bounces a ball.
* **goal_assists**: The number of times a player on the team assists another player on the team with a goal in the game.
* **coaches**: The coaches on the team during the game.
* **lbw**: Length behind winner, expressed in metres.
* **dividends**: The dividends the game pays out.
* **field_goals_percentage**: The ratio of field goals scored by field goals attempted by the players on the team in the game.
* **three_point_field_goals**: The number of three point field goals scored by the players on the team in the game.
* **three_point_field_goals_attempted**: The number of three point field goals attempted by the players on the team in the game.
* **three_point_field_goals_percentage**: The ratio of three point field goals scored by the three point field goals attempted by the players on the team in the game.
* **free_throws**: The number of free throws scored by the players on the team in the game.
* **free_throws_attempted**: The number of free throws attempted by the players on the team in the game.
* **free_throws_percentage**: The ratio of free throws scored by the free throws attempted by the players on the team in the game.
* **defensive_rebounds**: The number of defensive rebounds made by the players on the team in the game.
* **total_rebounds**: The number of offensive and defensive rebounds made by the players on the team in the game.
* **steals**: The number of steals made by the players on the team in the game.
* **blocks**: The number of blocks made by the players on the team in the game.
* **personal_fouls**: The number of personal fouls made by the players on the team in the game.
* **version**: The version of the team model.
* **runs**: The total number of runs scored by the batting side so far in the innings.
* **wickets**: The total number of batters dismissed so far in the innings.
* **overs**: The total number of overs (and partial overs) faced so far in the innings, counting only legal deliveries.
* **balls**: The total number of legal deliveries faced so far in the innings.
* **byes**: Runs scored when the ball passes the batter without touching their bat or body, and the batters run or the ball reaches the boundary.
* **leg_byes**: Runs scored when the ball hits the batter’s body (but not the bat or hand holding the bat) and then the batters run or the ball reaches the boundary.
* **wides**: Illegal deliveries bowled too far from the batter to be hit with a normal cricket stroke, resulting in extra runs for the batting side.
* **no_balls**: Illegal deliveries by the bowler that give the batting side extra runs and an extra delivery.
* **penalties**: Extra runs awarded to a team by the umpire for breaches of the Laws of Cricket or playing conditions.
* **balls_per_over**: The number of legal deliveries that make up one over in that match format.
* **fours**: The total number of times batters have hit the ball to the boundary for exactly four runs in that innings, across all players.
* **sixes**: The total number of times batters have hit the ball over the boundary rope on the full, scoring six runs each time, across all players in that innings.
* **catches**: The total number of dismissals in the field where a fielder cleanly catches the ball before it touches the ground, across all players in that innings or match.
* **catches_dropped**: The number of catching opportunities missed by fielders, where the ball could have been caught to dismiss a batter but was not held.

#### Player

A representation of a player within a team within a game.

* **identifier**: The unique identifier for the player.
* **jersey**: The jersey identifying the player.
* **kicks**: The number of kicks the player made in the game.
* **fumbles**: The number of times the player fumbled the ball in the game.
* **fumbles_lost**: The number of times the player loses possession of the ball due to a fumble and the opposing team recovers the ball.
* **field_goals**: The number of field goals the player made in the game.
* **field_goals_attempted**: The number of field goal attempts the player made in the game.
* **offensive_rebounds**: The number of rebounds during offense by the player made in the game.
* **assists**: The number of times the player made a pass that resulted in a field goal in the game.
* **turnovers**: The number of times a player loses possession of the ball in the game.
* **name**: The name of the player.
* **marks**: The number of marks the player performed in the game.
* **handballs**: The number of handballs the player performed in the game.
* **disposals**: The number of disposals the player performed in the game.
* **goals**: The number of goals scored by the player in the game.
* **behinds**: The number of behinds scored by the player in the game.
* **hit_outs**: The number of hit outs scored by the player in the game.
* **tackles**: The number of tackles performed by the player in the game.
* **rebounds**: The number of rebounds performed by the player in the game.
* **insides**: The number of insides performed by the player in the game.
* **clearances**: The number of clearances performed by the player in the game.
* **clangers**: The number of clangers performed by the player in the game.
* **free_kicks_for**: The number of free kicks given to the player in the game.
* **free_kicks_against**: The number of free kicks given against an action taken by the player in the game.
* **brownlow_votes**: The number of votes for the brownlow medal the player has in the current season.
* **contested_possessions**: The number of possessions the player had in the game that were contested.
* **uncontested_possessions**: The number of posessions the player had in the game that were uncontested.
* **contested_marks**: The number of marks the player had in the game that were contested.
* **marks_inside**: The number of marks the player had in the game inside the 50.
* **one_percenters:** The number of times the player spoils, knock-ons, smothers or shepherds the ball during the game.
* **bounces**: The number of bounces the player makes in the game.
* **goal_assists**: The number of assists on goal the player had in the game.
* **percentage_played**: The percentage of the game the player was on the field.
* **birth_date**: The birth date of the player.
* **species**: The species of the player.
* **handicap_weight**: The handicap weight of the player (in KGs).
* **father**: The player representing the father of the player.
* **sex**: The sex of the player.
* **age**: The age of the player in years.
* **starting_position**: The starting position of the player.
* **weight**: The weight of the player (in KGs).
* **birth_address**: The address model for the players birth location.
* **seconds_played**: The amount of seconds the player played the game for.
* **field_goals_percentage**: The ratio of field goals scored by field goals attempted for the player during the game.
* **three_point_field_goals**: The number of three point field goals scored by the player during the game.
* **three_point_field_goals_attempted**: The number of three point field goals attempted by the player during the game.
* **three_point_field_goals_percentage**: The ratio of three point field goals scored by three point field goals attempted by the player during the game.
* **free_throws**: The number of free throws scored by the player during the game.
* **free_throws_attempted**: The number of free throws attempted by the player during the game.
* **free_throws_percentage**: The ratio of free throws scored by free throws attempted by the player during the game.
* **defensive_rebounds**: The number of defensive rebounds made by the player during the game.
* **total_rebounds**: The number of rebounds (both offensive and defensive) made by the player during the game.
* **steals**: The number of steals made by the player during the game.
* **blocks**: The number of blocks made by the player during the game.
* **personal_fouls**: The number of personal fouls made by the player during the game.
* **points**: The points made by the player during the game.
* **game_score**: The [John Hollinger game score](https://www.nbastuffer.com/analytics101/game-score/) of the player during the game.
* **point_differential**: The points scored by the players team while the player was on the court minus the points scored by the opposing team when the player is off the court.
* **version**: The version of the player model.
* **height**: The height of the player in (in CMs).
* **college**: The college the player went to.
* **headshot**: An image URL representing the headshot of the player.
* **forced_fumbles**: The number of forced fumbles made by the player during the game.
* **fumbles_recovered**: The number of fumbles recovered made by the player during the game.
* **fumbles_recovered_yards**: The yards gained during fumbles recovered by the player during the game.
* **fumbles_touchdowns**: The number of fumble touchdowns made by the player during the game.
* **offensive_two_point_returns**: The number of offensive two point returns made by the player during the game.
* **offensive_fumbles_touchdowns**: The number of offensive fumbles touchdowns made by the player during the game.
* **defensive_fumbles_touchdowns**: The number of defensive fumbles touchdowns made by the player during the game.
* **average_gain**: The average number of yards gained by the player during the game.
* **completion_percentage**: The completion percentage of the player during the game.
* **completions**: The number of completions made by the player during the game.
* **espn_quarterback_rating**: The number of ESPN quarterback rating of the player.
* **interception_percentage**: The interception percentage of the player during the game.
* **interceptions**: The number of interceptions made by the player during the game.
* **long_passing**: The number of long passes made by the player during the game.
* **misc_yards**: The miscellaneous yards gained by the player during the game.
* **net_passing_yards**: The total passing yards gained by the player during the game.
* **net_total_yards**: The net total yards gained by the player during the game.
* **passing_attempts**: The number of attempted passes made by the player during the game.
* **passing_big_plays**: The number of passes that led to big plays made by the player during the game.
* **passing_first_downs**: The number of passes first downs made by the player during the game.
* **passing_fumbles**: The number of passing fumbles made by the player during the game.
* **passing_fumbles_lost**: The number of passing fumbles lost by the player during the game.
* **passing_touchdown_percentage**: The percentage of passing touchdowns by the player during the game.
* **passing_touchdowns**: The number of passing touchdowns made by the player during the game.
* **passing_yards**: The yards gained by the player during passing during the game.
* **passing_yards_after_catch**: The yards gained by the player after passing after a catch during the game.
* **passing_yards_at_catch**: The yards gained by the player after passing before a catch during the game.
* **quarterback_rating**: The quarterback rating of the player.
* **sacks**: The number of sacks made by the player during the game.
* **sacks_yards_lost**: The yards lost by the player performing a sack during the game.
* **net_passing_attempts**: The number of passing attempts made by the player during the game.
* **total_offensive_plays**: The number of offensive plays made by the player during the game.
* **total_points**: The number of points made by the player during the game.
* **total_touchdowns**: The number of touchdowns made by the player during the game.
* **total_yards**: The total yards gained by the player during the game.
* **total_yards_from_scrimmage**: The total yards gained by the player from scrimmage during the game.
* **two_point_pass**: The two point passes made by the player during the game.
* **two_point_pass_attempt**: The attempts at two point passes made by the player during the game.
* **yards_per_completion**: The yards gained per completion by the player during the game.
* **yards_per_pass_attempt**: The yards gained per pass attempt by the player during the game.
* **net_yards_per_pass_attempt**: The net number of yards gained per pass attempt by the player during the game.
* **long_rushing**: The long rushes made by the player during the game.
* **rushing_attempts**: The attempted rushes made by the player during the game.
* **rushing_big_plays**: The rushes resulting in big plays made by the player during the game.
* **rushing_first_downs**: The rushing first downs made by the player during the game.
* **rushing_fumbles**: The rushing fumbles made by the player during the game.
* **rushing_fumbles_lost**: The rushing fumbles lost by the player during the game.
* **rushing_touchdowns**: The rushing touchdowns made by the player during the game.
* **rushing_yards**: The yards made by rushing by the player during the game.
* **stuffs**: The stuffs made by the player during the game.
* **stuff_yards_lost**: The yards lost while stuffing by the player during the game.
* **two_point_rush**: The number of two point rushes made by the player during the game.
* **two_point_rush_attempts**: The number of attempted two point rushes made by the player during the game.
* **yards_per_rush_attempt**: The number of yards per rush attempt made by the player during the game.
* **espn_widereceiver**: The ESPN rating for the wide receiver.
* **long_reception**: The number of long receptions made by the player during the game.
* **receiving_big_plays**: The number of receives that resulted in big plays made by the player during the game.
* **receiving_first_downs**: The number of first down receives made by the player during the game.
* **receiving_fumbles**: The number of fumble receives made by the player during the game.
* **receiving_fumbles_lost**: The number of fumble receives lost by the player during the game.
* **receiving_targets**: The number of target receives made by the player during the game.
* **receiving_yards**: The number of yards gained by receives by the player during the game.
* **receiving_yards_after_catch**: The number of yards gained by receives by the player during the game after a catch.
* **receiving_yards_at_catch**: The number of yards gained by the receives by the player during the game at a catch.
* **receptions**: The number of receptions made by the player during the game.
* **two_point_receptions**: The number of two point receptions made by the player during the game.
* **two_point_reception_attempts**: The number of two point reception attempts made by the player during the game.
* **yards_per_reception**: The yards gained on average per reception by the player during the game.
* **assist_tackles**: The number of assist tackles made by the player during the game.
* **average_interception_yards**: The average number of yards gained by an interception made by the player during the game.
* **average_sack_yards**: The average number of yards gained by a sack made by the player during the game.
* **average_stuff_yards**: The average number of yards gained by a stuff made by the player during the game.
* **blocked_field_goal_touchdowns**: The number of blocked field goal touchdowns made by the player during the game.
* **blocked_punt_touchdowns**: The number of blocked punt touchdowns made by the player during the game.
* **defensive_touchdowns**: The number of defensive touchdowns made by the player during the game.
* **hurries**: The number of hurries made by the player during the game.
* **kicks_blocked**: The number of kicks blocked by the player during the game.
* **long_interception**: The number of long interceptions made by the player during the game.
* **misc_touchdowns**: The number of miscellaneous touchdowns made by the player during the game.
* **passes_batted_down**: The number of passes batted down by the player during the game.
* **passes_defended**: The number of passes defended by the player during the game.
* **quarterback_hits**: The number of quarterback hits made by the player during the game.
* **sacks_assisted**: The number of sacks the player assisted with during the game.
* **sacks_unassisted**: The number of sacks the player made unassisted during the game.
* **sacks_yards**: The number of yards gained by the player making a sack during the game.
* **safeties**: The safeties made by the player during the game.
* **solo_tackles**: The number of solo tackles made by the player during the game.
* **stuff_yards**: The yards gained by the stuffs made by the player during the game.
* **tackles_for_loss**: The tackles for losses made by the player during the game.
* **tackles_yards_lost**: The yards lost by tackles made by the player during the game.
* **yards_allowed**: The yards allowed to be gained by the player during the game.
* **points_allowed**: The points allowed to be gained by the player during the game.
* **one_point_safeties_made**: The one point safeties made by the player during the game.
* **missed_field_goal_return_td**: The missed field goal return TD made by the player during the game.
* **blocked_punt_ez_rec_td**: The blocked punt EZ rec TD of the player during the game.
* **interception_touchdowns**: The number of interception touchdowns made by the player during the game.
* **interception_yards**: The number of yards gained by interceptions made by the player during the game.
* **average_kickoff_return_yards**: The average number of kickoff return yards made by the player during the game.
* **average_kickoff_yards**: The average number of kickoff yards made by the player during the game.
* **extra_point_attempts**: The number of extra point attempts made by the player during the game.
* **extra_point_percentage**: The number of extra point percentages made by the player during the game.
* **extra_point_blocked**: The number of extra points blocked by the player during the game.
* **extra_points_blocked_percentage**: The percentage of extra points blocked by the player during the game.
* **extra_points_made**: The number of extra points made by the player during the game.
* **fair_catches**: The number of fair catches made by the player during the game.
* **fair_catch_percentage**: The percentage of fair catches made by the player during the game.
* **field_goal_attempts_max_19_yards**: The field goal attempts between 0-19 yards made by the player during the game.
* **field_goal_attempts_max_29_yards**: The field goal attempts between 19-29 yards made by the player during the game.
* **field_goal_attempts_max_39_yards**: The field goal attempts between 29-39 yards made by the player during the game.
* **field_goal_attempts_max_49_yards**: The field goal attempts between 39-49 yards made by the player during the game.
* **field_goal_attempts_max_59_yards**: The field goal attempts between 49-59 yards made by the player during the game.
* **field_goal_attempts_max_99_yards**: The field goal attempts between 59-99 yards made by the player during the game.
* **field_goal_attempts_above_50_yards**: The field goal attempts above 50 yards made by the player during the game.
* **field_goal_attempt_yards**: The yards gained by field goal attempts made by the player during the game.
* **field_goals_blocked**: The field goals blocked by the player during the game.
* **field_goals_blocked_percentage**: The percentage of field goals made by the player during the game.
* **field_goals_made**: The number of field goals made by the player during the game.
* **field_goals_made_max_19_yards**: The number of field goals made between 0-19 yards by the player during the game.
* **field_goals_made_max_29_yards**: The number of field goals made between 19-29 yards by the player during the game.
* **field_goals_made_max_39_yards**: The number of field goals made between 29-39 yards by the player during the game.
* **field_goals_made_max_49_yards**: The number of field goals made between 39-49 yards by the player during the game.
* **field_goals_made_max_59_yards**: The number of field goals made between 49-59 yards by the player during the game.
* **field_goals_made_max_99_yards**: The number of field goals made between 59-99 yards by the player during the game.
* **field_goals_made_above_50_yards**: The number of field goals made over 50 yards by the player during the game.
* **field_goals_made_yards**: The number of yards gained by field goals made by the player during the game.
* **field_goals_missed_yards**: The number of yards gained by missed field goals made by the player during the game.
* **kickoff_out_of_bounds**: The number of out of bounds kickoffs made by the player during the game.
* **kickoff_returns**: The number of kickoff returns made by the player during the game.
* **kickoff_returns_touchdowns**: The number of kickoff returns touchdowns made by the player during the game.
* **kickoff_return_yards**: The yards gained by kickoff returns made by the player during the game.
* **long_field_goal_attempt**: The number of long field goal attempts made by the player during the game.
* **long_field_goal_made**: The number of long field goals made by the player during the game.
* **long_kickoff**: The number of long kickoffs made by the player during the game.
* **total_kicking_points**: The number of kicking points made by the player during the game.
* **touchback_percentage**: The percentage of touchbacks made by the player during the game.
* **touchbacks**: The touchbacks made by the player during the game.
* **defensive_fumble_returns**: The number of defensive fumble returns made by the player during the game.
* **defensive_fumble_return_yards**: The yards gained by defensive fumble returns made by the player during the game.
* **fumble_recoveries**: The fumble recoveries made by the player during the game.
* **fumble_recovery_yards**: The yards gained by fumble recoveries made by the player during the game.
* **kick_return_fair_catches**: The kick return fair catches made by the player during the game.
* **kick_return_fair_catch_percentage**: The percentage of kick return fair catches made by the player during the game.
* **kick_return_fumbles**: The kick return fumbles made by the player during the game.
* **kick_return_fumbles_lost**: The kick return fumbles lost by the player during the game.
* **kick_returns**: The kick returns made by the player during the game.
* **kick_return_touchdowns**: The kick return touchdowns made by the player during the game.
* **kick_return_yards**: The yards gained by kick returns made by the player during the game.
* **long_kick_return**: The long kick returns made by the player during the game.
* **long_punt_return**: The long punt returns made by the player during the game.
* **misc_fumble_returns**: The miscellaneous fumble returns made by the player during the game.
* **misc_fumble_return_yards**: The yards gained by miscellaneous fumble returns made by the player during the game.
* **opposition_fumble_recoveries**: The opposition fumble recoveries made by the player during the game.
* **opposition_fumble_recovery_yards**: The yards gained by opposition fumble recoveries made by the player during the game.
* **opposition_special_team_fumble_returns**: The opposition special team fumble returns made by the player during the game.
* **opposition_special_team_fumble_return_yards**: The opposition special team fumble return yards made by the player during the game.
* **punt_return_fair_catches**: The number of punt return fair catches made by the player during the game.
* **punt_return_fair_catch_percentage**: The percentage of punt return fair catches made by the player during the game.
* **punt_return_fumbles**: The number of punt return fumbles made by the player during the game.
* **punt_return_fumbles_lost**: The number of punt return fumbles lost by the player during the game.
* **punt_returns**: The number of punt returns made by the player during the game.
* **punt_returns_started_inside_the_10**: The number of punt returns started inside the 10 yard line by the player during the game.
* **punt_returns_started_inside_the_20**: The number of punt returns started inside the 20 yard line by the player during the game.
* **punt_return_touchdowns**: The number of punt return touchdowns made by the player during the game.
* **punt_return_yards**: The yards gained by the player during the game.
* **special_team_fumble_returns**: The special team fumble returns made by the player during the game.
* **yards_per_kick_return**: The yards gained per kick return made by the player during the game.
* **yards_per_punt_return**: The yards gained per punt return made by the player during the game.
* **yards_per_return**: The yards gained per return made by the player during the game.
* **average_punt_return_yards**: The average yards gained per punt return made by the player during the game.
* **fair_catches**: The number of fair catches made by the player during the game.
* **gross_average_punt_yards**: The gross average punt yards made by the player during the game.
* **long_punt**: The long punts made by the player during the game.
* **net_average_punt_yards**: The net average punt yards made by the player during the game.
* **punts**: The punts made by the player during the game.
* **punts_blocked**: The punts blocked made by the player during the game.
* **punts_blocked_percentage**: The percentage of punts blocked by the player during the game.
* **punts_inside_10**: The punts made by the player inside the 10 yard line during the game.
* **punts_inside_10_percentage**: The percentage of punts made by the player inside the 10 yard line during the game.
* **punts_inside_20**: The punts made by the player inside the 20 yard line during the game.
* **punts_inside_20_percentage**: The percentage of punts made by the player inside the 20 yard line during the game.
* **punts_over_50**: The punts over the 50 yard line made by the player during the game.
* **punt_yards**: The punt yards made by the player during the game.
* **defensive_points**: The points scored defensively by the player during the game.
* **misc_points**: The miscellaneous points made by the player during the game.
* **return_touchdowns**: The return touchdowns made by the player during the game.
* **total_two_point_conversions**: The total two point conversions made by the player during the game.
* **passing_touchdowns_9_yards**: The passing touchdowns made by the player during the game from 9 yards.
* **passing_touchdowns_19_yards**: The passing touchdowns made by the player during the game from 19 yards.
* **passing_touchdowns_29_yards**: The passing touchdowns made by the player during the game from 29 yards.
* **passing_touchdowns_39_yards**: The passing touchdowns made by the player during the game from 39 yards.
* **passing_touchdowns_49_yards**: The passing touchdowns made by the player during the game from 49 yards.
* **passing_touchdowns_above_50_yards**: The passing touchdowns made by the player during the game above 50 yards.
* **receiving_touchdowns_9_yards**: The receiving touchdowns made by the player during the game from 9 yards.
* **receiving_touchdowns_19_yards**: The receiving touchdowns made by the player during the game from 19 yards.
* **receiving_touchdowns_29_yards**: The receiving touchdowns made by the player during the game from 29 yards.
* **receiving_touchdowns_39_yards**: The receiving touchdowns made by the player during the game from 39 yards.
* **receiving_touchdowns_49_yards**: The receiving touchdowns made by the player during the game from 49 yards.
* **receiving_touchdowns_above_50_yards**: The receiving touchdowns made by the player during the game above 50 yards.
* **rushing_touchdowns_9_yards**: The rushing touchdowns made by the player during the game from 9 yards.
* **rushing_touchdowns_19_yards**: The rushing touchdowns made by the player during the game from 19 yards.
* **rushing_touchdowns_29_yards**: The rushing touchdowns made by the player during the game from 29 yards.
* **rushing_touchdowns_39_yards**: The rushing touchdowns made by the player during the game from 39 yards.
* **rushing_touchdowns_49_yards**: The rushing touchdowns made by the player during the game from 49 yards.
* **rushing_touchdowns_above_50_yards**: The rushing touchdowns made by the player during the game above 50 yards.
* **penalties_in_minutes**: The penalties in minutes for the player during the game (in seconds).
* **even_strength_goals**: The even strength goals by the player during the game.
* **power_play_goals**: The power play goals by the player during the game.
* **short_handed_goals**: The short handed goals by the player during the game.
* **game_winning_goals**: The game winning goals by the player during the game.
* **even_strength_assists**: The even strength assists by the player during the game.
* **power_play_assists**: The power play assists by the player during the game.
* **short_handed_assists**: The short handed assists by the player during the game.
* **shots_on_goal**: The shots on goal by the player during the game.
* **shooting_percentage**: The shooting percentage by the player during the game.
* **shifts**: The shifts by the player during the game.
* **time_on_ice**: The time on the ice by the player during the game in seconds.
* **decision**: The goalie decision by the player during the game.
* **goals_against**: The goals against the player during the game.
* **shots_against**: The shots against the player during the game.
* **saves**: The saves by the player during the game.
* **save_percentage**: The save percentage of the player during the game.
* **shutouts**: The shutouts by the player during the game.
* **individual_corsi_for_events**: Individual Corsi refers to the number of shot attempts (including shots on goal, blocked shots, and missed shots) taken by a player's team while that player is on the ice, compared to the number of shot attempts taken by the opposing team.
* **on_shot_ice_for_events**: : The total number of shot attempts (shots on goal, missed shots, and blocked shots) a player is on the ice for, both for and against their team, during a specific game or time period.
* **on_shot_ice_against_events**: The number of shot attempts the opposing team makes while that same player is on the ice.
* **corsi_for_percentage**: Measures a player's or team's shot attempt differential while on the ice.
* **relative_corsi_for_percentage**: Measures how much a player's on-ice Corsi For Percentage (CF%) differs from their team's overall CF% when the player is not on the ice.
* **offensive_zone_starts**: Indicates how frequently a player begins a shift in the offensive zone compared to the defensive zone.
* **defensive_zone_starts**: Indicates how frequently a player begins a shift in the defensive zone compared to the offensize zone.
* **offensive_zone_start_percentage**: The percentage a player begins a shift in the offensize zone to the defensize zone compared to the defensize zone to the offensize zone.
* **hits**: The hits made by the player during the game.
* **true_shooting_percentage**: The true shooting percentage of the player during the game.
* **at_bats**: An at-bat (AB) is a statistic that counts how many times a batter faces the pitcher, excluding instances where the batter reaches base on a walk, is hit by a pitch, or reaches base via sacrifice.
* **runs_scored**: A run is scored when a player legally advances around all four bases (first, second, third, and home) and safely crosses home plate.
* **runs_batted_in**: A run batted in (RBI) is a statistic that credits a batter for actions that lead to a runner scoring a run, with a few exceptions.
* **bases_on_balls**: A "base on balls" (often abbreviated as "BB" and commonly referred to as a "walk") occurs when a batter receives four pitches that the umpire deems outside of the strike zone.
* **strikeouts**: A strikeout (K or SO) occurs when a batter accumulates three strikes against them during their at-bat.
* **plate_appearances**: A plate appearance refers to each time a batter steps up to the plate to face the pitcher.
* **hits_at_bats**: Hits at bats refers to the number of times a player gets a hit divided by their number of official at-bats, representing their batting average.
* **obp**: On-base percentage (OBP) in baseball measures how often a player reaches base per plate appearance, calculated as (hits + walks + hit by pitch) ÷ (at-bats + walks + hit by pitch + sacrifice flies).
* **slg**: Slugging percentage (SLG) in baseball measures the power of a hitter by calculating the total number of bases they earn per at-bat, using the formula: (singles + 2×doubles + 3×triples + 4×home runs) ÷ at-bats.
* **ops**: On-base plus slugging (OPS) is a baseball statistic that combines a player's ability to get on base and hit for power, calculated as OPS = OBP + SLG.
* **pitches**: In baseball, pitches refer to the individual throws made by the pitcher to the batter, each counted as part of the game’s progression and used to assess the pitcher's workload and performance.
* **strikes**: In baseball, strikes are pitches that either are swung at and missed, hit foul (with less than two strikes), or land in the strike zone without being swung at, and three strikes result in a strikeout.
* **win_probability_added**: Win Probability Added (WPA) is a baseball statistic that measures how much a player's actions increase or decrease their team’s chances of winning, based on the change in win probability before and after each play.
* **average_leverage_index**: Average Leverage Index (aLI) measures the pressure of the game situations a player faces, showing how important their plate appearances or pitching moments are relative to the average, where 1.0 is average pressure, and higher values indicate higher-stakes situations.
* **wpa_plus**: WPA+ (Win Probability Added Plus) is a metric that measures the total positive contributions a player makes to their team’s win probability over the course of a game or season, summing only the plays that increased the team’s chances of winning.
* **wpa_minus**: WPA– (Win Probability Added Minus) measures the total negative impact a player has on their team’s win probability, summing only the plays that decreased the team's chances of winning.
* **cwpa**: cWPA (Championship Win Probability Added) is a baseball statistic that measures how much a player's actions increase or decrease their team’s chances of winning the championship, rather than just a single game—essentially applying WPA to postseason and championship context.
* **acli**: aCLI (Average Championship Leverage Index) measures the average pressure or importance of the situations a player faces in terms of their impact on winning the championship, where 1.0 is average and higher values indicate higher championship-impact moments—similar to aLI but scaled for postseason stakes.
* **re24**: RE24 (Run Expectancy 24) is a baseball statistic that measures a player's total impact on run expectancy over all 24 base-out states, calculating how much each play increased or decreased the expected number of runs scored in that inning.
* **putouts**: Putouts are credited to a defensive player in baseball when they record an out by actions such as catching a fly ball, tagging a runner, being the receiver on a force out, or stepping on a base for an unassisted out.
* **innings_pitched**: Innings Pitched (IP) is a baseball statistic that measures the number of innings a pitcher has completed, with each out recorded counting as one-third of an inning (e.g., 5.2 IP means 5 innings and 2 outs).
* **earned_runs**: Earned runs are the runs a pitcher allows that result from hits, walks, or other offensive actions not involving errors or passed balls, and are used to evaluate the pitcher’s performance in preventing scoring.
* **home_runs**: Home runs are hits in baseball where the batter rounds all the bases and scores without being put out, typically by hitting the ball over the outfield fence in fair territory.
* **era**: ERA (Earned Run Average) is a pitching statistic in baseball that measures the average number of earned runs a pitcher allows per nine innings pitched, calculated as: ERA = (Earned Runs × 9) ÷ Innings Pitched.
* **batters_faced**: Batters Faced (BF) is a baseball statistic that counts the total number of individual hitters a pitcher has pitched to, regardless of the outcome (hit, walk, strikeout, etc.).
* **strikes_by_contact**: Strikes by Contact refers to pitches that result in a strike because the batter made contact with the ball—typically including foul balls (except with two strikes) and weak contact within the strike zone that doesn't result in a hit. This stat helps evaluate how often pitchers induce contact that still counts as a strike.
* **strikes_swinging**: Strikes Swinging are pitches where the batter swings and misses entirely, resulting in a strike; they’re a key indicator of a pitcher’s dominance and ability to deceive hitters.
* **strikes_looking**: Strikes Looking are pitches that are called strikes by the umpire when the batter does not swing, typically because the pitch lands within the strike zone.
* **ground_balls**: Ground balls are batted balls that hit the ground and roll or bounce in the infield, typically resulting in ground outs, double plays, or base hits depending on placement and defense.
* **fly_balls**: Fly balls are batted balls hit high into the air, usually into the outfield, that can result in outs (like flyouts), extra-base hits, or home runs depending on distance and placement.
* **line_drives**: Line drives are batted balls hit hard and relatively level, traveling in a straight or slightly rising trajectory, often resulting in base hits due to their speed and low arc.
* **inherited_runners**: Inherited runners are baserunners a relief pitcher takes over when entering the game, meaning they were already on base due to the previous pitcher, and if they score, the runs are charged to the previous pitcher, not the reliever.
* **inherited_scores**: Inherited Scores refers to the number of inherited runners that a relief pitcher allows to score after entering the game; although the runs count against the previous pitcher, this stat reflects how well the reliever manages pressure situations.
* **penalty_kicks_made**: The number of penalty kicks successfully scored by the player.
* **penalty_kicks_attempted**: The total number of penalty kicks the player has attempted, regardless of whether they were successful.
* **shots_total**: The total number of shots taken by the player, including both on-target and off-target attempts.
* **shots_on_target**: The number of shots that were directed on goal and would have scored if not for a save or block by the goalkeeper.
* **yellow_cards**: The number of yellow cards a player or team has received as a caution for unsporting behavior or rule violations.
* **red_cards**: The number of red cards a player or team has received, resulting in immediate ejection from the match.
* **touches**: The total number of times a player has made contact with the ball during the match.
* **expected_goals**: The total expected goals (xG) value, estimating how likely a shot is to result in a goal based on factors like shot location, type, and assist.
* **non_penalty_expected_goals**: The total expected goals (xG) from all shots excluding penalty kicks, providing a measure of scoring chances from open play and non-penalty set pieces.
* **expected_assisted_goals**: The total expected assisted goals (xAG), estimating the likelihood that a player's passes or crosses will lead to a goal, based on the quality of the resulting shots.
* **shot_creating_actions**: The number of actions (such as passes, dribbles, or drawing fouls) that directly lead to a shot attempt, credited to the two players most involved before the shot.
* **goal_creating_actions**: The number of actions (such as passes, dribbles, or drawn fouls) that directly lead to a goal, credited to the two players most involved in the build-up.
* **passes_completed**: The total number of passes successfully completed by a player or team to a teammate.
* **passes_attempted**: The total number of pass attempts made by a player or team, regardless of whether they were completed successfully.
* **pass_completion**: The percentage of attempted passes that were successfully completed by a player or team.
* **progressive_passes**: The number of completed passes that move the ball significantly forward toward the opponent's goal, typically at least 10 yards closer or into the penalty area.
* **carries**: The number of times a player controls the ball with their feet and moves it a measurable distance across the field.
* **progressive_carries**: The number of times a player carries the ball at least 5–10 yards closer to the opponent’s goal or into the penalty area, contributing to forward attacking movement.
* **take_ons_attempted**: The number of times a player has attempted to dribble past an opponent in a one-on-one situation.
* **successful_take_ons**: The number of times a player successfully dribbled past an opponent in a one-on-one situation.
* **total_passing_distance**: The cumulative distance, in yards or meters, that a player's or team's passes have traveled during a match.
* **progressive_passing_distance**: The total distance, in yards or meters, that completed passes have moved the ball closer to the opponent’s goal.
* **passes_completed_short**: The number of short passes (typically under 15 yards/meters) successfully completed by a player or team.
* **passes_attempted_short**: The number of short passes (typically under 15 yards/meters) attempted by a player or team, regardless of success.
* **pass_completion_short**: The percentage of short passes (typically under 15 yards/meters) that were successfully completed by a player or team.
* **passes_completed_medium**: The number of medium-range passes (typically 15 to 30 yards/meters) successfully completed by a player or team.
* **passes_attempted_medium**: The number of medium-range passes (typically 15 to 30 yards/meters) attempted by a player or team, regardless of success.
* **pass_completion_medium**: The percentage of medium-range passes (typically 15 to 30 yards/meters) that were successfully completed by a player or team.
* **passes_completed_long**: The number of long passes (typically over 30 yards/meters) successfully completed by a player or team.
* **passes_attempted_long**: The number of long passes (typically over 30 yards/meters) attempted by a player or team, regardless of success.
* **pass_completion_long**: The percentage of long passes (typically over 30 yards/meters) that were successfully completed by a player or team.
* **expected_assists**: The total expected assists (xA), measuring the likelihood that a pass will become a goal based on the quality of the resulting shot.
* **key_passes**: The number of passes that directly lead to a teammate taking a shot, regardless of whether the shot results in a goal.
* **passes_into_final_third**: The number of completed passes that move the ball into the attacking third of the pitch.
* **passes_into_penalty_area**: The number of completed passes that deliver the ball into the opponent’s penalty area.
* **crosses_into_penalty_area**: The number of crosses that successfully reach the opponent’s penalty area.
* **live_ball_passes**: The number of passes made while the ball is in play (i.e., not from set pieces like corners, free kicks, or throw-ins).
* **dead_ball_passes**: The number of passes made from dead-ball situations, such as free kicks, corners, goal kicks, or throw-ins.
* **passes_from_free_kicks**: The number of passes made directly from free kick situations.
* **through_balls**: The number of passes that split the defense and send a teammate through on goal, typically between defenders.
* **switches**: The number of long passes that switch the point of attack by moving the ball across the width of the field to the opposite flank.
* **crosses**: The number of passes played from wide areas into the penalty box, typically intended to create a scoring opportunity.
* **throw_ins_taken**: The number of throw-ins a player or team has taken to restart play from the sidelines.
* **corner_kicks**: The number of corner kicks taken by a player or team to restart play from the corner arc after the ball has gone out over the goal line, last touched by a defender.
* **inswinging_corner_kicks**: Corner kicks that curve inward toward the goal, typically delivered with the inside of the foot from the opposite side of the kicker’s strong foot.
* **outswinging_corner_kicks**: Corner kicks that curve away from the goal, typically delivered with the inside of the foot from the same side as the kicker’s strong foot.
* **straight_corner_kicks**: Corner kicks that are delivered with little or no curve, traveling in a relatively straight path toward the goal area.
* **passes_offside**: The number of passes that resulted in a teammate being caught in an offside position.
* **passes_blocked**: The number of passes that were obstructed or deflected by an opposing player before reaching their intended target.
* **tackles_won**: The number of times a player successfully takes the ball away from an opponent through a tackle and retains possession or directs it to a teammate.
* **tackles_in_defensive_third**: The number of tackles made by a player or team within their own defensive third of the field.
* **tackles_in_middle_third**: The number of tackles made by a player or team in the middle third of the field.
* **tackles_in_attacking_third**: The number of tackles made by a player or team in the attacking third of the field.
* **dribblers_tackled**: The number of times a player successfully dispossessed an opponent who was attempting to dribble past them.
* **dribbles_challenged**: The number of times a player attempted to stop an opponent from dribbling past them, regardless of whether the challenge was successful.
* **percent_of_dribblers_tackled**: The percentage of dribble challenges in which a player successfully tackled the opponent attempting to dribble past them.
* **challenges_lost**: The number of defensive challenges (such as tackles or duels) a player engaged in but failed to win.
* **shots_blocked**: The number of opponent shot attempts that were deflected or stopped by a player before reaching the goal.
* **tackles_plus_interceptions**: The combined total of tackles and interceptions made by a player or team, reflecting overall defensive activity.
* **errors**: The number of mistakes made by a player that directly lead to an opponent's shot or goal.
* **touches_in_defensive_penalty_area**: The number of times a player made contact with the ball while inside their own team’s penalty area.
* **touches_in_defensive_third**: The number of times a player touched the ball within their own defensive third of the pitch.
* **touches_in_middle_third**: The number of times a player touched the ball in the middle third of the pitch.
* **touches_in_attacking_third**: The number of times a player touched the ball in the attacking third of the pitch.
* **touches_in_attacking_penalty_area**: The number of times a player touched the ball inside the opponent’s penalty area.
* **live_ball_touches**: The number of times a player touched the ball while it was in play, excluding dead-ball situations like set pieces or throw-ins.
* **successful_take_on_percentage**: The percentage of take-on attempts (dribbles past an opponent) that were successful.
* **times_tackled_during_take_ons**: The number of times a player was tackled by a defender while attempting to dribble past them.
* **tackled_during_take_on_percentage**: The percentage of take-on attempts during which the player was tackled by a defender.
* **total_carrying_distance**: The cumulative distance a player has carried the ball with their feet during a match.
* **progressive_carrying_distance**: The total distance a player has carried the ball toward the opponent’s goal, significantly advancing it up the field.
* **carries_into_final_third**: The number of times a player carried the ball into the attacking third of the pitch.
* **carries_into_penalty_area**: The number of times a player carried the ball into the opponent’s penalty area.
* **miscontrols**: The number of times a player failed to control the ball properly, leading to a loss of possession.
* **dispossessed**: The number of times a player lost possession of the ball due to an opponent’s defensive action.
* **passes_received**: The number of times a player successfully received a pass from a teammate.
* **progressive_passes_received**: The number of times a player received a pass that moved the ball significantly forward toward the opponent’s goal.
* **second_yellow_card**: The number of times a player received a second yellow card in a match, resulting in a red card and ejection from the game.
* **fouls_committed**: The number of times a player has committed a foul by violating the rules against an opponent.
* **fouls_drawn**: The number of times a player was fouled by an opponent, resulting in a free kick or advantage for their team.
* **offsides**: The number of times a player was caught in an offside position during an attacking play.
* **penalty_kicks_won**: The number of times a player or team earned a penalty kick by being fouled or fouled upon inside the opponent’s penalty area.
* **penalty_kicks_conceded**: The number of times a player or team has caused fouls inside their own penalty area, resulting in a penalty kick awarded to the opponent.
* **own_goals**: The number of goals a player or team has accidentally scored against themselves.
* **ball_recoveries**: The number of times a player or team regains possession of the ball after it was lost or loose.
* **aerials_won**: The number of aerial duels (contests for the ball in the air) that a player has successfully won.
* **aerials_lost**: The number of aerial duels (contests for the ball in the air) that a player has lost to an opponent.
* **percentage_of_aerials_won**: The percentage of aerial duels contested by a player that they successfully won.
* **shots_on_target_against**: The number of shots on target that an opponent has taken against a team or goalkeeper.
* **post_shot_expected_goals**: The expected goals (xG) value assigned after a shot is taken, considering the actual outcome and quality of the shot, such as placement and goalkeeper reaction.
* **passes_attempted_minus_goal_kicks**: The number of pass attempts made by a team or player excluding passes originating from goal kicks.
* **throws_attempted**: The number of throw-ins attempted by a player or team to restart play from the sidelines.
* **percentage_of_passes_that_were_launched**: The percentage of a player’s or team’s passes that were long or 'launched' passes, typically covering a significant distance forward or across the field.
* **average_pass_length**: The average distance, in yards or meters, of all passes attempted by a player or team.
* **goal_kicks_attempted**: The number of goal kicks taken by a team to restart play from their own goal area.
* **percentage_of_goal_kicks_that_were_launched**: The percentage of goal kicks that were played as long, launched passes covering significant distance downfield.
* **average_goal_kick_length**: The average distance, in yards or meters, that goal kicks travel from the goal area.
* **crosses_faced**: The number of crosses directed into the penalty area that a team or goalkeeper has had to defend against.
* **crosses_stopped**: The number of opponent crosses into the penalty area that a team or goalkeeper successfully intercepted, blocked, or cleared.
* **percentage_crosses_stopped**: The percentage of opponent crosses into the penalty area that a team or goalkeeper successfully stopped or defended.
* **defensive_actions_outside_penalty_area**: The number of defensive actions (such as tackles, interceptions, or clearances) made by a player or team outside their own penalty area.
* **average_distance_of_defensive_actions**: The average distance from a team’s own goal where defensive actions (tackles, interceptions, clearances) occur.
* **three_point_attempt_rate**: The number of three points attempted by a player.
* **batting_style**: Describes whether a player bats right-handed or left-handed.
* ***bowling_style**: Describes how a player bowls — specifically their arm used (right-arm or left-arm) and their type of bowling (pace or spin, and the specific variety within those).
* ***playing_roles**: Describe a player’s primary job in the team — whether they are mainly there to bat, bowl, keep wicket, or contribute in multiple ways.
* **runs**: The number of runs the batter scored themselves (excluding extras).
* ***balls**: Balls in a player’s batting record represent the number of legal deliveries they have faced from bowlers.
* ***fours**: The number of times a batter hits the ball to the boundary for exactly four runs in a legal delivery.
* **sixes**: The number of times a batter hits the ball over the boundary rope without it touching the ground, scoring six runs automatically.
* **strikerate**: Strike rate (for batting) measures how quickly a batter scores runs and is expressed as runs scored per 100 balls faced
* **fall_of_wicket_order**: The sequence in which a batter got out during an innings — basically which wicket they were.
* **fall_of_wicket_num**: Score at the exact moment a particular wicket fell.
* **fall_of_wicket_runs**: The number of runs the dismissed batter scored in the innings at the moment their wicket fell.
* **fall_of_wicket_balls**: The number of legal deliveries faced by the dismissed batter at the time their wicket fell.
* **fall_of_wicket_overs**: The exact over (and ball within the over) when a wicket fell in the innings.
* **fall_of_wicket_over_number**: The whole-number over count when a wicket fell — without including the ball number like fall_of_wicket_overs does.
* **ball_over_actual**: The precise over and ball number of a specific delivery in the innings — recorded in the same decimal style as fall_of_wicket_overs, but for every ball, not just wickets.
* **ball_over_unique**: A sequential, unique index for every delivery in the innings, regardless of overs, expressed as a single running number.
* **ball_total_runs**: The total number of runs scored from a single delivery.
* **ball_batsman_runs**: The number of runs credited directly to the batter from a single legal delivery — excluding any extras.
* **overs**: A set of six legal deliveries bowled by one bowler from one end of the pitch.
* **maidens**: Overs in which the bowler concedes zero runs — counting only runs from the bat and byes/leg byes.
* **conceded**: The total number of runs a bowler has given away while bowling
* **wickets**: The number of batters they have dismissed while bowling.
* **economy**: Measures how many runs a bowler concedes per over they bowl.
* **runs_per_ball**: The average number of runs scored per legal delivery over a given period — it’s essentially the ball-level equivalent of strike rate or economy.
* **dots**: Deliveries from which no runs are scored by the batting side.
* **wides**: Deliveries that the umpire judges to be too far from the batter to hit with a normal cricket stroke, resulting in an extra run to the batting team.
* **no_balls**: An illegal delivery by the bowler.
* **free_throw_attempt_rate**: Measures how often a player or team gets to the free throw line relative to their shot attempts.
* **offensive_rebound_percentage**: Estimates the percentage of available offensive rebounds a player or team grabs while they are on the floor.
* **defensive_rebound_percentage**: Estimates the percentage of available defensive rebounds a player or team secures while they’re on the floor.
* **total_rebound_percentage**: Estimates the percentage of all available rebounds—offensive and defensive—that a player or team grabs while on the floor.
* **assist_percentage**: Estimates the percentage of a team’s made field goals that a player assists on while they’re on the floor.
* **steal_percentage**: Estimates the percentage of opponent possessions that end with a steal by a player while they’re on the floor.
* **block_percentage**: Estimates the percentage of opponent two-point field goal attempts that a player blocks while they’re on the court.
* **turnover_percentage**: Estimates the percentage of a player’s possessions that end in a turnover — essentially, how often they lose the ball when they finish a possession.
* **usage_percentage**: Estimates the percentage of a team’s possessions that a player “uses” while they’re on the floor — meaning possessions that end with the player’s shot attempt, trip to the free throw line, or turnover.
* **offensive_rating**: Estimates how many points a player (or team) produces per 100 possessions.
* **defensive_rating**: Estimates how many points a player (or team) allows per 100 possessions while they’re on the floor.
* **box_plus_minus**: Estimates a player’s overall impact on team performance per 100 possessions, compared to an average player, using only box score data (no play-by-play).
* **ace_percentage**: Percentage of the players serves that were aces.
* **double_fault_percentage**: Percentage of the players serves that were double faults.
* **first_serves_in**: The number of first serves in.
* **first_serve_percentage**: Percentage of the players serves that landed on the first try.
* **second_serve_percentage**: Percentage of the players second serves that landed.
* **break_points_saved**: Number of break points saved.
* **return_points_won_percentage**: Percentage of the return points won.
* **winners**: Number of rallies that the player won.
* **winners_fronthand**: Number of rallies that the player won with their fronthand.
* **winners_backhand**: Number of rallies that the player won with their backhand.
* **unforced_errors**: Number of unforced errors that the player made.
* **unforced_errors_fronthand**: Number of unforced errors that the player made with their fronthand.
* **unforced_errors_backhand**: Number of unforced errors that the player made with their backhand.
* **serve_points**: Number of points the player made from their serves.
* **serves_won**: Number of serves won by the player.
* **serves_aces**: Number of serves that are aces by the player.
* **serves_unreturned**: Number of serves made by the player that were unreturned.
* **serves_forced_error_percentage**: Percentage of serves that contained a forced error.
* **serves_won_in_three_shots_or_less**: Percentage of rallies served by the player won in 3 shots or less.
* **serves_wide_percentage**: Percentage of serves that went wide.
* **serves_body_percentage**: Percentage of serves the player made aimed at the body.
* **serves_t_percentage**: Percentage of serves the player made down the T.
* **serves_wide_deuce_percentage**: Percentage of serves the player made that were wide from the deuce.
* **serves_body_deuce_percentage**: Percentage of serves the player made that were aimed at the body from the deuce.
* **serves_t_deuce_percentage**: Percentage of serves the player made down the T from the deuce.
* **serves_wide_ad_percentage**: Percentage of serves the player made that were wide from the ad.
* **serves_body_ad_percentage**: Percentage of serves the player made that were aimed at the body from the ad.
* **serves_t_ad_percentage**: Percentage of serves the player made down the T from the ad.
* **serves_net_percentage**: Percentage of serves that hit the net.
* **serves_wide_direction_percentage**: Percentage of serves that were wide.
* **shots_deep_wide_percentage**: Percentage of shots that were deep and wide.
* **shots_foot_errors_percentage**: Percentage of shots that were foot errors.
* **shots_unknown_percentage**: Percentage of shots that had an unknown classification.
* **points_won_percentage**: Percentage of rallies won.

#### Odds

A representation of the odds for a team to win within a game.

* **odds**: The decimal odds offered by a bookie for the team to win in the game.
* **bookie**: The bookie offering these odds.
* **dt**: When the odds were posted.
* **canonical**: Whether these odds can be treated as canonical for the purposes of backtesting.
* **bet**: The type of bet the odds represent.

#### Venue

The venue the game is played at.

* **identifier**: The unique identifier for the venue.
* **names**: The name of the venue.
* **address**: The address of the venue.
* **is_grass**: Whether the venue has a grass field.
* **is_indoor**: Whether the venue is indoors.
* **is_turf**: Whether the venue is turf.
* **is_dirt**: Whether the venue is dirt.
* **version**: The version of the game model.

#### Address

The address of the venue.

* **city**: The city of the address.
* **state**: The state of the address.
* **zipcode**: The postal/zip code of the address.
* **latitude**: The latitude of the address.
* **longitude**: The longitude of the address.
* **housenumber**: The house/street number of the address.
* **weather**: The weather at the address at the game start time.
* **timezone**: The time zone at the address.
* **country**: The country of the address.
* **altitude**: The altitude of the address.
* **version**: The version of the address model.

#### Weather

The forecasted weather one day out at the address of the game start time.

* **temperature**: The temperature at the address at the game start time.
* **relative_humidity**: The relative humidity at the address at the game start time.
* **dew_point**: The temperature at the address at the game start time.
* **apparent_temperature**: The apparent temperature at the address at the game start time.
* **precipitation_probability**: The precipitation probability at the address at the game start time.
* **precipitation**: The precipitation at the address at the game start time.
* **rain**: The rain at the address at the game start time.
* **showers**: The showers at the address at the game start time.
* **snowfall**: The snowfall at the address at the game start time.
* **snow_depth**: The snow depth at the address at the game start time.
* **weather_code**: The weather code at the address at the game start time.
* **sealevel_pressure**: The sealevel pressure at the address at the game start time.
* **surface_pressure**: The surface pressure at the address at the game start time.
* **cloud_cover_total**: The total cloud cover at the address at the game start time.
* **cloud_cover_low**: The low cloud cover at the address at the game start time.
* **cloud_cover_mid**: The mid cloud cover at the address at the game start time.
* **cloud_cover_high**: The high cloud cover at the address at the game start time.
* **visibility**: The visibility at the address at the game start time.
* **evapotranspiration**: The evapotranspiration at the address at the game start time.
* **reference_evapotranspiration**: The reference evapotranspiration at the address at the game start time.
* **vapour_pressure_deficit**: The vapour pressure deficit at the address at the game start time.
* **wind_speed_10m**: The wind speed at 10m at the address at the game start time.
* **wind_speed_80m**: The wind speed at 80m at the address at the game start time.
* **wind_speed_120m**: The wind speed at 120m at the address at the game start time.
* **wind_speed_180m**: The wind speed at 180m at the address at the game start time.
* **wind_direction_10m**: The wind direction at 10m at the address at the game start time.
* **wind_direction_80m**: The wind direction at 80m at the address at the game start time.
* **wind_direction_120m**: The wind direction at 120m at the address at the game start time.
* **wind_direction_180m**: The wind direction at 180m at the address at the game start time.
* **wind_gusts**: The wind gusts at the address at the game start time.
* **temperature_80m**: The temperature at 80m at the address at the game start time.
* **temperature_120m**: The temperature at 120m at the address at the game start time.
* **temperature_180m**: The temperature at 180m at the address at the game start time.
* **soil_temperature_0cm**: The soil temperature at the address at the game start time.
* **soil_temperature_6cm**: The soil temperature at 6cm at the address at the game start time.
* **soil_temperature_18cm**: The soil temperature at 18cm at the address at the game start time.
* **soil_temperature_54cm**: The soil temperature at 54cm at the address at the game start time.
* **soil_moisture_0cm**: The soil moisture at the address at the game start time.
* **soil_moisture_1cm**: The soil moisture at 1cm at the address at the game start time.
* **soil_moisture_3cm**: The soil moisture at 3cm at the address at the game start time.
* **soil_moisture_9cm**: The soil moisture at 9cm at the address at the game start time.
* **soil_moisture_27cm**: The soil moisture at 27cm at the address at the game start time.
* **daily_weather_code**: The daily weather code at the address at the game start time.
* **daily_maximum_temperature_2m**: The daily maximum temperature at 2m at the address at the game start time.
* **daily_minimum_temperature_2m**: The daily minimum temperature at 2m at the address at the game start time.
* **daily_maximum_apparent_temperature_2m**: The daily maximum apparent temperature at 2m at the address at the game start time.
* **daily_minimum_apparent_temperature_2m**: The daily minimum apparent temperature at 2m at the address at the game start time.
* **sunrise**: The sunrise at the address at the game start time.
* **sunset**: The sunset at the address at the game start time.
* **daylight_duration**: The daylight duration at the address at the game start time.
* **sunshine_duration**: The sunshine duration at the address at the game start time.
* **uv_index**: The UV index at the address at the game start time.
* **uv_index_clear_sky**: The UV index for clear sky at the address at the game start time.
* **rain_sum**: The rain sum at the address at the game start time.
* **showers_sum**: The showers sum at the address at the game start time.
* **snowfall_sum**: The snowfall sum at the address at the game start time.
* **precipitation_sum**: The precipitation sum at the address at the game start time.
* **precipitation_hours**: The precipitation hours at the address at the game start time.
* **precipitation_probability_max**: The maximum precipitation probability at the address at the game start time.
* **maximum_wind_speed_10m**: The maximum wind speed at 10m at the address at the game start time.
* **maximum_wind_gusts_10m**: The maximum wind gusts at 10m at the address at the game start time.
* **dominant_wind_direction**: The dominant wind direction at the address at the game start time.
* **shortwave_radiation_sum**: The shortwave radiation sum at the address at the game start time.
* **daily_reference_evapotranspiration**: The daily reference evapotranspiration at the address at the game start time.
* **version**: The version of the weather model.

#### News

The news one day out from the game.

* **title**: The title of the article
* **published**: When the article was published.
* **summary**: The summary of the article.
* **source**: The source of the article.

#### Social

Social media posts one day out from the game.

* **network**: The social network this post was made from.
* **post**: The text of the post.
* **comments**: The number of comments on the post.
* **reposts**: The number of reposts.
* **likes**: The number of likes the post received.
* **views**: The number of views the post has.
* **published**: When the post was published.

#### Coach

The coach on the team at the time of the game.

* **identifier**: The unique identifier for the coach.
* **name**: The name of the coach.
* **birth_date**: The birth date of the coach.
* **age**: The age of the coach.
* **sex**: The sex of the coach.
* **version**: The version of the coach model.

#### Dividend

The dividend payout at the end of the game.

* **pool**: The type of bet paying the dividend.
* **combination**: The combination of team identifiers making up the dividend.
* **dividend**: The payout of the dividend.

#### Owner

The owner of a player.

* **name**: The name of the owner.
* **identifier**: The unique identifier of the owner.
* **sex**: The sex of the owner.
* **version**: The version of the owner model.

#### Umpire

An umpire within the game.

* **name**: The name of the umpire.
* **identifier**: The unique identifier of the umpire.
* **sex**: The sex of the umpire.
* **birth_date**: The date the umpire was born.
* **age**: The age of the umpire at the time of the game.
* **birth_address**: The address of the birthplace of the umpire.
* **high_school**: The high school the umpire went to.
* **version**: The version of the umpire model.

## Caching

This library uses very aggressive caching due to the large data requirements. If the requests are about a recent game (generally in the last 7 days) the caching is bypassed. The caching is as follows:

1. A joblib disk cache that caches calls to pydantic model creation functions. This changes on every version update to keep the models in sync. This is the fastest cache.
2. A requests cache backed by sqlite that caches requests forever.
3. An attempt to find the response is made to the wayback machine, and used if found.

It's very recommended that the user uses proxies defined in the `PROXIES` environment variable. The more proxies the easier it is to collect data.

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install sportsball`

or install using this local repository:

`python setup.py install --old-and-unmanageable`

## Usage example :eyes:

There are many different ways of using sportsball, but we generally recommend the CLI.

### CLI

To fetch a dataframe containing information about a league, you can use the following CLI:

```
sportsball --league=nfl -
```

The final argument denotes the file to write to, in this case `-` is stdout.

### Python

To pull a dataframe containing all the information for a particular league, the following example can be used:

```python
from sportsball import sportsball as spb

ball = spb.SportsBall()
league = ball.league(spb.League.AFL)
df = league.to_frame()
```

This results in a dataframe where each game is represented by all its features.

### Environment

If you wish to use the providers that require API keys, you can create a `.env` file with the following variables inside it:

```
GOOGLE_API_KEY=APIKEY
GRIBSTREAM_API_KEY=APIKEY
X_API_KEY=APIKEY
X_API_SECRET_KEY=APISECRETKEY
X_ACCESS_TOKEN=ACCESSTOKEN
X_ACCESS_TOKEN_SECRET=ACCESSTOKENSECRET
PROXIES=CSVPROXIESLIST
```

## License :memo:

The project is available under the [MIT License](LICENSE).
