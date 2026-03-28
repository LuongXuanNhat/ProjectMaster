import json
import os
import sys
import time
from typing import List
from pydantic import BaseModel, Field

# Fix for windows console printing unicode characters
sys.stdout.reconfigure(encoding='utf-8')

try:
    from google import genai
except ImportError:
    print("Vui lòng cài đặt các thư viện yêu cầu: pip install google-genai pydantic")
    sys.exit(1)

# Định nghĩa Schema cho kết quả của 1 câu
class LabelOutput(BaseModel):
    name: str = Field(description="Tên tiêu chí. Phải là một trong: 'Food quality', 'Price', 'Service quality', 'Hygiene and safety', 'Atmosphere'")
    value: float = Field(description="Giá trị cảm xúc. Chỉ dùng: 0.0 (NEGATIVE), 0.5 (NEUTRAL), hoặc 1.0 (POSITIVE)")

class ReviewAnalysis(BaseModel):
    original_index: int = Field(description="Chỉ số (index) của review được đưa vào để đối chiếu.")
    reasoning: str = Field(description="Dẫn chứng/lý giải ngắn gọn bằng Tiếng Việt tại sao lại chọn các nhãn này.")
    labels: List[LabelOutput] = Field(description="Danh sách các nhãn được trích xuất.")

# Định nghĩa Schema cho kết quả của cả 1 batch
class BatchReviewAnalysis(BaseModel):
    results: List[ReviewAnalysis] = Field(description="Danh sách kết quả gán nhãn cho các review, đảm bảo trả về đủ số lượng truyền vào.")

def read_prompt(filepath="label_studio_prompt.txt"):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # CÁCH 1: Xoay vòng (Rotate) API Key
    # Bạn có thể đăng ký 2-3 acc clone lấy key dán vào đây, code sẽ tự nhảy sang key khác khi 1 key bị limit.
    api_keys = [
        "AIzaSyCtEHSLUZuzrnFEyeoXPJkuRx4SYksYwiU",
        # "DÁN_API_KEY_2_CỦA_BẠN_VÀO_ĐÂY", 
        # "DÁN_API_KEY_3_CỦA_BẠN_VÀO_ĐÂY"
    ]
    current_key_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])

    sys_prompt = read_prompt("label_studio_prompt.txt")
    
    input_file = "exported_data_02.json"
    output_file = "labeled_results_batch.json"
    
    data_all = load_data(input_file)
    total_reviews = len(data_all)
    print(f"Tổng số review cần xử lý: {total_reviews}")

    # Đọc kết quả đã lưu trước đó nếu có (để chạy tiếp nếu bị ngắt)
    if os.path.exists(output_file):
        labeled_data = load_data(output_file)
        print(f"Đã tìm thấy file {output_file} chứa {len(labeled_data)} kết quả.")
    else:
        labeled_data = []

    # Số lượng dữ liệu đã gán nhãn thành công dựa theo index
    processed_indices = {item.get("index") for item in labeled_data if item.get("index") is not None}
    
    BATCH_SIZE = 50 
    
    # Lọc ra những review chưa được xử lý
    reviews_to_process = []
    for idx, item in enumerate(data_all):
        if idx not in processed_indices:
            reviews_to_process.append({"index": idx, "review": item})
            
    if not reviews_to_process:
        print("Đã xử lý xong toàn bộ dữ liệu!")
        return

    print(f"Còn lại {len(reviews_to_process)} review cần xử lý. Bắt đầu chạy theo batch size = {BATCH_SIZE}...")

    # Chạy từng Batch
    for i in range(0, len(reviews_to_process), BATCH_SIZE):
        batch = reviews_to_process[i : i + BATCH_SIZE]
        
        # Format đầu vào cho batch
        batch_text_input = ""
        for b in batch:
            batch_text_input += f"[{b['index']}] {b['review'].get('textTranslated', '')}\n\n"
            
        prompt = (
            f"{sys_prompt}\n\nDưới đây là danh sách các Review thực tế cần đánh giá. Mỗi review bắt đầu bằng [index]. "
            "Hãy phân tích và trả về mảng kết quả 'results'. Đảm bảo phần 'original_index' trong JSON đầu ra ứng với số [index] của Review đó.\n\n"
            f"DANH SÁCH REVIEW:\n{batch_text_input}"
        )
        
        print(f"Đang xử lý batch từ index {batch[0]['index']} đến {batch[-1]['index']} (Kích thước: {len(batch)})...")
        
        while True:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": BatchReviewAnalysis,
                        "temperature": 0.1,
                    }
                )
                
                result_json = json.loads(response.text)
                batch_results = result_json.get("results", [])
                
                # Map kết quả lại vào dữ liệu gốc
                for res in batch_results:
                    original_idx = res.get("original_index")
                    
                    # Check for bounds to prevent IndexError if Gemini hallucinates an index
                    if not isinstance(original_idx, int) or original_idx < 0 or original_idx >= len(data_all):
                        print(f"Bỏ qua kết quả do index không hợp lệ: {original_idx}")
                        continue

                    # Tìm item gốc tương ứng
                    original_item = data_all[original_idx]
                    
                    # Tạo bản ghi mới gộp thông tin
                    labeled_item = {
                        "index": original_idx,
                        "original_data": original_item,
                        "reasoning": res.get("reasoning", ""),
                        "labels": res.get("labels", [])
                    }
                    labeled_data.append(labeled_item)
                    processed_indices.add(original_idx)
                    
                # Lưu liên tục sau mỗi batch để không mất dữ liệu
                save_data(labeled_data, output_file)
                print(f" => Thành công! Đã lưu tiến độ ({len(processed_indices)}/{total_reviews}).")
                
                # Sleep một chút để tránh rate limit (20 reqs/phút cho bản Free)
                time.sleep(3)
                break  # Thành công thì thoát vòng lặp while để sang batch tiếp theo
                
            except Exception as e:
                error_str = str(e)
                print(f"Lỗi khi xử lý batch {batch[0]['index']} - {batch[-1]['index']}: {error_str[:300]}...\n")
                
                # Bắt lỗi dính Rate Limit (429) hoặc Limit Quota
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if len(api_keys) > 1:
                        # Cách giải quyết triệt để 1: Đổi sang key khác chạy luôn không cần đợi
                        current_key_idx = (current_key_idx + 1) % len(api_keys)
                        print(f"-> Quá tải! Tự động chuyển qua xài API Key số {current_key_idx + 1}...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(1)
                    else:
                        # Cách giải quyết 2 (Của hiện tại): Đoán đúng số giây cần dừng
                        import re
                        match = re.search(r"retry in (\d+\.?\d*)s", error_str)
                        wait_seconds = int(float(match.group(1))) + 2 if match else 65
                        
                        print(f"-> Quá tải (chỉ có 1 key)! Google yêu cầu chờ khôi phục... Đang tự động ngủ {wait_seconds} giây!")
                        time.sleep(wait_seconds)
                else:
                    print("-> Lỗi khác (không phải rate limit). Chờ 10s rồi thử lại vòng lặp...")
                    time.sleep(10)
            
    print(f"\nHoàn tất! Kết quả được lưu tại {output_file}")

if __name__ == "__main__":
    main()
