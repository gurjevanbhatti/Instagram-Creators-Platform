import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast

# ------------------- AUDIENCE DEMOGRAPHISCS PART -------------------------
demo_df = pd.read_csv("audience_demographics_cleaned.csv")
print("Demographics Columns:", demo_df.columns.tolist())

#Gender Pie Chart 
gender = {
    "Men": float(demo_df["Men (%)"].iloc[0].replace("%", "")),
    "Women": float(demo_df["Women (%)"].iloc[0].replace("%", ""))
}

plt.figure(figsize=(5, 5))
plt.pie(gender.values(), labels=gender.keys(), autopct='%1.1f%%', startangle=90, colors=["skyblue", "pink"])
plt.title("Gender Distribution")
plt.tight_layout()
plt.show()

def parse_label_percent_string(raw_string):
    parts = raw_string.split(", ")
    parsed_dict = {}
    for part in parts:
        label, percent = part.split(": ")
        parsed_dict[label.strip()] = float(percent.strip().replace("%", ""))
    return parsed_dict

#Age Breakdown Graph
age_all = parse_label_percent_string(demo_df["Age Breakdown (All)"].iloc[0])

plt.figure(figsize=(7, 4))
plt.bar(age_all.keys(), age_all.values(), color='mediumseagreen')
plt.title("Age Breakdown (All Genders)")
plt.ylabel("Percentage")
plt.xlabel("Age Range")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Country Breakdown Graph
country_data = parse_label_percent_string(demo_df["Top Countries"].iloc[0])

plt.figure(figsize=(7, 5))
plt.pie(country_data.values(), labels=country_data.keys(), autopct="%1.1f%%", startangle=140)
plt.title("Top Countries")
plt.tight_layout()
plt.show()

# City Breakdown Graph - It's all in India so I didn't have to put Country in here lol
city_data = parse_label_percent_string(demo_df["Top Cities"].iloc[0])

plt.figure(figsize=(8, 4))
plt.bar(city_data.keys(), city_data.values(), color='gold')
plt.title("Top Cities")
plt.ylabel("Follower %")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Follower Activity by Day Graph
activity_cols = [col for col in demo_df.columns if "Activity on" in col]
activity_data = {
    col.replace("Activity on ", ""): int(demo_df[col].iloc[0]) for col in activity_cols
}
sorted_activity = dict(sorted(activity_data.items(), key=lambda item: item[1], reverse=True))

plt.figure(figsize=(8, 4))
plt.bar(sorted_activity.keys(), sorted_activity.values(), color='mediumpurple')
plt.title("Follower Activity by Weekday")
plt.ylabel("Estimated Impressions")
plt.xlabel("Weekday")
plt.tight_layout()
plt.show()
# ------------------- END AUDIENCE DEMOGRAPHISCS PART -------------------------

