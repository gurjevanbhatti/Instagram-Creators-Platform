import json
import pandas as pd
import os

#Load JSON
with open("audience_insights.json", "r") as f:
    audience_data = json.load(f)["organic_insights_audience"][0]["string_map_data"]

#Parse general stats and follower activity
followers = audience_data["Followers"]["value"]
followers_delta = audience_data["Followers Delta"]["value"]
countries = audience_data["Follower Percentage by Country"]["value"]
cities = audience_data["Follower Percentage by City"]["value"]
gender_men = audience_data["Total Follower Percentage for Men"]["value"]
gender_women = audience_data["Total Follower Percentage for Women"]["value"]
age_all = audience_data["Follower Percentage by Age for All Genders"]["value"]
age_men = audience_data["Follower Percentage by Age for Men"]["value"]
age_women = audience_data["Follower Percentage by Age for Women"]["value"]

activity_data = {}
for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
    raw_value = audience_data[f"{day} Follower Activity"]["value"]
    count = int(raw_value.lower().replace("k", "000").replace(".", ""))
    activity_data[day] = count

#Create a single-row dataframe with all stats
data_dict = {
    "Total Followers": followers,
    "Follower Growth": followers_delta,
    "Men (%)": gender_men,
    "Women (%)": gender_women,
    "Age Breakdown (All)": age_all,
    "Age Breakdown (Men)": age_men,
    "Age Breakdown (Women)": age_women,
    "Top Countries": countries,
    "Top Cities": cities,
}
data_dict.update({f"Activity on {day}": count for day, count in activity_data.items()})

audience_df = pd.DataFrame([data_dict])

audience_df.to_csv("audience_demographics_cleaned.csv", index=False)
print("\nSaved full demographic + activity report to 'audience_demographics_cleaned.csv'")
print("Location:", os.path.abspath("audience_demographics_cleaned.csv"))

