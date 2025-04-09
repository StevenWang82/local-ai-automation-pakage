import yt_dlp
import sys
import os
import json
import glob  # 確保 glob 已導入

class Chapter:
    def __init__(self, start_time, title, end_time):
        self.start_time = start_time
        self.title = title
        self.end_time = end_time

class DownloadResponse:
    def __init__(self, title, description, chapters, subtitle_file=None):  # 新增 subtitle_file
        self.title = title
        self.description = description
        self.chapters = chapters
        self.subtitle_file = subtitle_file  # 新增 subtitle_file

def download_video_info(url, download_folder='downloads',ffmpeg_path=None): #ffmpeg 在虛擬環境中已被安裝
    """
    下載影片的原始字幕（如果存在），或影片原始語言的自動字幕，
    並提取影片的 title、description 和 chapters 信息。

    Args:
        url: 影片的網址。
        download_folder: 儲存字幕檔案的資料夾名稱。
    """

    # 建立下載資料夾，如果不存在的話
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # 程式開始前，先自動清空download_folder資料夾。
    clear_download_folder(download_folder)

    ydl_opts = {
        'writesubtitles': True,  # 嘗試下載字幕
        'writeautomaticsub': True, # 嘗試下載自動字幕
        'writethumbnail': False, # 不下載縮圖
        'writeinfojson': False,   # 不下載 JSON 信息檔案 (修改為 False)
        'skip_download': True,  # 不下載影片本體
        'outtmpl': os.path.join(download_folder, '%(title)s-%(id)s.%(ext)s'),  # 檔案名稱模板
        'subtitleslangs': ['zh-Hant', 'zh-TW', 'zh-CN', 'zh', 'en', 'ja', 'ko', 'th', 'vi'],  # 字幕語言優先順序
        'subformat': 'vtt', #字幕格式設定
        'noplaylist': True,  # 避免下載整個播放清單
        'logger': MyLogger(),  # 使用自定義 logger
        'ffmpeg_location': ffmpeg_path
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False) # 獲取影片資訊，不下載

            video_title = info_dict.get('title', None)
            video_description = info_dict.get('description', None)
            video_url = info_dict.get('webpage_url', None)

            chapters = []
            if "chapters" in info_dict:
                for chapter_data in info_dict['chapters']:
                    chapter = Chapter(
                        start_time=chapter_data.get("start_time"),
                        title=chapter_data.get("title"),
                        end_time=chapter_data.get("end_time")
                    )
                    chapters.append(chapter)

            ydl.download([url])  # 使用 yt-dlp 下載字幕 (只下載字幕)
            # 下載字幕，並獲取字幕檔案路徑
            subtitle_file = cleanup_subtitles(download_folder, info_dict['title'], info_dict['id'], ydl_opts['subtitleslangs'])

            # 檢查並重新命名檔案（如果需要）
            subtitle_file = ensure_subtitle_name(download_folder)

            response = DownloadResponse(title=video_title, description=video_description, chapters=chapters, subtitle_file=subtitle_file)  # 傳遞 subtitle_file

            # 將 DownloadResponse 物件轉換為字典，然後轉換為 JSON 格式並輸出
            output_data = {
                "title": response.title,
                "description": response.description,
                "chapters": [{"start_time": c.start_time, "chapter_title": c.title, "end_time": c.end_time} for c in response.chapters],
                "subtitle_file": response.subtitle_file,
                "url": video_url
            }
            print(json.dumps(output_data, ensure_ascii=False))
            return # 確保只輸出json, 不要再有其他字串

    except yt_dlp.utils.DownloadError as e:
        print(f"下載錯誤：{e}", file=sys.stderr)  # 輸出到 stderr
        print(json.dumps({}))  # 發生錯誤時輸出空的 JSON
        return # 確保只輸出json, 不要再有其他字串
    except Exception as e:
        print(f"發生錯誤：{e}", file=sys.stderr)  # 輸出到 stderr
        print(json.dumps({})) # 發生錯誤時輸出空的 JSON
        return # 確保只輸出json, 不要再有其他字串

