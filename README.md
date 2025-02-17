# Gordian
'Gordian' is an experimental techno fantasy strategic text game
```
║    ┏━╮┏━┓┏━┓╺┳┓╻┏━┓┏┓╻    ║
║    ┃╺┓┃ ┃┣┳┛ ┃┃┃┣━┫┃┗┫    ║
║    ┗━┛┗━┛╹┗╸╺┻┛╹╹ ╹╹ ╹    ║
║                           ║
║         a Game by         ║
║       Daniel Sandner      ║ 
║         © 2024-25         ║
```

Command a growing settlement through text-based decision making. Build fortifications, manage resources, and protect your followers from a mysterious threat that lurks in the shadows.

Developer screenshot (v0.0.2a):

```console

GORDIAN  Turn: 15        Food: 10 | Wood: 2 | Stone: 20 
--------------------------------------------------------
           People: 0  |  Hero: Unavl (Quest)
                  Structures: HOUSE:1
--------------------------------------------------------
--- Events ---
  Resources collected!
  Rumors spread of a powerful Obelisk in the distance.  
  Resources collected!
  Miners found a hidden cache! You gain 10 stone.       
  stone: 20
--------------------------------------------------------
(C)ollect, (B)uild, (H)ero, (P)eople, (U)pgrades, (Q)uit
                        Action:
```

Developer screenshot (v0.0.1a):

```console
Turn: 0
Resources - Wood: 10, Stone: 10, Food: 10
Structures - Houses: 0, Farms: 0, Mines: 0
People - Total: 0, In Houses: 0
In Farms: 0
In Mines: 0
Hero Available: No
Popularity Points: 0
Victory Condition - Wood: 50, Stone: 50, Food: 50, People: 50
What would you like to do? (collect/build/status/hero/quit): collect
Resources collected!

========================================
       A raid! You lose 5 stone.        
========================================


========================================
An adversary attacks and steals some resources!
========================================


Turn: 1
Resources - Wood: 13, Stone: 7, Food: 10
Structures - Houses: 0, Farms: 0, Mines: 0
People - Total: 0, In Houses: 0
In Farms: 0
In Mines: 0
Hero Available: No
Popularity Points: 0
Victory Condition - Wood: 50, Stone: 50, Food: 50, People: 50
What would you like to do? (collect/build/status/hero/quit): build
What would you like to build? (house/farm/mine): house
House built!

Turn: 2
Resources - Wood: 3, Stone: 2, Food: 10
Structures - Houses: 1, Farms: 0, Mines: 0
People - Total: 0, In Houses: 0
In Farms: 0
In Mines: 0
Hero Available: No
Popularity Points: 0
Victory Condition - Wood: 50, Stone: 50, Food: 50, People: 50
What would you like to do? (collect/build/status/hero/quit): collect
Resources collected!

```

Refactored structure:

```
gordian/
├── gordian.py     (main.py - Entry point)
├── config.json     (General game settings)
├── core/
│   ├── game.py      (Core game logic - Game class)
│   ├── buildings.py (Building classes)
│   ├── resources.py (Resource class)
│   ├── hero.py      (Hero class)
│   ├── events.py     (Event handling - Event classes, EventManager)
│   ├── ui.py         (User interface functions)
│   └── audio.py      (Audio handling functions)
├── data/
│   ├── buildings.json
│   ├── events.json
│   ├── characters.json
│   └── story.json
├── assets/          (NEW - All game assets)
│   ├── sound/       (Sound effect files)
│   ├── music/       (Music files)
│   └── themes/      (Theme definition files - JSON)
│       └── default.json (Example theme file)
└── save/            (Save files)
```
