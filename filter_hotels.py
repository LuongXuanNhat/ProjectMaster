import json

def main():
    input_file = 'labeled_results_batch.json'
    output_file = 'labeled_results_batch_02.json'

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    filtered_data = []
    for item in data:
        # Check original_data title if available
        original = item.get('original_data', {})
        title = original.get('title', item.get('title', ''))
        
        title_lower = title.lower()
        if 'hotel' not in title_lower and 'khách sạn' not in title_lower:
            filtered_data.append(item)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)

    print(f"Original items: {len(data)}")
    print(f"Filtered items: {len(filtered_data)}")

if __name__ == "__main__":
    main()
