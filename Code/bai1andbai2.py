import time
import pandas as pd
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from io import StringIO
import matplotlib.pyplot as plt
import os

def parse_age_to_decimal(age_str):
    try:
        if pd.isna(age_str) or age_str == "N/A":
            return "N/A"
        age_str = str(age_str).strip()
        if "-" in age_str:
            years, days = map(int, age_str.split("-"))
            decimal_age = years + (days / 365)
            return round(decimal_age, 2)
        if "." in age_str:
            return round(float(age_str), 2)
        if age_str.isdigit():
            return round(float(age_str), 2)
        return "N/A"
    except (ValueError, AttributeError) as e:
        print(f"⚠️ Age conversion error for '{age_str}': {e}")
        return "N/A"

def get_country_code(nation_str):
    try:
        if pd.isna(nation_str) or nation_str == "N/A":
            return "N/A"
        return nation_str.split()[-1]
    except (AttributeError, IndexError):
        return "N/A"

def format_player_name(name):
    try:
        if pd.isna(name) or name == "N/A":
            return "N/A"
        if "," in name:
            parts = [part.strip() for part in name.split(",")]
            if len(parts) >= 2:
                return " ".join(parts[::-1])
        return " ".join(name.split()).strip()
    except (AttributeError, TypeError):
        return "N/A"

