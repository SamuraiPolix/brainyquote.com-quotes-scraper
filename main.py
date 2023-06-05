import os
import extractor
import merge_files

# Limit the length of every scraped verse (verses with more chars than CHARS_LIMIT will not be scraped)
# Set to -1 to disable limit
CHARS_LIMIT = 175

authors = ['Albert Einstein']

if __name__ == "__main__":
    count_quotes = 0;
    json_files = list()
    for author in authors:
        output = extractor.extract(author, CHARS_LIMIT)
        json_files.append(output[0])
        count_quotes += output[1]

    if len(authors) > 1:
        output = merge_files.merge_json_files(json_files)
        merged_file = output[0]
        count_quotes = output[1]
        # Delete temp files
        for file in json_files:
            os.remove(file)

    print(f"\nDONE Scraping {count_quotes} quotes by {authors}!!!")