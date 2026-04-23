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

        for item in data:
            title = item.get("title")
            text_translated = item.get("textTranslated")
            text = item.get("text")
            
            published_at_date = item.get("publishedAtDate")
            if published_at_date and len(published_at_date) >= 10:
                # Extract yyyy-MM-dd
                published_at_date = published_at_date[:10]

            if text_translated is None and text is None:
                continue

            final_text = text_translated if text_translated is not None else text
            final_text = clean_text(final_text)

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
        # r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-03-17_08-23-53-140.json",
        # r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-03-17_09-36-02-989.json",
        #  r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-04-06_04-19-03-018.json"
        #  r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-04-06_06-14-18-944.json"
         r"d:\Gab\ProjectMaster\scrape\data\dataset_crawler-google-places_2026-04-23_08-19-34-212.json"
    ]
    output_file = r"d:\Gab\ProjectMaster\exported_data_05.json"
    process_json(input_files, output_file)
    print(f"Done! Exported to {output_file}")
