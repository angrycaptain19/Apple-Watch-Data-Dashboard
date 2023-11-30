
def Get_Drop_Choices():
    return [
        {
            "label": "Active Energy Burned",
            "value": "HKQuantityTypeIdentifierActiveEnergyBurned",
        },
        {
            "label": "Apple Exercise Time",
            "value": "HKQuantityTypeIdentifierAppleExerciseTime",
        },
        {
            "label": "Apple Stand Time",
            "value": "HKQuantityTypeIdentifierAppleStandTime",
        },
        {
            "label": "Basal Energy Burned",
            "value": "HKQuantityTypeIdentifierBasalEnergyBurned",
        },
        {
            "label": "Distance Walking Running",
            "value": "HKQuantityTypeIdentifierDistanceWalkingRunning",
        },
        {
            "label": "Environmental Audio Exposure",
            "value": "HKQuantityTypeIdentifierEnvironmentalAudioExposure",
        },
        {
            "label": "Flights Climbed",
            "value": "HKQuantityTypeIdentifierFlightsClimbed",
        },
        {"label": "Heart Rate", "value": "HKQuantityTypeIdentifierHeartRate"},
        {"label": "Step Count", "value": "HKQuantityTypeIdentifierStepCount"},
        {
            "label": "Heart Rate Standard Deviation",
            "value": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
        },
        {
            "label": "Walking Heart Rate Average",
            "value": "HKQuantityTypeIdentifierWalkingHeartRateAverage",
        },
        {
            "label": "Resting Heart Rate",
            "value": "HKQuantityTypeIdentifierRestingHeartRate",
        },
    ]


Explination_Table = {
    "HKQuantityTypeIdentifierActiveEnergyBurned" : 
    {"Explination" : "Measures the amount of active energy burned by the user during physical activity and exercise. This is measured in calories."},

    "HKQuantityTypeIdentifierAppleExerciseTime": 
    {"Explination" : "Measures the amount of time the user spent exercising. This includes work out sessions and movement with an average intensity of a brisk walker or better. This is measured in minutes."},

    "HKQuantityTypeIdentifierAppleStandTime": 
    {"Explination": "Measures the amount of time the user has been standing. This is measured in minutes"},

    "HKQuantityTypeIdentifierBasalEnergyBurned": 
    {"Explination" : "Measures the resting energy burned by the user. The body burns this energy to preform basic functions like breathing, blood circulation, and cell growth/maintence. This is measured in calories."},

    "HKQuantityTypeIdentifierDistanceWalkingRunning": 
    {"Explination" : "Measures the total distance the user has moved by walking or running. This is measured in miles."},

    "HKQuantityTypeIdentifierEnvironmentalAudioExposure": 
    {"Explination" : "Measures the total audio exposure from the environment that user has experienced. This is measured in decibles."},

    "HKQuantityTypeIdentifierFlightsClimbed": 
    {"Explination" : "Measures the number of flights of stairs that the user has climbed up. This is measured in count."},

    "HKQuantityTypeIdentifierHeartRate": 
    {"Explination" : "Measures the user's heart rate. This is measured in count per minutes"},

    "HKQuantityTypeIdentifierStepCount": 
    {"Explination" : "Measures the number of steps the user has taken. This is measured in count"},

    "HKQuantityTypeIdentifierWalkingHeartRateAverage": 
    {"Explination" : "Measures the user’s heart rate while walking. This is calculated by averaging the heart rate samples taken while the user is walking and physically active."},
    
    "HKQuantityTypeIdentifierRestingHeartRate" : 
    {"Explination" : "Measures the user's resting heart rate. Resting heart rate is an estimation of the user's lowest heart rate during periods of rest. This is calculated by estimating the resting heart rate by analyzing sedentary heart rate samples. Measured in count per minute."},

    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN" : 
    {"Explination" : "Heart rate variability is calculated by measuring the variation between individual heartbeats. HRV is calculated using the standard deviation of the inter-beat (RR) intervals between normal heartbeats (typically measured in milliseconds).",
    }
    
}

