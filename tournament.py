#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    query = "delete from matches"
    c.execute(query)
    # commit is needed if data are modified
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    query = "delete from players"
    c.execute(query)
    DB.commit()
    DB.close()


def countPlayers(tour_id=1):
    """Returns the number of players in the tournament specfied by tour_id
    
    Args:
      tour_id: id of tournament
    """
    DB = connect()
    c = DB.cursor()
    query = "select count(*) from players where tour_id=%s"
    c.execute(query, (tour_id, ))
    # fetchone returns a tuple (row)
    # To extract the value, query_result[0] is used
    query_result = c.fetchone()
    DB.close()
    player_count = query_result[0]
    return player_count


def registerPlayer(name, tour_id=1):
    """Adds a player to the tournament specified by tour_id.
  
    Args:
      name: the player's full name (need not be unique).
      tour_id: id of tournament
    """
    DB = connect()
    c = DB.cursor()
    query = "insert into players (name, tour_id) values (%s, %s)"
    # Use c.execute to format query command instead of directly string 
    # formatting to prevent SQL injection
    c.execute(query, (name, tour_id))
    DB.commit()
    DB.close()


def playerStandings(tour_id=1):
    """Returns a list of the players and their win records, sorted by wins.
       Ties are broken with OMW, the total number of wins by players they 
       have played against

    Args:
      tour_id: id of tournament

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    query = '''select players.id, name, match_won, match_played
                 from players, player_match_num, player_standing
                where players.id = player_match_num.id
                  and players.id = player_standing.id
                  and players.tour_id = %s
             order by standing
            '''
    c.execute(query, (tour_id, ))
    rows = c.fetchall()
    DB.close()
    return rows


def reportMatch(winner, loser, tied=False):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      tied:  if it's a draw match, tied is True
             Any other value will be converted to False
    """
    tied = bool(tied)
    DB = connect()
    c = DB.cursor()
    query = '''insert into matches (winner_id, loser_id, tied) 
               values (%s, %s, %s)
            '''
    c.execute(query, (winner, loser, tied))
    DB.commit()
    DB.close()
 
# Judge whether a given pair is valid
# (i.e. two players can't be paired twice
#       player can't receive more than one 'bye' round)
def isValidPair(player1_id, player2_id):
    DB = connect()
    c = DB.cursor()
    # player_opponents contains all pairs of players that have played before
    # It's symmetircal: (id1, id2) and (id2, id1) should be both present or
    # unpresent (except for None, which can only be player2)
    query = '''select count(*) from player_opponents 
                where id=%s 
                  and opponent_id=%s'''
    c.execute(query, (player1_id, player2_id))
    query_result = c.fetchone()[0]
    DB.commit()
    DB.close()
    if query_result == 0:
        return True
    # the two players had played before, thus the pair is invalid
    return False

# This function will perform Depth First Search to pair players according
# to the following two rules:
#   1. Two players that had played before can't be paired again
#      (This rule guarantees that no player can receive more than one bye 
#       rounds, or free wins)
#   2. Try to match two players that have similar standings
# 
# Main steps of pairing process includes:
#   1. Pair two players in unpaired_rows with similar standing
#   2. Recursively call itself until all rows are paired
#   3. Backtracking if unable to find valid pairings
# 
# Assumptions about input:
#   1. Even number of players. If not, add a None player first
#   2. Players are ranked by their standings
def pairRestRows(paired_rows, unpaired_rows):
    # Uncomment for debugging
    # print '='*50
    # print paired_rows
    # print unpaired_rows
    # No unpaired rows, thus return directly
    if len(unpaired_rows) == 0:
        return (paired_rows, unpaired_rows)
    # The best unpaired player
    best_player = unpaired_rows.pop(0)
    best_player_id = best_player[0]
    # Iterate all potential opponents in the order of their standings
    for idx, opponent in enumerate(unpaired_rows):
        opponent_id = opponent[0]
        # Only valid pair is considered
        if isValidPair(best_player_id, opponent_id):
            # Move the potential pair to paired list
            paired_rows_new = paired_rows + [(best_player, opponent)]
            unpaired_rows_new = unpaired_rows[:idx] + unpaired_rows[idx+1:]
            # Recursively pair the rest players
            result = pairRestRows(paired_rows_new, unpaired_rows_new)
            # Rest players are successfully paired, return result
            if result != 'pair failed':
                return result
    # Can't find valid pairs, return failed flag. Backtracking may follow
    return 'pair failed'

def swissPairings(tour_id=1):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Args:
      tour_id: id of tournament
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    player_num = countPlayers(tour_id=tour_id)
    # unpaired_rows is sorted according to standings of players
    unpaired_rows = playerStandings(tour_id=tour_id)
    # Odd number of players. Temporally add a None player, which means a bye 
    # round, or a free win
    if player_num%2 == 1:
        unpaired_rows.append((None, None, None, None))
    result = pairRestRows([], unpaired_rows)
    if result == 'pair failed':
        raise ValueError("No pairing strategy available to prevent rematches")
    # pairRestRows return two list, the first list contains the pairings
    pairs = result[0]
    # Formatting pairs as required
    pairs = [(player1[0], player1[1], player2[0], player2[1])
                 for (player1, player2) in pairs]
    return pairs





