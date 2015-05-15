# Overview

This is a project for [Full Stack Web Developer Nanodegree](https://www.udacity.com/course/nd004) provided by [Udacity](https://www.udacity.com). 

In this project, I was required to write a Python module that uses the PostgreSQL database to keep track of players and matches in a game tournament.

The game tournament will use the Swiss system for pairing up players in each round: players are not eliminated, and each player should be paired with another player with the same number of wins, or as close as possible.

In addition to the basic requirements, I implememted several extra feathures:

* Prevent rematches between players.
* Support odd number of players. It's handled by assigning one player a "bye" (skipped round). A bye counts as a free win. A player should not receive more than one bye in a tournament.
* Support games where a draw (tied game) is possible. 
* When two players have the same number of wins, rank them according to OMW (Opponent Match Wins), the total number of wins by players they have played against.
* Support more than one tournament in the database, so matches do not have to be deleted between tournaments. 

# Usage

1. Install [Vagrant](http://vagrantup.com) and [VirtualBox](https://www.virtualbox.org)
1. Download the source code and unzip it
1. Launch the Vagrant VM and log in
```sh
$ vagrant up
$ vagrant ssh
$ cd path/to/project/folder
```
1. Initialize database
```sh
$ psql
=> \i tournament.sql
=> \q
```
1. Run test script
```sh
$ python tournament_test.py
```

# References

All Web sites, books, forums, blog posts, github repositories etc. that I referred to or used are listed in "references.md". 
