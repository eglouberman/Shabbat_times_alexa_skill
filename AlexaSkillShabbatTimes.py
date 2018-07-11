import urllib,json
import datetime
import calendar

#Python script that runs with AWS Lambda
#Shabbat times Alexa Skill ---> gives the starting time of shabbat for any given date and any given place.
def convertToPacific(time):
    #converts any time (UTC) to pacific time
    if int(time[0]) <10 and time[1] == ":":
        time = "0"+time
    t = int(time[0:2])
    minutes = int(time[3:5])
    ampm= time[9:]
    if t< 8 or t == 12:
        if ampm == "AM":
            ampm = "PM"
        else:
            ampm = "AM"
    if t==12: 
        t= 4
    elif t ==11:
        t=3
    elif t==10:
        t= 2
    elif t== 9: 
        t= 1
    elif t ==8:
        t= 12
    elif t == 7:
        t= 11
    elif t== 6:
        t= 10
    elif t==5: 
        t= 9
    elif t ==4: 
        t= 8
    elif t ==3: 
        t= 7
    elif t == 2: 
        t= 6
    elif t == 1: 
        t= 5
    if minutes <10:
        mins = "0" + str(minutes)
    else:
        mins = str(minutes)
    return str(t) +":" + mins + " " + ampm

def find_sunset_time(date, address):
    #takes a date in (YYYY-MM-DD) format as a string and address as a string ("Los Angeles")
    GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    geo_args = {
        'address': address
    }
    
    url = GEOCODE_BASE_URL + '?' + urllib.urlencode(geo_args)
    
    result = json.load(urllib.urlopen(url))
    
    latitude= json.dumps([s['geometry']['location']['lat'] for s in result['results']])
    latitude =latitude[1:-1]
    longitude = json.dumps([s['geometry']['location']['lng'] for s in result['results']])
    longitude =longitude[1:-1]
    
    #finding the sunset time based off of coordinates of city
    sunset_time_URL = 'https://api.sunrise-sunset.org/json?lat=' + latitude + '&lng=' + longitude + "&date="+date
    print sunset_time_URL
    result_time = json.load(urllib.urlopen(sunset_time_URL))
    sunset_time = result_time['results']['sunset']
    return sunset_time

def configureToFriday(k):
    #Shabbat is on Friday night of every week. We need to convert whatever date that we have to get the Friday of that week
    #paraneter if input is a date in (YYYY-MM-DD) format as a string
    year = int(k[0:4])
    month = int(k[5:7])
    day1 = int(k[8:])
    date = datetime.datetime(year,month, day1)
    while date.weekday()!=4:
        day1 += 1
        try:
            date = datetime.datetime(year,month, day1)
        except ValueError:
            month+=1
            day1 = 1
            date = datetime.datetime(year,month,day1)
    return date

def getDayandMonth(fridayDate):
    #gets a date and converts it to a readable string ("November 1, 2017") to spit back to user
    k = fridayDate
    year = int(k[0:4])
    month = int(k[5:7])
    day1 = int(k[8:])
    return calendar.month_name[month] +" "+ str(day1)+ " " + str(year)
    


def lambda_handler(event, context):

    # TODO implement
    outputSpeech = {"type": "PlainText", "text": "Hello World"}
    r= {"outputSpeech": outputSpeech, "shouldEndSession": True} 
    
    if event["request"]["type"] == "LaunchRequest": 
        outputSpeech["text"] = "Where or when would you like to know Shabbat times?"
        r["shouldEndSession"] = False

    if event["request"]["type"] == "IntentRequest":
        if event["request"]["intent"]["name"] == "AMAZON.HelpIntent":
            outputSpeech["text"] = "This is all the help you get."
        elif event["request"]["intent"]["name"] == "shabbatTimeIntent":
            try:
                date = event["request"]["intent"]["slots"]["date"]["value"]
            except: 
                date = str(datetime.datetime.today())
                date = date[0:10]
            
            try:
                address = event["request"]["intent"]["slots"]["location"]["value"]
                address1 = address
                for x in address: 
                    if x== " ": 
                        x == "+"
            except:
                address = "Los+Angeles"
                address1 = "Los Angeles"
            
            try:
                fridayDate = str(configureToFriday(date))
                fridayDate = fridayDate[:10]
                print fridayDate
                sunset_time = find_sunset_time(fridayDate,address)
                print sunset_time
                sunset_time = convertToPacific(sunset_time)
                printedDate = getDayandMonth(date)
                print printedDate
                outputSpeech["text"] = "During the Friday of " + printedDate + " Shabbat starts at " + sunset_time + " Pacific Time in " + address1
                
            except: 
                outputSpeech["text"] = "I'm sorry, but your request is invalid. Please try asking again."
                r["shouldEndSession"] = False
    print outputSpeech["text"]
    
    response = {"version": "1.0", "response": r}
    return response
