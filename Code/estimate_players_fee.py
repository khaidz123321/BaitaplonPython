import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fuzzywuzzy import fuzz, process
from selenium.common.exceptions import TimeoutException, NoSuchElementException

"""
Mục đích: Crawl dữ liệu giá trị chuyển nhượng ước tính (ETV) từ FootballTransfers
để tạo file all_estimate_transfer_fee.csv với số lượng cầu thủ tối đa.
"""

# Thư mục gốc và đường dẫn
base_dir = r"C:\Users\DD\OneDrive\Documents\newfolder(2)\btlpython"
csv_dir = os.path.join(base_dir, "csv")
os.makedirs(csv_dir, exist_ok=True)
result_path = os.path.join(csv_dir, "result.csv")
output_path = os.path.join(csv_dir, "all_estimate_transfer_fee.csv")

# Hàm rút ngắn tên để so khớp
def shorten_name(name):
    special_cases = {
        "Manuel Ugarte Ribeiro": "Manuel Ugarte",
        "Igor Júlio": "Igor",
        "Igor Thiago": "Thiago",
        "Felipe Morato": "Morato",
        "Nathan Wood-Gordon": "Nathan Wood",
        "Bobby Reid": "Bobby Cordova-Reid",
        "J. Philogene": "Jaden Philogene Bidace"
    }
    if name in special_cases:
        return special_cases[name]
    parts = name.strip().split()
    return f"{parts[0]} {parts[-1]}" if len(parts) >= 3 else name

# Đọc danh sách cầu thủ từ result.csv (nếu có)
player_positions = {}
player_original_names = {}
player_names = []

if os.path.exists(result_path):
    try:
        df_players = pd.read_csv(result_path)
        player_positions = dict(zip(df_players['Player'].str.strip().apply(shorten_name), df_players['Position']))
        player_original_names = dict(zip(df_players['Player'].str.strip().apply(shorten_name), df_players['Player'].str.strip()))
        player_names = list(player_positions.keys())
        print(f"Loaded {len(player_names)} players from result.csv")
    except Exception as e:
        print(f"Error reading result.csv: {e}")
        print("Proceeding without player matching...")
else:
    print("result.csv not found. Crawling all players without matching.")

# Cấu hình trình duyệt
options = Options()
options.add_argument("--headless")  # Chạy ẩn, bỏ comment để debug: # options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Khởi tạo ChromeDriver
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
except Exception as e:
    print(f"Error initializing ChromeDriver: {e}")
    exit(1)

# Xác định số trang tối đa bằng cách kiểm tra nút phân trang
base_url = "https://www.footballtransfers.com/us/players/uk-premier-league/"
max_pages = 1
try:
    driver.get(base_url + "1")
    pagination = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
    )
    page_links = pagination.find_elements(By.TAG_NAME, "a")
    for link in page_links:
        try:
            page_num = int(link.text)
            max_pages = max(max_pages, page_num)
        except ValueError:
            continue
    print(f"Detected {max_pages} pages to crawl")
except Exception as e:
    print(f"Error detecting pagination: {e}. Defaulting to 22 pages.")
    max_pages = 22

urls = [f"{base_url}{i}" for i in range(1, max_pages + 1)]

# Danh sách dữ liệu
data_gk = []
data_df = []
data_mf = []
data_fw = []
all_data_unmatched = []  # Lưu cầu thủ không khớp (nếu không có result.csv)

try:
    for url in urls:
        print(f"Scraping: {url}")
        for attempt in range(3):  # Thử lại tối đa 3 lần nếu lỗi
            try:
                driver.get(url)
                # Đợi bảng xuất hiện
                table = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "similar-players-table"))
                )
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if cols and len(cols) >= 2:
                        # Lấy tên cầu thủ
                        player_name = cols[1].text.strip().split("\n")[0].strip()
                        shortened_player_name = shorten_name(player_name)
                        # Lấy ETV
                        etv = cols[-1].text.strip() if len(cols) >= 3 else "N/A"
                        
                        # So khớp tên
                        if player_names:
                            best_match = process.extractOne(
                                shortened_player_name, player_names, scorer=fuzz.token_sort_ratio
                            )
                            if best_match and best_match[1] >= 70:  # Giảm ngưỡng để giữ nhiều cầu thủ hơn
                                matched_name = best_match[0]
                                original_name = player_original_names.get(matched_name, matched_name)
                                position = player_positions.get(matched_name, "Unknown")
                                print(f"Match found: {player_name} -> {original_name} (score: {best_match[1]}, Position: {position})")
                                
                                # Lưu theo vị trí
                                if "GK" in position:
                                    data_gk.append([original_name, position, etv])
                                elif position.startswith("DF"):
                                    data_df.append([original_name, position, etv])
                                elif position.startswith("MF"):
                                    data_mf.append([original_name, position, etv])
                                elif position.startswith("FW"):
                                    data_fw.append([original_name, position, etv])
                            else:
                                print(f"No match for: {player_name} (best match: {best_match[0] if best_match else 'None'}, score: {best_match[1] if best_match else 'N/A'})")
                                all_data_unmatched.append([player_name, "Unknown", etv])
                        else:
                            # Lưu tất cả cầu thủ nếu không có result.csv
                            all_data_unmatched.append([player_name, "Unknown", etv])
                break  # Thoát vòng lặp thử lại nếu thành công
            except TimeoutException:
                print(f"Timeout on {url}, attempt {attempt + 1}/3")
                time.sleep(2)
            except Exception as e:
                print(f"Error processing {url}, attempt {attempt + 1}/3: {e}")
                time.sleep(2)
        else:
            print(f"Failed to process {url} after 3 attempts")
finally:
    driver.quit()
    print("WebDriver closed.")

# Gộp dữ liệu
all_data = data_gk + data_df + data_mf + data_fw
if not player_names:
    all_data += all_data_unmatched  # Thêm cầu thủ không khớp nếu không có result.csv

# Lưu vào CSV
if all_data:
    df_all = pd.DataFrame(all_data, columns=['Player', 'Position', 'Price'])
    df_all = df_all.drop_duplicates(subset=['Player'])  # Loại bỏ trùng lặp
    df_all.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"File 'all_estimate_transfer_fee.csv' saved to: {output_path}")
    print(f"Total players scraped: {len(df_all)} (GK: {len(data_gk)}, DF: {len(data_df)}, MF: {len(data_mf)}, FW: {len(data_fw)})")
    if all_data_unmatched and player_names:
        print(f"Unmatched players: {len(all_data_unmatched)}")
else:
    print("No players found. Check URL, table structure, or internet connection.")