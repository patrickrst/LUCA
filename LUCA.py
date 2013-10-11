#! /usr/bin/python3
# -*- coding: utf-8 -*-
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
import time
import requests
from bs4 import BeautifulSoup

app = "LUCA"
majver = "0.4"
minver = ""

# Write window title
os.system("title {0} v{1}".format(app, majver))
localUserName = input("\nEnter your Creation Lab Username: ")

# Search the localUserName on the Creation Lab
url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}&order=oldest&show=12".format(
    localUserName)
r = requests.get(url).content
soup = BeautifulSoup(r)
creations = []
for link in soup.find_all('a'):
    if link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx":
        creations.append('http://universe.lego.com{0}'.format(link.get('href')))

# Check if links were found/added for the entered username
# If not, close LUCA
if not creations:
    print('The username "{0}" was not found on the Creation Lab.'.format(
        localUserName))
    input("\nPress Enter to close LUCA.")
    raise SystemExit(0)

# Check if one link contains the localUserName
r = requests.get(creations[0]).content
soup = BeautifulSoup(r)
onlineUserName = soup.find(
    id="ctl00_ContentPlaceHolderUniverse_HyperLinkUsername")

# The username entered matched the one online,
# begin downloading the creations
if localUserName.lower() == onlineUserName.string.lower():
    memberid = onlineUserName.get('href')[63:99]
    print("\nYour Creations are now downloading, {0}.\n".format(localUserName))

# The name could not be found, close LUCA.
else:
    print('The username "{0}" does not appear to match with any usernames online.'
    .format(localUserName))
    input("\nPress Enter to close LUCA.")
    raise SystemExit(0)


url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?memberid={0}&show=48".format(
    memberid)
r = requests.get(url).content
soup = BeautifulSoup(r)

# Create folder to save files in,
# unless it already exists
if not os.path.exists(localUserName):
    os.mkdir(localUserName)


creations = []
for link in soup.find_all('a'):
    if link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx":
        creations.append('http://universe.lego.com{0}'.format(link.get('href')))


# ------- INFORMATION GATHERING ------- #

for creation in creations:
    r = requests.get(creation).content
    soup = BeautifulSoup(r)

    title = soup.find_all('h1')[2]   # add .string to get only the text
    titleString = title.string
    titleString = titleString.replace('/', '')
    description = soup.find(id="creationInfoText")
    tags = soup.find_all(class_='column-round-body')[3].contents[9]
    challenge = soup.find(id="CreationChallenge").contents[1].contents[1]

    date = soup.find(id="CreationUser")
    date.div.decompose()
    date.a.decompose()

    # Create string versions of the text
    title_str = str(title)
    description_str = str(description)

    # Update adnd fix original HTML errors
    # WARNING: Do not change the tabbed strings to spaces
    title_str = title_str.replace("<h1>", '<h1 class="center">')
    description_str = description_str.replace("</br></br></br></br></br></br>", "")
    description_str = description_str.replace("									", "")
    description_str = description_str.replace('''
								''', "")

    # List of non-HTML files to download
    imgLinkList = []
    i = 1

    # Populate the list
    for imgLink in soup.find_all('a'):
        if imgLink.get('href')[0:13] == "GetMedia.aspx":
            imgLinkList.append('http://universe.lego.com/en-us/community/creationlab/{0}'
            .format(imgLink.get('href')))

    # ------- INFORMATION WRITING ------- #

    # List of illegal characters for filenames
    blacklist = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    # The folders to which the creations will be saved
    mainfilepath = os.path.join(os.getcwd(), localUserName)
    subfilepath = os.path.join(mainfilepath, titleString)

    # If the folder for each Creation does not exist, create it
    if not os.path.exists(subfilepath):
        os.makedirs(subfilepath)

    # List of images in Creation
    image_list = []

    for imgLink in imgLinkList:
        r = requests.get(imgLink)
        img = r.content

        # Original filename
        filename = "{0}{1}.jpg".format(titleString, i)
        for char in blacklist:
            if char in filename:
                # If an illegal character is found, replace it with a dash
                filename = filename.replace(char, "-")

        # Write all non-HTML files.
        with open(os.path.join(subfilepath, filename), 'wb') as newImg:
            newImg.write(img)

        # Display filename after it was installed,
        # part of LUCA's non-GUI progress bar.
        print(filename)
        i += 1
        image_list.append(filename)
        img_num = i - 1

        # Original filename
        HTMLfilename = "{0}.html".format(titleString)
        for char in blacklist:
            if char in HTMLfilename:
                # If an illegal character is found, replace it with a dash
                HTMLfilename = HTMLfilename.replace(char, "-")

        # Code to display the images
        img_display = '<a href="file:///{0}"><img src="file:///{0}" width="300" /></a>'.format(
            os.path.join(mainfilepath, filename))

    # HTML document structure
    page = '''<!-- Creation archive saved by LUCA on {1} UTC
https://github.com/Brickever/LUCA#readme -->

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{0}</title>
<style>
{9}
</style>
</head>
<body>
{2}
{3}
{4}
<h1 class="center">Images</h1>
<p class="center">{8}</p>
<h1 class="center">Challenge</h1>
{5}{6}
Creation saved from
<br>
<a href="{7}" target="_blank">{7}</a>
</body>
</html>
    '''.format(titleString, time.strftime("%c", time.gmtime()),
               title_str, description_str, tags, challenge, date, creation,
               img_display * img_num, ".center { text-align: center; }")

    # Write HTML documents.
    with open(os.path.join(subfilepath, HTMLfilename), "wt") as newHTML:
        newHTML.write(page)

    # Display filename after it was installed,
    # part of LUCA's non-GUI progress bar.
    print(HTMLfilename)


# ------- Final Actions ------- #

# Get list of all downloaded files
num_of_files = []
for root, dirnames, filenames in os.walk(mainfilepath):

    # Remove Thumbs.db from list
    if "Thumbs.db" in filenames:
        filenames.remove("Thumbs.db")

    # Remove ehthumbs.db from list
    if "ehthumbs.db" in filenames:
        filenames.remove("ehthumbs.db")

    # Remove Desktop.ini from list
    if "Desktop.ini" in filenames:
        filenames.remove("Desktop.ini")

    # How many files were downloaded?
    for files in filenames:
        myfiles = os.path.join(root, files)
        num_of_files.append(myfiles)

# Display success message containing number
# of files downloaded and where they were saved.
print('\n{0} files successfully downloaded and saved to \n"{1}"'.format(
    len(num_of_files), mainfilepath))
input("\nPress Enter to close LUCA.")
raise SystemExit(0)
