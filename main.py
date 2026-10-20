import os, decimal, datetime, math, sys, argparse # native functions in python
import cv2 # pip install opencv-python
decimal.getcontext().prec = 3
from utils.errors import (EnvReadError,InvalidPathError)
from utils.scanFiles import (getFootageFolders, getGameMetadata)
from utils.validateFiles import (ValidateFootagePath, ValidateObsidianPath, ValidateOutputPath)
from utils.testHelpers import UnpackTests, ValidateTestFiles, GenerateTestFileValidationBaseline, DeleteTestFiles
from utils.settingsLoader import Settings
from pathlib import Path
import time

def GameplayFootageReportGenerator(argv: list[str]) -> int:

    # Parse arguments of script

    parser = argparse.ArgumentParser(description="Gameplay footage report generator")
    
    parser.add_argument("--initialize-obsidian", action="store_true", help="Initialize the Obsidian database to supplement the video footage folder")

    parser.add_argument("--footage-path", type=str, metavar="Footage_path", help="The path where the footage is stored")
    parser.add_argument("--obsidian-path", type=str, metavar="Obsidian_path", help="The path where the complementary obsidian database folder is located")
    parser.add_argument("--output-to", type=str, metavar="Output_path", help="The custom path to output the analysis report to")
    parser.add_argument("--calculate-test-file-hash-baseline", action="store_true", help="Create a JSON file of all of the test files' sha256 hashes so that their integrity can be verified.")
    #parser.add_argument("--create-env-files", action="store_true", help="Add the template .env files.")
    parser.add_argument("--unpack-tests", action="store_true", help="Unpack the test files for the program.")
    parser.add_argument("--remove-test-files", action="store_true", help="Free disk space by removing the test files.")

    args = parser.parse_args(argv[1:])

    print("\n"+"*"*56+"\n*** Gameplay footage and game notes report generator ***\n"+"*"*56+"\n")

    try:
        if args.calculate_test_file_hash_baseline:
            GenerateTestFileValidationBaseline()
            return 0
    except AttributeError:
        pass # allow for commenting out temporarily used funcs

    if args.unpack_tests:
        print("Unpacking the test files from the .zip archive...")
        UnpackTests()
        print("Validating test files...")
        ValidateTestFiles()
        print("Test data succesfully unpacked.")
        return 0

    if args.remove_test_files:
        print("Removing test files from ./Test/Testdata...")
        DeleteTestFiles()
        print("Test data cleared.")
        return 0

    # Validate paths and arguments

    settings = Settings()

    # TODO: remove test paths
    settings.GAMEPLAY_FOOTAGE_PATH = ("/mnt/data/repos/GameplayFootageReporter/Test/Testdata/Gameplay-Footage")
    settings.OBSIDIAN_DB_PATH = ("/mnt/data/repos/GameplayFootageReporter/Test/Testdata/Obsidian-Notes")
    settings.OUTPUT_TO_CUSTOM_DIRECTORY = False

    Footage_path_candidate = args.footage_path or settings.GAMEPLAY_FOOTAGE_PATH
    Obsidian_path_candidate = args.obsidian_path or settings.OBSIDIAN_DB_PATH
    Output_path_candidate = args.output_to or settings.CUSTOM_OUTPUT_PATH
    Initialize_Obsidian = args.initialize_obsidian

    settings.GAMEPLAY_FOOTAGE_PATH = ValidateFootagePath(
        footage_path=Footage_path_candidate
        )
    settings.OBSIDIAN_DB_PATH = ValidateObsidianPath(
        obsidian_path=Obsidian_path_candidate, 
        scan_obsidian=settings.SCAN_OBSIDIAN_DB, 
        initialize_obsidian=Initialize_Obsidian
    )

    if Initialize_Obsidian:
        # TODO
        print("WIP not implemented yet")
        return 0

    settings.OUTPUT_PATH = ValidateOutputPath(
        output_path=Output_path_candidate,
        use_custom_output_path=settings.OUTPUT_TO_CUSTOM_DIRECTORY, 
        sysargv=argv
    )

    print("Generating report from gameplay footage and note directories...\n")
    print(f"Reading gameplay footage from '{settings.GAMEPLAY_FOOTAGE_PATH}'")
    if settings.SCAN_OBSIDIAN_DB:
        print(f"Reading supplementary Obsidian note database from '{settings.OBSIDIAN_DB_PATH}'")
    print(f"Writing analysis files to '{settings.OUTPUT_PATH}'.\n")

    Games_raw = getFootageFolders(settings.GAMEPLAY_FOOTAGE_PATH)

    if len(Games_raw) == 0:
        print("There are no footage folders under your footage directory!")
        return 1

    print(f"Found {len(Games_raw)} game footage folders.\n")
    
    for GameFolder in Games_raw:

        game_footage_path = Path(settings.GAMEPLAY_FOOTAGE_PATH / GameFolder)

        game_metadata = getGameMetadata(game_footage_path, settings)

        print(game_metadata)
        

    # TODO: go from there

    return 1

