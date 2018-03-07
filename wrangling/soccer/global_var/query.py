class SQLpatterns:
    select_players_attr = \
        """
        select p.player_name, pa_id.player_fifa_api_id, pa_id.player_api_id, pa_id.preferred_foot, pa_id.avr_sp, pa_id.avr_r
            from
                (select player_fifa_api_id, player_api_id, preferred_foot, avg(shot_power) as avr_sp, avg(overall_rating) as avr_r
                    from Player_Attributes
                    where overall_rating is not null and preferred_foot is not null and shot_power is not null
                    group by player_fifa_api_id)  pa_id
            inner join Player p
            on p.player_fifa_api_id = pa_id.player_fifa_api_id
            Order by avr_r DESC, avr_sp DESC
        """

    select_team_attr_score = \
        """
select ta.team_api_id as id, 
		substr(date,0,5) as season,
		(buildUpPlaySpeed+buildUpPlayPassing+
		chanceCreationPassing+chanceCreationCrossing+chanceCreationShooting+
		defencePressure+defenceAggression+defenceTeamWidth)/8 as average,		
		sum(year_stats.scored) as scored, 
		sum(year_stats.got) as got,
		sum(year_stats.won) as won, 
		sum(year_stats.draw) as draw, 
		sum(year_stats.lose) as lose, 
		t.team_long_name,
		t.team_short_name
		
from Team_Attributes ta 
INNER JOIN Team t
ON ta.team_api_id = t.team_api_id
INNER JOIN
		(select match_stat.id as id, 
				sum(match_stat.scored) as scored, 
				sum(match_stat.won) as won, 
				sum(match_stat.draw) as draw, 
				sum(match_stat.lose) as lose, 
				sum(match_stat.lost) as got, 
				match_stat.y as years
from
		(select away_team_api_id as id, 
				sum(away_team_goal) as scored, 
				sum(home_team_goal) as lost, 
			    count(case when away_team_goal > home_team_goal then 1 end) as won,
				count(case when away_team_goal = home_team_goal then 1 end ) as draw,
				count(case when away_team_goal < home_team_goal then 1 end) as lose,
				date as y
		from Match
		group by y,  id
	union
		select home_team_api_id as id, 
				sum(home_team_goal) as scored, 
				sum(away_team_goal) as lost, 
				count(case when home_team_goal > away_team_goal then 1 end) as won,
				count(case when home_team_goal = away_team_goal then 1 end ) as draw,
				count(case when home_team_goal < away_team_goal then 1 end) as lose,
				date as y
		from Match
		group by y, id) match_stat
    group by years, id
    order by id) year_stats
ON year_stats.id = ta.team_api_id 
AND substr(year_stats.years, 0, 5) = substr(season, 0, 5)
GROUP BY ta.team_api_id, season
ORDER BY id
    
        """
    get_all_countries = "select * from Country"
    get_all_games = "select * from Match"
    get_all_players = "select * from Players"
    get_all_players_attr = "select * from Player_Attributes"


class REGEXpatterns:
    player_ids = '(<player1>(?P<id>[0-9]+)</player1>)'
