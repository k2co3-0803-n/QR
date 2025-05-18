import os
import winsound
import win32print
import win32api
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import cv2
import gspread
import base64
import urllib.parse
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Googleスプレッドシート認証設定
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name('./KEY/gspread-for-python.json', SCOPE)
CLIENT = gspread.authorize(CREDS)
SPREADSHEET = CLIENT.open_by_key('HERE: PASTE SHEET_ID')
SHEET = SPREADSHEET.worksheet('受付中')

# ✅ フォントのパス（Windows用。相対パスでOK）
FONT_PATH = os.path.join("FONT", "ipaexm.ttf")

# ✅ フォント登録（IPAex明朝）
pdfmetrics.registerFont(TTFont("IPAexMincho", FONT_PATH))

# ✅ 出力ディレクトリを作成（存在しない場合）
OUTPUT_DIR = "OUTPUT"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ すでに処理済みのQRコードを記録するセット
scanned_qr_codes = set()


def get_next_filename():
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("business_card_") and f.endswith(".pdf")]
    numbers = [int(f.split("_")[-1].split(".")[0]) for f in files if f.split("_")[-1].split(".")[0].isdigit()]
    next_number = max(numbers) + 1 if numbers else 1
    return f"business_card_{next_number:03}.pdf"


# def generatePDF(affiliation, grade, name):
#     filename = get_next_filename()
#     output_path = os.path.join(OUTPUT_DIR, filename)

#     c = canvas.Canvas(output_path, pagesize=(258, 156))
#     c.setFont("IPAexMincho", 14)
#     text_y = 120
#     c.drawCentredString(129, text_y, affiliation)

#     c.setFont("IPAexMincho", 12)
#     text_y -= 25
#     c.drawCentredString(129, text_y, grade)

#     c.setFont("IPAexMincho", 16)
#     text_y -= 30
#     c.drawCentredString(129, text_y, name)

#     c.save()
#     print(f"✅ PDF を保存しました: {output_path}")
#     return output_path


def generatePDF(affiliation, grade, name):
    filename = get_next_filename()
    output_path = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(output_path, pagesize=(258, 156))
    
    # フォントサイズを全体的に2回り（+6pt程度）大きくする
    c.setFont("IPAexMincho", 20)
    text_y = 120
    c.drawCentredString(129, text_y, affiliation)

    c.setFont("IPAexMincho", 18)
    text_y -= 30
    c.drawCentredString(129, text_y, grade)

    c.setFont("IPAexMincho", 24)
    text_y -= 35
    c.drawCentredString(129, text_y, name)

    c.save()
    print(f"✅ PDF を保存しました: {output_path}")
    return output_path


# def scan_qr():
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("❌ エラー: カメラを開けません。")
#         return None

#     detecter = cv2.QRCodeDetector()

#     while True:
#         ret, frame = cap.read()
#         if not ret or frame is None:
#             continue

#         data, bbox, _ = detecter.detectAndDecode(frame)

#         if data:
#             print("✅ QRコードを検出しました:", data)
#             cap.release()
#             cv2.destroyAllWindows()
#             return data

#         cv2.imshow("QR Scanner", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     return None


def scan_qr():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ エラー: カメラを開けません。")
        return None

    detecter = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        try:
            # QRコードの検出とデコード
            data, bbox, _ = detecter.detectAndDecode(frame)
        except cv2.error as e:
            print(f"⚠️ QRコード解析エラー: {e}")
            continue  # エラーが出てもスキップして次のフレームへ

        if data:
            print("✅ QRコードを検出しました:", data)
            cap.release()
            cv2.destroyAllWindows()
            return data

        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


def play_success_sound():
    winsound.MessageBeep(winsound.MB_OK)


def play_error_sound():
    winsound.MessageBeep(winsound.MB_ICONHAND)


def print_pdf(file_path, printer_name="Brother TD-4550DNWB"):
    win32print.SetDefaultPrinter(printer_name)
    win32api.ShellExecute(
        0,
        "print",
        file_path,
        None,
        ".",
        0
    )