# ------------------- POST AND REELS INSIGHTS PART -------------------------
df = pd.read_csv("instagram_posts_cleaned.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

# Add my boundaries like what I consider high views 
df["high_views_100k"] = df["plays"] >= 100000
df["high_views_200k"] = df["plays"] >= 200000

# Find the highest viewed trial reel
trial_reel = df[(df["source"] == "reel") & (df["is_trial_reel"] == True)]
top_trial = trial_reel.sort_values("plays", ascending=False).iloc[0]

# Find the highest viewed non-trial reel (public reel on my page)
non_trial_reel = df[(df["source"] == "reel") & (df["is_trial_reel"] != True)]
top_non_trial = non_trial_reel.sort_values("plays", ascending=False).iloc[0]

# Find the highest viewed post (public on my page)
post = df[df["source"] == "post"]
top_post = post.sort_values("plays", ascending=False).iloc[0]

# Print the results
print("Highest Viewed Trial Reel:")
print(f"Views: {top_trial['plays']}")

print("Highest Viewed Non-Trial Reel:")
print(f"Views: {top_non_trial['plays']}")

print("Highest Viewed Post:")
print(f"Views: {top_post['plays']}")

# Count how many duplicate captions are from reels (you will be surprised how many duplicates I have lol)
duplicate_reels = df[(df["source"] == "reel") & (df["is_duplicate_caption"] == True)]
print("Number of Reels with Duplicate Captions:", len(duplicate_reels))

# Average word count per caption (Yah that's what I thought)
avg_word_count = df["word_count"].mean()
print(f"Average Words per Caption: {avg_word_count:.2f}")

# Average hashtag count per caption 
avg_hashtags = df["hashtag_count"].mean()
print(f"Average Hashtags per Caption: {avg_hashtags:.2f}")

# Most common hour and day of posting
common_hour = df["hour"].mode()[0]
print(f"Most Common Posting Hour: {common_hour}:00")
common_day = df["weekday"].mode()[0]
print(f"Most Common Posting Day: {common_day}")

# Reel vs Post percentage - to see if I post mostly reels or posts from my profile 
reel_count = (df["source"] == "reel").sum()
post_count = (df["source"] == "post").sum()
total = len(df)
reel_pct = (reel_count / total) * 100
post_pct = (post_count / total) * 100

print(f"Total Reels: {reel_count} ({reel_pct:.1f}%)")
print(f"Total Posts: {post_count} ({post_pct:.1f}%)")

# Basic questions I had for my profile in general
print("Trial vs. Non-Trial Reels:")
print(df[df["source"] == "reel"]["is_trial_reel"].value_counts())
print("\n Posts vs. Reels:")
print(df["source"].value_counts())
print("\n Long vs. Short Captions (≥50 words):")
print(df["is_long_caption"].value_counts())
print("\n Posts per Weekday:")
print(df["weekday"].value_counts())
print("\n Reels with ≥100k Views:")
print(df[(df["source"] == "reel") & (df["high_views_100k"])].shape[0])
print("Trial Reels with ≥100k Views:")
print(df[(df["source"] == "reel") & (df["high_views_100k"]) & (df["is_trial_reel"] == True)].shape[0])

# Calculate averages of my reels and posts plays and trial reels 
overall_avg = df["plays"].mean()
reel_avg = df[df["source"] == "reel"]["plays"].mean()
post_avg = df[df["source"] == "post"]["plays"].mean()
trial_reel_avg = df[(df["source"] == "reel") & (df["is_trial_reel"] == True)]["plays"].mean()

# Print results
print(f"Overall Average Views: {overall_avg:.2f}")
print(f"Average Reel Views: {reel_avg:.2f}")
print(f"Average Post Views: {post_avg:.2f}")
print(f"Average Trial Reel Views: {trial_reel_avg:.2f}") 

# Filtered subsets
df_caption_zoom = df[df["plays"] <= 100000]
df_weekday_zoom = df[df["plays"] <= 100000]
df_type_zoom = df[df["plays"] <= 100000]
df_trial_zoom = df[df["plays"] <= 100000]

# ----------------------- GRAPHS ------------------------------
sns.set(style="whitegrid")

#1. Views by Caption Length Graph 
plt.figure(figsize=(7, 5))
sns.boxplot(x="is_long_caption", y="plays", data=df_caption_zoom)
plt.xticks([0, 1], ['Short Caption', 'Long Caption'])
plt.title("Views by Caption Length (<=100K views)")
plt.xlabel("Caption Length")
plt.ylabel("Views")
plt.tight_layout()
plt.show()

#2. Views by Weekday Graph
plt.figure(figsize=(10, 5))
sns.boxplot(x="weekday", y="plays", data=df_weekday_zoom,
            order=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
plt.title("Views by Day of the Week (<=100K views)")
plt.xlabel("Weekday")
plt.ylabel("Views")
plt.tight_layout()
plt.show()

#3. Reel vs Post (<=100K views)
plt.figure(figsize=(7, 5))
sns.boxplot(x="source", y="plays", data=df_type_zoom)
plt.title("Views: Reels vs Posts (<=100K views)")
plt.xlabel("Content Type")
plt.ylabel("Views")
plt.tight_layout()
plt.show()

# 4. Trial vs Non-Trial Reels (<=100K views) 
df_trial_only = df_type_zoom[df_type_zoom["source"] == "reel"]
plt.figure(figsize=(7, 5))
sns.boxplot(x="is_trial_reel", y="plays", data=df_trial_only)
plt.xticks([0, 1], ['Non-Trial', 'Trial'])
plt.title("Views: Trial vs Non-Trial Reels (<=100K views)")
plt.xlabel("Trial Status")
plt.ylabel("Views")
plt.tight_layout()
plt.show()

df_under_100k = df[df["plays"] <= 100000]

df["is_high_view"] = df["plays"] >= 100000
ratio_cols = ["likes_per_view", "comments_per_view", "shares_per_view", "saves_per_view"]

for c in ratio_cols:
    plt.figure(figsize=(6,4))
    sns.boxplot(x="is_high_view", y=c, data=df)
    plt.xticks([0,1], ["<100k views", "≥100k views"])
    plt.title(f"{c.replace('_',' ').title()} vs High Views")
    
    # Zoom in for all except shares
    if c != "shares_per_view":
        plt.ylim(df[c].min(), df[c].quantile(0.95))  # trims extreme outliers for better view
    
    plt.tight_layout()
    plt.show()