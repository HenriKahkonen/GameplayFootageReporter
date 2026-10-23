"""
Specify your operation variables in this file and in the '.env' file. Check the '.env.example' file for formatting guide, copy and rename the file and replace the paths with your own.

To specify a path or a custom name, use quotation marks
To specify a boolean (= True / False) value, specify the value with an uppercase first letter

Do you want to specify a specific folder where the output of the analysis is saved in
If False, outputs to an /Output directory under this program
If True, outputs to the directory specified in the .env file
"""

import os
import dotenv


# Specify your operation variables in this file and in the '.env' file. 
# Check the '.env.example' file for formatting guide, copy and rename the file 
# and replace the paths with your own.

# To specify a path or a custom name, use quotation marks
# To specify a boolean (= True / False) value, specify the value with an 
# uppercase first letter

# Do you want to specify a specific folder where the output of the analysis is saved in
# If False, outputs to an /Output directory under this program
# If True, outputs to the directory specified in the .env file
OUTPUT_TO_CUSTOM_DIRECTORY = False
# Do you want a .txt log of the operation
LOG_OUTPUT = True

# Do you want a comma-separated-value list (readable with e.g. Google Sheets 
# and Microsoft Excel) of the operation?
CSV_OUTPUT = True # set to false if you don't want a csv report
CSV_SEPARATOR = ";" # character to separate values in csv. Cannot be set to "," if CSV_FLOATS_WITH_COMMA is set to true.
CSV_FLOATS_WITH_COMMA = True # if true floats are represented as 3,14 instead of 3.14

# Do you want a Sqlite database of the video files?
# Sqlite is a small, local database that holds all of the database data in 
# a static file instead of a complex database engine running on the machine
SQLITE_OUTPUT = True

# In which formats are your video files? Ffmpeg will try to parse video types 
# listed here.
SUPPORTED_VIDEO_FILETYPES = [
    ".mp4", ".mov", ".mkv", ".mpg", ".ts", ".ogg", ".avi"
]

# Which files are skipped
IGNORED_FILETYPES = [
    ".ignr"
]

# Naming conventions:
# If you follow a naming convention like such:
#
# /Footage/NES - Battletoads (1991)
#
# The set to following to true to above folder to resolve to
# {Gamename: "Battletoads", Year: "1991", Platform: "Nintendo Entertainment System"}
# If the following are set to False, the same folder gets parsed to the database as
# {Gamename: "NES - Battletoads (1991), Year: None, Platform: None"}
PLATFORM_IN_FOLDERNAME = True
PLATFORM_PREFIX_SEPARATOR = " - "
RELEASE_YEAR_IN_FOLDERNAME = True

# What shorthands are used
# Specify as "shorthand_as_in_the_folder_name" : "The full name of the platform"
GAME_PLATFORMS = {
    "00" : "Not a game",
    "Arcade" : "Pelihallipelit",
    "Atari 2600" : "Atari 2600",
    "CDi" : "Philips CD-i",
    "DOS" : "MS-DOS",
    "Dreamcast" : "Sega Dreamcast",
    "GB" : "Nintendo Game Boy",
    "GBA" : "Nintendo Game Boy Advance",
    "GBC" : "Nintendo Game Boy Color",
    "Lautapelit" : "Lautapelit",
    "Mobiilipelit" : "Mobiilipelit",
    "N64" : "Nintendo 64",
    "NES" : "Nintendo Entertainment System",
    "NGC" : "Nintendo Gamecube",
    "NS"  : "Nintendo Switch",
    "PC"  : "PC",
    "PICO-8" : "Pico-8",
    "PS2" : "Sony Playstation 2",
    "PS3" : "Sony Playstation 3",
    "PS4" : "Sony Playstation 4",
    "PS5" : "Sony Playstation 5",
    "PSX" : "Sony Playstation",
    "Sega Genesis" : "Sega Genesis",
    "Sega Saturn" : "Sega Saturn",
    "SNES" : "Super Nintendo Entertainment System",
    "TIC-80" : "TIC-80",
    "XBOX" : "Xbox",
    "XBOX360" : "Xbox 360",
    "XBOX-1" : "Xbox One",
    "XBOX-SX" : "Xbox Series X",
    "Virtual Boy" : "Nintendo Virtual Boy",
    "Web" : "Browser",
}

