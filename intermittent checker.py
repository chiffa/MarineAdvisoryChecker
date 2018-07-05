import requests
from bs4 import BeautifulSoup
from datetime import datetime
from csv import writer as csv_writer
from csv import reader as csv_reader
from time import sleep
import atexit
from twilio.rest import Client
import os


# # Your Account SID from twilio.com/console
account_sid = os.environ['TWILIOSID']
# # Your Auth Token from twilio.com/console
auth_token = os.environ['TWILIOTOKEN']

# print account_sid, auth_token

client = Client(account_sid, auth_token)

broadcast_list = ["+18163160883"]


def broadcast(message):
    print 'broadcasting:', message
    for number in broadcast_list:
        client.messages.create(
            to=number,
            from_="+18162819687",
            body=message)


def message_admin(message):
    print 'to admin: ', message
    client.messages.create(
        to="+18163160883",
        from_="+18162819687",
        body=message)


def pull_advisory(marine_zone):

    url = 'https://forecast.weather.gov/shmrn.php?mz=%s' % marine_zone
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    prediction = soup.find('div', attrs={"id": "content"})

    forecast_datetime = None
    advisory = []

    line_list = prediction.text.splitlines()

    for i, line in enumerate(line_list):

        if "EDT" in line and 'ADVISORY' not in line:
            line = line.strip()
            forecast_datetime = datetime.strptime(line, "%I%M %p %Z %a %b %d %Y")

        if "ADVISORY" in line:
            tmp_advisory = line.strip()
            if line_list[i+1] != '' and "ADVISORY" not in line_list[i+1]:
                tmp_advisory += ' '
                tmp_advisory += line_list[i+1].strip()
            advisory.append(tmp_advisory)

    return datetime.now(), forecast_datetime, ' - '.join(advisory)


def check_loop():

    while True:

        prev_advisory = ['', '', '']

        with open('data.log', 'a') as sink:

            advisory = pull_advisory('anz538')

            if advisory[2] and (advisory[2] != prev_advisory[2] and advisory[1] != prev_advisory[1]):
                msg = 'according to bulletin released on %s \n %s' % (advisory[1], advisory[2])
                broadcast(msg)

            prev_advisory = advisory

            writer = csv_writer(sink)
            writer.writerow(advisory)

        sleep(1800)


def test_loop():

    with open('data.log', 'r') as source:
        reader = csv_reader(source)
        prev_advisory = ['', '', '']
        for line in reader:
            advisory = [datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S.%f"),
                        datetime.strptime(line[1], "%Y-%m-%d %H:%M:%S"),
                        line[2]]

            if advisory[2] and (
                    advisory[2] != prev_advisory[2] and advisory[1] != prev_advisory[1]):
                print 'according to bulletin released on %s \n %s' % (advisory[1], advisory[2])

            prev_advisory = advisory


@atexit.register
def termination_detected():
    message_admin("Marine Advisory monitor has terminated")
    broadcast("Marine Advisory Monitor for the Baltimore Harbour area (ANZ538) is going down\n Please don't expect messages announcing Marine advisories for now")


if __name__ == "__main__":
    broadcast('Welcome to the Marine Advisory Monitor for the Baltimore Harbour area (ANZ538)\n In case a Marine advisory appears we will message you')
    # print pull_advisory('anz538')
    # print pull_advisory('anz531')
    check_loop()
    # test_loop()
    # pass