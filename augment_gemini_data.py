import json
import os
import sys
import time
import random
from typing import List
from collections import defaultdict

# Fix for windows console printing unicode characters
sys.stdout.reconfigure(encoding='utf-8')

try:
    from google import genai
    from pydantic import BaseModel, Field
except ImportError:
    print("Vui lòng cài đặt các thư viện yêu cầu: pip install google-genai pydantic")
    sys.exit(1)

class AugmentedReview(BaseModel):
    original_index: int = Field(description="Chỉ số (index) của review gốc được đưa vào.")
    augmented_text: str = Field(description="Nội dung review sau khi được viết lại (paraphrase).")

class BatchAugmented(BaseModel):
    results: List[AugmentedReview] = Field(description="Danh sách các review đã được viết lại.")

def load_data(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_stats(data_list):
    stats = defaultdict(lambda: defaultdict(int))
    for item in data_list:
        for label in item.get('labels', []):
            stats[label['name']][label['value']] += 1
    return stats

def main():
    api_keys = [
        # "AIzaSyAVX6xqswPMNQS16GJMsgyICgTkNx02Y1A",  # toiyeuntl@gmail.com
        # "AIzaSyBPzoKhML0Rz20MvcccHNIrKQ2AA1_SY6E", # xuannhat1832002
        # "AIzaSyCi4sABANCYtF2L7G-HdmwJ2boW2Jc2MCw" # xuannhat1932002
        "AIzaSyBKYln2X1b27_HEptr8jHSztLSIgpscwwk", 
        "AIzaSyBXAc8bTpgUPAwbPWou4QTfddykZZI4Am8",
        "AIzaSyD8i6h7K55NaoKbWcurFajlHvxNGZJyixg"
    ]
    current_key_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])

    base_file = "data_balanced.json"
    output_file = "augmented_data_only.json"
    
    if not os.path.exists(base_file):
        print(f"Không tìm thấy {base_file}. Vui lòng chạy script cân bằng dữ liệu trước.")
        return

    data_balanced = load_data(base_file)
    augmented_data = load_data(output_file)
    
    print(f"Đã tải {len(data_balanced)} mẫu từ {base_file}")
    print(f"Đã tải {len(augmented_data)} mẫu từ {output_file} (Tiến độ cũ)")

    target = 2500
    BATCH_SIZE = 20  # Batch nhỏ hơn để Gemini paraphrase chất lượng tốt hơn

    sys_prompt = (
        "Bạn là một chuyên gia ngôn ngữ. Dưới đây là các đánh giá của khách hàng về nhà hàng "
        "(mỗi đánh giá bắt đầu bằng [index]). Nhiệm vụ của bạn là VIẾT LẠI (paraphrase) từng đánh giá "
        "thành một phiên bản MỚI (thay đổi từ vựng, cấu trúc câu, cách diễn đạt) nhưng BẮT BUỘC "
        "phải giữ nguyên vẹn các ý nghĩa khen/chê gốc. Giữ ngôn ngữ tự nhiên như người thật viết.\n\n"
        "ĐẶC BIỆT CHÚ Ý: Sử dụng từ ngữ phong phú liên quan đến các khía cạnh:\n"
        "- Vệ sinh (Hygiene): sạch sẽ, bẩn, bụi bặm, chén bát, sàn nhà, khu vệ sinh, bóng loáng, mất vệ sinh...\n"
        "- Không khí (Atmosphere): không gian, trang trí, ánh sáng, âm nhạc, view, thoáng, chật, ồn, ấm cúng, decor...\n"
        "- Giá cả (Price): đắt, rẻ, hợp lý, giá chát, bình dân, giá cao, đáng đồng tiền..."
    )

    while True:
        # Tính toán lại stats sau mỗi vòng
        current_stats = calculate_stats(data_balanced + augmented_data)
        
        # Xác định các nhãn đang còn thiếu
        deficient_labels = []
        for cat in ['Food quality', 'Price', 'Service quality', 'Hygiene and safety', 'Atmosphere']:
            for val in [0.0, 0.5, 1.0]:
                if current_stats[cat][val] < target:
                    # Chỉ quan tâm những nhãn thiếu hụt < 2500
                    deficient_labels.append((cat, val))
        
        if not deficient_labels:
            print("\nTuyệt vời! Toàn bộ các nhãn đều đã đạt mốc 2500 mẫu.")
            break
            
        print(f"\nCòn {len(deficient_labels)} nhãn chưa đạt mốc 2500:")
        for cat, val in deficient_labels:
            print(f"  - {cat} {val}: {current_stats[cat][val]}/{target} (Cần {(target - current_stats[cat][val])} nữa)")

        # Tính điểm ưu tiên cho từng mẫu dựa trên độ thiếu hụt của các nhãn mà nó chứa
        scored_pool = []
        for item in data_balanced:
            labels = [(l['name'], l['value']) for l in item.get('labels', [])]
            score = 0
            for cat, val in labels:
                if (cat, val) in deficient_labels:
                    # Điểm càng cao khi nhãn đó càng cần nhiều mẫu
                    score += (target - current_stats[cat][val])
            
            if score > 0:
                scored_pool.append((score, item))
                
        if not scored_pool:
            print("CẢNH BÁO: Không có mẫu gốc nào chứa nhãn bị thiếu để làm cơ sở sinh thêm!")
            break
            
        # Sắp xếp theo điểm giảm dần
        scored_pool.sort(key=lambda x: x[0], reverse=True)
        
        # Lấy top 100 mẫu có điểm cao nhất rồi shuffle để chọn batch
        # Điều này giúp tập trung vào các nhãn 'khó' (Hygiene 0.0, Atmosphere 0.0)
        top_k = min(100, len(scored_pool))
        top_candidates = [item for score, item in scored_pool[:top_k]]
        random.shuffle(top_candidates)
        
        batch = top_candidates[:BATCH_SIZE]
        
        batch_text_input = ""
        for b in batch:
            batch_text_input += f"[{b['index']}] {b['original_data'].get('textTranslated', '')}\n\n"
            
        prompt = (
            f"{sys_prompt}\n\nHãy phân tích và trả về mảng 'results'. Đảm bảo 'original_index' ứng với số [index].\n\n"
            f"DANH SÁCH REVIEW:\n{batch_text_input}"
        )
        
        print(f"\nĐang gọi API sinh thêm dữ liệu cho {len(batch)} mẫu...")
        
        while True:
            try:
                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_schema": BatchAugmented,
                        "temperature": 0.7, # Nhiệt độ cao một chút để có văn bản đa dạng
                    }
                )
                
                result_json = json.loads(response.text)
                batch_results = result_json.get("results", [])
                
                added_count = 0
                for res in batch_results:
                    orig_idx = res.get("original_index")
                    
                    # Tìm item gốc để copy labels
                    orig_item = next((x for x in batch if x['index'] == orig_idx), None)
                    if not orig_item:
                        continue
                        
                    new_item = {
                        "index": f"{orig_idx}_aug_{int(time.time())}_{random.randint(100,999)}",
                        "original_data": {
                            "title": orig_item["original_data"].get("title", ""),
                            "textTranslated": res.get("augmented_text", ""),
                            "publishedAtDate": orig_item["original_data"].get("publishedAtDate", ""),
                            "is_augmented": True
                        },
                        "reasoning": "Paraphrased via LLM",
                        "labels": orig_item["labels"] # Kế thừa nguyên vẹn label
                    }
                    augmented_data.append(new_item)
                    added_count += 1
                    
                save_data(augmented_data, output_file)
                print(f" => Thành công! Sinh thêm được {added_count} mẫu. Đã lưu tiến độ.")
                time.sleep(3)
                break
                
            except Exception as e:
                error_str = str(e)
                print(f"Lỗi: {error_str[:200]}...\n")
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    if len(api_keys) > 1:
                        current_key_idx = (current_key_idx + 1) % len(api_keys)
                        print(f"-> Chuyển sang API Key {current_key_idx + 1}...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(1)
                    else:
                        print("-> Quá tải! Đợi 60s...")
                        time.sleep(60)
                else:
                    print("-> Lỗi khác. Đợi 10s...")
                    time.sleep(10)

if __name__ == "__main__":
    main()
