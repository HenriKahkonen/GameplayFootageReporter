import dotenv, os
from utils.errors import (
    EnvReadError
)

# Specify your operation variables in this file and in the '.env' file. Check the '.env.example' file for formatting guide, copy and rename the file and replace the paths with your own.

# To specify a path or a custom name, use quotation marks
# To specify a boolean (= True / False) value, specify the value with an uppercase first letter

# Do you want to specify a specific folder where the output of the analysis is saved in
# If False, outputs to an /Output directory under this program
# If True, outputs to the directory specified in the .env file
OUTPUT_TO_CUSTOM_DIRECTORY = False

# Do you want a .txt log of the operation
LOG_OUTPUT = True

# Do you want a comma-separated-value list (readable with e.g. Google Sheets and Microsoft Excel) of the operation?
CSV_OUTPUT = True # set to false if you don't want a csv report
CSV_SEPARATOR = ";" # character to separate values in csv. Cannot be set to "," if CSV_FLOATS_WITH_COMMA is set to true.
CSV_FLOATS_WITH_COMMA = True # if true floats are represented as 3,14 instead of 3.14


# Do you want a Sqlite database of the video files?
# Sqlite is a small, local database that holds all of the database data in a static file instead of a
# complex database engine running on the machine
SQLITE_OUTPUT = True

# In which formats are your video files? Ffmpeg will try to parse video types listed here.
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
DEFAULT_PLATFORM = "PC" # If folder doesn't match any platform prefix
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
    "PICO-8" : "Pico-8",
    "PS2" : "Sony Playstation 2",
    "PSX" : "Sony Playstation",
    "Sega Genesis" : "Sega Genesis",
    "Sega Saturn" : "Sega Saturn",
    "SNES" : "Super Nintendo Entertainment System",
    "TIC-80" : "TIC-80",
    "XBOX" : "XBox",
    "Virtual Boy" : "Nintendo Virtual Boy",
    "Web" : "Browser"
}

# Other custom categories for footage folders
# Specify as a tuple what the cateory is and what the platform of that category is
# This allows
FOOTAGE_CATEGORIES = {
    "Doom Mods" : ("Doom Mod","PC"),
    "Suomipelit": ("Suomipelit","PC")
}

# Do you want to cross-reference the scanned folders to an Obsidian database to try to find additional data on the games?
SCAN_OBSIDIAN_DB = True
# What headers to search for in Obsidian files and what are their datatypes?
OBSIDIAN_HEADERS = {
    "year": int,
    "Genret": [str],
    "tags" : [str],
    "Playtime_hrs" : int,
    "Playtime_mins" : int,
    "Rating": float, # 0 - 5, 3,5 allowed
    "Play_Status" : str,
    "Pelisarja" : str,
    "Kehittäjä(t)" : [str],
    "Julkaisija(t)" : [str],
}

# Load env variables and throw errors if appropriate
env_vars = dotenv.load_dotenv()
GAMEPLAY_FOOTAGE_PATH=os.getenv("GAMEPLAY_FOOTAGE_PATH",None)
OBSIDIAN_DB_PATH=os.getenv("OBSIDIAN_DB_PATH",None)
CUSTOM_OUTPUT_PATH=os.getenv("CUSTOM_OUTPUT_PATH",None)

