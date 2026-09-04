import os
import json
import urllib.request

os.makedirs('assets/memes', exist_ok=True)
headers = {'User-Agent': 'Mozilla/5.0'}

req = urllib.request.Request('https://api.imgflip.com/get_memes', headers=headers)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

memes = data['data']['memes']
print(f"Fetched {len(memes)} meme templates from Imgflip API!")

target_memes = [
    'drake_hotline_bling',
    'distracted_boyfriend',
    'two_buttons',
    'change_my_mind',
    'roll_safe_think_about_it',
    'epic_handshake',
    'buff_doge_vs_cheems',
    'disappointed_muhammad_sarim_akhtar',
    'grus_plan',
    'trade_offer',
    'left_exit_12_off_ramp',
    'brain_expanding',
    'unfaithful_boyfriend',
    'running_away_balloon',
    'finding_neverland'
]

count = 0
for m in memes:
    name_slug = m['name'].lower().replace(' ', '_').replace("'", "").replace('/', '_')
    url = m['url']
    
    # Save standard name
    file_path = os.path.join('assets/memes', f"{name_slug}.jpg")
    try:
        r = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(r) as response, open(file_path, 'wb') as f:
            f.write(response.read())
        count += 1
        print(f"Downloaded [{count}]: {name_slug}.jpg")
    except Exception as e:
        print(f"Error saving {name_slug}: {e}")

print(f"Total downloaded memes: {count}")
