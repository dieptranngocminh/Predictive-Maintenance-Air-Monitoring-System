#Calculation of AQI day-based

import MQTT_Listener

from enum import Enum


class Pollutant(Enum):
    PM25 = "PM2.5"
    PM10 = "PM10"
    O3 = "O3"
    CO = "CO"
    SO2 = "SO2"
    NO2 = "NO2"

    def get_literal(self):
        return self.value

    @staticmethod
    def parse_from_string(text):
        for pollutant in Pollutant:
            if pollutant.get_literal() == text:
                return pollutant
        return None


# PM2.5 Sub-Index calculation
def get_PM25_subindex(x):
    if x <= 25:
        return x * 50 / 25
    elif x <= 50:
        return 50 + (x - 25) * 50 / 25
    elif x <= 80:
        return 100 + (x - 50) * 50 / 30
    elif x <= 150:
        return 150 + (x - 80) * 50 / 70
    elif x <= 250:
        return 200 + (x - 150) * 100 / 100
    elif x <= 350:
        return 300 + (x - 250) * 100 / 100
    elif x < 500:
        return 400 + (x - 350) * 100 / 150
    else:
        return 500 + (x - 500) * 100 / 150

#df["PM2.5_SubIndex"] = df["PM2.5_24hr_avg"].apply(lambda x: get_PM25_subindex(x))

# PM10 Sub-Index calculation
def get_PM10_subindex(x):
    if x <= 50:
        return x
    elif x <= 150:
        return 50 + (x - 50) * 50 / 100
    elif x <= 250:
        return 100 + (x - 150) * 50 / 150
    elif x <= 350:
        return 150 + (x - 250) * 50 / 100
    elif x <= 420:
        return 200 + (x - 350) * 100 / 70
    elif x <= 500:
        return 300 + (x - 420) * 100 / 80
    elif x < 600:
        return 400 + (x - 500) * 100 / 100
    else:
        return 500 + (x - 600) * 100 / 100

# SO2 Sub-Index calculation
def get_SO2_subindex(x):
    if x <= 40:
        return x * 50 / 40
    elif x <= 80:
        return 50 + (x - 40) * 50 / 40
    elif x <= 380:
        return 100 + (x - 80) * 100 / 300
    elif x <= 800:
        return 200 + (x - 380) * 100 / 420
    elif x <= 1600:
        return 300 + (x - 800) * 100 / 800
    elif x > 1600:
        return 400 + (x - 1600) * 100 / 800
    else:
        return 0

# NO2 Sub-Index calculation
def get_NO2_subindex(x):
    if x <= 100:
        return x * 50 / 100
    elif x <= 200:
        return 50 + (x - 100) * 50 / 100
    elif x <= 700:
        return 100 + (x - 200) * 100 / 500
    elif x <= 1200:
        return 200 + (x - 700) * 100 / 500
    elif x <= 2350:
        return 300 + (x - 1200) * 200 / 1150
    elif x <= 3100:
        return 400 + (x - 2350) * 100 / 750
    elif x < 3850:
        return 500 + (x - 3100) * 100 / 750
    else:
        return 600

# CO Sub-Index calculation
def get_CO_subindex(x):
    if x <= 10000:
        return x * 50 / 10000
    elif x <= 30000:
        return 50 + (x - 10000) * 50 / 20000
    elif x <= 45000:
        return 100 + (x - 30000) * 50 / 15000
    elif x <= 60000:
        return 200 + (x - 45000) * 100 / 15000
    elif x <= 90000:
        return 300 + (x - 60000) * 100 / 30000
    elif x <= 120000:
        return 400 + (x - 90000) * 100 / 30000
    elif x < 150000:
        return 500 + (x - 120000) * 100 / 30000
    else:
        return 600


# O3 Sub-Index calculation
def get_O3_subindex_1h(x):
    if x <= 160:
        return x * 50 / 160
    elif x <= 200:
        return 50 + (x - 160) * 50 / 40
    elif x <= 300:
        return 100 + (x - 200) * 100 / 100
    elif x <= 400:
        return 200 + (x - 300) * 100 / 100
    elif x <= 800:
        return 300 + (x - 400) * 100 / 400
    elif x < 1200:
        return 400 + (x - 800) * 100 / 400
    else:
        return 500

def get_O3_subindex_8h(x):
    if x <= 100:
        return x * 50 / 100
    elif x <= 120:
        return 50 + (x - 100) * 50 / 20
    elif x <= 170:
        return 100 + (x - 120) * 100 / 50
    elif x <= 210:
        return 200 + (x - 170) * 100 / 40
    elif x <= 400:
        return 300 + (x - 210) * 100 / 190
    else:
        return 400