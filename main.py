import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from m import scan_qr

# ✅ フォントのパスを修正（IPAex明朝を使用）
FONT_PATH = "/Users/chino/Library/Fonts/ipaexm.ttf"

# ✅ フォント登録（IPAex明朝）
pdfmetrics.registerFont(TTFont("IPAexMincho", FONT_PATH))

# ✅ 出力ディレクトリを作成（存在しない場合）
OUTPUT_DIR = "OUTPUT"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generatePDF(affiliation, grade, name, filename="business_card.pdf"):
    """QRコードの情報から名刺PDFを作成"""
    # ✅ 出力ファイルのパスを設定
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


def scanQR():
    """QRコードの情報を手動で入力して解析"""
    print("📸 お手持ちのQRコードをリーダーにかざして下さい。")
    raw_input = input("QRコードの内容を入力してください: ")  # 例: 理工学部/学部3年/山田 太郎

    # ✅ 期待する形式: 「学部/学年/名前」
    informations = raw_input.split("/")

    # ✅ エラーチェック（最低3つのデータがあるか）
    if len(informations) < 3:
        print("❌ QRコードの情報が不足しています！ 正しいフォーマットで入力してください。")
        return None, None, None

    # ✅ 各情報を取得（strip() で前後の空白を削除）
    affiliation = informations[0].strip()
    grade = informations[1].strip()
    name = informations[2].strip()

    print(f"📥 読み取った情報：学部={affiliation}, 学年={grade}, 名前={name}")
    return affiliation, grade, name


def main():
    """QRコードをスキャンし、PDFを生成するメイン関数"""
    read = scan_qr()
    reads = read.split("/")
    affiliation = reads[0]
    grade = reads[1]
    name = reads[2]
    # affiliation, grade, name = scan_qr()

    if not affiliation or not grade or not name:
        print("❌ PDFの生成を中止しました（入力データが不完全）。")
        return

    generatePDF(affiliation, grade, name)


# ✅ スクリプトとして実行する場合、main() を呼び出す
if __name__ == "__main__":
	while True:
		main()
