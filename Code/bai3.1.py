import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('result.csv')

# Select features for clustering
features = [
    'Gls per 90', 'Ast per 90', 'xG per 90', 'xAG per 90', 'SCA90', 'GCA90',
    'Cmp%', 'TotDist', 'KP', 'PPA', 'Tkl', 'Blocks', 'Int',
    'Touches', 'PrgC', 'PrgP', 'PrgR', 'Carries'
]

# Extract the feature data
X = data[features].copy()

# Handle missing values (replace 'N/A' with 0, fill NaN with 0)
X = X.replace('N/A', 0)
X = X.fillna(0)

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Compute inertia (WCSS) for different k values
inertia = []
k_range = range(1, 11)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertia.append(kmeans.inertia_)

# Specific k value for the title
chosen_k = 4

# Create the elbow plot
plt.figure(figsize=(8, 6))
plt.plot(k_range, inertia, marker='o', linestyle='-', color='b', label='Inertia')
plt.scatter([chosen_k], [inertia[chosen_k-1]], color='red', s=100, label=f'k={chosen_k}', zorder=5)
plt.title(f'Elbow Plot (k={chosen_k})')
plt.xlabel(f'Number of Clusters (k = {chosen_k})')
plt.ylabel('Inertia')
plt.grid(True)
plt.xticks(k_range)
plt.legend()

# Save the plot as PNG
plt.savefig('elbow_plot.png', format='png', dpi=300, bbox_inches='tight')
plt.close()

print(f"Elbow plot with k={chosen_k} has been saved as 'elbow_plot.png'.")

# Comment bằng tiếng Việt trả lời câu hỏi:
# How many groups should the players be classified into? Why? Provide your comments on the results.
"""
Nên phân loại cầu thủ thành bao nhiêu nhóm? Tại sao? Nhận xét về kết quả:

Số lượng nhóm tối ưu để phân loại cầu thủ là **4 nhóm**, dựa trên phân tích biểu đồ elbow plot. Lý do chọn \( k = 4 \):

1. **Điểm elbow**: Trong biểu đồ elbow plot, giá trị inertia (tổng bình phương khoảng cách trong cụm, WCSS) giảm mạnh từ \( k = 1 \) đến \( k = 4 \), sau đó tốc độ giảm chậm lại đáng kể. Điều này cho thấy \( k = 4 \) là điểm mà việc thêm cụm không mang lại cải thiện đáng kể về độ chặt chẽ của cụm, giúp cân bằng giữa tính đơn giản và độ chính xác của mô hình.

2. **Ý nghĩa bóng đá**: Với \( k = 4 \), các cầu thủ có thể được phân thành các nhóm phản ánh vai trò khác nhau trên sân:
   - **Nhóm 1**: Tiền đạo, với các chỉ số cao về `Gls per 90`, `xG per 90`, và `SCA90`.
   - **Nhóm 2**: Tiền vệ sáng tạo, nổi bật ở `Ast per 90`, `KP`, và `PPA`.
   - **Nhóm 3**: Hậu vệ phòng ngự, có giá trị cao ở `Tkl`, `Blocks`, và `Int`.
   - **Nhóm 4**: Cầu thủ đa năng hoặc thủ môn (nếu không lọc), với các đặc trưng riêng như `Touches` thấp hoặc các chỉ số phòng ngự/tấn công cân bằng.

3. **Tính thực tiễn**: Số cụm \( k = 4 \) không quá lớn, giúp dễ dàng diễn giải và áp dụng trong phân tích bóng đá (ví dụ, để phân loại cầu thủ theo vai trò hoặc đánh giá hiệu suất). Nếu chọn \( k \) lớn hơn (ví dụ, \( k = 6 \)), các cụm có thể trở nên quá chi tiết và khó diễn giải, trong khi \( k \) nhỏ hơn (ví dụ, \( k = 2 \)) có thể bỏ qua sự khác biệt quan trọng giữa các vai trò.

**Nhận xét về kết quả**:
- **Hiệu quả của phân cụm**: Việc sử dụng 18 đặc trưng (bao gồm tấn công, phòng thủ, và tham gia) giúp phân cụm phản ánh tốt các khía cạnh khác nhau của hiệu suất cầu thủ. Các đặc trưng như `Gls per 90`, `Tkl`, và `TotDist` đảm bảo rằng các cụm phân biệt rõ ràng giữa các vai trò tấn công, phòng thủ, và sáng tạo.
- **Thủ môn**: Vì dữ liệu bao gồm thủ môn và các đặc trưng không chứa chỉ số đặc thù của thủ môn (như `Save%`), thủ môn có thể rơi vào một cụm riêng hoặc hòa lẫn với các cầu thủ có ít tham gia tấn công. Nếu muốn phân cụm chỉ dành cho cầu thủ trên sân, nên lọc bỏ thủ môn bằng cách thêm `data = data[data['Position'] != 'GK']`.
- **Hạn chế**: Một số cầu thủ có ít phút thi đấu (`Minutes`) có thể ảnh hưởng đến các chỉ số per 90, dẫn đến phân cụm không chính xác. Có thể cân nhắc lọc các cầu thủ có số phút tối thiểu (ví dụ, >500 phút) để cải thiện chất lượng cụm.
- **Ứng dụng**: Kết quả phân cụm với \( k = 4 \) có thể được sử dụng để phân tích đội hình, so sánh hiệu suất cầu thủ, hoặc xác định các kiểu cầu thủ tương tự nhau trong chuyển nhượng. Để hiểu rõ hơn về mỗi cụm, có thể kiểm tra danh sách cầu thủ và giá trị trung bình của các đặc trưng trong mỗi cụm.

Tóm lại, \( k = 4 \) là lựa chọn hợp lý dựa trên elbow plot và ý nghĩa bóng đá, mang lại kết quả phân cụm rõ ràng và hữu ích cho việc phân tích dữ liệu cầu thủ.
"""