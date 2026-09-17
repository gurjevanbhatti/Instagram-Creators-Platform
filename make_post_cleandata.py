import json
import pandas as pd
from datetime import datetime
import os
import re
import emoji
import codecs
import ftfy

# Load posts
with open("posts.json", "r") as f:
    posts_data = json.load(f)["organic_insights_posts"]

# Load reels
with open("reels.json", "r") as f:
    reels_data = json.load(f)["organic_insights_reels"]

# Function to clean individual entry
def parse_entry(entry, source="post"):
    try:
        media_info = entry.get("media_map_data", {}).get("Media Thumbnail", {})
        raw_caption = media_info.get("title", "")
        caption = ftfy.fix_text(raw_caption) 
        timestamp = media_info.get("creation_timestamp")
        dt = pd.to_datetime(timestamp, unit='s', utc=True).tz_convert("America/Vancouver") if timestamp else None


        metrics = entry.get("string_map_data", {})
        
        if source == "reel":
            likes = int(metrics.get("Instagram Likes", {}).get("value", "0").replace(",", ""))
            comments = int(metrics.get("Instagram Comments", {}).get("value", "0").replace(",", ""))
            shares = int(metrics.get("Instagram Shares", {}).get("value", "0").replace(",", ""))
            saves = int(metrics.get("Instagram Saves", {}).get("value", "0").replace(",", ""))
            plays = int(metrics.get("Instagram Plays", {}).get("value", "0").replace(",", ""))
            accounts_reached = int(metrics.get("Accounts reached", {}).get("value", "0").replace(",", ""))
        else:  # post
            likes = int(metrics.get("Likes", {}).get("value", "0").replace(",", ""))
            comments = int(metrics.get("Comments", {}).get("value", "0").replace(",", ""))
            shares = int(metrics.get("Shares", {}).get("value", "0").replace(",", ""))
            saves = int(metrics.get("Saves", {}).get("value", "0").replace(",", ""))
            plays = int(metrics.get("Impressions", {}).get("value", "0").replace(",", ""))
            accounts_reached = int(metrics.get("Accounts reached", {}).get("value", "0").replace(",", ""))

        # if source == "post":
        #     follows = int(metrics.get("Follows", {}).get("value", "0").replace(",", ""))
        # else:
        #     follows = 0  # or 0 if you prefer to keep numeric
    
        caption_lower = caption.lower()
        caption_no_hashtags = re.sub(r"#\S+", "", caption_lower)

        # Prioritize based on your typical post types
        if any(word in caption_no_hashtags for word in ["before", "after", "4 months", "6 months", "transformation"]):
            content_type = "transformation"
        elif any(word in caption_no_hashtags for word in ["smoothie", "mango", "recipe", "calories", "calorie", "protein"]):
            content_type = "recipe"
        elif any(word in caption_no_hashtags for word in ["glutes", "biceps", "push", "pull", "upper", "leg day", "workout"]):
            content_type = "workout"
        else:
            content_type = "other"

            
        caption_no_emoji = emoji.replace_emoji(caption, replace='')  # For word count only
        word_count = len(caption_no_emoji.split())

        hashtag_count = caption.count("#")
        is_long_caption = word_count >= 50

        # New logic: detect trial reel
        is_trial_reel = None
        if source == "reel":
            is_trial_reel = media_info.get("media_trial", {}).get("status", "").lower() == "active"
        else:
            is_trial_reel = False 

        return {
            "source": source,
            "caption": caption,
            "timestamp": dt,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "plays": plays,
            "accounts_reached": accounts_reached,
            # "follows": follows,
            "word_count": word_count,
            "hashtag_count": hashtag_count,
            "is_long_caption": is_long_caption,
            "is_trial_reel": is_trial_reel,
            "content_type": content_type


        }
    except Exception as e:
        print("Error parsing:", e)
        return None


# Parse everything
cleaned_posts = [parse_entry(p, "post") for p in posts_data]  
cleaned_reels = [parse_entry(r, "reel") for r in reels_data]
all_cleaned = [p for p in cleaned_posts + cleaned_reels if p is not None]

# Create DataFrame
df = pd.DataFrame(all_cleaned)

# Add time-based features
df["hour"] = df["timestamp"].dt.hour
df["weekday"] = df["timestamp"].dt.day_name()
df["month"] = df["timestamp"].dt.month_name()

# Engagement ratios
df["is_duplicate_caption"] = df.duplicated(subset=["caption"], keep=False)
df["likes_per_view"] = df["likes"] / df["plays"]
df["comments_per_view"] = df["comments"] / df["plays"]
df["shares_per_view"] = df["shares"] / df["plays"]
df["saves_per_view"] = df["saves"] / df["plays"]

# Save and show
df.to_csv("instagram_posts_cleaned.csv", index=False)
print(df)
print(df[["is_trial_reel", "saves"]])

print("Saved to:", os.path.abspath("instagram_posts_cleaned.csv"))

