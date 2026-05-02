import json
from collections import defaultdict
import os

def main():
    input_file = 'labeled_results_all_v3.json'
    output_file = 'data_balanced.json'
    
    print(f"Dang doc du lieu tu {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Các class đang bị thiếu hụt so với mục tiêu 2500
    deficient_classes = [
        ('Food quality', 0.0),
        ('Price', 0.0),
        ('Service quality', 0.0),
        ('Hygiene and safety', 0.0),
        ('Hygiene and safety', 1.0),
        ('Atmosphere', 0.0)
    ]

    mandatory_samples = []
    remaining_samples = []

    # Bước 1: Phân loại data
    # Giữ lại toàn bộ các câu chứa nhãn thuộc nhóm "khan hiếm" (deficient_classes)
    for item in data:
        labels = [(l['name'], l['value']) for l in item['labels']]
        is_mandatory = any(lbl in deficient_classes for lbl in labels)
        if is_mandatory:
            mandatory_samples.append(item)
        else:
            remaining_samples.append(item)

    stats = defaultdict(lambda: defaultdict(int))
    final_dataset = []

    # Thêm các câu bắt buộc phải giữ
    for item in mandatory_samples:
        final_dataset.append(item)
        for label in item['labels']:
            stats[label['name']][label['value']] += 1

    # Bước 2: Smart Undersampling cho các nhãn thừa (như 0.5 hoặc 1.0)
    # Sắp xếp các câu còn lại theo độ dài giảm dần để ưu tiên giữ lại các câu phức tạp (nhiều khía cạnh)
    remaining_samples.sort(key=lambda x: len(x['original_data'].get('textTranslated', '')), reverse=True)

    # Bước 3: Thêm các câu còn lại cho đến khi các nhãn đạt tối thiểu 2500
    target = 2500
    for item in remaining_samples:
        labels = [(l['name'], l['value']) for l in item['labels']]
        
        # Kiểm tra xem câu này có chứa nhãn nào ĐANG CẦN thêm để đạt 2500 hay không
        needs_this_sample = any(stats[name][val] < target for name, val in labels)
        
        if needs_this_sample:
            final_dataset.append(item)
            for name, val in labels:
                stats[name][val] += 1

    # In kết quả phân phối sau khi cân bằng
    print(f"\nDa hoan tat can bang. Tong so sample: {len(final_dataset)}")
    print("\nPhan phoi du lieu sau khi can bang (Smart Undersampling):")
    print(f"{'Tieu chi':<20} | {'0.0':<6} | {'0.5':<6} | {'1.0':<6}")
    print("-" * 47)
    for cat in ['Food quality', 'Price', 'Service quality', 'Hygiene and safety', 'Atmosphere']:
        dist = stats[cat]
        print(f"{cat:<20} | {dist[0.0]:<6} | {dist[0.5]:<6} | {dist[1.0]:<6}")

    # Re-index
    for i, item in enumerate(final_dataset):
        item['index'] = i

    # Ghi ra file
    print(f"\nDang luu ra {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_dataset, f, ensure_ascii=False, indent=2)
    print("Xong!")

if __name__ == "__main__":
    main()
