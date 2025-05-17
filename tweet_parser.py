import json
import os

def extract_tweet_details(tweet_data_result):
    """Extracts desired information from a single tweet_results.result object."""
    if not tweet_data_result or tweet_data_result.get('__typename') != 'Tweet':
        return None

    legacy = tweet_data_result.get('legacy', {})
    core_user_data = tweet_data_result.get('core', {}).get('user_results', {}).get('result', {})
    
    if not legacy or not core_user_data: # Ensure essential parts exist
        return None

    core_user_legacy = core_user_data.get('legacy', {})

    extracted_info = {
        'tweet_id': tweet_data_result.get('rest_id'),
        'user_screen_name': core_user_legacy.get('screen_name'),
        'user_name': core_user_legacy.get('name'),
        'user_id': core_user_legacy.get('id_str') or core_user_data.get('rest_id'), # Fallback if id_str is not in legacy
        'created_at': legacy.get('created_at'),
        'full_text': legacy.get('full_text'),
        'language': legacy.get('lang'),
        'favorite_count': legacy.get('favorite_count', 0),
        'retweet_count': legacy.get('retweet_count', 0),
        'reply_count': legacy.get('reply_count', 0),
        'quote_count': legacy.get('quote_count', 0),
        'source': tweet_data_result.get('source'), # This is HTML, might need parsing or storing as is
    }

    # Entities
    entities = legacy.get('entities', {})
    extracted_info['entities'] = {
        'hashtags': [ht.get('text') for ht in entities.get('hashtags', [])],
        'user_mentions': [um.get('screen_name') for um in entities.get('user_mentions', [])],
        'urls': [url.get('expanded_url') for url in entities.get('urls', [])]
    }

    # Reply information
    extracted_info['is_reply'] = bool(legacy.get('in_reply_to_status_id_str'))
    if extracted_info['is_reply']:
        extracted_info['reply_to_screen_name'] = legacy.get('in_reply_to_screen_name')
        extracted_info['reply_to_tweet_id'] = legacy.get('in_reply_to_status_id_str')
    else:
        extracted_info['reply_to_screen_name'] = None
        extracted_info['reply_to_tweet_id'] = None
        
    # Quoted tweet information
    extracted_info['is_quote'] = legacy.get('is_quote_status', False)
    quoted_status_result = tweet_data_result.get('quoted_status_result', {}).get('result')
    if extracted_info['is_quote'] and quoted_status_result and quoted_status_result.get('__typename') == 'Tweet':
        # Recursively extract for the quoted tweet, or simplify if too deep
        # For simplicity here, we'll extract key fields directly
        q_legacy = quoted_status_result.get('legacy', {})
        q_core_user_data = quoted_status_result.get('core', {}).get('user_results', {}).get('result', {})
        q_core_user_legacy = q_core_user_data.get('legacy', {})
        
        extracted_info['quoted_tweet_details'] = {
            'tweet_id': quoted_status_result.get('rest_id'),
            'user_screen_name': q_core_user_legacy.get('screen_name'),
            'user_name': q_core_user_legacy.get('name'),
            'created_at': q_legacy.get('created_at'),
            'full_text': q_legacy.get('full_text'),
            'favorite_count': q_legacy.get('favorite_count', 0),
            'retweet_count': q_legacy.get('retweet_count', 0),
            'reply_count': q_legacy.get('reply_count', 0),
            'quote_count': q_legacy.get('quote_count', 0),
        }
    else:
        extracted_info['quoted_tweet_details'] = None
        
    return extracted_info

def process_har_file(filepath):
    """Processes a single HAR-like JSON file and extracts tweet data."""
    tweets = []
    print(f"Processing file: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            har_data_list = json.load(f) # The file contains a list of HAR entries

        for har_entry in har_data_list:
            response_data = har_entry.get('response', {})
            
            # Check for errors in the response itself first
            if 'errors' in response_data:
                # print(f"  Skipping entry due to API errors: {response_data['errors']}")
                continue # Skip this HAR entry if Twitter API returned an error

            # The actual tweet data is nested within 'data' if the response was successful
            # The provided structure has response_data = {"data": {"search_by_raw_query": ...}}
            # or response_data = {"errors": [...], "data": {"search_by_raw_query": {}}}
            
            search_results = response_data.get('data', {}).get('search_by_raw_query', {})
            if not search_results: # Could be empty if API error was at this level
                # print(f"  No 'search_by_raw_query' data in an entry of {filepath}")
                continue

            timeline = search_results.get('search_timeline', {}).get('timeline', {})
            instructions = timeline.get('instructions', [])

            for instruction in instructions:
                if instruction.get('type') == "TimelineAddEntries":
                    entries = instruction.get('entries', [])
                    for entry in entries:
                        content = entry.get('content', {})
                        if content.get('entryType') == "TimelineTimelineItem" and \
                           content.get('itemContent', {}).get('itemType') == "TimelineTweet":
                            
                            tweet_result = content.get('itemContent', {}).get('tweet_results', {}).get('result')
                            tweet_details = extract_tweet_details(tweet_result)
                            if tweet_details:
                                tweets.append(tweet_details)
    except FileNotFoundError:
        print(f"  Error: File not found at {filepath}")
    except json.JSONDecodeError:
        print(f"  Error: Could not decode JSON from {filepath}")
    except Exception as e:
        print(f"  An unexpected error occurred with {filepath}: {e}")
    return tweets

def main():
    # List of your input JSON files
    input_folder = "./captured_tweets"  # Example: "./json_inputs"
    input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".json")]

    # Add more file names to this list if you have them, e.g.,
    # input_files = ["file1.json", "file2.json", "file3.json"]

    output_file = "data_combined_tweets.json"
    
    all_tweets_combined = []
    processed_tweet_ids = set() # To avoid duplicates if tweets appear in multiple API calls/files

    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"Warning: Input file {file_path} does not exist. Skipping.")
            continue
        
        extracted_tweets = process_har_file(file_path)
        for tweet in extracted_tweets:
            if tweet['tweet_id'] not in processed_tweet_ids:
                all_tweets_combined.append(tweet)
                processed_tweet_ids.add(tweet['tweet_id'])
            else:
                print(f"  Duplicate tweet ID {tweet['tweet_id']} found. Skipping.")

    # Sort tweets by creation date (optional, but good for consistency)
    # Timestamps are like "Tue Dec 22 19:54:02 +0000 2020"
    # We need to parse them for proper sorting.
    from datetime import datetime
    
    def parse_twitter_date(date_str):
        if date_str:
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S +0000 %Y')
        return datetime.min # for cases where date might be missing, sort them first/last

    all_tweets_combined.sort(key=lambda x: parse_twitter_date(x.get('created_at')), reverse=True) # Newest first

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_tweets_combined, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully processed {len(all_tweets_combined)} unique tweets.")
        print(f"Combined data saved to {output_file}")
    except IOError:
        print(f"Error: Could not write to output file {output_file}")
    except Exception as e:
        print(f"An unexpected error occurred while writing output: {e}")

if __name__ == "__main__":
    main()
