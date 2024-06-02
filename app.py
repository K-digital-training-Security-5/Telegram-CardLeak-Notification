from flask import Flask, render_template, request, jsonify
import requests
import concurrent.futures
import pymysql

app = Flask(__name__)

# 데이터베이스 연결 설정
db_config = {
    'host': 'database-1.cvoiy60m2yeo.ap-southeast-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'power1234',
    'database': 'card_info',
}

# 데이터베이스 연결 함수
def get_db_connection():
    connection = pymysql.connect(**db_config)
    return connection

# 데이터베이스에서 카드 정보 가져오기
def fetch_cards():
    connection = get_db_connection()
    cards = []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, AES_DECRYPT(cardnum, id), AES_DECRYPT(cardmonth, id), AES_DECRYPT(cardyear, id), AES_DECRYPT(cardcvc, id) FROM tb_cardinfo_encrypted"
            cursor.execute(sql)
            result = cursor.fetchall()
            for row in result:
                cardnum = row[1]
                cardmonth = row[2]
                cardyear = row[3]
                cardcvc = row[4]
                
                # None 값에 대한 처리 및 문자열 변환 시 오류 처리
                cards.append({
                    'id': row[0],
                    'cardnum': cardnum.decode('utf-8') if cardnum else None,
                    'cardmonth': cardmonth.decode('utf-8') if cardmonth else None,
                    'cardyear': cardyear.decode('utf-8') if cardyear else None,
                    'cardcvc': cardcvc.decode('utf-8') if cardcvc else None
                })
    except UnicodeDecodeError as e:
        print(f"Decoding error: {e}")
    finally:
        connection.close()
    return cards

# 카드 번호가 유출되었는지 확인하는 함수
def is_card_leaked(card_number):
    cards = fetch_cards()
    card_numbers = [card['cardnum'].replace("-", "") for card in cards if card['cardnum']]
    return card_number.replace("-", "") in card_numbers

# 판매자 정보 추적 함수
def track_seller(seller_id):
    social_media_platforms = {
        "Facebook": f"https://www.facebook.com/{seller_id}",
        "Telegram": f"https://t.me/{seller_id}",
        "Blogspot": f"https://{seller_id}.blogspot.com",
        "Twitter": f"https://twitter.com/{seller_id}",
        "Wordpress": f"https://{seller_id}.wordpress.com",
        "Reddit": f"https://www.reddit.com/user/{seller_id}",
        "GitHub": f"https://github.com/{seller_id}",
        "Pinterest": f"https://www.pinterest.com/{seller_id}",
        "Medium": f"https://medium.com/@{seller_id}",
        "Bitbucket": f"https://bitbucket.org/{seller_id}",
        "Ebay": f"https://www.ebay.com/usr/{seller_id}",
        "Slack": f"https://{seller_id}.slack.com",
        "ProtonMail": f"https://account.protonmail.com/api/users/available?Name={seller_id}",
        "0day":f"https://0day.red/User-{seller_id}"
    }

    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {platform: executor.submit(requests.get, url, timeout=2) for platform, url in social_media_platforms.items()}
        for platform, future in futures.items():
            try:
                response = future.result()
                if response.status_code == 200:
                    results[platform] = response.url
                else:
                    results[platform] = None
            except requests.RequestException:
                results[platform] = None
    
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_card', methods=['GET', 'POST'])
def check_card():
    if request.method == 'POST':
        card_number = request.form['card_number']
        # 하이픈 제거
        card_number = card_number.replace("-", "")
        if is_card_leaked(card_number):
            result_class = "leaked"
            result = "입력하신 카드 번호가 유출되었습니다!"
        else:
            result = "입력하신 카드 번호는 안전합니다."
            result_class = "safe"
        return render_template('check_card.html', result=result, result_class=result_class)
    return render_template('check_card.html')

@app.route('/track_seller', methods=['GET', 'POST'])
def track_seller_view():
    if request.method == 'POST':
        seller_id = request.form['seller_id']
        results = track_seller(seller_id)
        return render_template('track_seller.html', results=results, seller_id=seller_id)
    return render_template('track_seller.html')

@app.route('/get_cards', methods=['GET'])
def get_cards():
    cards = fetch_cards()
    return jsonify(cards)

if __name__ == '__main__':
    app.run(debug=True)
