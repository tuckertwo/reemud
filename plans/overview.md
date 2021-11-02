# System overview

> You find yourself in the middle of a reasonably-sized public square in the
> middle of a big city.
> As it appears to be around 5:12 PM, you are in the middle of a small stream
> of commuters on foot.
> 
> From here, you take your bearings and see to your north a public library,
> and to the east a small shelter over a staircase.
> To the west is Piedmont Avenue, and to the south is Harrisburg Street.

This document gives an overview of the architecture, story, and technical
characteristics of the rMUD system.
Furthermore, it should outline technical commitments (*i.e.* programming
decisions that ought to be thought out before we make them),
grading strategy and plans,
and procedures to follow (coding style, unit tests, *etc.*).

# Story
The story at the moment is unclear, but a few details have been determined.
The character is to start in a generic urban center from the mid-twentieth
century (maybe),
which exists to provide a central location for the player to start, become
acquainted with the setting of the game,
conduct certain plot-relevant tasks,
and go to other locations.

On a high level, the story should be manually created,
but individual subplots can and should involve automatically-generated areas,
tasks, puzzles, and rules.

Certain objects and characters should be interactive, allowing the user to talk,
tinker, and use the environment to their advantage.
For example, a player may find during a puzzle a scrap of paper with an encoded
message; an Enigma machine found elsewhere, when given a key based on other
clues and the message, would reveal a hint.
Or, say, a player may need to study the behavior of rapidly-evolving birds
(without being harmed themselves)
to satisfy the request of a non-player character.

Certain regions may be dymanically created, randomized, destroyed, or modified
as the game goes on and players interact with the world.
This adds variety and ensures that uncharacteristically-difficult randomly
generated puzzles or other things do not cripple the game.

Players may be able to interact with each other,
and specific tasks may require cooperation (or competition or combat) among
two players.
The system shall be designed to allow two players in the same place to interact,
and should also provide means for geographically-distributed players to interact
(to a more limited extent).

# Technical architecture
The system shall be written in Python using object-oriented methods.
(This is a parameter of the assignment.)
Players should interact with the system via Telnet or a WebSockets/AJAX-based
web client.
Each player should be connected to an individual process running an
"interposer" application that manages the state of one particular player.
Said application should then communicate with a database or server
to preserve said player's state and allow for interaction between multiple
players and the environment.
