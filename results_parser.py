#!/usr/bin/env python3

import os
import json
import datetime
import argparse
import sys # For sys.exit
import re # For regular expressions

def parse_arguments():
    parser = argparse.ArgumentParser(description="Parse result files from a specified directory.")
    parser.add_argument(
        "--dir",
        metavar="DIRECTORY_PATH",
        type=str,
        required=True,
        help="Path to the directory containing the result files."
    )
    return parser.parse_args()

def parse_datetime_from_string_key(key_string):
    """
    Parses a symbol and a datetime.date object from a string key like "('ticker', datetime.date(Y, M, D))".
    Returns a tuple (symbol, datetime.date_object) or (None, None) if parsing fails.
    """
    # Pattern to capture symbol (group 1) and date components (groups 2, 3, 4 for Y, M, D)
    pattern = r"\(\s*'([^']*)'\s*,\s*datetime\.date\s*\(\s*(\d{4})\s*,\s*(\d{1,2})\s*,\s*(\d{1,2})\s*\)\s*\)"
    match = re.search(pattern, key_string)

    if match:
        symbol = match.group(1)
        year_str, month_str, day_str = match.group(2), match.group(3), match.group(4)
        try:
            year = int(year_str)
            month = int(month_str)
            day = int(day_str)
            date_obj = datetime.date(year, month, day)
            return symbol, date_obj
        except ValueError as e:
            print(f"Error parsing date components from key '{key_string}': year={year_str}, month={month_str}, day={day_str}. Error: {e}")
            return None, None
    else:
        # print(f"Warning: Could not find symbol/date pattern in key: '{key_string}'") # Can be noisy
        return None, None

def identify_files(directory_path):
    """
    Identifies '_history.json' files and other '.json' files in the specified directory.
    Returns a tuple: (history_files_list, other_json_files_list)
    """
    history_files = []
    other_json_files = []
    try:
        if not os.path.isdir(directory_path): # Redundant check if called after main's check, but good for standalone use
            print(f"Error in identify_files: Directory not found at path: {directory_path}")
            return history_files, other_json_files

        for entry in os.listdir(directory_path):
            full_path = os.path.join(directory_path, entry)
            if os.path.isfile(full_path):
                if entry.endswith("_history.json"):
                    history_files.append(full_path)
                elif entry.endswith(".json"):
                    other_json_files.append(full_path)
    except FileNotFoundError: # Should not happen if directory_path is validated before call
        print(f"Error in identify_files: Path not found {directory_path} during listdir. This should not happen if path was pre-validated.")
        return [], [] # Return empty lists
    except Exception as e:
        print(f"An unexpected error occurred in identify_files: {e}")
        return [], [] # Return empty lists in case of other errors

    return history_files, other_json_files

