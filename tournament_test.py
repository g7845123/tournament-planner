#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    deleteMatches()
    deletePlayers()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    deleteMatches()
    deletePlayers()
    registerPlayer("Chandra Nalaar")
    c = countPlayers()
    if c != 1:
        raise ValueError(
            "After one player registers, countPlayers() should be 1.")
    print "4. After registering a player, countPlayers() returns 1."


def testRegisterCountDelete():
    deleteMatches()
    deletePlayers()
    registerPlayer("Markov Chaney")
    registerPlayer("Joe Malik")
    registerPlayer("Mao Tsu-hsi")
    registerPlayer("Atlanta Hope")
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Melpomene Murray")
    registerPlayer("Randy Schwartz")
    standings = playerStandings()
    if len(standings) < 2:
        raise ValueError("Players should appear in playerStandings even before "
                         "they have played any matches.")
    elif len(standings) > 2:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 4:
        raise ValueError("Each playerStandings row should have four columns.")
    [(id1, name1, wins1, matches1), (id2, name2, wins2, matches2)] = standings
    if matches1 != 0 or matches2 != 0 or wins1 != 0 or wins2 != 0:
        raise ValueError(
            "Newly registered players should have no matches or wins.")
    if set([name1, name2]) != set(["Melpomene Murray", "Randy Schwartz"]):
        raise ValueError("Registered players' names should appear in standings, "
                         "even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    deleteMatches()
    deletePlayers()
    registerPlayer("Bruno Walton")
    registerPlayer("Boots O'Neal")
    registerPlayer("Cathy Burton")
    registerPlayer("Diane Grant")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    standings = playerStandings()
    for (i, n, w, m) in standings:
        if m != 1:
            raise ValueError("Each player should have one match recorded.")
        if i in (id1, id3) and w != 1:
            raise ValueError("Each match winner should have one win recorded.")
        elif i in (id2, id4) and w != 0:
            raise ValueError("Each match loser should have zero wins recorded.")
    print "7. After a match, players have updated standings."


def testPairings():
    deleteMatches()
    deletePlayers()
    registerPlayer("Twilight Sparkle")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    standings = playerStandings()
    [id1, id2, id3, id4] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    pairings = swissPairings()
    if len(pairings) != 2:
        raise ValueError(
            "For four players, swissPairings should return two pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4)] = pairings
    correct_pairs = set([frozenset([id1, id3]), frozenset([id2, id4])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After one match, players with one win should be paired.")
    print "8. After one match, players with one win are paired."


# To further test the ability of my program to handle
#   1. Tie-breaking based on OMW
#   2. Rematch prevention
#   3. Odd players handling based on skipped round
#   4. Tied game
#   5. Multiple tournament
# A simulated tournament was used, with 5 players and 3 round
# 
# Matches in round 1: 
#   A won B
#   C drew with D
#   E skipped
# Scores after round 1:
#   A, E:       1
#   B, C, D:    0
# Pairing for round 2:
#   A and E should be paired
# 
# Matches in round 2: 
#   A won E
#   B won C
#   D skipped
# Scores after round 2:
#   A:          2
#   B, D, E:    1
#   C:          0
# Pairing for round 3:
#   C should skipped
#   A and D should be paired (because AB and AE were already paired)
#   B and E should be paired
# 
# Matches in round 3: 
#   D won A
#   B won E
#   C skipped
# Scores after round 3:
#   A, B, D:    2
#   C, E:       1
# 
# Tournament rank (Rank by number of wins. Ties were broken by OMW) 
#   A: 1
#   B: 2
#   C: 4
#   D: 3
#   E: 4
def testSimulatedTournament():
    # Initial state
    registerPlayer('A', tour_id=2)
    registerPlayer('B', tour_id=2)
    registerPlayer('C', tour_id=2)
    registerPlayer('D', tour_id=2)
    registerPlayer('E', tour_id=2)
    standings = playerStandings(tour_id=2)
    [idA, idB, idC, idD, idE] = [row[0] for row in standings]
    correct_standing = [(idA, 0),   # Rank 1
                        (idB, 0),   # Rank 1
                        (idC, 0),   # Rank 1
                        (idD, 0),   # Rank 1
                        (idE, 0)]   # Rank 1
    actual_standing = [(row[0], row[2]) for row in standings]
    if correct_standing != actual_standing:
        raise ValueError(
            "The standings before match are incorrect")
    print "9. Multiple tournaments are supported by the program"
    # Round 1
    reportMatch(idA, idB)
    try:
        reportMatch(idC, idD, tied=True)
        print "10. Draw matches are supported"
    except:
        raise ValueError(
            "Unable to handle a draw match")
    try:
        reportMatch(idE, None)
        print "11. Odd number of players are supported by the program"
    except:
        raise ValueError(
            "Unable to handle skipped rounds")
    standings = playerStandings(tour_id=2)
    correct_standing = [(idA, 1),   # Rank 1
                        (idE, 1),   # Rank 2
                        (idB, 0),   # Rank 3
                        (idC, 0),   # Rank 4
                        (idD, 0)]   # Rank 4
    actual_standing = [(row[0], row[2]) for row in standings]
    if correct_standing != actual_standing:
        raise ValueError(
            "The standings after round 1 are incorrect")
    pairings = swissPairings(tour_id=2)
    [(pid1, pname1, pid2, pname2), 
     (pid3, pname3, pid4, pname4),
     (pid5, pname5, pid6, pname6)] = pairings
    correct_pairs = set([frozenset([idA, idE]), 
                         frozenset([idB, idC]),
                         frozenset([idD, None])])
    actual_pairs = set([frozenset([pid1, pid2]), 
                        frozenset([pid3, pid4]),
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After round 1, players are not correctly paired")
    # Round 2 
    reportMatch(idA, idE)
    reportMatch(idB, idC)
    reportMatch(idD, None)
    standings = playerStandings(tour_id=2)
    correct_standing = [(idA, 2),   # Rank 1
                        (idB, 1),   # Rank 2
                        (idE, 1),   # Rank 2
                        (idD, 1),   # Rank 4, D ranked below B and E
                                    #         due to the lower OMW 
                        (idC, 0)]   # Rank 5
    actual_standing = [(row[0], row[2]) for row in standings]
    if correct_standing != actual_standing:
        raise ValueError(
            "The standings after round 2 are incorrect")
    print "12. Players with same number of wins are ranked by their OMW"
    pairings = swissPairings(tour_id=2)
    [(pid1, pname1, pid2, pname2), 
     (pid3, pname3, pid4, pname4),
     (pid5, pname5, pid6, pname6)] = pairings
    correct_pairs = set([frozenset([idA, idD]), # Rematch between A and B
                                                # are prevented
                         frozenset([idB, idE]),
                         frozenset([idC, None])])
    actual_pairs = set([frozenset([pid1, pid2]), 
                        frozenset([pid3, pid4]),
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After round 2, players are not correctly paired")
    print "13. Rematches between players are prevented"
    # Round 3 
    reportMatch(idD, idA)
    reportMatch(idB, idE)
    reportMatch(idC, None)
    standings = playerStandings(tour_id=2)
    correct_standing = [(idA, 2),   # Rank 1
                        (idB, 2),   # Rank 2
                        (idD, 2),   # Rank 3
                        (idC, 1),   # Rank 4
                        (idE, 1)]   # Rank 4
    actual_standing = [(row[0], row[2]) for row in standings]
    if correct_standing != actual_standing:
        raise ValueError(
            "The standings after round 3 are incorrect")
    print "Extra test suite passed!"


if __name__ == '__main__':
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testPairings()
    print "Success!  All tests pass!"
    print "Below are tests for extra functionalities:"
    testSimulatedTournament()


