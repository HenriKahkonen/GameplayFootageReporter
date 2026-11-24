# Gameplay Footage Report generator

A tool for video editors and video game content creators. 

## What it does and how it works

This console app is useful if you record a lot of video game gameplay footage and, optionally, write notes about the games you play. The tool can be used to scan a directory of gameplay footage in different video formats and cross-reference a matching Obsidian markdown file database to create a data report of the games played and the amount of their footage. This data report can then be used to identify how much footage there exists per game in minutes and in megabytes as well as identify trends in e.g. what genres the user has played and in what gaming platforms. I personally use this tool to help strip down excessive amounts of unnecessary footage as well as identify which games are recorded at an unnecessarily large bitrate (an NES game doesn't need as high bitrate video as a modern AAA game). The obsidian markdown files' scanning also allows for some data analysis on e.g. games review scores, playtimes, platforms and genres.

Some of the data (game platform, release year, game name and length and size of video clips) can be deduced from the video footage files themselves, and supplementary metadata can be extracted from the Obsidian database.

The app can be used if you have a collection of footage folders in a footage directory named for example like:

```
> your/path/footage/
>> DOS - Boppin' (1991)/
>> PSX - Rayman (1995)/
>> Web - Cookie Clicker (2013)/
>> Wingspan (2020)/
```

Each game's footage directory names can follow a naming convention where the directory name contains a prefix acting as a shorthand for the gaming platform or category of the game as well as a four-digit release year inside brackets at the directory name's end.

The behaviour to either parse the release platforms or release years as well as the platform shorthand-full name mappings can be edited in the file **settings.py**.

To cross-reference an obsidian markdown file, the obsidian files need to be named to match the directory names of their respective game footage directories:

```
>your/path/obsidian/notes/games/
>> DOS - Boppin' (1991).md
>> PSX - Rayman (1995).md
>> Web - Cookie Clicker (2013).md
>> Wingspan (2020).md
```

The app, when run, then attemps to match a .md file for every footage directory it finds and to read from the matching .md file the game's:

- Release year
- Platform(s)
- Categories
- Genres
- Rating
- Playtime in minutes and hours
- Game series
- Developers
- Publishers

By parsing the markdown files frontmatter, separated from the rest of the markdown text by the long line symbols "---" at the note's beginning. The markdown files should thus be formatted to use Obsidian's frontmatter formatting like below:

```
# (PS2 - Mega Man X (2004).md

---
year: 2004
Genret:
  - "[[Tasoloikkapelit]]"
  - "[[Shooter platformer -pelit|Shooter platformer -pelit]]"
tags:
  - Peli
Alusta(t): "[[PS2]]"
Kategoria(t):
Playtime_hrs: "5"
Playtime_mins: "45"
Pelisarja: "[[Mega Man -pelisarja]]"
Kehittäjä(t):
  - "[[Capcom Production Studio 1]]"
Julkaisija(t):
  - "[[Capcom]]"
Play_Status: "[[Completed]]"
Rating: 3,5
---
```

The key mapping can be edited in the file **settings.py** to allow for custom naming of these variables. My notes are written in Finnish, so the template settings file follows mostly finnish naming conventions.

Paths to the footage master directory and the optional Obsidian markdown database are set in a **.env** file at the project root. Copy and rename the **.env.example** file and replace the paths with your own.

## How to install and use the app

### Prerequisities

The app launches subprocesses to probe the video files' metadata and this process uses **ffmpeg**. Before using the application make sure ffmpeg is installed in your system and is properly set in your PATH environment variables. This is also a python app, so make sure **python3.14 or higher** is installed on the machine. The app isn't very complex and it might run with older versions as well but this is not tested.

### Installing the app

The app runs in a python virtual environment (venv). This way the app doesn't install anything outside of its own directory and the user's machine remains unchanged if the app is installed or deleted.

To create the venv and install the dependencies the program needs, download the files, navigate to the project's root and run:

```
# macOS/Linux
python -m venv venv
source venv/bin/activate # if using fish terminal (e.g. in CachyOS), run source venv/bin/activate.fish
pip install -r requirements.txt

# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### Updating the paths and settings

Like described above, the user's footage directory and markdown file directory must be set in the **.env** file. Copypaste the **.env.example** and edit it to contain:

```
GAMEPLAY_FOOTAGE_PATH=~/Videos/Gameplay-footage
OBSIDIAN_DB_PATH=~/Documents/Obsidianvaults/Game-notes/or/whatever/if/not/using/the/obsidian/feature
CUSTOM_OUTPUT_PATH=~/Documents/Gameplay-Footage-Report/or/whatever/if/not/using/custom/output/folder
```
Then read through the **settings.py** and edit the settings to your liking. 

### Generating the gameplay footage and notes data report

After the settings have been properly defined, and the venv has been activated, run:

> python main.py

If so desired, the footage and obsidian markdown file paths can also be supplied via command line arguments. This overrides any values set in the .env file:

> python main.py --footage-path "path/to/your/footage/dir" --obsidian-path "path/to/your/obsidian/notes" ---output-to "path/to/your/desired/output/"

This reads through your footage directories and outputs a .csv file, an SQLite database and a text log file based on the settings file. The csv and the SQLite file can the be studied to identify trends in the data.

### Initializing the Obsidian markdown database

WIP: not implemented yet


