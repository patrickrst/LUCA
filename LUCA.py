#! /usr/bin/python3

"""
    This file is part of LUCA.

    LUCA - LEGO Universe Creation (Lab) Archiver
    Created 2013 Brickever <http://systemonbrick.wordpress.com/>

    LUCA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    LUCA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with LUCA If not, see <http://www.gnu.org/licenses/>.
"""
import os
import sys
import time
import requests
from bs4 import BeautifulSoup

app = "LUCA"
majver = "0.4"
minver = ""

# Write window title
os.system("title {0} v{1}".format(app, majver))
localUserName = input("\nEnter your Creation Lab Username: ")


url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}&order=oldest&show=12".format(localUserName)
r = requests.get(url).content
soup = BeautifulSoup(r)
creations = []
for link in soup.find_all('a'): 
    if link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx": 
        creations.append('http://universe.lego.com' + link.get('href'))

#Check if links were found/added for the entered username 
if not creations:
    print('The username "{0}" does not result in any search entry on the Creation Lab.'.format(localUserName))
    input("Press Enter to close LUCA.")
    raise SystemExit(0) 
        

r = requests.get(creations[0]).content
soup = BeautifulSoup(r)
onlineUserName = soup.find(id="ctl00_ContentPlaceHolderUniverse_HyperLinkUsername")
if localUserName.lower() == onlineUserName.string.lower():
    memberid = onlineUserName.get('href')[63:99]
    print("\nYour Creations are now downloading, {0}.\n".format(localUserName))
else:
    # The username entered could not be found online
    # TODO: update message to include onlineUserName or memberid,
    # or does this mean the username does not exist?
    print('The username "{0}" does not match with the one online.'.format(localUserName))
    input("Press Enter to close LUCA.")
    raise SystemExit(0) 





url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?memberid={0}&show=48".format(memberid)
r = requests.get(url).content
soup = BeautifulSoup(r)

# Create folder to save files in,
# unless it already exists
if not os.path.exists(localUserName):
    os.mkdir(localUserName)


creations = []
for link in soup.find_all('a'): 
    if link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx": 
        creations.append('http://universe.lego.com' + link.get('href'))
        

for creation in creations:

    r = requests.get(creation)
    status = r.status_code
    creationPage = r.content
    soup = BeautifulSoup(creationPage)

    title = soup.find_all('h1')[2]   #add .string to get only the text
    titleT = soup.find_all('h1')[2].string
    titleT = titleT.replace('/','')
    description = soup.find(id="creationInfoText")
    tags = soup.find_all(class_='column-round-body')[3].contents[9]
    challenge = soup.find(id="CreationChallenge").contents[1].contents[1]

    date = soup.find(id="CreationUser")
    date.div.decompose()
    date.a.decompose()
    
    page = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{0}</title>
</head>
<body>
{1}
{2}
{3}
{4}
{5}
</body>
</html>
    '''.format(titleT, title, description, tags, challenge, date)

    # Old code
    #imgM = soup.find("a", id="ctl00_ContentPlaceHolderUniverse_HyperLinkMainImage").get('href')
    #imgM = "http://universe.lego.com/en-us/community/creationlab/" + imgM

    imgT = []
    i = 1

    for img in soup.find_all('a'):
        if img.get('href')[0:13] == "GetMedia.aspx":
            imgT.append('http://universe.lego.com/en-us/community/creationlab/'+ img.get('href'))

    # --- BEGIN NEW CODE --- #
    # List of illegal characters for filenames
    blacklist = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    # Makes it easier to understand what is going on.
    filepath = os.path.join(os.getcwd(), localUserName)
    # --- END NEW CODE --- #

    for imgLink in imgT:
        r = requests.get(imgLink)
        img = r.content            

        # --- BEGIN NEW CODE --- #
        # Original filename  
        filename = "{0}{1}.jpg".format(titleT, i)
        for char in blacklist:  
            if char in filename:
                # If an illegal character is found, replace it with a dash
                filename = filename.replace(char, "-")


        # Write all non HTML files.  
        with open(os.path.join(filepath, filename), 'wb') as newImg:
            newImg.write(img)
       # --- END NEW CODE --- #

        # Display filename after it was installed, 
        # part of LUCA's non-GUI progress bar.
        print(os.path.basename(filename), end="\n")
        i = i + 1

    # --- BEGIN NEW CODE --- #
    # TODO: Is supposed to do the same thing as non-HTML stuff,
    # but it fails for some reason.
    HTMLfilename = "{0}.html".format(titleT)
    for char in blacklist:  
        if char in HTMLfilename:
            HTMLfilename = HTMLfilename.replace(char, "-")

    # Write HTML documents.        
    with open(os.path.join(filepath, HTMLfilename), "wt") as newHTML:
        newHTML.write(page)
    # --- END NEW CODE --- #

    # Display filename after it was installed, 
    # part of LUCA's non-GUI progress bar.
    print(os.path.basename(HTMLfilename), end="\n")


# Get list of all downloaded files
num_of_files = os.listdir(os.path.join(os.getcwd(), localUserName))
# Remove Thumbs.db from list
if "Thumbs.db" in num_of_files:
    num_of_files.remove("Thumbs.db")

# Display success message containing number
# of files downloaded and where they were saved.
print('\n{0} files successfully downloaded and saved to \n"{1}"'.format(len(num_of_files), os.path.join(os.getcwd(), localUserName)))
input("\nPress Enter to close LUCA.\n")
raise SystemExit(0)
    