if __name__ == "__main__":
    args = parse_arguments()
    print(f"Results directory specified: {args.dir}")

    # Further script logic will be added here
    # For now, check if the directory exists
    if not os.path.isdir(args.dir):
        print(f"Error: Directory not found at path: {args.dir}")
        sys.exit(1) # Exit if directory not found

    print(f"Directory '{args.dir}' found. Identifying files...")
    history_files, other_json_files = identify_files(args.dir)

    print(f"Identified history files: {history_files}")
    print(f"Identified other JSON files: {other_json_files}")

    print("\n--- Testing datetime parser (now expecting (symbol, date_obj) tuple) ---")
    test_key1 = "('000001.SS', datetime.date(1997, 7, 1))"
    test_key2 = "('MSFT', datetime.date(2023, 12, 25))"
    test_key_invalid_date = "('ERR', datetime.date(2023, 2, 30))"
    test_key_malformed_regex_no_match = "('BAD', datetime.date(2023, 12))"
    test_key_malformed_int_error = "('BADINT', datetime.date(2023, 12, XX))"
    test_key_no_date = "('NODATE', 123)"
    test_key_only_symbol = "('SYMBOL_ONLY', )" # Test case for regex robustness

    results = [
        parse_datetime_from_string_key(test_key1),
        parse_datetime_from_string_key(test_key2),
        parse_datetime_from_string_key(test_key_invalid_date),
        parse_datetime_from_string_key(test_key_malformed_regex_no_match),
        parse_datetime_from_string_key(test_key_malformed_int_error),
        parse_datetime_from_string_key(test_key_no_date),
        parse_datetime_from_string_key(test_key_only_symbol),
    ]
    test_keys = [test_key1, test_key2, test_key_invalid_date, test_key_malformed_regex_no_match, test_key_malformed_int_error, test_key_no_date, test_key_only_symbol]

    for key_str, result_tuple in zip(test_keys, results):
        if result_tuple and result_tuple[0] is not None and result_tuple[1] is not None:
            symbol, date_obj = result_tuple
            print(f"'{key_str}' -> Symbol: '{symbol}', Date: {date_obj} (type: {type(date_obj)})")
        else:
            print(f"'{key_str}' -> Parsing failed, returned: {result_tuple}")
    print("--- End Datetime Parser Test ---\n")

    # --- Parsing History Files ---
    print("\n--- Parsing History Files ---")
    all_history_data = {}
    # total_history_symbols_overall = set() # Replaced by len(all_history_data) later
    total_history_items_overall = 0
    successfully_processed_history_files = 0 # Initialize counter for history files

    # Create dummy history files for testing if no files are identified
    # This part is for local testing; normally, history_files would come from identify_files()
    if not history_files and os.path.isdir(args.dir): # only create if dir exists and no files found
        print(f"No history files found in {args.dir}. Creating dummy files for testing purposes.")
        dummy_hf_path1 = os.path.join(args.dir, "dummy_AAPL_history.json")
        dummy_data1 = {
            "close": {
                "('AAPL', datetime.date(2023, 1, 1))": 150.0,
                "('AAPL', datetime.date(2023, 1, 2))": 152.5
            },
            "open": {
                "('AAPL', datetime.date(2023, 1, 1))": 149.0,
                "('AAPL', datetime.date(2023, 1, 2))": 150.2
            }
        }
        try:
            with open(dummy_hf_path1, 'w') as f:
                json.dump(dummy_data1, f, indent=2) # Save with readable format
            history_files.append(dummy_hf_path1) # Add to list for processing
            print(f"Created dummy file: {dummy_hf_path1}")
        except Exception as e:
            print(f"Could not create dummy history file {dummy_hf_path1}: {e}")

        dummy_hf_path2 = os.path.join(args.dir, "dummy_MSFT_history.json")
        # Contains a malformed key string
        dummy_data2 = {
            "close": {
                "('MSFT', datetime.date(2023, 1, 1))": 250.0,
                "('MSFT', datetime.date(2023, 1, XX))": 252.5 # Malformed key
            }
        }
        try:
            with open(dummy_hf_path2, 'w') as f:
                json.dump(dummy_data2, f, indent=2)
            history_files.append(dummy_hf_path2)
            print(f"Created dummy file: {dummy_hf_path2}")
        except Exception as e:
            print(f"Could not create dummy history file {dummy_hf_path2}: {e}")


    if not history_files:
        print("No history files found or created to parse.")

    for hf_path in history_files:
        print(f"Parsing history file: {hf_path}")
        parsed_data_from_file, sym_count_in_file, item_count_in_file = parse_history_file(hf_path, parse_datetime_from_string_key)

        if parsed_data_from_file is not None:
            print(f"  Loaded {sym_count_in_file} symbols and {item_count_in_file} data items from {os.path.basename(hf_path)}")

            for symbol, symbol_data in parsed_data_from_file.items():
                if symbol not in all_history_data:
                    all_history_data[symbol] = {}

                for data_type_key, type_data_dict in symbol_data.items():
                    if data_type_key not in all_history_data[symbol]:
                        all_history_data[symbol][data_type_key] = {}
                    all_history_data[symbol][data_type_key].update(type_data_dict)

            total_history_items_overall += item_count_in_file
            successfully_processed_history_files += 1 # Increment counter
        else:
            print(f"  Failed to parse {os.path.basename(hf_path)}")

    # Removed summary prints here, will be done by print_data_summary
    # print(f"Finished parsing history files.")
    # print(f"Total unique symbols from history files: {len(all_history_data)}. Total items processed: {total_history_items_overall}.")
    # print(f"Aggregated history data (sample): {dict(list(all_history_data.items())[:1])}") # Print sample
    # Further processing will use all_history_data

    # --- Parsing Other JSON Files ---
    print("\n--- Parsing Other JSON Files ---")
    all_other_data = {}
    successfully_parsed_other_files = 0 # Renamed for clarity and initialized

    # Create dummy other JSON files for testing if no files are identified
    # total_other_symbols_loaded will effectively be the count of successfully parsed files
    # if each file contains one symbol as expected.

    # Create dummy other JSON files for testing if no files are identified
    if not other_json_files and os.path.isdir(args.dir): # only create if dir exists and no files found
        print(f"No other JSON files found in {args.dir}. Creating dummy files for testing purposes.")
        dummy_other_path1 = os.path.join(args.dir, "dummy_info_AAPL.json")
        dummy_other_data1 = [["AAPL", {"name": "Apple Inc.", "sector": "Technology"}]]
        try:
            with open(dummy_other_path1, 'w') as f:
                json.dump(dummy_other_data1, f, indent=2)
            other_json_files.append(dummy_other_path1)
            print(f"Created dummy file: {dummy_other_path1}")
        except Exception as e:
            print(f"Could not create dummy other JSON file {dummy_other_path1}: {e}")

        dummy_other_path2_invalid_structure = os.path.join(args.dir, "dummy_info_INVALID.json")
        dummy_other_data2_invalid = {"symbol": "INVALID", "data": "WrongStructure"} # Not a list of lists
        try:
            with open(dummy_other_path2_invalid_structure, 'w') as f:
                json.dump(dummy_other_data2_invalid, f, indent=2)
            other_json_files.append(dummy_other_path2_invalid_structure)
            print(f"Created dummy file: {dummy_other_path2_invalid_structure}")
        except Exception as e:
            print(f"Could not create dummy other JSON file {dummy_other_path2_invalid_structure}: {e}")


    if not other_json_files:
        print("No other JSON files found or created to parse.")

    for ojf_path in other_json_files:
        print(f"Parsing other JSON file: {ojf_path}")
        parsed_content = parse_other_json_file(ojf_path)

        if parsed_content:
            symbol, details_dict = parsed_content
            all_other_data[symbol] = details_dict
            print(f"  Loaded data for symbol '{symbol}' from {os.path.basename(ojf_path)}")
            successfully_parsed_other_files +=1
        else:
            print(f"  Failed to parse or validate structure of {os.path.basename(ojf_path)}")

    # Removed summary prints here, will be done by print_data_summary
    # print(f"Finished parsing other JSON files. Successfully processed {successfully_parsed_other_files} files.")
    # print(f"Total unique symbols loaded from other files: {len(all_other_data)}")
    # print(f"Other data (sample): {dict(list(all_other_data.items())[:1])}")

    # --- Final Data Summary ---
    print_data_summary(all_history_data, total_history_items_overall, all_other_data,
                       successfully_processed_history_files,
                       successfully_parsed_other_files)
    pass