def clear_download_folder(download_folder):
    """清空下載資料夾中的所有檔案"""
    files = glob.glob(os.path.join(download_folder, "*"))
    for f in files:
        try:
            os.remove(f)
            # print(f"已移除檔案：{f}") #  註解: 清空資料夾的訊息通常不需要
        except OSError as e:
            print(f"移除檔案 {f} 失敗：{e}", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr


def cleanup_subtitles(download_folder, video_title, video_id, langs):
    """
    在下載資料夾中，根據語言優先順序，刪除多餘的字幕檔案，只保留一個，並將其重命名為 "subtitle.vtt"。
    返回保留的字幕檔案路徑，如果沒有找到字幕檔案則返回 None。
    修改邏輯: 優先保留英文[en]的字幕檔案。
    """
    import glob
    import os

   # 建立檔名範本
    filename_pattern = os.path.join(download_folder, f"{video_title}-{video_id}.*.vtt")

    # 轉換為絕對路徑
    filename_pattern = os.path.abspath(filename_pattern)
    # print(f"使用的檔名範本 (絕對路徑): {filename_pattern}")  # 註解: 檔名範本訊息可能不需要

    # 找到所有符合的字幕檔案
    subtitle_files = glob.glob(filename_pattern)
    # print(f"找到的字幕檔案: {subtitle_files}")  # 註解: 找到的字幕檔案訊息可能不需要

    if not subtitle_files:
        print("找不到字幕檔案。", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
        return None  # 沒有找到字幕檔案

    # 如果只有一個字幕檔案，直接重新命名
    if len(subtitle_files) == 1:
        old_file = subtitle_files[0]
        new_file = os.path.join(download_folder, "subtitle.vtt")
        # print(f"將 {old_file} 重新命名為 {new_file}")  # 註解: 重新命名訊息可能不需要
        try:
            os.rename(old_file, new_file)
            # print(f"已將字幕檔案重新命名為: {new_file}")  # 註解: 重新命名成功訊息可能不需要
            return new_file
        except Exception as e:
            print(f"重新命名檔案 {old_file} 時發生錯誤：{e}", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
            return old_file  # 發生錯誤時返回原始檔名

    # 建立語言與檔案的對應關係
    lang_files = {}
    for file in subtitle_files:
        try:
            # 從檔名中提取語言代碼
            lang = file.split(".")[-2]
            lang_files[lang] = file
        except:
            print(f"無法從檔名 {file} 提取語言代碼。", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
            continue

    # 優先檢查是否有英文 [en] 字幕
    kept_file = None
    if 'en' in lang_files:
        kept_file = lang_files['en']
    else:
        # 若沒有英文字幕，則回退到原先的語言優先順序邏輯
        for lang in langs:
            if lang in lang_files:
                kept_file = lang_files[lang]
                break
            elif lang == 'auto':
                # 自動字幕的檔名可能沒有明確的語言代碼，需要額外判斷
                for l, f in lang_files.items():
                    if l not in langs and l != 'en': #排除已知的字幕和 'en'
                        kept_file = f
                        break
                if kept_file:
                    break

    if kept_file:
        # 刪除其他字幕檔案
        for file in subtitle_files:
            if file != kept_file:
                try:
                    os.remove(file)
                    # print(f"已刪除多餘的字幕檔案：{file}") # 註解: 刪除多餘檔案訊息可能不需要
                except Exception as e:
                    print(f"刪除檔案 {file} 時發生錯誤：{e}", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr

        # 重新命名保留的字幕檔案
        new_file = os.path.join(download_folder, "subtitle.vtt")
        # print(f"將 {kept_file} 重新命名為 {new_file}")  # 註解: 重新命名訊息可能不需要
        try:
            os.rename(kept_file, new_file)
            # print(f"已將字幕檔案重新命名為: {new_file}")  # 註解: 重新命名成功訊息可能不需要
            return new_file
        except Exception as e:
            print(f"重新命名檔案 {kept_file} 時發生錯誤：{e}", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
            return kept_file

    else:
        print("找不到符合優先順序的字幕檔案。", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
        return None  # 沒有找到字幕檔案

def ensure_subtitle_name(download_folder):
    """確保資料夾中的檔案名稱是 subtitle.vtt"""
    files = glob.glob(os.path.join(download_folder, "*"))
    if files:
        existing_file = files[0]
        if os.path.basename(existing_file) != "subtitle.vtt":
            new_name = os.path.join(download_folder, "subtitle.vtt")
            try:
                os.rename(existing_file, new_name)
                # print(f"檔案已重新命名為 subtitle.vtt") # 註解: 重新命名訊息可能不需要
                return new_name
            except Exception as e:
                print(f"重新命名檔案時發生錯誤：{e}", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
                return existing_file
        else:
            # print("檔案已經命名為 subtitle.vtt") # 註解: 檔案已正確命名訊息可能不需要
            pass # 檔案已經命名正確，不需要額外訊息
            return existing_file
    else:
        print("資料夾中沒有檔案", file=sys.stderr) # 保留錯誤訊息，輸出到 stderr
        return None


class MyLogger(object):  # 自定義 Logger 類別
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg, file=sys.stderr)  # 重新導向 warning 到 stderr

    def error(self, msg):
        print(msg, file=sys.stderr)  # 重新導向 error 到 stderr

    def info(self,msg):
        print(msg,file=sys.stderr)  # 重新導向 info 到 stderr


# if __name__ == "__main__":
#     url = 'https://www.youtube.com/watch?v=PoFvGqd0RgI'
#     download_video_info(url)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <video_url>")
        sys.exit(1)

    url = sys.argv[1]

    download_video_info(url)