root_dir = r"C:\Users\DD\OneDrive\Documents\newfolder(2)\btlpython"
browser_options = Options()
browser_options.add_argument("--headless")
browser_options.add_argument("--disable-gpu")
browser_options.add_argument("--no-sandbox")
browser_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)
stat_urls = [
    "https://fbref.com/en/comps/9/2024-2025/stats/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/keepers/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/shooting/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/passing/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/gca/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/defense/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/possession/2024-2025-Premier-League-Stats",
    "https://fbref.com/en/comps/9/2024-2025/misc/2024-2025-Premier-League-Stats",
]
table_identifiers = [
    "stats_standard",
    "stats_keeper",
    "stats_shooting",
    "stats_passing",
    "stats_gca",
    "stats_defense",
    "stats_possession",
    "stats_misc",
]
target_columns = [
    "Player", "Nation", "Team", "Position", "Age",
    "Matches Played", "Starts", "Minutes",
    "Gls", "Ast", "crdY", "crdR",
    "xG", "xAG",
    "PrgC", "PrgP", "PrgR",
    "Gls per 90", "Ast per 90", "xG per 90", "xAG per 90",
    "GA90", "Save%", "CS%", "PK Save%",
    "SoT%", "SoT per 90", "G per Sh", "Dist",
    "Cmp", "Cmp%", "TotDist", "ShortCmp%", "MedCmp%", "LongCmp%", "KP", "Pass into 1_3", "PPA", "CrsPA",
    "SCA", "SCA90", "GCA", "GCA90",
    "Tkl", "TklW",
    "Deff Att", "Lost",
    "Blocks", "Sh", "Pass", "Int",
    "Touches", "Def Pen", "Def 3rd", "Mid 3rd", "Att 3rd", "Att Pen",
    "Take-Ons Att", "Succ%", "Tkld%",
    "Carries", "ProDist", "Carries 1_3", "CPA", "Mis", "Dis",
    "Rec", "Rec PrgR",
    "Fls", "Fld", "Off", "Crs", "Recov",
    "Aerl Won", "Aerl Lost", "Aerl Won%"
]
rename_columns_map = {
    "stats_standard": {
        "Unnamed: 1": "Player",
        "Unnamed: 2": "Nation",
        "Unnamed: 3": "Position",
        "Unnamed: 4": "Team",
        "Unnamed: 5": "Age",
        "Playing Time": "Matches Played",
        "Playing Time.1": "Starts",
        "Playing Time.2": "Minutes",
        "Performance": "Gls",
        "Performance.1": "Ast",
        "Performance.6": "crdY",
        "Performance.7": "crdR",
        "Expected": "xG",
        "Expected.2": "xAG",
        "Progression": "PrgC",
        "Progression.1": "PrgP",
        "Progression.2": "PrgR",
        "Per 90 Minutes": "Gls per 90",
        "Per 90 Minutes.1": "Ast per 90",
        "Per 90 Minutes.5": "xG per 90",
        "Per 90 Minutes.6": "xAG per 90"
    },
    "stats_keeper": {
        "Unnamed: 1": "Player",
        "Performance.1": "GA90",
        "Performance.4": "Save%",
        "Performance.9": "CS%",
        "Penalty Kicks.4": "PK Save%"
    },
    "stats_shooting": {
        "Unnamed: 1": "Player",
        "Standard.3": "SoT%",
        "Standard.5": "SoT per 90",
        "Standard.6": "G per Sh",
        "Standard.8": "Dist"
    },
    "stats_passing": {
        "Unnamed: 1": "Player",
        "Total": "Cmp",
        "Total.2": "Cmp%",
        "Total.3": "TotDist",
        "Short.2": "ShortCmp%",
        "Medium.2": "MedCmp%",
        "Long.2": "LongCmp%",
        "Unnamed: 26": "KP",
        "Unnamed: 27": "Pass into 1_3",
        "Unnamed: 28": "PPA",
        "Unnamed: 29": "CrsPA",
    },
    "stats_gca": {
        "Unnamed: 1": "Player",
        "SCA.1": "SCA90",
        "GCA.1": "GCA90",
    },
    "stats_defense": {
        "Unnamed: 1": "Player",
        "Tackles": "Tkl", "Tackles.1": "TklW",
        "Challenges.1": "Deff Att",
        "Challenges.3": "Lost",
        "Blocks": "Blocks",
        "Blocks.1": "Sh",
        "Blocks.2": "Pass",
        "Unnamed: 20": "Int",
    },
    "stats_possession": {
        "Unnamed: 1": "Player",
        "Touches": "Touches",
        "Touches.1": "Def Pen",
        "Touches.2": "Def 3rd",
        "Touches.3": "Mid 3rd",
        "Touches.4": "Att 3rd",
        "Touches.5": "Att Pen",
        "Touches.6": "Live",
        "Take-Ons": "Take-Ons Att",
        "Take-Ons.2": "Succ%",
        "Take-Ons.4": "Tkld%",
        "Carries": "Carries",
        "Carries.2": "ProDist",
        "Carries.4": "Carries 1_3",
        "Carries.5": "CPA",
        "Carries.6": "Mis",
        "Carries.7": "Dis",
        "Receiving": "Rec",
        "Receiving.1": "Rec PrgR",
    },
    "stats_misc": {
        "Unnamed: 1": "Player",
        "Performance.3": "Fls",
        "Performance.4": "Fld",
        "Performance.5": "Off",
        "Performance.6": "Crs",
        "Performance.12": "Recov",
        "Aerial Duels": "Aerl Won",
        "Aerial Duels.1": "Aerl Lost",
        "Aerial Duels.2": "Aerl Won%"
    }
}
table_collection = {}
for url, table_id in zip(stat_urls, table_identifiers):
    print(f"🔍 Processing {table_id} from {url}")
    browser_driver.get(url)
    time.sleep(3)
    page_soup = BeautifulSoup(browser_driver.page_source, "html.parser")
    html_comments = page_soup.find_all(string=lambda text: isinstance(text, Comment))
    data_table = None
    for comment in html_comments:
        if table_id in comment:
            comment_soup = BeautifulSoup(comment, "html.parser")
            data_table = comment_soup.find("table", {"id": table_id})
            if data_table:
                break
    if not data_table:
        print(f"⚠️ Table {table_id} not found!")
        continue
    try:
        table_data = pd.read_html(StringIO(str(data_table)), header=0)[0]
    except Exception as e:
        print(f"❌ Error reading table {table_id}: {e}")
        continue
    print(f"📋 Original columns in {table_id}:", table_data.columns.tolist())
    table_data = table_data.rename(columns=rename_columns_map.get(table_id, {}))
    table_data = table_data.loc[:, ~table_data.columns.duplicated()]
    if "Player" in table_data.columns:
        table_data["Player"] = table_data["Player"].apply(format_player_name)
        print(f"Sample Player names in {table_id}:", table_data["Player"].head(5).tolist())
    if "Age" in table_data.columns:
        print(f"Raw Age values in {table_id} (before conversion):", table_data["Age"].head(5).tolist())
        table_data["Age"] = table_data["Age"].apply(parse_age_to_decimal)
        print(f"Processed Age values in {table_id} (after conversion):", table_data["Age"].head(5).tolist())
    print(f"📝 Renamed and cleaned columns in {table_id}:", table_data.columns.tolist())
    table_collection[table_id] = table_data
combined_data = None
for table_id, table_data in table_collection.items():
    table_data = table_data[[col for col in table_data.columns if col in target_columns]]
    table_data = table_data.drop_duplicates(subset=["Player"], keep="first")
    if combined_data is None:
        combined_data = table_data
    else:
        try:
            combined_data = pd.merge(combined_data, table_data, on="Player", how="outer", validate="1:1")
        except Exception as e:
            print(f"❌ Merge error for {table_id}: {e}")
            continue
