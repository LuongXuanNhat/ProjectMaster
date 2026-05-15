import json
import re

def clean_text(text):
    if text is None:
        return None
    # Remove special characters and emojis, keeping words, spaces, and basic punctuation
    text = re.sub(r'[^\w\s.,!?\-\'\"]', '', text)
    return text.strip()

def process_json(input_filepaths, output_filepath):
    result = []
    
    for file_path in input_filepaths:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for place in data:
            title = place.get("title")
            reviews = place.get("reviews", [])
            
            if not reviews:
                continue

            for review in reviews:
                text_translated = review.get("textTranslated")
                text = review.get("text")
                
                published_at_date = review.get("publishedAtDate")
                if published_at_date and len(published_at_date) >= 10:
                    # Extract yyyy-MM-dd
                    published_at_date = published_at_date[:10]

                if text_translated is None and text is None:
                    continue

                final_text = text_translated if text_translated is not None else text
                final_text = clean_text(final_text)

                # Keep reviews longer than 50 characters, as in the original script
                if final_text and len(final_text) > 50:
                    result.append({
                        "title": title,
                        "textTranslated": final_text,
                        "publishedAtDate": published_at_date
                    })

    with open(output_filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_files = [
        # r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-04-23_08-19-34-212.json"
        # r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-04-23_09-32-14-390.json"
        # r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-04-24_01-37-49-075.json"
        r"D:\BTMONHOC\Master\scrape\data\dataset_crawler-google-places_2026-05-14_05-36-54-059.json"
    ]
    output_file = r"d:\BTMONHOC\Master\exported_data_08.json"
    process_json(input_files, output_file)
    print(f"Done! Exported to {output_file}")
