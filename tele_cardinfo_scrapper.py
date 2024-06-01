from telethon import TelegramClient, sync
import re

# 텔레그램 API 정보
api_id = '26318137'      # my.telegram.org에서 받은 API ID
api_hash = '8a45166cb0c8cb9812b77e50ce94ea0b'  # my.telegram.org에서 받은 API Hash

# 클라이언트 생성
client = TelegramClient('scraper_session', api_id, api_hash)

# 클라이언트 시작
client.start()

# 채널 URL
channels = ['https://t.me/xforce8']

# 카드 정보 정규 표현식
card_pattern = re.compile(r"\b\d{16}[|/ ]\d{2}[|/ ]\d{2,4}[|/ ]\d{3}\b")

# 출력 파일 경로
output_file = 'scraped_data.txt'

# 메시지 스크래핑 함수
def scrape_channel(channel_url):
    entity = client.get_entity(channel_url)
    messages = client.get_messages(entity, limit=10000)  # 마지막 10000개의 메시지 가져오기 (필요에 따라 조절)
    
    results = []

    for message in messages:
        if message.text:  # 메시지 텍스트가 None이 아닌 경우에만 처리
            matches = card_pattern.findall(message.text)
            for match in matches:
                formatted_match = re.sub(r'[|/ ]', ',', match)  # 구분자를 ','로 변경
                parts = formatted_match.split(',')
                formatted_output = f"('{parts[0]}', '{parts[1]}', '{parts[2]}', '{parts[3]}'),"
                results.append(formatted_output)

    return results

# 각 채널에서 메시지 스크래핑
all_results = []
for channel in channels:
    print(f'Scraping channel: {channel}')
    all_results.extend(scrape_channel(channel))

# 결과를 파일에 저장
with open(output_file, 'w') as f:
    for result in all_results:
        f.write(result + '\n')

print(f"Scraped data saved to {output_file}")

# 클라이언트 종료
client.disconnect()
