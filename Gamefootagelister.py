import os, decimal, datetime, math # native functions in python
import cv2 # pip install opencv-python
decimal.getcontext().prec = 3

## SPECIFY YOUR FOOTAGE FOLDER PATH AND OUTPUT PATHS
Folder = r"I:\V\Pelifootage\\";
UseTestFolder = False
if UseTestFolder:
    Folder = r".\Data\TestData\\";

try:
    OutputCsv = open(r'.\Output\GameFootagesData.csv','w')
except FileNotFoundError:
    OutputCsv = open(r'.\Output\GameFootagesData.csv','x')
try:
    OutputLog = open(r'.\Output\GameFootagesLog.txt','w')
except FileNotFoundError:
    OutputLog = open(r'.\Output\GameFootagesLog.txt','x')
try:
    OutputHtml = open(r'.\Output\GameFootagesTable.html','w')
except FileNotFoundError:
    OutputHtml = open(r'.\Output\GameFootagesTable.html','x')

LogOutput = True # set to false if you dont' want to write the print logs to file
CSVSep = ";" # character to separate values in csv
CSVFloatComma = True # if true floats are represented as 3,14 instead of 3.14

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
with open(".\\Data\\HtmlTableBase.html") as base:
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

    for path, subdirs, files in os.walk(Folder+"\\"+directory):
        for filename in files:

            totalfilesize += decimal.Decimal(os.path.getsize(path+"\\"+filename)/1073741824) # Filesize in gigabytes

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

    writeCsv("\""+gamename+"\""+CSVSep+gameyear+CSVSep+totalfilesize+CSVSep+totalvideolength+CSVSep+totalvideofiles+CSVSep+videolengthavg+CSVSep+extensionsList+"\n")
    writeHtml("<tr><td>"+gamename+"</td><td>"+gameyear+"</td><td>"+totalfilesize+"</td><td>"+totalvideolength+"</td><td>"+totalvideofiles+"</td><td>"+videolengthavg+"</td><td>"+extensionsList+"</td></tr>\n")  
    
    writeLog(gamename+" ("+gameyear+"): "+totalfilesize+"GB and "+totalvideolength+"min in "+totalvideofiles+" file(s) ("+extensionsList+"), avg video length of "+videolengthavg+"sec.")

endTime = datetime.datetime.now()
TimeDelta = (endTime - startTime)
TotalSeconds = int(TimeDelta.total_seconds())
OpMinutes = math.floor(TotalSeconds / 60)
OpSeconds = TotalSeconds % 60

writeLog("Footage listing complete in "+str(OpMinutes)+" min, "+str(OpSeconds)+" seconds.")

with open(".\\Data\\HtmlTableSortScript.html") as script:
    writeHtml(script.read())