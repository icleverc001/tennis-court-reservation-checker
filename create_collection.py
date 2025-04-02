import csv
import os
import datetime
import re
from pathlib import Path

def parse_datetime(entry):
    # エントリの例：03/24(月),11:00-13:00,甘泉園公園,yana
    parts = entry.split(',')
    date_str = parts[0]  # 03/24(月)
    time_str = parts[1]  # 11:00-13:00
    
    # 日付の解析
    month, day = re.match(r'(\d+)/(\d+)', date_str).groups()
    month, day = int(month), int(day)
    
    # 時間の解析（開始時間のみ使用）
    start_time = time_str.split('-')[0]  # 11:00
    hour, minute = map(int, start_time.split(':'))
    
    # 現在の年を取得
    current_year = datetime.datetime.now().year
    
    # 日付時間オブジェクトを作成
    try:
        dt_obj = datetime.datetime(current_year, month, day, hour, minute)
        # 過去の日付なら来年と仮定（4月のデータに3月が含まれているため）
        if dt_obj.month < 4 and datetime.datetime.now().month >= 4:
            dt_obj = datetime.datetime(current_year + 1, month, day, hour, minute)
    except ValueError:
        # 無効な日付の場合は遠い未来の日付にする
        dt_obj = datetime.datetime(9999, 12, 31, 23, 59)
    
    return dt_obj

def main():
    # 入力ファイルと出力ファイルのパス
    input_files = [
        'output/shinjuku.csv',
        'output/suginami.csv',
        'output/tokyo.csv'
    ]
    output_file = 'output.csv'  # 出力ファイル名をoutput.csvに戻す
    
    all_entries = []
    
    # 各ファイルから内容を読み込む
    for file_path in input_files:
        try:
            # 複数のエンコーディングを試す
            encodings = ['shift_jis', 'cp932', 'utf-8', 'euc-jp']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        lines = file.readlines()
                        
                        # 最初の行（ヘッダー）をスキップ
                        for line in lines[1:]:
                            line = line.strip()
                            if line and not line.startswith('<'):  # 不要な行をスキップ
                                # 各フィールドに分割
                                all_entries.append(line)
                        
                        # 正常に読み込めたらループを抜ける
                        break
                except UnicodeDecodeError:
                    # このエンコーディングで読めなければ次を試す
                    continue
                except Exception as e:
                    print(f"Error reading {file_path} with {encoding}: {e}")
                    break
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # 日付と時間でソート
    sorted_entries = sorted(all_entries, key=parse_datetime)
    
    # 出力ファイルに書き込み（shift_jisエンコーディングを使用）
    with open(output_file, 'w', encoding='shift_jis', newline='') as f:
        for entry in sorted_entries:
            f.write(f"{entry}\n")
    
    print(f"完了: {len(sorted_entries)}件のデータを{output_file}に書き込みました。")
    print(f"エンコーディング: shift_jis")

if __name__ == "__main__":
    main() 