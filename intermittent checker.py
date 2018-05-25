import requests
from bs4 import BeautifulSoup
from datetime import datetime
from csv import writer as csv_writer
from time import sleep


def pull_advisory(marine_zone):

    url = 'https://forecast.weather.gov/shmrn.php?mz=%s' % marine_zone
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    prediction = soup.find('div', attrs={"id": "content"})

    forecast_datetime = None
    advisory = None

    for line in prediction.text.splitlines():

        if "EDT" in line:
            line = line.strip()
            forecast_datetime = datetime.strptime(line, "%I%M %p %Z %a %b %d %Y")

        if "ADVISORY" in line:
            advisory = line.strip()

    return datetime.now(), forecast_datetime, advisory


def check_loop():

    for i in range(0, 1000):

        with open('data.log', 'wa') as sink:
            writer = csv_writer(sink)
            writer.writerow(pull_advisory('anz538'))

        sleep(1800)


# general logic - if the adivsory is detected:
# parse start/stop date/time
# add to calendar
# if alert was already there, update it
#   start time in the past - leave it
#   start time in the future - adjust it
#   end time - adjust it
# if alert is not there
#   insert it onto the calendar.


if __name__ == "__main__":
    # print pull_advisory('anz538')
    # print pull_advisory('anz531')
    check_loop()