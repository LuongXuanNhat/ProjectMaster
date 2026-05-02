# Chiến lược Cân bằng Dữ liệu - Phân tích Cảm xúc theo Khía cạnh (ABSA) - Giai đoạn 2

## 1. Tóm tắt kết quả xử lý Giai đoạn 1 (Smart Undersampling)

Trong Giai đoạn 1, chúng ta đã tiến hành chạy thuật toán **Smart Undersampling** trên tập dữ liệu gốc `labeled_results_all_v3.json` (hơn 516k mẫu). Quá trình xử lý tuân thủ các bước:

1. **Bảo tồn nhãn hiếm:** Giữ lại 100% các câu review chứa ít nhất một nhãn đang bị thiếu hụt (tất cả các nhãn `0.0` và nhãn `Hygiene 1.0`).
2. **Lọc câu phức tạp:** Sắp xếp các mẫu còn lại theo độ dài văn bản giảm dần, ưu tiên giữ lại các review dài, có cấu trúc phức để làm phong phú dữ liệu.
3. **Cân bằng số lượng:** Tiến hành điền thêm các câu vào tập dữ liệu mới cho đến khi tất cả các nhãn (kể cả nhóm trung tính `0.5` hoặc tích cực `1.0`) đạt đến điểm bão hòa mục tiêu là 2500 mẫu.
4. **Chuẩn hóa Index:** Đánh lại `index` từ `0` cho toàn bộ tập dữ liệu đã lọc.

**Kết quả thu được trong file `data_balanced.json` (Tổng cộng: 8,442 mẫu):**

| Tiêu chí | 0.0 (Tiêu cực) | 0.5 (Trung tính) | 1.0 (Tích cực) |
|---|---|---|---|
| **Food quality** | 1,131 *(Max gốc)* | 2,500 | 4,810 |
| **Price** | 831 *(Max gốc)* | 5,080 | 2,522 |
| **Service quality**| 1,601 *(Max gốc)* | 3,032 | 3,808 |
| **Hygiene and safety**| 504 *(Max gốc)* | 6,401 | 1,526 *(Max gốc)* |
| **Atmosphere** | 514 *(Max gốc)* | 4,077 | 3,849 |

**Đánh giá:** Giai đoạn 1 đã giải quyết triệt để sự mất cân bằng của các nhãn thừa (ví dụ: `Hygiene 0.5` giảm từ 14,604 xuống 6,401; `Food 1.0` giảm từ 12,094 xuống 4,810). Tuy nhiên, do bản chất tập dữ liệu gốc bị thiếu hụt, số lượng nhãn `0.0` đã đạt tối đa giới hạn có thể lấy nhưng vẫn chưa đủ 2500 mẫu/nhãn.

---

## 2. Chiến lược xử lý mới (Giai đoạn 2 - Tập trung tăng cường nhãn 0.0)

Mục tiêu chính hiện tại là lấp đầy khoảng trống của nhóm nhãn `0.0` (còn thiếu từ 899 đến 1,996 mẫu tùy tiêu chí) và `Hygiene 1.0`. Dưới đây là 3 hướng giải quyết được đề xuất ưu tiên theo tính khả thi:

### Phương án 1: Data Augmentation thông qua LLM (Đề xuất cao nhất)
Thay vì đi thu thập thêm (crawling) mất nhiều công sức làm sạch lại từ đầu, chúng ta có thể sử dụng các API LLM (như Gemini, GPT) để sinh thêm dữ liệu dựa trên tập 0.0 hiện có.
- **Cách làm:** Lấy 100 câu review `0.0` có sẵn, yêu cầu LLM "Viết lại 10 câu này thành các đoạn review khác nhau về cách diễn đạt, từ vựng nhưng giữ nguyên ý nghĩa chê bai về Không gian/Giá cả/Vệ sinh".
- **Ưu điểm:** Nhanh chóng tạo ra chính xác lượng data bị thiếu, ngôn từ tự nhiên, không bị nhiễu nhãn.

### Phương án 2: Data Augmentation bằng Back-Translation
Sử dụng các công cụ dịch thuật tự động (Google Translate API).
- **Cách làm:** Dịch câu tiếng Việt (nhãn 0.0) -> Tiếng Anh / Tiếng Hàn -> Dịch ngược lại tiếng Việt.
- **Ưu điểm:** Tạo ra biến thể từ ngữ đồng nghĩa (Ví dụ: "Quán bẩn quá" -> "The restaurant is too dirty" -> "Nhà hàng quá dơ bẩn"). Tự động hóa hoàn toàn 100% bằng script Python.

### Phương án 3: Targeted Crawling (Cào dữ liệu có chủ đích)
Nếu muốn dữ liệu thực tế 100% thay vì sinh tự động.
- **Cách làm:** Viết script cào dữ liệu trên ShopeeFood, Google Maps, nhưng **CHỈ LỌC** các đánh giá có mức rating `1 sao` hoặc `2 sao`.
- **Nhược điểm:** Phải trải qua bước Labeling lại từ đầu cho các dữ liệu mới cào này để lấy nhãn 0.0 chính xác cho từng tiêu chí.

**Hành động tiếp theo:** Quyết định chọn 1 trong 3 phương án trên và viết script xử lý cho file `data_balanced.json` để hoàn thiện bộ data chuẩn cuối cùng.
