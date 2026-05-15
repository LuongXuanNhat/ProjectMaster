import json

input_file_1 = "labeled_results_all_v3_cut.json"
input_file_2 = "labeled_results_batch_07.json"
output_file = "labeled_results_all_v4.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print(f"Doc du lieu tu {input_file_1}...")
    data_1 = load_json(input_file_1)

    print(f"Doc du lieu tu {input_file_2}...")
    data_2 = load_json(input_file_2)

    merged_data = data_1 + data_2

    print("Danh lai index cho toan bo du lieu...")
    for i, item in enumerate(merged_data):
        item["index"] = i

    print(f"Ghi file ket qua: {output_file}...")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)

    print("Hoan tat!")
    print(f"Tong so ban ghi: {len(merged_data)}")


if __name__ == "__main__":
    main()