combined_data = combined_data.loc[:, [col for col in target_columns if col in combined_data.columns]]
combined_data["Minutes"] = pd.to_numeric(combined_data["Minutes"], errors="coerce")
integer_columns = ["Matches Played", "Starts", "Minutes", "Gls", "Ast", "crdY", "crdR", "PrgC", "PrgP", "PrgR",
                   "Cmp", "TotDist", "Tkl", "TklW", "Deff Att", "Lost", "Blocks", "Sh", "Pass", "Int",
                   "Touches", "Def Pen", "Def 3rd", "Mid 3rd", "Att 3rd", "Att Pen", "Take-Ons Att",
                   "Carries", "Carries 1_3", "CPA", "Mis", "Dis", "Rec", "Rec PrgR",
                   "Fls", "Fld", "Off", "Crs", "Recov", "Aerl Won", "Aerl Lost"]
decimal_columns = ["Age", "xG", "xAG", "Gls per 90", "Ast per 90", "xG per 90", "xAG per 90", "GA90", "Save%", "CS%", "PK Save%",
                   "SoT%", "SoT per 90", "G per Sh", "Dist", "Cmp%", "ShortCmp%", "MedCmp%", "LongCmp%", "KP", "Pass into 1_3", "PPA",
                   "CrsPA", "SCA", "SCA90", "GCA", "GCA90", "Succ%", "Tkld%", "ProDist", "Aerl Won%"]
text_columns = ["Player", "Nation", "Team", "Position"]
for col in integer_columns:
    if col in combined_data.columns:
        combined_data[col] = pd.to_numeric(combined_data[col], errors="coerce").astype("Int64")
for col in decimal_columns:
    if col in combined_data.columns:
        combined_data[col] = pd.to_numeric(combined_data[col], errors="coerce").round(2)
combined_data = combined_data[combined_data["Minutes"].notna() & (combined_data["Minutes"] > 90)]
if "Nation" in combined_data.columns:
    combined_data["Nation"] = combined_data["Nation"].apply(get_country_code)
if "Player" in combined_data.columns:
    combined_data["Player"] = combined_data["Player"].apply(format_player_name)
for col in text_columns:
    if col in combined_data.columns:
        combined_data[col] = combined_data[col].fillna("N/A")
print("\n📊 Preview of final DataFrame (first 5 rows) before saving to result.csv:")
print(combined_data.head(5).to_string())
result_csv_path = os.path.join(root_dir, "result.csv")
combined_data.to_csv(result_csv_path, index=False, encoding="utf-8-sig", na_rep="N/A")
print(f"✅ Successfully saved merged data to {result_csv_path} with {combined_data.shape[0]} rows and {combined_data.shape[1]} columns.")
browser_driver.quit()
input_data = pd.read_csv(result_csv_path, na_values=["N/A"])
calc_data = input_data.copy()
non_numeric_columns = ["Player", "Nation", "Team", "Position"]
numeric_columns = [col for col in calc_data.columns if col not in non_numeric_columns]
for col in numeric_columns:
    calc_data[col] = pd.to_numeric(calc_data[col], errors="coerce").fillna(0)
stat_rankings = {}
for col in numeric_columns:
    top_three_high = calc_data[["Player", "Team", col]].sort_values(by=col, ascending=False).head(3)
    top_three_high = top_three_high.rename(columns={col: "Value"})
    top_three_high["Rank"] = ["1st", "2nd", "3rd"]
    if calc_data[col].eq(0).all():
        top_three_low = calc_data[["Player", "Team", col]].sort_values(by=col, ascending=True).head(3)
    else:
        non_zero_data = calc_data[calc_data[col] > 0]
        top_three_low = non_zero_data[["Player", "Team", col]].sort_values(by=col, ascending=True).head(3)
    top_three_low = top_three_low.rename(columns={col: "Value"})
    top_three_low["Rank"] = ["1st", "2nd", "3rd"]
    stat_rankings[col] = {
        "Highest": top_three_high,
        "Lowest": top_three_low
    }
top_three_path = os.path.join(root_dir, "top_3.txt")
with open(top_three_path, "w", encoding="utf-8") as f:
    for stat, data in stat_rankings.items():
        f.write(f"\nStatistic: {stat}\n")
        f.write("\nTop 3 Highest:\n")
        f.write(data["Highest"][["Rank", "Player", "Team", "Value"]].to_string(index=False))
        f.write("\n\nTop 3 Lowest:\n")
        f.write(data["Lowest"][["Rank", "Player", "Team", "Value"]].to_string(index=False))
        f.write("\n" + "-" * 50 + "\n")
