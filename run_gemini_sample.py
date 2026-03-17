import json
import os
import sys
from typing import List

# Fix for windows console printing unicode characters
sys.stdout.reconfigure(encoding='utf-8')

try:
    from google import genai
    from pydantic import BaseModel, Field
except ImportError:
    print("Vui lòng cài đặt các thư viện yêu cầu: pip install google-genai pydantic")
    sys.exit(1)

# Định nghĩa Template Schema để ép Gemini trả về định dạng JSON mong muốn
class LabelOutput(BaseModel):
    name: str = Field(description="Tên tiêu chí. Phải là một trong: 'Food quality', 'Price', 'Service quality', 'Hygiene and safety', 'Atmosphere'")
    value: float = Field(description="Giá trị cảm xúc. Chỉ dùng: 0.0 (NEGATIVE), 0.5 (NEUTRAL), hoặc 1.0 (POSITIVE)")

class ReviewAnalysis(BaseModel):
    reasoning: str = Field(description="Dẫn chứng/lý giải ngắn gọn bằng Tiếng Việt tại sao lại chọn các nhãn này dựa trên từ khóa trong câu.")
    labels: List[LabelOutput] = Field(description="Danh sách các nhãn được trích xuất từ câu đánh giá.")

def read_prompt(filepath="label_studio_prompt.txt"):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def load_data(filepath, limit=5):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data[:limit]

def main():
    # 1. SETUP API KEY
    api_key = "AIzaSyCtEHSLUZuzrnFEyeoXPJkuRx4SYksYwiU"
    if not api_key:
        print("LỖI: Không tìm thấy GEMINI_API_KEY.")
        print("Vui lòng cung cấp API key để chạy script.")
        return

    # Khởi tạo client thay cho google.generativeai (đã deprecated)
    client = genai.Client(api_key=api_key)

    # 3. ĐỌC PROMPT VÀ DATA MẪU
    sys_prompt = read_prompt("label_studio_prompt.txt")
    data_samples = load_data("exported_data_02.json", limit=5)

    print("Bắt đầu lấy mẫu gán nhãn 5 Reviews với Gemini API...\n")
    
    for idx, item in enumerate(data_samples):
        review_text = item.get("textTranslated", "")
        
        prompt = f"{sys_prompt}\n\nDưới đây là một Review thực tế. Hãy trích xuất nhãn:\n\"{review_text}\""
        
        try:
            # Generate content với JSON Schema ràng buộc qua response_schema
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ReviewAnalysis,
                    "temperature": 0.1,  # Độ sáng tạo thấp để bám sát prompt
                }
            )
            
            result_json = json.loads(response.text)
            
            print(f"[{idx+1}] ĐÁNH GIÁ (Review): {review_text}")
            print("==> KẾT QUẢ GÁN NHÃN:")
            print(json.dumps(result_json, indent=2, ensure_ascii=False))
            print("-" * 60)
            
        except Exception as e:
            print(f"Lỗi khi gọi API cho mẫu số {idx+1}: {e}")

if __name__ == "__main__":
    main()
