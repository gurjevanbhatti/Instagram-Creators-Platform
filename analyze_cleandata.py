import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from sklearn.utils import resample
from scipy.stats import mannwhitneyu, chi2_contingency
from scipy.stats import ttest_ind


# Load your cleaned data
df = pd.read_csv("instagram_posts_cleaned.csv")

# Step 1: Label high views (100K+)
df["is_high_view"] = df["plays"] >= 100_000


# List of engagement metrics to test
engagement_cols = [
    "likes_per_view",
    "comments_per_view",
    "shares_per_view",
    "saves_per_view",
]

print("\nT-Tests for High vs Low Views")

# Split data by is_high_view
high = df[df["is_high_view"] == True]
low = df[df["is_high_view"] == False]

for col in engagement_cols:
    high_vals = high[col].dropna()
    low_vals = low[col].dropna()

    # T-test
    t_stat, t_p = ttest_ind(high_vals, low_vals, equal_var=False)
    
    # Mann–Whitney U
    u_stat, u_p = mannwhitneyu(high_vals, low_vals, alternative="two-sided")

    # Mean comparison
    high_mean = high_vals.mean()
    low_mean = low_vals.mean()
    higher_group = "High-View" if high_mean > low_mean else "Low-View"

    print(f"\n{col}")
    print(f"T-test: t = {t_stat:.3f}, p = {t_p:.4f}")
    print(f"Mann–Whitney U: U = {u_stat:.3f}, p = {u_p:.4f}")
    print(f"Higher Mean: {higher_group} group ({high_mean:.4f} vs {low_mean:.4f})")


# Drop rows with missing values in features
df_model = df.dropna(subset=engagement_cols)

X = df_model[engagement_cols]
y = df_model["is_high_view"].astype(int)

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)


#-----------------------------------------------
## DONT HAVE ENOUGH VIRAL POSTS FOR 20% SAMPLE SO 
# Combine for upsampling
train_df = pd.concat([X_train, y_train], axis=1)

# Separate majority and minority
majority = train_df[train_df["is_high_view"] == 0]
minority = train_df[train_df["is_high_view"] == 1]

# Upsample minority class
minority_upsampled = resample(
    minority,
    replace=True,
    n_samples=len(majority),
    random_state=42
)

# Combine upsampled training data
upsampled_df = pd.concat([majority, minority_upsampled])

# Split again into X and y
X_train_upsampled = upsampled_df[engagement_cols]
y_train_upsampled = upsampled_df["is_high_view"]

#-----------------------------------------------

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Logistic Regression
log_model = LogisticRegression()
log_model.fit(X_train_scaled, y_train)
log_preds = log_model.predict(X_test_scaled)
print("\nLogistic Regression")
print(classification_report(y_test, log_preds))

# Random Forest
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)
rf_preds = rf_model.predict(X_test)
print("\nRandom Forest")
print(classification_report(y_test, rf_preds))

importances = rf_model.feature_importances_
feat_names = X.columns

plt.figure(figsize=(6, 4))
sns.barplot(x=importances, y=feat_names)
plt.title("Random Forest Feature Importance")
plt.xlabel("Importance")
plt.ylabel("Engagement Feature")
plt.tight_layout()
plt.show()

# Scale features for PCA + Clustering
X_scaled = StandardScaler().fit_transform(X)

# Run PCA to reduce dimensions
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Apply KMeans (choose 2 clusters to start with)
kmeans = KMeans(n_clusters=2, random_state=42)
clusters = kmeans.fit_predict(X_pca)

# Add results to DataFrame
df_model["cluster"] = clusters

# Plot
plt.figure(figsize=(8,6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=clusters, palette='Set2')
plt.title("K-Means Clustering on Engagement Features (PCA Reduced)")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")
plt.show()

explained_variance = pca.explained_variance_ratio_
print(f"Explained variance by PC1: {explained_variance[0]:.2f}")
print(f"Explained variance by PC2: {explained_variance[1]:.2f}")


