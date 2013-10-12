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
majver = "1.0"
minver = ""


def charCheck(text, folders=False):
    """Checks for illegal characters in text"""
    # List of illegal characters for filenames
    illegal_chars = ["\\", "/", ":", "*", "?", '"', "'", "<", ">", "|"]

    if folders:
        illegal_chars.append(".")
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

    # A(n) illegal character(s) was found
    if illa:
        for char in found_chars:
            # Replace it (them) with a space
            text = text.replace(char, "-")
    return text


def searchUser(username, take2=False):
    """Find a username on the Creation Lab"""
    # Set initial page number
    num_of_pages = 1

    if take2:
        # Backup search method for finding the username on the Creation Lab
        print("take2")
        url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}&show=48&page={1}".format(
            username, num_of_pages)
    else:
        print("not take2")
        # Search the username on the Creation Lab
        url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}&order=oldest&show=48&page={1}".format(
            username, num_of_pages)

    # Get search page content
    r = requests.get(url).content
    soup = BeautifulSoup(r)

    # Find area containing number of pages
    num_of_pages = soup.find("p", class_="column-navigation").get_text()

    # Remove unneeded text: part 1
    num_of_pages = num_of_pages.replace('''
\t\t\t\t\t\t»
Show:

12
24
36
48

Order:

Most Recent
Oldest
Rating''', "")

    # Remove unneeded text: part 2
    num_of_pages = num_of_pages.replace('''\r
\t\t\t\t\t\t\xad\r
\t\t\t\t\t\t«\r
\t\t\t\t\t\t\t\r
\t\t\t\t\t\t''', "")

    # Remove unneeded text: part 3
    num_of_pages = num_of_pages.replace("\r\n\t\t\t\t\t\t\r\n\n", "")
    num_of_pages = num_of_pages.replace("1 of ", "")

    # Convert the number to an integer
    num_of_pages = int(num_of_pages)

    # Holding pen for  possible Creations by the user
    creations = []

    # Gather the creations from the page
    for link in soup.find_all('a'):
        if link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx":
            creations.append('http://universe.lego.com{0}'.format(
                link.get('href')))

    # Check if links were found/added for the entered username
    # If not, close LUCA
    if not creations:
        print('The username "{0}" was not found on the Creation Lab.'.format(
            username))
        input("\nPress Enter to close LUCA.")
        raise SystemExit(0)

    num_of_creations = len(creations) - 1
    names = []

    # Get the usernames from all Creations from the search
    while num_of_creations != -1:
        r = requests.get(creations[num_of_creations]).content
        soup = BeautifulSoup(r)
        onlineUserName = soup.find(
            id="ctl00_ContentPlaceHolderUniverse_HyperLinkUsername")
        names.append(onlineUserName)
        num_of_creations -= 1

    # These are the first search results
    if not take2:
        memberid = checkUser(username, names, take2=False)
        return (memberid, num_of_pages)

    # These are the second search results
    elif take2:
        memberid = checkUser(username, names, take2=True)
        #main(True, memberid=memberid, num_of_pages=num_of_pages, localUserName=username)
        return (memberid, num_of_pages)


