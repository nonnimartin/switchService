import oauth2
import json
import datetime
import time
import sys

monthsMap = {
 'Mar': 3,
 'Feb': 2,
 'Aug': 8,
 'Sep': 9,
 'Apr': 4,
 'Jun': 6,
 'Jul': 7,
 'Jan': 1,
 'May': 5,
 'Nov': 11,
 'Dec': 12,
 'Oct': 10
 }

def writeJsonDate(dateValue, handle):
    jsonFileStr               = readFileToText('lastDate.json')
    lastHandleDateMap         = json.loads(jsonFileStr)
    newLastDateMap            = {'lastDate' : str(dateValue)}
    lastHandleDateMap[handle] = newLastDateMap

    with open('lastDate.json', 'w') as outfile:
        json.dump(lastHandleDateMap, outfile)

def getLastDate(jsonFile, handle):

    jsonFileStr = readFileToText(jsonFile)
    lastDate    = json.loads(jsonFileStr)

    if handle in lastDate.keys():
        record      = lastDate[handle]
        lastDate    = record['lastDate']
    else:
        writeJsonDate(0, handle)
        # random early date
        lastDate    = '1559436480'
        

    if lastDate == '':
        return 0
    else:
        return int(lastDate)

def getAuthorizationMap(authFile):

    authMap = {}
    fileStr     = readFileToText(authFile)
    jsonFile    = json.loads(fileStr)
    consumerKey = jsonFile['consumer_key']
    consumerSec = jsonFile['consumer_secret']
    oAuthKey    = jsonFile['oAuth_Key']
    oAuthSec    = jsonFile['oAuth_Secret']
    authMap['consumerKey'] = consumerKey
    authMap['consumerSec'] = consumerSec
    authMap['oAuthKey']    = oAuthKey
    authMap['oAuthSec']    = oAuthSec

    return authMap

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

def getDateFromString(dateString):

    if dateString == '' or dateString == None:
        return None

    splitString = dateString.split(' ')
    month       = monthsMap[splitString[1]]
    day         = int(splitString[2])
    year        = int(splitString[5])
    timeStr     = splitString[3]
    hour        = int(timeStr.split(':')[0])
    minutes     = int(timeStr.split(':')[1])

    return time.mktime(datetime.datetime(year, month, day, hour, minutes, 0, 0).timetuple())

def oauth_req(url, http_method="GET", post_body="", http_headers=None):
    authMap  = getAuthorizationMap('auth.json')
    consumer = oauth2.Consumer(key=authMap['consumerKey'], secret=authMap['consumerSec'])
    token    = oauth2.Token(key=authMap['oAuthKey'], secret=authMap['oAuthSec'])
    client   = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers )
    return content

def readFileToText(filePath):
    f = open(filePath, "r")
    return f.read()

def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v))
        for k, v in dictionary.items())

def getLatestTweetsMap(username):

    tweetsJson = oauth_req('https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=' + username)
    tweetsList = json.loads(tweetsJson)

    tweetsListConverted = convert_keys_to_string(tweetsList)
    tweetsMap  = {}

    for tweet in tweetsListConverted:
        try:
            dateKey     = str(tweet['created_at'])
            dateKeyUnix = int(getDateFromString(dateKey))
            thisMap     = convert_keys_to_string(tweet['entities'])
            if 'media' in thisMap.keys():
                tweetsMap[dateKeyUnix] = str(thisMap['media'][0]['media_url_https'])
        except:
            continue

    return tweetsMap

def getMostRecentTweet(tweetsMap):
    unixTimeSet = tweetsMap.keys()
    highestNum  = getHighestNumber(unixTimeSet)
    return tweetsMap[highestNum]

def getMostRecentTweetDate(tweetsMap):
    unixTimeSet = tweetsMap.keys()
    highestNum  = getHighestNumber(unixTimeSet)
    return highestNum

def getHighestNumber(numSet):
    numSet.sort()
    size = len(numSet)
    if size > 0:
        return numSet[size - 1]
    else:
        return 0

def main():

        handle    = sys.argv[1]
        if isinstance(handle, str):
            tweetsMap = getLatestTweetsMap(handle)
            lastDate  = getLastDate('lastDate.json', handle)
            mostRecentDate = getMostRecentTweetDate(tweetsMap)

            if lastDate == '':
                writeJsonDate(getMostRecentTweetDate(tweetsMap), handle)
                getMostRecentTweet(tweetsMap)
                print(getMostRecentTweet(tweetsMap))
            elif lastDate == 0:
                # cover case where new subscription was created
                # don't send any SMS
                print('None')
            elif mostRecentDate > lastDate:
                writeJsonDate(getMostRecentTweetDate(tweetsMap), handle)
                print(getMostRecentTweet(tweetsMap))
            else:
                print('None')
        else:
            print('None')



if __name__ == '__main__':
    main()