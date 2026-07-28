import json
import sys
import argparse


def filter_food_quality(input_path: str, output_path: str, target_value: float = 1.0, criteria: str = "Food quality"):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    with open(output_path, "w", encoding="utf-8") as out:
        for item in data:
            labels = item.get("labels", [])
            food_quality = next(
                (lb["value"] for lb in labels if lb.get("name") == criteria),
                None
            )
            if food_quality == target_value:
                index = item.get("index")
                text = item.get("original_data", {}).get("textTranslated", "")
                out.write(f'#{index} | "{text}"\n')
                count += 1

    print(f"Đã ghi {count} dòng vào {output_path}")


if __name__ == "__main__":
    # Add cứng path input ở đây
    INPUT_PATH = r"D:\Gab\ProjectMaster\labeled_results_all_v6.json"
    CRITERIA = "Atmosphere"  # Thay đổi tiêu chí nếu cần

    parser = argparse.ArgumentParser(
        description="Lọc các review theo tiêu chí và xuất textTranslated ra file .txt"
    )
    parser.add_argument(
        "-o", "--output",
        default="output_atmosphere.txt",
        help="Đường dẫn file .txt đầu ra (mặc định: output_atmosphere.txt)"
    )
    parser.add_argument(
        "-v", "--value",
        type=float,
        default=1.0,
        help="Giá trị cần lọc (mặc định: 1.0)"
    )
    args = parser.parse_args()

    filter_food_quality(INPUT_PATH, args.output, args.value, CRITERIA)