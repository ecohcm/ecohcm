from flask import Flask, render_template_string, request, jsonify, session, redirect
import requests

app = Flask(__name__)
app.secret_key = "super-secret-key-2025"

# ==================== 설정 ====================
FOLDER1_ID = "15cN-w5yjUTog-bXmDn8RGVTZzBDm6Uw_"
FOLDER2_ID = "1stNTBFJsKDiHymMFgAANcAZqwxpCom4y"

TELEGRAM_TOKEN = "8418423317:AAHodaij34Zu5MZciHWLBXbgAUzKBkUL4Rs"
YOUR_CHAT_ID = "7737429021"

CURRENT_PIN = "1234"
CHANGE_PIN = "000000"

API_KEY = "AIzaSyD9JqlO1r4WozGod_vd5R6DOQB_HRits18"

cart1 = []
cart2 = []

# ==================== 사진 가져오기 ====================
def get_drive_photos(folder_id):
    try:
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed=false",
            "fields": "files(id, name, mimeType)",
            "orderBy": "name",
            "key": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('files', [])
    except Exception as e:
        print("Drive 오류:", e)
        return []

# ==================== PIN 페이지 ====================
def show_pin_page():
    html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>ecohcm - PIN 인증</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-white min-h-screen flex items-center justify-center">
    <div class="bg-gray-900 p-12 rounded-3xl w-full max-w-md text-center">
        <h1 class="text-5xl font-bold mb-8">🔒 ecohcm 접근 권한 필요</h1>
        <p class="text-gray-400 mb-10 text-lg">4자리 PIN 번호를 입력해주세요</p>
        
        <input id="pinInput" type="password" maxlength="4" 
               class="w-full bg-gray-800 text-5xl text-center tracking-widest p-6 rounded-2xl focus:outline-none focus:ring-4 focus:ring-blue-500 mb-8"
               placeholder="••••" autofocus>
        
        <button onclick="checkPin()" 
                class="w-full bg-blue-600 hover:bg-blue-700 py-6 rounded-2xl text-2xl font-bold">
            확인
        </button>
    </div>

    <script>
    function checkPin() {
        const pin = document.getElementById('pinInput').value.trim();
        fetch('/check_pin', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pin: pin})
        }).then(r => r.json()).then(data => {
            if (data.success) window.location.href = "/main";
            else {
                alert("❌ PIN 번호가 틀렸습니다.");
                document.getElementById('pinInput').value = '';
            }
        });
    }
    </script>
</body>
</html>
    """
    return render_template_string(html)

# ====================== 메인 사이트 (1번, 2번 명확하게 표시) ======================
def show_main_site():
    photos1 = get_drive_photos(FOLDER1_ID)
    photos2 = get_drive_photos(FOLDER2_ID)
    
    html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>ecohcm - 사진 예약 사이트</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        .folder-label { font-size: 2.2rem; font-weight: 800; margin-bottom: 1.5rem; }
        img { cursor: pointer; transition: transform 0.2s; }
        img:hover { transform: scale(1.05); }
        .cart-img { max-height: 180px; object-fit: cover; border-radius: 12px; }
    </style>
</head>
<body class="bg-gray-900 text-white">
<div class="max-w-7xl mx-auto p-6">
    <h1 class="text-5xl font-bold text-center my-10 text-white">ecohcm - 사진 예약 사이트</h1>

    <!-- 1번 폴더 -->
    <div class="mb-16">
        <div class="folder-label text-blue-400">📁 1번 폴더</div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {% for photo in photos1 %}
            <div class="bg-gray-800 rounded-3xl overflow-hidden shadow-xl">
                <img src="https://drive.google.com/thumbnail?id={{ photo.id }}&sz=w800" 
                     onclick="openLightbox(this, 1)" class="w-full h-64 object-cover">
                <div class="p-4"><p class="font-medium truncate">{{ photo.name }}</p></div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- 2번 폴더 -->
    <div>
        <div class="folder-label text-purple-400">📁 2번 폴더</div>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {% for photo in photos2 %}
            <div class="bg-gray-800 rounded-3xl overflow-hidden shadow-xl">
                <img src="https://drive.google.com/thumbnail?id={{ photo.id }}&sz=w800" 
                     onclick="openLightbox(this, 2)" class="w-full h-64 object-cover">
                <div class="p-4"><p class="font-medium truncate">{{ photo.name }}</p></div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>

<!-- 장바구니 버튼 -->
<div class="fixed bottom-8 right-8 flex flex-col gap-3 z-40">
    <button onclick="showCart(1)" class="bg-green-600 hover:bg-green-700 w-64 py-4 rounded-2xl text-lg font-bold shadow-2xl">1번 장바구니 보기</button>
    <button onclick="showCart(2)" class="bg-green-600 hover:bg-green-700 w-64 py-4 rounded-2xl text-lg font-bold shadow-2xl">2번 장바구니 보기</button>
</div>

<!-- 장바구니, 예약, 라이트박스 모달과 JS 코드는 이전과 동일 -->
<!-- (공간상 생략했으나, 실제로는 이전에 사용하던 전체 JS 코드를 그대로 넣어주세요) -->

</body>
</html>
"""
    return render_template_string(html, photos1=photos1, photos2=photos2)

# ====================== API 라우트 (장바구니, 예약 등) ======================
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    t = data.get('type')
    photo_id = data.get('id')
    name = data.get('name')
    cart = cart1 if t == "1" else cart2
    if any(item['id'] == photo_id for item in cart):
        return jsonify({"status": "duplicate", "message": "⚠️ 이미 추가된 사진입니다!"})
    cart.append({"id": photo_id, "name": name})
    return jsonify({"status": "ok", "message": f"✅ {name}을(를) {t}번 장바구니에 담았습니다!"})

@app.route('/get_cart', methods=['GET'])
def get_cart():
    t = request.args.get('type')
    return jsonify(cart1 if t == "1" else cart2)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    t = data.get('type')
    index = int(data.get('index', -1))
    cart = cart1 if t == "1" else cart2
    if 0 <= index < len(cart):
        removed = cart.pop(index)
        return jsonify({"status": "ok", "message": f"🗑️ {removed['name']}을(를) 삭제했습니다."})
    return jsonify({"status": "error", "message": "삭제할 수 없습니다."})

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.get_json()
    t = data.get('type')
    photos = data.get('photos', [])
    date = data.get('date')
    tg_id = data.get('tg_id')
    
    cart_name = "1번" if t == "1" else "2번"
    msg = f"🚨 <b>새 예약 들어왔습니다!</b> ({cart_name})\n\n📅 날짜: {date}\n👤 고객 Telegram: {tg_id}\n🖼️ 미디어 ({len(photos)}개):\n" + "\n".join([p['name'] for p in photos])
    
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                  json={"chat_id": YOUR_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    
    for photo in photos:
        photo_url = f"https://drive.google.com/uc?id={photo['id']}"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
                      json={"chat_id": YOUR_CHAT_ID, "photo": photo_url, "caption": photo['name']})
    
    if t == "1": cart1.clear()
    else: cart2.clear()
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("🚀 서버 시작!")
    print("접속 주소 → http://192.168.0.9:5000")
    print(f"사이트 PIN: {CURRENT_PIN}")
    app.run(host='0.0.0.0', port=5000, debug=True)
