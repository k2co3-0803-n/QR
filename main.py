import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import cv2
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ Googleスプレッドシート認証設定
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name('./KEY/gspread-for-python.json', SCOPE)
CLIENT = gspread.authorize(CREDS)
SPREADSHEET = CLIENT.open_by_key('1yVVzEtgICXiWCFEsp8kTUSgj8LqgzH5ki64f345NuqE')
SHEET = SPREADSHEET.worksheet('受付データ')

# ✅ フォントのパスを修正（IPAex明朝を使用）
FONT_PATH = "./FONT/ipaexm.ttf"

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


def generatePDF(affiliation, year, name):
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
    c.drawCentredString(129, text_y, year)  # 学年

    c.setFont("IPAexMincho", 16)  # 名前を目立たせる
    text_y -= 30
    c.drawCentredString(129, text_y, name)  # 名前

    c.save()
    print(f"✅ PDF を保存しました: {output_path}")


def scan_qr():
    """QRコードをスキャンし、データを返す関数"""
    cap = cv2.VideoCapture(0)  # カメラを起動

    if not cap.isOpened():
        print("❌ エラー: カメラを開けません。")
        return None

    detecter = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()  # フレームを取得

        # フレーム取得に失敗した場合は次のループへ
        if not ret or frame is None:
            continue  # ループの先頭に戻る

        # QRコードの検出とデコード
        data, bbox, _ = detecter.detectAndDecode(frame)

        # QRコードが検出された場合、データを返す
        if data:
            print("✅ QRコードを検出しました:", data)
            cap.release()
            return data

        # カメラ映像を表示（デバッグ用）
        cv2.imshow("QR Scanner", frame)

        # `q` を押したらスキャンを終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


def play_success_sound():
    os.system("afplay ./SOUND/Ping.aiff")

def play_error_sound():
    os.system("afplay ./SOUND/Basso.aiff")

def main():
    """QRコードをスキャンし、PDFを生成するメイン関数"""
    read = scan_qr().strip()  # 空白や改行を除去

    # ✅ すでに読み取ったQRコードの場合はスキップ
    if read in scanned_qr_codes:
        print("⚠️ このQRコードはすでに処理済みです。スキャンをスキップします。")
        play_error_sound()
        return

    # `?` を削除し、パラメータを分割
    params = read.lstrip('?').split('&')
    # params = read.split('&')

    # パラメータを辞書に変換
    param_dict = {}
    for param in params:
        if '=' in param:
            key, value = param.split('=', 1)  # '=' で分割（最大1回）
            param_dict[key] = value.strip()

    # 必要なキーがすべて存在するかチェック
    required_keys = {"form_id", "affiliation", "year", "name"}
    if not required_keys.issubset(param_dict.keys()):
        print("❌ PDFの生成を中止しました（入力データが不完全または無効です）。")
        play_error_sound()
        return

    # 各値を取得
    form_id = param_dict["form_id"]
    affiliation = param_dict["affiliation"]
    year = param_dict["year"]
    name = param_dict["name"]

    # ✅ スプレッドシートの最下行にデータを追加
    SHEET.append_row([form_id, affiliation, year, name])
    print(f"✅ スプレッドシートに追加: {form_id}, {affiliation}, {year}, {name}")

    # ✅ PDF を生成
    generatePDF(affiliation, year, name)

    # ✅ 読み取ったQRコードを記録
    scanned_qr_codes.add(read)
    play_success_sound()


# ✅ スクリプトとして実行する場合
if __name__ == "__main__":
    while True:
        main()
