import array
import io
import json

def merge_json_files(files):
    duplicates = 0
    all_data = []
    found = False

    # Loop through each JSON file and extract the quotes and authors
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for i in data:
            # Make sure the quote wasn't added yet
            for j in all_data:
                if j['quote'] == i['quote']:
                    found = True
            # Add if wasn't added
            if not found:
                all_data.append(i)
            found = False

    print(f"There were {duplicates} duplicated verses.")

    # Create combined file
    with io.open(f'merged_data.json', 'w', encoding='utf8') as outfile:
        str_ = json.dumps(all_data, ensure_ascii=False, indent=4)
        outfile.write(str_)
    return outfile.name, len(all_data)