def parse_qr_query_from_url(input_str):
    try:
        encoded_data = None

        if isinstance(input_str, str) and ('://' in input_str):
            query_index = input_str.find('?')
            query_string = input_str[query_index + 1:] if query_index >= 0 else input_str
            params = query_string.split('&')
            for pair in params:
                if '=' in pair:
                    key, val = pair.split('=', 1)
                    if key == 'data':
                        encoded_data = val
                        break
            if not encoded_data:
                print(f'data パラメータが見つかりません: {input_str}')
                return []
        else:
            encoded_data = input_str

        try:
            padded_data = encoded_data + '=' * (-len(encoded_data) % 4)
            decoded_bytes = base64.urlsafe_b64decode(padded_data)
            decoded_str = decoded_bytes.decode('utf-8')
            print(f"デコードデータ> {decoded_str}")
        except Exception as err:
            print(f'Base64 デコード失敗: {err}, {encoded_data}')
            return []

        if decoded_str.startswith('?'):
            decoded_str = decoded_str[1:]

        obj = {}
        for pair in decoded_str.split('&'):
            if '=' in pair:
                key, val = pair.split('=', 1)
                try:
                    val = urllib.parse.unquote(urllib.parse.unquote(val))
                except Exception as e:
                    print(f'decodeURIComponent エラー: {key}, {val}, {e}')
                if val.lower() == "null":
                    val = " "
                obj[key] = val

        return [obj.get('form_id'), obj.get('affiliation'), obj.get('grade'), obj.get('name')]

    except Exception as e:
        print(f'エラー: {e}')
        return []


def main():
    read = scan_qr()
    if not read:
        return
    read = read.strip()

    if read in scanned_qr_codes:
        print("⚠️ このQRコードはすでに処理済みです。スキャンをスキップします。")
        play_error_sound()
        return

    decoded_values = parse_qr_query_from_url(read)
    print("デコード結果:", decoded_values)

    # if len(decoded_values) != 4 or any(v is None or v.strip() == '' for v in decoded_values):
    if len(decoded_values) != 4:
        print("❌ PDFの生成を中止しました（QRコード内容が不完全または無効です）。")
        play_error_sound()
        return

    form_id, affiliation, grade, name = decoded_values
    name = name.replace('\u3000', ' ')  # ← ここで全角スペースを半角に置換

    play_success_sound()
    output_path = generatePDF(affiliation, grade, name)
    print_pdf(output_path)
    scanned_qr_codes.add(read)
    SHEET.append_row([form_id])
    print(f"✅ スプレッドシートに追加: {form_id}")


# def main():
#     read = scan_qr()
#     if not read:
#         return
#     read = read.strip()

#     if read in scanned_qr_codes:
#         print("⚠️ このQRコードはすでに処理済みです。スキャンをスキップします。")
#         play_error_sound()
#         return

#     params = read.lstrip('?').split('&')
#     param_dict = {}
#     for param in params:
#         if '=' in param:
#             key, value = param.split('=', 1)
#             param_dict[key] = value.strip()

#     required_keys = {"form_id", "affiliation", "grade", "name"}
#     if not required_keys.issubset(param_dict.keys()):
#         print("❌ PDFの生成を中止しました（入力データが不完全または無効です）。")
#         play_error_sound()
#         return

#     form_id = param_dict["form_id"]
#     affiliation = param_dict["affiliation"]
#     grade = param_dict["grade"]
#     name = param_dict["name"]

#     SHEET.append_row([form_id, affiliation, grade, name])
#     print(f"✅ スプレッドシートに追加: {form_id}, {affiliation}, {grade}, {name}")

#     output_path = generatePDF(affiliation, grade, name)
#     scanned_qr_codes.add(read)
#     print_pdf(output_path)
#     play_success_sound()

if __name__ == "__main__":
    while True:
        main()