def checkUser(locuser, webusers, take2=False):
    """Checks if this is the proper username"""
    # Get the proper index of all the names to check
    num_of_names = len(webusers) - 1
    print(num_of_names)
    found_name = True

    while num_of_names > -1:
        # The username entered was found
        # begin downloading the creations
        if locuser.lower() == webusers[num_of_names].string.lower():
            memberid = webusers[num_of_names].get('href')[63:99]
            return memberid

        # That username did not match, try next one
        #elif locuser.lower() != webusers[num_of_names].string.lower():
        else:
            num_of_names -= 1
            found_name = False

    # We are using the first search results
    if not take2:
        #print("not take2")
        # Search again, using a different query
        if not found_name:
            searchUser(locuser, take2=True)

    # We are using the second query results
    if take2:
        #print("take2")
        # The username could not be found
        if not found_name:
            #print("final fail")
            print('The username "{0}" does not appear to match with any usernames online.'
                  .format(locuser))
            input("\nPress Enter to close LUCA.")
            raise SystemExit(0)


        #while num_of_names != -1:

            ## The username entered was found
            ## begin downloading the creations
            #if locuser.lower() == webusers[num_of_names].string.lower():
                #memberid = webusers[num_of_names].get('href')[63:99]
                #return memberid

            ## That username did not match, try next one
            #else:
                #num_of_names -= 1



    # We are using the second query results
    #elif take2:
        #print("take2")

        # Let's assume search 2 will find it
        #found_name = True

        #while num_of_names != -1:

            ## The username entered was found
            ## begin downloading the creations
            #if locuser.lower() == webusers[num_of_names].string.lower():
                #memberid = webusers[num_of_names].get('href')[63:99]
                #return memberid

            ## That username did not match, try next one
            #else:
                #num_of_names -= 1
                #found_name = False

        ## The username could not be found
        #if not found_name:
            #print('The username "{0}" does not appear to match with any usernames online.'
                  #.format(locuser))
            #input("\nPress Enter to close LUCA.")
            #raise SystemExit(0)


def byteme(text):
    """Convert text to binary"""
    bin_text = str.encode(text, encoding="utf-8", errors="strict")
    return bin_text


