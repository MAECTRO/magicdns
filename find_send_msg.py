with open('support_bot.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'def send_message\(.*?\):.*?(?=def |\Z)', text, re.DOTALL)
if matches:
    with open('send_msg_def.txt', 'w', encoding='utf-8') as out:
        out.write(matches[0][:1500])
    print("Found send_message, written to send_msg_def.txt")
else:
    print("Not found")
