import os
import requests
from bs4 import BeautifulSoup


memberid = input("Enter your memberid:")
userName = input("Enter your username:")
os.makedirs(userName)

url = "http://universe.lego.com/en-us/community/creationlab/displaycreationlist.aspx?memberid=%s&show=48" % memberid


r = requests.get(url)
status = r.status_code
creationList = r.content
soup = BeautifulSoup(creationList)

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
	<title>%s</title>
	<body>
	%s
	%s
	%s
	%s
	%s
	</body>
	</html>
	''' %(titleT, title, description, tags, challenge, date)

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
		filename = 'hobino/' + titleT + str(i) + '.jpg'          
		newImg = open(filename, 'wb')
		newImg.write(img)
		newImg.close()
		i = i + 1
		
	newHTML = open('hobino/' + titleT + '.html', 'w')
	newHTML.write(page)
	newHTML.close()
	







