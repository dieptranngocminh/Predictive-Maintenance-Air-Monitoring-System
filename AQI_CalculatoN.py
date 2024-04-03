#Calculation of AQI day-based

from enum import Enum


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
        return x * 50 / 50
    elif x <= 150:
        return 50 + (x - 50) * 50 / 100
    elif x <= 250:
        return 100 + (x - 150) * 50 / 100
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
    x = 0.0409 * x * 64
    if x <= 125:
        return x * 50 / 125
    elif x <= 350:
        return 50 + (x - 125) * 50 / 225
    elif x <= 550:
        return 100 + (x - 350) * 50 / 200
    elif x <= 800:
        return 150 + (x - 550) * 50 / 250
    elif x <= 1600:
        return 200 + (x - 800) * 100 / 800
    elif x < 2100:
        return 300 + (x - 1600) * 100 / 500
    elif x < 2630:
        return 400 + (x - 2100) * 100 / 530
    else:
        return 500 + (x - 2630) * 100 / 530

# NO2 Sub-Index calculation
def get_NO2_subindex(x):
    x = 0.0409 * x * 46
    if x <= 100:
        return x * 50 / 100
    elif x <= 200:
        return 50 + (x - 100) * 50 / 100
    elif x <= 700:
        return 100 + (x - 200) * 50 / 500
    elif x <= 1200:
        return 150 + (x - 700) * 50 / 500
    elif x <= 2350:
        return 200 + (x - 1200) * 100 / 1150
    elif x <= 3100:
        return 300 + (x - 2350) * 100 / 750
    elif x < 3850:
        return 400 + (x - 3100) * 100 / 750
    else:
        return 500 + (x - 3850) * 100 / 750

# CO Sub-Index calculation
def get_CO_subindex(x):
    x = 0.0409 * x * 28
    if x <= 10000:
        return x * 50 / 10000
    elif x <= 30000:
        return 50 + (x - 10000) * 50 / 20000
    elif x <= 45000:
        return 100 + (x - 30000) * 50 / 15000
    elif x <= 60000:
        return 150 + (x - 45000) * 50 / 15000
    elif x <= 90000:
        return 200 + (x - 60000) * 100 / 30000
    elif x <= 120000:
        return 300 + (x - 90000) * 100 / 30000
    elif x < 150000:
        return 400 + (x - 120000) * 100 / 30000
    else:
        return 500 + (x - 150000) * 100 / 30000


# O3 Sub-Index calculation
def get_O3_subindex_1h(x):
    x = 0.0409 * x * 48
    if x <= 160:
        return x * 50 / 160
    elif x <= 200:
        return 50 + (x - 160) * 50 / 40
    elif x <= 300:
        return 100 + (x - 200) * 50 / 100
    elif x <= 400:
        return 150 + (x - 300) * 50 / 100
    elif x <= 800:
        return 200 + (x - 400) * 100 / 400
    elif x < 1000:
        return 300 + (x - 800) * 100 / 200
    elif x < 1200:
        return 400 + (x - 1000) * 100 / 200
    else:
        return 500 + (x - 1200) * 100 / 200

def get_O3_subindex_8h(x):
    x = 0.0409 * x * 48
    if x <= 100:
        return x * 50 / 100
    elif x <= 120:
        return 50 + (x - 100) * 50 / 20
    elif x <= 170:
        return 100 + (x - 120) * 50 / 50
    elif x <= 210:
        return 150 + (x - 170) * 50 / 40
    elif x <= 400:
        return 200 + (x - 210) * 100 / 190
    else:
        return 300 + (x - 400) * 100 / 190

def get_O3_AQI(O3_1h, O3_8h):
    if O3_8h > 400:
        return get_O3_subindex_1h(O3_1h)
    else:
        return get_O3_subindex_8h(O3_8h)


def get_overall_daily_AQI(PM25, PM10, SO2, NO2, CO, O3_1h, O3_8h):
    # Calculate AQI for each pollutant
    AQI_PM25 = get_PM25_subindex(PM25)
    AQI_PM10 = get_PM10_subindex(PM10)
    AQI_SO2 = get_SO2_subindex(SO2)
    AQI_NO2 = get_NO2_subindex(NO2)
    AQI_CO = get_CO_subindex(CO)
    AQI_O3 = get_O3_AQI(O3_1h, O3_8h)

    # Find the maximum AQI among all pollutants
    max_AQI = max(AQI_PM25, AQI_PM10, AQI_SO2, AQI_NO2, AQI_CO, AQI_O3)

    return max_AQI

def get_AQI_bucket(x):
    if x <= 50:
        return "Good"
    elif x <= 100:
        return "Moderate"
    elif x <= 150:
        return "Unhealthy for sensitive groups"
    elif x <= 200:
        return "Unhealthy"
    elif x <= 300:
        return "Very unhealthy"
    elif x > 300:
        return "Hazardous"
    else:
        return

def test_AQI_calculation():
    try:
        # Sample sensor values
        PM25 = 28.00
        PM10 = 39.00
        SO2 = 0.00
        NO2 = 1.00
        CO = 1.00
        O3_1h = 3.00
        O3_8h = 3.00

        # Calculate overall daily AQI
        overall_aqi = get_overall_daily_AQI(PM25, PM10, SO2, NO2, CO, O3_1h, O3_8h)

        # Get AQI bucket
        aqi_bucket = get_AQI_bucket(overall_aqi)

        # Print test results
        print("Overall Daily AQI:", overall_aqi)
        print("AQI Bucket from function:", aqi_bucket)

    except Exception as e:
        print("Test failed due to an exception:", e)

# Run the test function
#test_AQI_calculation()

