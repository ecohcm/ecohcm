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

# ==================== 사진 가져오기 (더 안전하게) ====================
def get_drive_photos(folder_id):
    try:
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and (mimeType contains 'image/' or mimeType contains 'video/') and trashed=false",
            "fields": "files(id, name, mimeType)",
            "orderBy": "name",
            "key": API_KEY,
            "pageSize": 50
        }
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Drive API 오류: {response.status_code} - {response.text}")
            return []
        data = response.json()
        return data.get('files', [])
    except Exception as e:
        print("Drive 오류:", str(e))
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
        
        <button onclick="goToChangePin()" 
                class="mt-6 w-full text-blue-400 hover:text-blue-300 py-3 text-sm">
            PIN 번호 변경하기
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

    function goToChangePin() {
        const changePin = prompt("PIN 변경 창에 들어가려면 6자리 PIN을 입력하세요:");
        if (changePin) {
            fetch('/check_change_pin', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pin: changePin})
            }).then(r => r.json()).then(data => {
                if (data.success) window.location.href = "/change_pin";
                else alert("❌ 6자리 PIN이 틀렸습니다.");
            });
        }
    }
    </script>
</body>
</html>
    """
    return render_template_string(html)

def show_change_pin_page():
    html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>ecohcm - PIN 번호 변경</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-950 text-white min-h-screen flex items-center justify-center">
    <div class="bg-gray-900 p-12 rounded-3xl w-full max-w-md text-center">
        <h1 class="text-4xl font-bold mb-8">🔑 PIN 번호 변경</h1>
        <p class="text-gray-400 mb-8">새로운 4자리 PIN 번호를 입력하세요</p>
        
        <input id="newPin" type="password" maxlength="4" 
               class="w-full bg-gray-800 text-5xl text-center tracking-widest p-6 rounded-2xl mb-8 focus:outline-none focus:ring-4 focus:ring-green-500"
               placeholder="••••" autofocus>
        
        <button onclick="changePin()" 
                class="w-full bg-green-600 hover:bg-green-700 py-6 rounded-2xl text-2xl font-bold">
            PIN 번호 변경하기
        </button>
        
        <button onclick="window.location.href='/'" 
                class="mt-6 w-full text-gray-400 py-3">
            취소하고 돌아가기
        </button>
    </div>

    <script>
    function changePin() {
        const newPin = document.getElementById('newPin').value.trim();
        if (newPin.length !== 4 || !/^\d{4}$/.test(newPin)) {
            alert("PIN은 정확히 4자리 숫자여야 합니다.");
            return;
        }
        fetch('/update_pin', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({new_pin: newPin})
        }).then(r => r.json()).then(data => {
            if (data.success) {
                alert("✅ PIN 번호가 성공적으로 변경되었습니다!\\n새 PIN: " + newPin);
                window.location.href = '/';
            } else {
                alert("변경 실패");
            }
        });
    }
    </script>
</body>
</html>
    """
    return render_template_string(html)

# ====================== 메인 사이트 (모든 기능 포함) ======================
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
        .folder-label { font-size: 2.5rem; font-weight: 800; margin-bottom: 1.5rem; }
        img { cursor: pointer; transition: transform 0.2s; }
        img:hover { transform: scale(1.05); }
        .cart-img { max-height: 180px; object-fit: cover; border-radius: 12px; }
    </style>
</head>
<body class="bg-gray-900 text-white">
<div class="max-w-7xl mx-auto p-6">
    <h1 class="text-5xl font-bold text-center my-10">ecohcm - 사진 예약 사이트</h1>

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

<!-- 장바구니 모달 -->
<div id="cartModal" class="hidden fixed inset-0 bg-black/90 flex items-center justify-center z-50">
    <div class="bg-gray-800 rounded-3xl p-8 w-full max-w-2xl max-h-[85vh] overflow-auto">
        <h2 id="modalTitle" class="text-3xl font-bold mb-6"></h2>
        <div id="cartList" class="grid grid-cols-2 gap-4 mb-8"></div>
        <button onclick="goToReserve()" class="w-full bg-red-600 hover:bg-red-700 py-5 text-xl rounded-2xl font-bold">예약하기</button>
        <button onclick="hideCart()" class="mt-4 w-full text-gray-400 py-3">닫기</button>
    </div>
</div>

<!-- 예약 모달 -->
<div id="reserveModal" class="hidden fixed inset-0 bg-black/90 flex items-center justify-center z-50">
    <div class="bg-gray-800 rounded-3xl p-8 w-full max-w-md">
        <h2 class="text-3xl font-bold mb-6">예약 정보</h2>
        <input id="reserveDate" type="date" class="w-full p-4 bg-gray-700 rounded-2xl mb-4 text-white">
        <input id="reserveTgId" type="text" placeholder="Telegram ID 또는 @아이디" class="w-full p-4 bg-gray-700 rounded-2xl mb-6 text-white">
        <button id="submitBtn" onclick="submitReservation()" class="w-full bg-green-600 hover:bg-green-700 py-5 text-xl rounded-2xl font-bold">✅ 예약 전송하기</button>
        <button onclick="hideReserveModal()" class="mt-4 w-full text-gray-400 py-3">취소</button>
    </div>
</div>

