from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import datetime
import xml.etree.cElementTree as ET
import xml.etree.ElementTree
from bs4 import BeautifulSoup

monthsMap = {
 'March': 3,
 'February': 2,
 'August': 8,
 'September': 9,
 'April': 4,
 'June': 6,
 'July': 7,
 'January': 1,
 'May': 5,
 'November': 11,
 'December': 12,
 'October': 10
 }

def getHTML(url):
    req = requests.get(url)

    if req.status_code == 200:
        return req.content
    else:
        print('Error from request to ' + str(url))
        return

def writeXML(dateValue):
    root = ET.Element("root")
    doc = ET.SubElement(root, "doc")
    ET.SubElement(doc, "lastDate", name="lastDate").text = dateValue
    tree = ET.ElementTree(root)
    tree.write("lastDateData.xml")

def getDateFromXML(xmlFile):
    tree = xml.etree.ElementTree.parse(xmlFile).getroot()
    for child in tree.iter(tag='lastDate'):
        return(child.text)

def getMaxDateRowUrl(rowsList):
    maxDateIndex = 0
    maxDate      = datetime.datetime(1970, 1, 1, 1, 1)
    for row in rowsList:
        if row[1] is not None:
            thisDate = getDateFromString(row[1])
            if thisDate > maxDate:
                maxDate = thisDate
        maxDateIndex += 1

    return rowsList[maxDateIndex - 1][2]

def dateIsNew(maxDate, lastDate):
    if lastDate == None:
        return True
    else:
        return (maxDate > lastDate)

def getMaxDate(rowsList):
    #cheap to process but could be refactored to process
    #once for this and row url
    maxDateIndex = 0
    maxDate      = datetime.datetime(1970, 1, 1, 1, 1)
    for row in rowsList:
        if row[1] is not None:
            thisDate = getDateFromString(row[1])
            if thisDate > maxDate:
                maxDate = thisDate
        maxDateIndex += 1

    return rowsList[maxDateIndex - 1][1]

def getImageFromHTML(html):
    soup = BeautifulSoup(html, "html.parser")
    images = soup.find_all("img")
    imagesLength = len(images)
    #more than slightly hacky way of getting image url but
    #no tag seems unique, and url seems to be reliably final element
    return(images[imagesLength - 1]['src'])

def getDateFromString(dateString):

    if dateString == '' or dateString == None:
        return None

    splitString = dateString.split(' ')
    month       = monthsMap[splitString[0]]
    day         = int(splitString[1].replace(',', ''))
    year        = int(splitString[2])
    time        = splitString[4]
    hour        = int(time.split(':')[0])
    minutes     = time.split(':')[1]

    if 'PM' in minutes:
        amPm    = 'PM'
        minutes = int(minutes.replace('PM', ''))
    else:
        amPm    = 'AM'
        minutes = int(minutes.replace('AM', ''))

    dateTime = datetime.datetime(year, month, day, hour, minutes, 0, 0)
    return dateTime

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1EDKCtVAOoYPsfhGND-_IqhvXpAq4I2d5T6UErGcCKTg'
SAMPLE_RANGE_NAME = 'Sheet1'

def main():

    #handle oAuth for Google Sheet
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:

        #get max date from google sheet
        maxDate = getDateFromString(getMaxDate(values))
        #get last date from xml file
        lastDate = getDateFromString(getDateFromXML("lastDateData.xml"))

        if dateIsNew(maxDate, lastDate):
            # get image url and write to xml file the latest datetime
            imageUrl = getImageFromHTML(getHTML(getMaxDateRowUrl(values)))
            #write last date to xml file
            writeXML(getMaxDate(values))
            print(imageUrl)

if __name__ == '__main__':
    main()