print(f"✅ Saved top 3 rankings to {top_three_path}")
stat_rows = []
league_stats = {"": "all"}
for col in numeric_columns:
    league_stats[f"Median of {col}"] = calc_data[col].median()
    league_stats[f"Mean of {col}"] = calc_data[col].mean()
    league_stats[f"Std of {col}"] = calc_data[col].std()
stat_rows.append(league_stats)
teams = sorted(calc_data["Team"].unique())
for team in teams:
    team_subset = calc_data[calc_data["Team"] == team]
    team_metrics = {"": team}
    for col in numeric_columns:
        team_metrics[f"Median of {col}"] = team_subset[col].median()
        team_metrics[f"Mean of {col}"] = team_subset[col].mean()
        team_metrics[f"Std of {col}"] = team_subset[col].std()
    stat_rows.append(team_metrics)
stats_summary = pd.DataFrame(stat_rows)
stats_summary = stats_summary.rename(columns={"": ""})
for col in stats_summary.columns:
    if col != "":
        stats_summary[col] = stats_summary[col].round(2)
stats_csv_path = os.path.join(root_dir, "results2.csv")
stats_summary.to_csv(stats_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ Successfully saved statistics to {stats_csv_path} with {stats_summary.shape[0]} rows and {stats_summary.shape[1]} columns.")
plot_stats = ["Gls per 90", "xG per 90", "SCA90", "GA90", "TklW", "Blocks"]
histogram_folder = os.path.join(root_dir, "histograms")
league_histogram_folder = os.path.join(histogram_folder, "league")
team_histogram_folder = os.path.join(histogram_folder, "teams")
os.makedirs(league_histogram_folder, exist_ok=True)
os.makedirs(team_histogram_folder, exist_ok=True)
teams = sorted(calc_data["Team"].unique())
for stat in plot_stats:
    if stat not in calc_data.columns:
        print(f"⚠️ Statistic {stat} not found in DataFrame. Skipping...")
        continue
    plt.figure(figsize=(10, 6))
    plt.hist(calc_data[stat], bins=20, color="skyblue", edgecolor="black")
    plt.title(f"League-Wide Distribution of {stat}")
    plt.xlabel(stat)
    plt.ylabel("Number of Players")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(league_histogram_folder, f"{stat}_league.png"), bbox_inches="tight")
    plt.close()
    print(f"📊 Saved league-wide histogram for {stat}")
    for team in teams:
        team_subset = calc_data[calc_data["Team"] == team]
        plt.figure(figsize=(8, 6))
        plt.hist(team_subset[stat], bins=10, color="lightgreen" if stat in ["GA90", "TklW", "Blocks"] else "skyblue",
                 edgecolor="black", alpha=0.7)
        plt.title(f"{team} - Distribution of {stat}")
        plt.xlabel(stat)
        plt.ylabel("Number of Players")
        plt.grid(True, alpha=0.3)
        stat_file_name = stat.replace(" ", "_")
        plt.savefig(os.path.join(team_histogram_folder, f"{team}_{stat_file_name}.png"), bbox_inches="tight")
        plt.close()
        print(f"📊 Saved histogram for {team} - {stat}")
print("✅ All histograms for selected statistics have been generated and saved under 'histograms'.")
team_averages = calc_data.groupby("Team")[numeric_columns].mean().reset_index()
top_team_stats = []
for stat in numeric_columns:
    if stat not in calc_data.columns:
        print(f"⚠️ Statistic {stat} not found in DataFrame. Skipping...")
        continue
    top_row = team_averages.loc[team_averages[stat].idxmax()]
    top_team_stats.append({
        "Statistic": stat,
        "Team": top_row["Team"],
        "Mean Value": round(top_row[stat], 2)
    })
top_team_data = pd.DataFrame(top_team_stats)
top_team_csv_path = os.path.join(root_dir, "highest_team_stats.csv")
top_team_data.to_csv(top_team_csv_path, index=False, encoding="utf-8-sig")
print(f"✅ Saved highest team stats to {top_team_csv_path} with {top_team_data.shape[0]} rows.")
negative_metrics = [
    "GA90", "CrdY", "CrdR", "Lost", "Mis", "Dis", "Fls", "Off", "Aerl Lost"
]
top_team_data = pd.read_csv(top_team_csv_path)
positive_stats_data = top_team_data[~top_team_data["Statistic"].isin(negative_metrics)]
team_rank_counts = positive_stats_data["Team"].value_counts()
top_team = team_rank_counts.idxmax()
lead_count = team_rank_counts.max()
print(f"The best-performing team in the 2024-2025 Premier League season is: {top_team}")
print(f"They lead in {lead_count} out of {len(positive_stats_data)} positive statistics.")