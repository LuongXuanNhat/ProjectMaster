import json
import os

input_files = [
    # 'labeled_results_batch_02.json',
    # 'labeled_results_batch_03.json',
    # 'labeled_results_batch_04.json',
    # 'labeled_results_batch_05.json',
    # 'labeled_results_batch_06.json',
    # 'labeled_results_batch_07.json',
    'labeled_results_all_v4.json',
    'labeled_results_batch_08.json'
]
output_file = 'labeled_results_all_v6.json'

all_results = []

for file_name in input_files:
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_results.extend(data)
                    print(f"Đã load {len(data)} items từ {file_name}")
                else:
                    print(f"Cảnh báo: Dữ liệu trong {file_name} không phải là một list (mảng).")
        except Exception as e:
            print(f"Lỗi khi đọc file {file_name}: {e}")
    else:
        print(f"Không tìm thấy file: {file_name}")

# Cập nhật lại trường 'index' cho đúng thứ tự
for i, item in enumerate(all_results):
    if isinstance(item, dict):
        item['index'] = i

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f"\nĐã gộp xong! Tổng cộng {len(all_results)} items được lưu vào {output_file}")
