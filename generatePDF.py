import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# フォントのパス（IPAex明朝を使用）
FONT_PATH = "/Users/chino/Library/Fonts/ipaexm.ttf"

# フォント登録
pdfmetrics.registerFont(TTFont("Hiragino", FONT_PATH))

# 出力ディレクトリを作成（存在しない場合）
OUTPUT_DIR = "OUTPUT"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generatePDF(affiliation, grade, name, filename):
    # 出力ファイルのパスを設定
    output_path = os.path.join(OUTPUT_DIR, filename)

    c = canvas.Canvas(output_path, pagesize=(258, 156))

    # 日本語フォントを設定
    c.setFont("Hiragino", 14)
    text_y = 120  # 上からの位置調整
    c.drawCentredString(129, text_y, affiliation)

    c.setFont("Hiragino", 12)
    text_y -= 25
    c.drawCentredString(129, text_y, grade)

    c.setFont("Hiragino", 16)  # 名前を目立たせる
    text_y -= 30
    c.drawCentredString(129, text_y, name)

    c.save()

    print(f"✅ PDF を保存しました: {output_path}")

# 使用例（OUTPUT/business_card.pdf に保存）
generatePDF("理工学部", "学部3年", "山田 太郎", "business_card.pdf")
