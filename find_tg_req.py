with open('support_bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'def tg_request\(.*?\):.*?(?=def |\Z)', text, re.DOTALL)
if matches:
    with open('tg_req_def.txt', 'w', encoding='utf-8') as out:
        out.write(matches[0][:1500])
    print("Found tg_request, written to tg_req_def.txt")