<!-- 라이트박스 (슬라이드) -->
<div id="lightbox" class="hidden fixed inset-0 bg-black/95 flex items-center justify-center z-[60]">
    <div class="relative max-w-5xl w-full px-4">
        <button onclick="closeLightbox()" class="absolute -top-12 right-4 text-white text-5xl hover:text-gray-300">&times;</button>
        <img id="lightboxImg" class="max-h-[80vh] mx-auto rounded-2xl shadow-2xl" src="">
        <button onclick="prevImage()" class="absolute left-8 top-1/2 -translate-y-1/2 bg-black/60 text-white text-5xl w-14 h-14 rounded-full flex items-center justify-center">&lt;</button>
        <button onclick="nextImage()" class="absolute right-8 top-1/2 -translate-y-1/2 bg-black/60 text-white text-5xl w-14 h-14 rounded-full flex items-center justify-center">&gt;</button>
        <button onclick="addCurrentToCart()" class="absolute bottom-8 right-8 bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-2xl text-lg font-bold flex items-center gap-2">
            <i class="fas fa-cart-plus"></i> 장바구니에 담기
        </button>
        <p id="lightboxCaption" class="text-center text-white mt-6 text-lg"></p>
    </div>
</div>

<script>
let currentPhotos = [];
let currentIndex = 0;
let currentType = 1;
let isReserving = false;

window.switchTab = function(n) {
    document.getElementById('gallery1').classList.add('hidden');
    document.getElementById('gallery2').classList.add('hidden');
    document.getElementById('gallery' + n).classList.remove('hidden');
};

window.openLightbox = function(img, folder) {
    currentType = folder;
    currentPhotos = Array.from(document.querySelectorAll('#gallery' + folder + ' img'));
    currentIndex = currentPhotos.indexOf(img);
    showCurrentImage();
    document.getElementById('lightbox').classList.remove('hidden');
};

function showCurrentImage() {
    const img = currentPhotos[currentIndex];
    document.getElementById('lightboxImg').src = img.src.replace('&sz=w800', '&sz=w1200');
    document.getElementById('lightboxCaption').textContent = img.parentElement.querySelector('p').textContent || '';
}

window.prevImage = function() { currentIndex = (currentIndex - 1 + currentPhotos.length) % currentPhotos.length; showCurrentImage(); };
window.nextImage = function() { currentIndex = (currentIndex + 1) % currentPhotos.length; showCurrentImage(); };
window.closeLightbox = function() { document.getElementById('lightbox').classList.add('hidden'); };

window.addCurrentToCart = function() {
    const img = currentPhotos[currentIndex];
    const idMatch = img.src.match(/id=([a-zA-Z0-9_-]+)/);
    const photoId = idMatch ? idMatch[1] : '';
    const name = document.getElementById('lightboxCaption').textContent;
    if (photoId) addToCart(currentType, photoId, name);
};

window.addToCart = function(type, id, name) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type.toString(), id: id, name: name})
    }).then(r => r.json()).then(data => alert(data.message || data.status));
};

window.showCart = function(type) {
    currentType = type;
    fetch('/get_cart?type=' + type)
    .then(r => r.json())
    .then(items => {
        document.getElementById('modalTitle').innerHTML = type + '번 장바구니 (' + items.length + '장)';
        const container = document.getElementById('cartList');
        container.innerHTML = '';
        items.forEach((item, index) => {
            const div = document.createElement('div');
            div.className = "bg-gray-700 p-3 rounded-2xl relative";
            div.innerHTML = `
                <img src="https://drive.google.com/thumbnail?id=${item.id}&sz=w400" class="cart-img w-full">
                <p class="mt-2 text-center truncate">${item.name}</p>
                <button onclick="removeFromCart(${index}, ${type})" 
                        class="absolute top-2 right-2 bg-red-600 hover:bg-red-700 text-white w-8 h-8 rounded-full flex items-center justify-center text-xl font-bold">
                    ×
                </button>
            `;
            container.appendChild(div);
        });
        document.getElementById('cartModal').classList.remove('hidden');
    });
};

window.removeFromCart = function(index, type) {
    if (!confirm("이 사진을 장바구니에서 삭제하시겠습니까?")) return;
    fetch('/remove_from_cart', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type: type.toString(), index: index})
    }).then(r => r.json()).then(data => {
        alert(data.message);
        showCart(type);
    });
};

window.hideCart = function() { document.getElementById('cartModal').classList.add('hidden'); };
window.goToReserve = function() { hideCart(); document.getElementById('reserveModal').classList.remove('hidden'); resetReserveButton(); };
window.hideReserveModal = function() { document.getElementById('reserveModal').classList.add('hidden'); resetReserveButton(); };

function resetReserveButton() {
    isReserving = false;
    const btn = document.getElementById('submitBtn');
    if (btn) { btn.disabled = false; btn.innerHTML = '✅ 예약 전송하기'; }
}

window.submitReservation = function() {
    if (isReserving) return;
    isReserving = true;
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.innerHTML = '⏳ 예약 처리 중...';

    const date = document.getElementById('reserveDate').value;
    const tgId = document.getElementById('reserveTgId').value || "미입력";
    if (!date) {
        alert("날짜를 선택해주세요!");
        resetReserveButton();
        return;
    }

    fetch('/get_cart?type=' + currentType)
    .then(r => r.json())
    .then(photos => {
        fetch('/reserve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({type: currentType.toString(), photos: photos, date: date, tg_id: tgId})
        }).then(() => {
            alert("✅ 예약이 Telegram으로 전송되었습니다!");
            hideReserveModal();
            cart1 = []; cart2 = [];
        }).catch(() => {
            alert("전송 중 오류가 발생했습니다.");
            resetReserveButton();
        });
    });
};
</script>
</body>
</html>
"""
    return render_template_string(html, photos1=photos1, photos2=photos2)

# ====================== API 라우트 ======================
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
