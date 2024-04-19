from twilio.rest import Client
import requests
import datetime
import urllib.parse
import secrets
import string
import sys

account_sid = "ACada6b96e1053fc2a24eb5be1a1fb8908"
auth_token = "8048f676c3f3a13f509fd83b5e96a39f"
twilio_phone_number = "+18053514378"
recipient_phone_number = "+918618856297"

def Location():

    #Get Info
    response = requests.get("https://ipinfo.io")
    
    if response.status_code == 200:
        data = response.json()
       
        city = data.get("city")
        region = data.get("region")
        country = data.get("country")
        location = data.get("loc")
        y = location,[city,region,country]
    else:
        print("Failed to retrieve geolocation information.")

    x = (y[0]).split(',')
    lat = x[0]
    lon = x[1]

    lat_lon = f"{12.934995},{77.534744}"
    base_url = "https://www.google.com/maps/search/"
    params = {"api": 1, "query": lat_lon}
    url = base_url + "?" + urllib.parse.urlencode(params)

    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")

    return(url, y[0], y[1], current_time)

def Text():

    content = Location()
    actz = f"Location: {content[2][0]}, {content[2][1]}, {content[2][2]}"

    text = f"""
🚨 URGENT: EMERGENCY ALERT 🚨

Emergency ID: {(''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(6))).capitalize()}
Location: Bangalore, Karnataka, IN
Coordinates: {content[1]}

A vehicle accident has occurred, and the driver is unresponsive. Immediate intervention from emergency services is critical.

Time of Incident: {content[3]}
Location Link:
{content[0]}
    """

    return(text)

def SOS():

  account_sid = 'ACada6b96e1053fc2a24eb5be1a1fb8908'
  auth_token = '95cb115485e51392b7860548d350ceab'

  client = Client(account_sid, auth_token)

  message = client.messages.create(
    from_='+18053514378',
    to='+918618856297',
    body=Text()
  )
  x = (message.sid).upper()
  return(x[:6])

if __name__ == "__main__":
    SOS()