def print_data_summary(all_history_data, total_history_items, all_other_data,
                       num_history_files_processed, num_other_files_processed):
    """
    Prints a summary of the aggregated history and other JSON data.
    """
    print("\n======= Data Summary =======")
    print(f"\n--- History Data ---")
    print(f"Successfully processed {num_history_files_processed} history files.")
    print(f"Found {len(all_history_data)} unique symbols in history data, with a total of {total_history_items} data items (date entries).")

    max_symbols_to_print = 3
    max_entries_per_type = 2

    for i, (symbol, symbol_data) in enumerate(all_history_data.items()):
        if i >= max_symbols_to_print:
            print(f"... and {len(all_history_data) - max_symbols_to_print} more symbols.")
            break
        print(f"\n  Symbol: {symbol}")
        for data_type_key, type_data_dict in symbol_data.items():
            print(f"    {data_type_key}:")
            # Sort by date for consistent sample output
            # Ensure type_data_dict is actually a dict and keys are sortable (datetime.date)
            try:
                sorted_dates = sorted(type_data_dict.keys())
            except TypeError: # Handle cases where keys might not be date objects if parsing error occurred upstream
                print(f"      Could not sort dates for {data_type_key} (unexpected key types).")
                # Print unsorted or skip
                sorted_dates = list(type_data_dict.keys()) # Attempt to get keys anyway

            for entry_idx, date_obj in enumerate(sorted_dates):
                if entry_idx >= max_entries_per_type:
                    print(f"      ... and {len(type_data_dict) - max_entries_per_type} more entries for {data_type_key}.")
                    break
                print(f"      {date_obj}: {type_data_dict[date_obj]}")

    print(f"\n--- Other JSON Data ---")
    print(f"Successfully processed {num_other_files_processed} other JSON files.")
    print(f"Found {len(all_other_data)} unique symbols in other JSON data.")

    for i, (symbol, details_dict) in enumerate(all_other_data.items()):
        if i >= max_symbols_to_print: # Use the same limit for symbols
            print(f"... and {len(all_other_data) - max_symbols_to_print} more symbols.")
            break
        print(f"\n  Symbol: {symbol}")
        # Print a few selected details
        if 'summaryDetail' in details_dict and isinstance(details_dict['summaryDetail'], dict):
            sd = details_dict['summaryDetail']
            print(f"    Summary Detail:")
            print(f"      Previous Close: {sd.get('previousClose', 'N/A')}")
            print(f"      Open: {sd.get('open', 'N/A')}")
            print(f"      Volume: {sd.get('volume', 'N/A')}")
        if 'quoteType' in details_dict and isinstance(details_dict['quoteType'], dict):
            qt = details_dict['quoteType']
            print(f"    Quote Type:")
            print(f"      Short Name: {qt.get('shortName', 'N/A')}")
            print(f"      Exchange: {qt.get('exchange', 'N/A')}")
    print("\n==========================")


