## Gameplay Footage Reporter

A tool for video editors and content creators. 

Do you have a lot of gameplay footage lying around? This script can be used to gather data about large quantities of gameplay footage in .mp4 format to help identify which clips can be cut down in the interest of saving space on your drive.

Script scans its target directory recursively and generates a report as a **.csv file** as well as **a sortable table in an .html document** that states e.g. 
* Total size of files per subfolder
* Total length of .mp4 clips in minutes in per subfolder
* Average length of a clip in per subfolder
* What file extensions are present per subfolder

Script currently identifies clip lengths and such from .mp4 files, file size total cumulates from any files within a subfolder.

# How to use

Script requires Python to run (duh). Also needed dependency is opencv-python, which can be installed with command 

> pip install opencv-python

Edit the Gamefootagelister.py file to specify the path to your gameplay footage directory at row 6. If desired, you can test the script with a smaller dataset by placing files in the TestData subdirectory and setting the "UseTestFolder" value to True.

For best results, in your gameplay footage directory, include the game's release date in brackets in the game's folder name, for example:

> ./Gamefootage/Cyberpunk 2077 (2020)/footage...  
> ./Gamefootage/Witcher 3 (2015)/footage...  
> ./Gamefootage/Heroes of Might and Magic III (1999)/footage...  
> ./Gamefootage/The Sims 2 (2004)/footage...  
> ./Gamefootage/Crash Bandicoot (1996)/footage...

After specifying your gameplay directory, run the script.
