import cv2
from pyzbar.pyzbar import decode

def scan_qr():
    cap = cv2.VideoCapture(0)  # カメラを起動
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            try:
                qr_text = obj.data.decode("utf-8")  # ✅ UTF-8でデコード
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

scan_qr()
