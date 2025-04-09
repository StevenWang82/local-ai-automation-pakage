import json
import os
import re
import sys

def vtt_to_json(vtt_filepath="downloads/subtitle.vtt"):
    """
    Reads a VTT subtitle file, parses it, and converts it to JSON format.
    Handles both simple and complex VTT formats and removes duplicate subtitle entries
    based on consecutive identical subtitles.
    After successful JSON conversion, it removes the input VTT file.

    Args:
        vtt_filepath (str): The path to the VTT subtitle file.

    Returns:
        str: JSON string representation of the subtitles, or None if error.
    """

    subtitle_entries = []
    previous_entry = None  # To track the previous subtitle entry
    success = False # Flag to track if JSON conversion was successful

    try:
        with open(vtt_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if "-->" in line:  # Identify timestamp line
                times = line.split("-->")
                start_time_str = times[0].strip()
                end_time_str_raw = times[1].strip()

                # Modified: Take only the timestamp part before any extra info
                end_time_str = end_time_str_raw.split(' ')[0]
                start_time_sec = time_to_seconds(start_time_str)
                end_time_sec = time_to_seconds(end_time_str)

                i += 1
                subtitle_line = lines[i].strip() # Get subtitle line

                if "<c>" in subtitle_line: # Complex format detection
                    # For complex format, we expect the *next* line to be the full subtitle.
                    i += 1
                    if i < len(lines): # Check if there is a next line
                        next_subtitle_line = lines[i].strip()
                        # Check if the next line is indeed the subtitle text (not another timestamp etc.)
                        if "-->" not in next_subtitle_line and next_subtitle_line: # Basic check to avoid processing timestamp lines as subtitles
                            # Remove inline timestamps and tags, and join words
                            subtitle_text = re.sub(r'<.*?c>|<.*?/c>', '', next_subtitle_line)
                            subtitle_text = subtitle_text.replace("><", "> <").replace(">", "").replace("<", "").strip() # Clean up extra tags if any

                            current_entry = {
                                "start_time": start_time_sec,
                                "subtitle": subtitle_text,
                                "end_time": end_time_sec
                            }

                            # Check for duplicates based on subtitle text
                            if previous_entry is None or current_entry["subtitle"] != previous_entry["subtitle"]:
                                subtitle_entries.append(current_entry)
                                previous_entry = current_entry # Update previous entry

                        else:
                            # If next line is not a subtitle (or empty), we skip this entry
                            pass
                    else:
                        # If no next line (end of file after complex timestamp), skip entry
                        pass
                else: # Simple format
                    subtitle_text = subtitle_line
                    current_entry = {
                        "start_time": start_time_sec,
                        "subtitle": subtitle_text,
                        "end_time": end_time_sec
                    }
                    # Check for duplicates based on subtitle text (though less likely in simple format)
                    if previous_entry is None or current_entry["subtitle"] != previous_entry["subtitle"]:
                        subtitle_entries.append(current_entry)
                        previous_entry = current_entry # Update previous entry

            i += 1 # Move to the next line
        success = True # Set success flag if parsing completes without exception

    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {vtt_filepath}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"解析VTT檔案時發生錯誤: {e}", file=sys.stderr)
        return None

    if success: # Only attempt to delete if JSON conversion was successful
        try:
            os.remove(vtt_filepath)
            # print(f"成功移除檔案: {vtt_filepath}") # Optional: print success message to stdout/n8n log
        except Exception as e:
            print(f"移除檔案 {vtt_filepath} 時發生錯誤: {e}", file=sys.stderr)
            # Note: Even if deletion fails, we still return the JSON if conversion was successful
            # You might want to handle this differently based on your workflow requirements

    if success:
        return json.dumps(subtitle_entries, ensure_ascii=False, indent=2)
    else:
        return None


def time_to_seconds(time_str):
    """
    Converts time in HH:MM:SS.milliseconds format to seconds.

    Args:
        time_str (str): Time string in HH:MM:SS.milliseconds format.

    Returns:
        float: Time in seconds.
    """
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_milliseconds = parts[2].split('.')
    seconds = int(seconds_milliseconds[0])
    milliseconds = int(seconds_milliseconds[1]) if len(seconds_milliseconds) > 1 else 0

    total_seconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000)
    return total_seconds


if __name__ == "__main__":
    json_output = vtt_to_json()
    if json_output:
        print(json_output)