# If folder doesn't match any platform prefix, it will be treated if it had 
# this platform. If the default platform doesnt match any of the keys in the 
# platform map, it will be treaded as a custom defined platform name.
# DEFAULT_PLATFORM = "SNES" -> Games default platform will be "Super Nintendo Entertainment System"
# DEFAULT_PLATFORM = "Tiger Handheld" -> Games default platform will be "Tiger Handheld"
DEFAULT_PLATFORM = "PC"

# Other custom categories for footage folders
# If you want to group the footage into other custom non-platform categories such as
#
# / Doom (2016)
# / Doom Mods - Ancient Aliens (2016)
# / Doom Mods - Ghostbusters Doom (2002)
# / DOS - Jazz Jackrabbit (1994)
#
# If so, specify as a tuple what the cateory is and what the gaming platform of
# that category is
# # Only one prefix will be scanned from the folder name and custom categories
# are checked before checking game platform.
# If a custom category is found in the folder name, a platform is not checked
# from the folder name, instead it is defined here.
# As with the default platform, you may define either a shorthand that maps
# to a full name in GAME_PLATFORMS or a custom platform name.
#
FOLDERNAME_CUSTOM_CATEGORIES = True
FOOTAGE_FOLDERNAME_CATEGORIES = {
    "Doom Mods" : ("Doom Mod","PC"),
    "Suomipelit": ("Suomipelit","PC")
}

# Do you want to cross-reference the scanned folders to an Obsidian database
# to try to find additional data on the games?
SCAN_OBSIDIAN_DB = True

# These are the metadata values the program tries to assign
# when scanning the footage and notes folders.
# The left hand values are hard-coded to the program,
# and changing them will break things,
# but you can change the right hand values to match your Obsidian note headers.
OBSIDIAN_METADATA_MAPPING = {
    "year": "year",
    "platforms" : "Alusta(t)",
    "categories" : "Kategoria(t)",
    "genres" : "Genret",
    "rating" : "Rating",
    "playtime_hrs" : "Playtime_hrs",
    "playtime_mins" : "Playtime_mins",
    "game_series" : "Pelisarja",
    "developers" : "Kehittäjä(t)",
    "publishers" : "Julkaisija(t)",
}

# What headers to search for in Obsidian files' frontmatter and what are their datatypes?
# Note that the values must match to their counterparts in OBSIDIAN_METADATA_MAPPING
OBSIDIAN_HEADERS = {
    "year": int,
    "Genret": [str],
    "tags" : [str],
    "Alusta(t)" : [str],
    "Kategoria(t)" : [str],
    "Playtime_hrs" : int,
    "Playtime_mins" : int,
    "Rating": float,
    "Play_Status" : str,
    "Pelisarja" : str,
    "Kehittäjä(t)" : [str],
    "Julkaisija(t)" : [str],
}


OBSIDIAN_RATING_MIN = 0
OBSIDIAN_RATING_MAX = 5
OBSIDIAN_RATING_USE_STAR_SYSTEM = True # Makes non-half step ratings invalid, e.g. 4,7 not allowed

# Load env variables and throw errors if appropriate
dotenv.load_dotenv()
GAMEPLAY_FOOTAGE_PATH=os.getenv("GAMEPLAY_FOOTAGE_PATH",None)
OBSIDIAN_DB_PATH=os.getenv("OBSIDIAN_DB_PATH",None)
CUSTOM_OUTPUT_PATH=os.getenv("CUSTOM_OUTPUT_PATH",None)
