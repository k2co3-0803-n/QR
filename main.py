import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import cv2
# from pyzbar.pyzbar import decode
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証情報の設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('./KEY/gspread-for-python-420303-e7ddbb5d8fe7.json', scope)

# クライアントの作成
client = gspread.authorize(creds)

# スプレッドシートの取得
spreadsheet = client.open_by_key('1yVVzEtgICXiWCFEsp8kTUSgj8LqgzH5ki64f345NuqE')

# シートの取得
sheet = spreadsheet.worksheet('受付データ')

# 全データの取得
data = sheet.get_all_records()
print(data)

# ✅ フォントのパスを修正（IPAex明朝を使用）
FONT_PATH = "./FONTS/ipaexm.ttf"

# ✅ フォント登録（IPAex明朝）
pdfmetrics.registerFont(TTFont("IPAexMincho", FONT_PATH))

# ✅ 出力ディレクトリを作成（存在しない場合）
OUTPUT_DIR = "OUTPUT"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ すでに処理済みのQRコードを記録するセット
scanned_qr_codes = set()


def get_next_filename():
    """OUTPUTフォルダ内のファイル数をチェックし、連番ファイル名を作成"""
    files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("business_card_") and f.endswith(".pdf")]
    numbers = [int(f.split("_")[-1].split(".")[0]) for f in files if f.split("_")[-1].split(".")[0].isdigit()]
    next_number = max(numbers) + 1 if numbers else 1
    return f"business_card_{next_number:03}.pdf"


def generatePDF(affiliation, grade, name):
    """QRコードの情報から名刺PDFを作成"""
    filename = get_next_filename()
    output_path = os.path.join(OUTPUT_DIR, filename)

    # ✅ PDFのページサイズを設定（名刺サイズ: 91mm × 55mm = 258 × 156 pt）
    c = canvas.Canvas(output_path, pagesize=(258, 156))

    # ✅ 日本語フォントを設定
    c.setFont("IPAexMincho", 14)  # IPAex明朝フォントを適用
    text_y = 120  # 上からの位置調整
    c.drawCentredString(129, text_y, affiliation)  # 学部名

    c.setFont("IPAexMincho", 12)
    text_y -= 25
    c.drawCentredString(129, text_y, grade)  # 学年

    c.setFont("IPAexMincho", 16)  # 名前を目立たせる
    text_y -= 30
    c.drawCentredString(129, text_y, name)  # 名前

    c.save()
    print(f"✅ PDF を保存しました: {output_path}")


def scan_qr():
    cap = cv2.VideoCapture(0)  # カメラを起動
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        detecter = cv2.QRCodeDetector()
        data, bbox, _ = detecter.detectAndDecode(frame)
        # decoded_objects = decode(frame)
        # for obj in decoded_objects:
        if data:
            try:
                # qr_text = obj.data.decode("utf-8")  # ✅ UTF-8でデコード
                qr_text = data
                print(f"📥 読み取ったQRコードの内容: {qr_text}")
                cap.release()
                cv2.destroyAllWindows()
                return qr_text
            except UnicodeDecodeError:
                print("❌ デコードに失敗しました！エンコード方式を確認してください。")

        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):  # "q"キーで終了
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


def play_success_sound():
    os.system("afplay /System/Library/Sounds/Ping.aiff")

def play_error_sound():
    os.system("afplay /System/Library/Sounds/Basso.aiff")

def main():
    """QRコードをスキャンし、PDFを生成するメイン関数"""
    read = scan_qr()

    # ✅ すでに読み取ったQRコードの場合はスキップ
    if read in scanned_qr_codes:
        print("⚠️ このQRコードはすでに処理済みです。スキャンをスキップします。")
        play_error_sound()
        return

    reads = read.split("/")
    if len(reads) < 3:
        print("❌ PDFの生成を中止しました（入力データが不完全）。")
        play_error_sound()
        return
    
    affiliation, grade, name = reads[0].strip(), reads[1].strip(), reads[2].strip()

    # ✅ PDF を生成
    generatePDF(affiliation, grade, name)

    # ✅ 読み取ったQRコードを記録
    scanned_qr_codes.add(read)
    play_success_sound()


# ✅ スクリプトとして実行する場合
if __name__ == "__main__":
    while True:
        main()
