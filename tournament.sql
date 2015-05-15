-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Create tournament database and connect to it.

-- Uncomment for debuging purpose
-- DROP DATABASE IF EXISTS tournament;

-- Uncomment for debuging purpose
-- DROP DATABASE IF EXISTS tournament;

-- Warning: bug may occur if database 'tournament' already exists.
CREATE DATABASE tournament;
\c tournament;

-- Columns: 
--      id:         id of players
--      name:       name of players
--      tour_id:    id of tournaments. tour_id could be a foreign key to the
--                  table that contains tourment information. Here, for 
--                  simplicity, it's an independent integer instead
CREATE TABLE players (
    id          serial PRIMARY KEY,
    name        varchar(100),
    tour_id     integer 
);

-- Columns: 
--      id:         id of matches
--      winner_id:  id of winners (if not tied)
--      loser_id:   id of losers  (if not tied). loser_id could be NULL
--                  for a skipped round due to odd number of players
--      tied:       whether the game is tied
CREATE TABLE matches (
    id          serial PRIMARY KEY,
    -- serial is a psuedo type to integer/big
    winner_id   integer references players(id),
    loser_id    integer references players(id),
    tied        boolean
);

-- Columns: 
--      id:             id of players
--      match_played:   number of matches that player played. Skipped rounds
--                      are also counted
CREATE VIEW player_match_num AS
     SELECT players.id, count(matches.id) as match_played
       FROM players
  LEFT JOIN matches 
         ON players.id = winner_id
         OR players.id = loser_id
   GROUP BY players.id;

-- Columns: 
--      id:         id of players
--      match_won:  number of matches that player won. Skipped rounds are
--                  counted as free win, but tied rounds are not counted
CREATE VIEW player_win_num AS
     SELECT tour_id, players.id, count(matches.id) as match_won
       FROM players
  LEFT JOIN matches 
         ON players.id = winner_id
        AND tied = FALSE
   GROUP BY players.id;

-- Columns: 
--      id:             id of players
--      opponent_id:    id of opponent that players played against
CREATE VIEW player_opponents AS
     -- Select opponent id to whom the player won
     SELECT players.id, loser_id as opponent_id
       FROM players, matches
      WHERE players.id = winner_id
      UNION
     -- Select opponent id to whom the player lost
     SELECT players.id, winner_id as opponent_id
       FROM players, matches
      WHERE players.id = loser_id;

-- Columns: 
--      id:     id of players
--      OMW:    total number of wins by players they have played against
CREATE VIEW player_OMW AS
     SELECT player_opponents.id, sum(match_won) as OMW
       FROM player_opponents, player_win_num
      WHERE opponent_id = player_win_num.id
   GROUP BY player_opponents.id;

-- Columns: 
--      tour_id:    id of tournaments
--      id:         id of players
--      match_won:  number of matches that player won
--      standing:   ranking of that player, ties are breaking using OMW
CREATE VIEW player_standing AS
     SELECT tour_id, id, match_won, rank() OVER
               (PARTITION BY player_win_num.tour_id
                    ORDER BY match_won DESC, 
                                   OMW DESC NULLS LAST) as standing
       FROM player_win_num
  LEFT JOIN player_OMW
      USING (id);