def parse_history_file(file_path, datetime_parser_func):
    """
    Parses a single _history.json file.
    Returns a tuple (parsed_data, symbol_count, item_count) or (None, 0, 0) on failure.
    parsed_data format: {symbol: {data_type_key: {datetime.date_obj: value}}}
    """
    parsed_data = {}
    symbols_in_file = set()
    items_in_file = 0

    try:
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: History file not found at '{file_path}'")
        return None, 0, 0
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Please check its format.")
        return None, 0, 0
    except Exception as e:
        print(f"An unexpected error occurred opening or reading '{file_path}': {e}")
        return None, 0, 0

    for data_type_key, data_dict in raw_data.items():
        if not isinstance(data_dict, dict):
            print(f"Warning: Expected a dictionary for data_type_key '{data_type_key}' in '{file_path}', got {type(data_dict)}. Skipping.")
            continue
        for key_string, value in data_dict.items():
            symbol, date_obj = datetime_parser_func(key_string)
            if symbol and date_obj:
                if symbol not in parsed_data:
                    parsed_data[symbol] = {}
                symbols_in_file.add(symbol)

                if data_type_key not in parsed_data[symbol]:
                    parsed_data[symbol][data_type_key] = {}

                parsed_data[symbol][data_type_key][date_obj] = value
                items_in_file += 1
            else:
                print(f"Warning: Could not parse key '{key_string}' in file '{file_path}'. Skipping this entry.")

    return parsed_data, len(symbols_in_file), items_in_file

def parse_other_json_file(file_path):
    """
    Parses a single 'other' JSON file, expecting a specific structure: [["symbol", {details_dict}]].
    Returns a tuple (symbol, details_dict) or None on failure.
    """
    try:
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Other JSON file not found at '{file_path}'")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{file_path}'. Please check its format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred opening or reading '{file_path}': {e}")
        return None

    try:
        if not isinstance(raw_data, list) or not raw_data:
            print(f"Error: Expected a non-empty list in {os.path.basename(file_path)}, got {type(raw_data)}")
            return None

        inner_list = raw_data[0]
        if not isinstance(inner_list, list) or len(inner_list) < 2:
            print(f"Error: Expected a non-empty inner list with at least 2 elements in {os.path.basename(file_path)}")
            return None

        symbol = inner_list[0]
        details_dict = inner_list[1]

        if not isinstance(symbol, str):
            print(f"Error: Expected symbol to be a string in {os.path.basename(file_path)}, got {type(symbol)}")
            return None

        if not isinstance(details_dict, dict):
            print(f"Error: Expected details to be a dictionary in {os.path.basename(file_path)}, got {type(details_dict)}")
            return None

        return (symbol, details_dict)

    except (IndexError, TypeError) as e:
        print(f"Error: Unexpected JSON structure in file '{os.path.basename(file_path)}'. {e}")
        return None
    except Exception as e: # Catch any other unexpected error during structure validation
        print(f"An unexpected error occurred during structure validation of '{os.path.basename(file_path)}': {e}")
        return None
