#! /usr/bin/python3

import os
import sys
import requests
from bs4 import BeautifulSoup

# Write window title
os.system("title LUCA v0.2")
localUserName = input("\nEnter your Creation Lab username: ")


url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?SearchText={0}&order=oldest&show=12".format(localUserName)
r = requests.get(url).content
soup = BeautifulSoup(r)
creations = []
for link in soup.find_all('a'): 
    if link.get('href')[0:49] == "/en-us/Community/CreationLab/DisplayCreation.aspx": 
        creations.append('http://universe.lego.com' + link.get('href'))
        

r = requests.get(creations[0]).content
soup = BeautifulSoup(r)
onlineUserName = soup.find(id="ctl00_ContentPlaceHolderUniverse_HyperLinkUsername")
if localUserName == onlineUserName.string:
    memberid = onlineUserName.get('href')[63:99]
else:
    print("The username your enter does not match with the one online.")
    input("Press Enter to close LUCA.")
    raise SystemExit(1) 





url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?memberid={0}&show=48".format(memberid)
r = requests.get(url).content
soup = BeautifulSoup(r)
os.makedirs(localUserName)


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
    
    page = '''
    <!DOCTYPE html>
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
        
    for imgLink in imgT:
        r = requests.get(imgLink)
        img = r.content
        filename = localUserName + '/' + titleT + str(i) + '.jpg'          
        newImg = open(filename, 'wb')
        newImg.write(img)
        newImg.close()
        i = i + 1

    with open(localUserName + '/' + titleT + '.html', 'w') as newHTML:    
        newHTML.write(page)
    #newHTML = open(localUserName + '/' + titleT + '.html', 'w')
    #newHTML.write(page)
    #newHTML.close()
    








