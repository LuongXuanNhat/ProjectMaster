# Chiến lược Cân bằng Dữ liệu - Phân tích Cảm xúc theo Khía cạnh (ABSA)

## 1. Nhận xét tổng quan về phân phối dữ liệu hiện tại
- **"Khan hiếm" lời chê (Nhãn 0.0):** Cả 5 tiêu chí đều thiếu hụt nghiêm trọng nhãn 0.0 (nhiều nhất là 963 ở Phục vụ, ít nhất là 314 ở Vệ sinh).
- **Sự áp đảo của nhãn 1.0 ở Món ăn:** Chiếm tới 6802 mẫu.
- **"Bóng ma" Trung tính (Nhãn 0.5):** Nhãn 0.5 chiếm đến 8575 mẫu ở Vệ sinh và 7211 mẫu ở Giá cả, dễ gây nhiễu và làm mô hình thiên lệch (auto dự đoán 0.5).

## 2. Chiến lược Cân bằng lý tưởng
**Ngưỡng mục tiêu:** $N_{target} = 2500$ mẫu cho mỗi nhãn.
Đảm bảo $\sim 7500$ mẫu cho mỗi tiêu chí, hoàn toàn đủ lớn để train các mô hình Deep Learning/Transformer (như PhoBERT) mà không bị Overfitting.

| Tiêu chí | Nhãn | Số lượng hiện tại | Cần thêm/bớt (Mục tiêu 2500) | Hành động đề xuất |
|---|---|---|---|---|
| **Food quality** | Tiêu cực (0.0) | 702 | +1798 | Thu thập thêm / Augment |
| | Trung tính (0.5) | 2252 | +248 | Thu thập thêm nhẹ |
| | Tích cực (1.0) | 6802 | -4302 | Undersampling (Cắt giảm) |
| **Price** | Tiêu cực (0.0) | 504 | +1996 | Thu thập thêm / Augment |
| | Trung tính (0.5) | 7211 | -4711 | Undersampling (Cắt giảm) |
| | Tích cực (1.0) | 2041 | +459 | Thu thập thêm nhẹ |
| **Service quality** | Tiêu cực (0.0) | 963 | +1537 | Thu thập thêm / Augment |
| | Trung tính (0.5) | 3965 | -1465 | Undersampling (Cắt giảm) |
| | Tích cực (1.0) | 4828 | -2328 | Undersampling (Cắt giảm) |
| **Hygiene and safety**| Tiêu cực (0.0) | 314 | +2186 | Thu thập thêm / Augment |
| | Trung tính (0.5) | 8575 | -6075 | Undersampling (Cắt giảm) |
| | Tích cực (1.0) | 867 | +1633 | Thu thập thêm / Augment |
| **Atmosphere** | Tiêu cực (0.0) | 344 | +2156 | Thu thập thêm / Augment |
| | Trung tính (0.5) | 4813 | -2313 | Undersampling (Cắt giảm) |
| | Tích cực (1.0) | 4599 | -2099 | Undersampling (Cắt giảm) |

## 3. Phương án thực thi chi tiết

**Bước 1: Thu thập có chủ đích (Targeted Crawling) để cứu nhãn 0.0**
- Chỉ filter và cào các review **1 sao và 2 sao** trên các nền tảng (ShopeeFood, Foody, Google Maps).
- Các review này chắc chắn chứa nhãn 0.0 cho các tiêu chí Vệ sinh, Giá cả, Không gian và Phục vụ. Mục tiêu cào thêm khoảng 2000 - 3000 review.

**Bước 2: Cắt giảm dữ liệu thông minh (Smart Undersampling) cho nhãn 0.5 và 1.0**
- Đừng dùng hàm random.choice() để xóa đi, hãy xóa có chọn lọc.
- Loại bỏ các câu review quá ngắn (dưới 5 từ) hoặc chỉ chứa emoji (ví dụ: "ngon", "tốt", "ok").
- Giữ lại các câu review có cấu trúc câu phức tạp, chứa nhiều khía cạnh cùng lúc (ví dụ: "Đồ ăn ngon nhưng quán hơi dơ" -> Vừa giữ được 1.0 cho Food, vừa lấy được 0.0 cho Hygiene).

**Bước 3: Data Augmentation (Giải pháp chốt chặn)**
- Sau khi cào thêm review 1-2 sao, nếu nhãn 0.0 (ví dụ của Vệ sinh) vẫn chưa đủ 2500, tiến hành nhân bản dữ liệu.
- **Thay thế từ đồng nghĩa:** "Quán dơ quá" -> "Quán bẩn quá", "Không gian chật chội" -> "Chỗ ngồi bí bách".
- **Back-translation:** Dịch Việt -> Anh -> Việt.