if __name__ == "__main__":
    GameplayFootageReportGenerator(sys.argv)

exit()

#Folder = r"/run/media/henkka/TOSHIBA EXT/V/Pelifootage";
UseTestFolder = False
if UseTestFolder:
    Folder = r"./Data/TestData/";
LogOutput = True # set to false if you dont' want to write the print logs to file
CSVSep = ";" # character to separate values in csv
CSVFloatComma = True # if true floats are represented as 3,14 instead of 3.14

try:
    OutputCsv = open(r'./Output/GameFootagesData.csv','w')
except FileNotFoundError:
    OutputCsv = open(r'./Output/GameFootagesData.csv','x')
try:
    OutputLog = open(r'./Output/GameFootagesLog.txt','w')
except FileNotFoundError:
    OutputLog = open(r'./Output/GameFootagesLog.txt','x')
try:
    OutputHtml = open(r'./Output/GameFootagesTable.html','w')
except FileNotFoundError:
    OutputHtml = open(r'./Output/GameFootagesTable.html','x')



def writeCsv(text):
    OutputCsv.write(text)
def writeLog(text):
    print(text)
    if LogOutput:
        OutputLog.write(text+"\n")
def writeHtml(text):
    OutputHtml.write(text)

if CSVSep ==  "," and CSVFloatComma:
    writeLog("Error: CSV Float character cannot be comma ',' if CSV separator is set to ','")
    raise Exception("CSV Float character cannot be comma ',' if CSV separator is set to ','")

 # Initialize the html and csv files
with open("./Data/HtmlTableBase.html") as base:
    writeHtml(base.read())
writeCsv("Game title"+CSVSep+"Release year"+CSVSep+"Total file size in GB"+CSVSep+"Total video length"+CSVSep+"Total video files"+CSVSep+"Video length avg"+CSVSep+"File extensions\n")

startTime = datetime.datetime.now()

for directory in os.listdir(Folder): # Directory should in most cases correspond to a game in footage folder
    totalfilesize = 0
    totalfilesize = 0
    totalvideolength = 0
    totalvideofiles = 0
    videolengthavg = 0
    fileExtensions = []

    if directory[-1] == ')' and directory[-6] == '(': # If folder name ends with release year, i.e. "(2025)"
        gamename = directory[:-7]
        gameyear = directory[-5:-1]
    else:
        gamename = directory
        gameyear = ""

    for path, subdirs, files in os.walk(Folder+"/"+directory):
        for filename in files:

            totalfilesize += decimal.Decimal(os.path.getsize(path+"/"+filename)/1073741824) # Filesize in gigabytes

            extension = str(os.path.splitext(filename)[1]) 
            if extension not in fileExtensions:
                fileExtensions.append(extension)

            if filename.endswith(".mp4"):
                totalvideofiles=totalvideofiles+1
                videodata=cv2.VideoCapture(path+"\\"+filename)
                frames=int(videodata.get(cv2.CAP_PROP_FRAME_COUNT))
                fps=int(videodata.get(cv2.CAP_PROP_FPS))
                totalvideolength=totalvideolength+int(frames/fps) #seconds

    totalfilesize = str(decimal.Decimal(totalfilesize))
    if CSVFloatComma:
        totalfilesize = totalfilesize.replace(".",",")

    try:
        videolengthavg = str(int(totalvideolength/totalvideofiles))
    except ZeroDivisionError:
        videolengthavg = str(0)

    totalvideolength =str(int(totalvideolength/60))
    totalvideofiles = str(totalvideofiles)
    fileExtensions.sort()
    extensionsList = ""
    for x in fileExtensions:
        extensionsList = extensionsList+x+" "

    writeCsv("/"+gamename+"/"+CSVSep+gameyear+CSVSep+totalfilesize+CSVSep+totalvideolength+CSVSep+totalvideofiles+CSVSep+videolengthavg+CSVSep+extensionsList+"\n")
    writeHtml("<tr><td>"+gamename+"</td><td>"+gameyear+"</td><td>"+totalfilesize+"</td><td>"+totalvideolength+"</td><td>"+totalvideofiles+"</td><td>"+videolengthavg+"</td><td>"+extensionsList+"</td></tr>\n")  
    
    writeLog(gamename+" ("+gameyear+"): "+totalfilesize+"GB and "+totalvideolength+"min in "+totalvideofiles+" file(s) ("+extensionsList+"), avg video length of "+videolengthavg+"sec.")

endTime = datetime.datetime.now()
TimeDelta = (endTime - startTime)
TotalSeconds = int(TimeDelta.total_seconds())
OpMinutes = math.floor(TotalSeconds / 60)
OpSeconds = TotalSeconds % 60

writeLog("Footage listing complete in "+str(OpMinutes)+" min, "+str(OpSeconds)+" seconds.")

with open("./Data/HtmlTableSortScript.html") as script:
    writeHtml(script.read())