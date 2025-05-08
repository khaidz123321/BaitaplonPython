from fuzzywuzzy import fuzz, process
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os

# Thư mục gốc
root_dir = r"C:\Users\DD\OneDrive\Documents\newfolder(2)\btlpython"
csv_folder = os.path.join(root_dir, "csv")
os.makedirs(csv_folder, exist_ok=True)
result_csv_path = os.path.join(csv_folder, "result.csv")

# Kiểm tra file result.csv tồn tại
if not os.path.exists(result_csv_path):
    print(f"Error: File {result_csv_path} does not exist.")
    exit()

# Đọc file CSV
try:
    data_frame = pd.read_csv(result_csv_path, na_values=["N/A"])
except Exception as e:
    print(f"Error reading {result_csv_path}: {str(e)}")
    exit()

calc_data_frame = data_frame.copy()
filtered_data_frame = calc_data_frame[calc_data_frame['Minutes'] > 900].copy()
print(f"Number of players with more than 900 minutes: {len(filtered_data_frame)}")

filtered_csv_path = os.path.join(root_dir, "csv", "players_over_900_minutes.csv")
filtered_data_frame.to_csv(filtered_csv_path, index=False, encoding='utf-8-sig')
print(f"Saved filtered players to {filtered_csv_path} with {filtered_data_frame.shape[0]} rows and {filtered_data_frame.shape[1]} columns.")

def truncate_name(name):
    parts = name.strip().split()
    return " ".join(parts[:2]) if len(parts) >= 2 else name

# Đọc danh sách cầu thủ đã lọc
filtered_csv_file = os.path.join(root_dir, "csv", "players_over_900_minutes.csv")
try:
    players_data_frame = pd.read_csv(filtered_csv_file)
except Exception as e:
    print(f"Error reading {filtered_csv_file}: {str(e)}")
    exit()

short_player_names = [truncate_name(name) for name in players_data_frame['Player'].str.strip()]
minutes_by_player = dict(zip(players_data_frame['Player'].str.strip(), players_data_frame['Minutes']))

# Cấu hình trình duyệt
browser_options = Options()
browser_options.add_argument("--headless")
browser_options.add_argument("--no-sandbox")
browser_options.add_argument("--disable-dev-shm-usage")
browser_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Khởi tạo WebDriver
browser_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=browser_options)
transfer_base_url = "https://www.footballtransfers.com/us/transfers/confirmed/2024-2025/uk-premier-league/"
transfer_urls = [f"{transfer_base_url}{i}" for i in range(1, 15)]
transfer_data = []

try:
    for url in transfer_urls:
        print(f"Scraping: {url}")
        browser_driver.get(url)
        try:
            transfer_table = WebDriverWait(browser_driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "transfer-table"))
            )
            table_rows = transfer_table.find_elements(By.TAG_NAME, "tr")
            print(f"Found {len(table_rows)} rows in table at {url}")
            for row in table_rows:
                table_columns = row.find_elements(By.TAG_NAME, "td")
                if table_columns and len(table_columns) >= 2:
                    full_player_name = table_columns[0].text.strip().split("\n")[0].strip()
                    short_player_name = truncate_name(full_player_name)
                    transfer_fee = table_columns[-1].text.strip() if len(table_columns) >= 3 else "N/A"
                    print(f"Processing player: {full_player_name}, Short name: {short_player_name}, Fee: {transfer_fee}")
                    top_match = process.extractOne(short_player_name, short_player_names, scorer=fuzz.token_sort_ratio)
                    if top_match and top_match[1] >= 80:
                        matched_player_name = top_match[0]
                        print(f"Matched: {full_player_name} -> {matched_player_name} (Score: {top_match[1]})")
                        transfer_data.append([full_player_name, transfer_fee])
                else:
                    print(f"Skipping row with insufficient columns: {len(table_columns)}")
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
finally:
    browser_driver.quit()

if transfer_data:
    transfer_data_frame = pd.DataFrame(transfer_data, columns=['Player', 'Price'])
    transfer_data_frame.to_csv(os.path.join(root_dir, "csv", "player_transfer_fee.csv"), index=False)
    print(f"Results saved to '{os.path.join(root_dir, 'csv', 'player_transfer_fee.csv')}' with {len(transfer_data)} records")
else:
    print("No matching players found.")