def main(userfound=False, memberid=False, num_of_pages=False, localUserName=False):
    """Main LUCA Process"""
    if not userfound:
        localUserName = input("\nEnter your Creation Lab Username: ")
        #print('Searching the Creation Lab for user "{0}"'.format(localUserName))
        # Search for the username on the Creation Lab
        memberid, num_of_pages = searchUser(localUserName, take2=False)

    print("\nYour Creations are now downloading, {0}.\n".format(
        localUserName))

    print(memberid, num_of_pages, localUserName)

    # Create folder to save files in,
    # unless it already exists
    if not os.path.exists(localUserName):
        os.mkdir(localUserName)

    # List of Creations
    creations = []

    user_url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?memberid={0}&show=48".format(memberid)
    user_r = requests.get(user_url).content
    user_soup = BeautifulSoup(user_r)
    # Add the creations from page 1 to the list
    for user_link in user_soup.find_all('a'):
        if user_link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx":
            creations.append('http://universe.lego.com{0}'.format(
                user_link.get('href')))

    # If there is more than one page of Creations,
    # add the creations from the other pages to the list
    if num_of_pages > 1:
        new_url = user_url[:-1]
        while num_of_pages != 0:
            page_url = "{0}{1}".format(new_url, num_of_pages)
            num_of_pages -= 1

            req = requests.get(page_url).content
            soup = BeautifulSoup(req)
            for page_link in soup.find_all('a'):
                if page_link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx":
                    creations.append('http://universe.lego.com{0}'.format(
                        page_link.get('href')))

    # ------- Information Gathering ------- #

    for creation in creations:
        r = requests.get(creation).content
        soup = BeautifulSoup(r)

        title = soup.find_all('h1')[2]
         # add .string to get only the text
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
        date_str = str(date)
        tags_str = str(tags)

        # Update and fix original HTML errors
        title_str = title_str.replace("</h1>", "")
        title_str = '{0} - Created by <a target="_blank" href="{1}{2}.aspx">{2}</a></h1>'.format(
            title_str, "http://mln.lego.com/en-us/PublicView/", localUserName)
        description_str = description_str.replace("</br></br></br></br></br></br>",
                                                  "")
        description_str = description_str.replace("\t\t\t\t\t\t\t\t\t", "")
        description_str = description_str.replace('''
    \t\t\t\t\t\t\t\t''', "")
        tags_str = tags_str.lstrip('''<p>
    </p>''')
        date_str = date_str.replace("\t\t\t\t\t\t\t\t\t", "")
        date_str = date_str.replace("<br/>", "")
        date_str = date_str.replace("\t\t\t\t\t\t\t\t", "")
        date_str = date_str.replace('''<div class="column-round-body" id="CreationUser">
    <p>''', "")
        date_str = date_str.replace('''
    ''', "")
        tags_str = tags_str.replace(r'<a href="',
                                    r'<<a target="_blank" href="http://universe.lego.com/en-us/community/creationlab/')
        date_str = date_str.replace(r"</div>", "")

        # List of non-HTML files to download
        imgLinkList = []
        i = 1

        # Populate the list
        for imgLink in soup.find_all('a'):
            if imgLink.get('href')[0:13] == "GetMedia.aspx":
                imgLinkList.append(
                    'http://universe.lego.com/en-us/community/creationlab/{0}'
                    .format(imgLink.get('href')))

        # ------- Information Writing ------- #

        # The folders to which the creations will be saved
        mainfilepath = os.path.join(os.getcwd(), localUserName)

        # Check for illegal characters in the creation title
        subfilepathclean = charCheck(titleString, True)
        subfilepath = os.path.join(mainfilepath, subfilepathclean)

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
            filename = charCheck(filename)

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
                if header == b"PK\x03\x04\x14":
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
            try:
                print(new_filename)
            # If for some VERY strange reason if the filename cannot be displayed
            except UnicodeEncodeError:
                print("Filename display error. Creation saved!")
                pass

            i += 1
            image_list.append(new_filename)
            img_num = len(image_list)

        # HTML document structure
        page = '''<!-- Creation archive saved by LUCA v{11} on {0} UTC
https://github.com/Brickever/LUCA#readme
https://github.com/le717/LUCA#readme -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>{1}</title>
    <style>
    {2}
    {3}
    {4}
    {5}
    </style>
</head>

<body>
{6}
<div class="line-separator"></div>

<h2>Challenge</h2>
<p>{8}
<br>Submitted {9}
<div class="line-separator"></div>

<h2>Description</h2>
{10}

<h2>Images</h2>
<div id="pictures">'''.format(
            time.strftime("%c", time.gmtime()), titleString,
            "body { background-color: #212121; color: white; text-align: center;}",
            "h1, h2 {font-family: sans-serif; }",
            '''.line-separator {
        height:1px; background:#717171;
        border-bottom:1px solid #313030;
        }''',
            "a { color: #A9A9A9; text-decoration: none;}",
            title_str, localUserName, challenge, date_str, description_str,
            majver)

        # Original HTML filename
        HTMLfilename = "{0}.html".format(titleString)

        # Check for illegal characters in the filenames
        HTMLfilename = charCheck(HTMLfilename)

        # Write initial HTML document structure
        with open(os.path.join(subfilepath, HTMLfilename), "wb") as newHTML:
            newHTML.write(byteme(page))

        im = 0
        while im < img_num:

            # Code to display every image
            img_display = '''
<a title="Click for larger image" href="{0}"><img src="{0}" width="300" /></a>'''.format(
                image_list[im])

            # Write the HTML for the images
            with open(os.path.join(subfilepath, HTMLfilename), "ab") as updateHTML:
                updateHTML.write(byteme("{0}".format(img_display)))
            # Display each image once
            im += 1

        # Write the final HTML code
        with open(os.path.join(subfilepath, HTMLfilename), "ab") as finishHTML:
            finishHTML.write(byteme('''
</div>
<br>
<div class="line-separator"></div>
<br>
Original Creation Link
<br>
<a href="{0}" target="_blank">{0}</a>
<br>
<br>
Tags
<br>
{1}
</body>
</html>
    '''.format(creation, tags_str)))

        # Display filename after it was installed,
        # part of LUCA's non-GUI progress bar.
        try:
            print(HTMLfilename)
        # If for some VERY strange reason if the filename cannot be displayed
        except UnicodeEncodeError:
            print("Filename display error. Creation saved!")
            pass

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

if __name__ == "__main__":
    # Write window title
    os.system("title {0} v{1}".format(app, majver))
    main()