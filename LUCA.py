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
import imghdr
import requests
from bs4 import BeautifulSoup

app = "LUCA"
majver = "0.4"
minver = ""


def charCheck(text):
    """Checks for illegal characters in text"""
    # List of all illegal characters
    illegal_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|", "."]

    found_chars = []

    # Get the length of the text, minus one for proper indexing
    len_of_text = len(text) - 1

    # Assign variable containing result of check; default to False
    illa = False

    # -1 so the first character is caught too
    while len_of_text != -1:

        # This character is allowed
        if text[len_of_text] not in illegal_chars:
            # The check goes in reverse, checking the last character first.
            len_of_text -= 1

        # This character is not allowed
        elif text[len_of_text] in illegal_chars:
            # Change value of variable; kill the loop, as we only need
            # to find one illegal character to end the (ball) game.
            illa = True
            found_chars.append(text[len_of_text])
            len_of_text -= 1

    # An illegal character was found
    if illa:

        # Assign variable containing the illegal character
        #char = text[len_of_text]
        return (True, found_chars)

    # Return False only if no illegal character is found
    return (False, None)


def searchUser(username, take2=False):
    """Find a username on the Creation Lab"""
    # Backup search method for finding the username on the Creation Lab
    if take2:
        url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}&order=oldest&show=12".format(
            localUserName)

    # Search the username on the Creation Lab
    url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}".format(
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
        return memberid

    elif localUserName.lower() != onlineUserName.string.lower():
        searchUser(username, take2=True)

    # The name could not be found, close LUCA.
    else:
        print('The username "{0}" does not appear to match with any usernames online.'
              .format(localUserName))
        input("\nPress Enter to close LUCA.")
        raise SystemExit(0)

# Write window title
os.system("title {0} v{1}".format(app, majver))
localUserName = input("\nEnter your Creation Lab Username: ")

# Search for the username on the Creation Lab
memberid = searchUser(localUserName, take2=False)

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


# ------- Information Gathering ------- #

for creation in creations:
    r = requests.get(creation).content
    soup = BeautifulSoup(r)

    title = soup.find_all('h1')[2]   # add .string to get only the text
    titleString = title.string
    titleString = titleString.replace('/', '')
    titleString = titleString.strip()
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

    # ------- Information Writing ------- #

    # List of illegal characters for filenames
    blacklist = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    # The folders to which the creations will be saved
    mainfilepath = os.path.join(os.getcwd(), localUserName)
    subfilepath = os.path.join(mainfilepath, titleString)

    # Check for illegal characters in the creation title
    answer, chars = charCheck(titleString)

    # If there were illegal chracters, replace them with a dash
    if answer:
        for item in chars:
            new_titleString = titleString.replace(item, "-")
            subfilepath = os.path.join(mainfilepath, new_titleString)

    # If the folder for each Creation does not exist, create it
    if not os.path.exists(subfilepath):
        os.makedirs(subfilepath)

    # List of images in Creation
    image_list = []

    for imgLink in imgLinkList:
        r = requests.get(imgLink)
        img = r.content

        # Original filename
        filename = "{0}{1}".format(titleString, i)

        # Check for illegal characters in the filenames
        reply, letters = charCheck(filename)

        # If an illegal character is found, replace it with a dash
        if reply:
            for item in letters:
                filename = filename.replace(item, "-")

        # Write all non-HTML files.
        with open(os.path.join(subfilepath, filename), 'wb') as newImg:
            newImg.write(img)

        #  This is an GIF image
        if imghdr.what(os.path.join(subfilepath, filename)) == "gif":
            new_filename = "{0}.gif".format(filename)
            os.replace(os.path.join(subfilepath, filename),
                       os.path.join(subfilepath, new_filename))

        # This is an JPG image
        elif imghdr.what(os.path.join(subfilepath, filename)) == "jpeg":
            new_filename = "{0}.jpg".format(filename)
            os.replace(os.path.join(subfilepath, filename),
                       os.path.join(subfilepath, new_filename))

        else:
            # Read the first 5 bytes of the file
            with open(os.path.join(subfilepath, filename), "rb") as f:
                header = f.readline(5)

            # This is an LDD LXF model <http://ldd.lego.com/>
            if header[2] == b"PK":
                new_filename = "{0}.lxf".format(filename)
                os.replace(os.path.join(subfilepath, filename),
                           os.path.join(subfilepath, new_filename))

            # This is an WMV video
            elif header == b"0&\xb2u\x8e":
                new_filename = "{0}.wmv".format(filename)
                os.replace(os.path.join(subfilepath, filename),
                           os.path.join(subfilepath, new_filename))

            # This is an MPG video
            elif header == b"\x00\x00\x01\xba!":
                new_filename = "{0}.mpg".format(filename)
                os.replace(os.path.join(subfilepath, filename),
                           os.path.join(subfilepath, new_filename))

            # This is an AVI video
            # NOTE: This was found in an H.264 AVI file
            elif header == b"\x00\x00\x00\x1cf":
                new_filename = "{0}.mpg".format(filename)
                os.replace(os.path.join(subfilepath, filename),
                           os.path.join(subfilepath, new_filename))

            # This is MOV video
            else:
                new_filename = "{0}.mov".format(filename)
                os.replace(os.path.join(subfilepath, filename),
                           os.path.join(subfilepath, new_filename))

            """
            The AVI and MOV file type is a container, meaning different types
            of codecs (what the real format is) can vary.
            In this sense, AVI and MOV file detection is fuzzy.
            """

        # Display filename after it was installed,
        # part of LUCA's non-GUI progress bar.
        print(new_filename)
        i += 1

        image_list.append(new_filename)
        img_num = i - 1

        # Original HTML filename
        HTMLfilename = "{0}.html".format(titleString)

        # Check for illegal characters in the filenames
        response, symbol = charCheck(HTMLfilename)

        # If an illegal character is found, replace it with a dash
        if response:
            for piece in symbol:
                HTMLfilename = HTMLfilename.replace(piece, "-")

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
# of files downloaded from number of Creations, and where they were saved.
print('''
{0} files from {1} Creations successfully downloaded and saved to
"{2}"'''.format(
    len(num_of_files),
    len(os.listdir(mainfilepath)),
    mainfilepath))
input("\nPress Enter to close LUCA.")
raise SystemExit(0)
