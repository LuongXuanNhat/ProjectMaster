import json

input_file = "labeled_results_all_v3.json"
output_file = "labeled_results_all_v3_cut.json"
label_to_remove = "Hygiene and safety"

def main():
    print(f"Đang đọc dữ liệu từ {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Đang xử lý dữ liệu (loại bỏ nhãn '{label_to_remove}')...")
    for item in data:
        if 'labels' in item:
            # Lọc bỏ nhãn "Hygiene and safety"
            item['labels'] = [label for label in item['labels'] if label.get('name') != label_to_remove]

    print(f"Đang lưu dữ liệu vào {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Hoàn tất!")

if __name__ == "__main__":
    main()
