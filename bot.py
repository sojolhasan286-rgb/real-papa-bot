import asyncio
import os
import json
import uuid
import aiohttp
from aiohttp import web
import edge_tts
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession

# ================= আপনার কনফিগারেশন =================
API_ID = 37955730
API_HASH = "04e2ff804f416307a54eb9ab2931795f"
BOT_TOKEN = "8900620215:AAEABOrr5o5xFMJYMXjkUv_Xoy-V89Ev38k"
SESSION_STRING = "1BVtsOKkBuzAgqgaS2uS3BMSafTSMr6UH67vSqIUgExv8fS_hBPnvE1GrXnC3QNU1JMAqmKGqSUO8SvusFpbeoInEG51E_2Kqk4mBPEAvyUry7K1JpoajAiL8hR0qJufIR6HL_yXYGLdfP7azPd2UmDpm5yuZWZ9cwiGQX1LzWGRaMhwgR1WwiiG6IOHyQG-Wzf7l0VJw7aapbB1lergh7mrF7CCZ6zlVbCklz6PxvaQMHy13Yy1Bw7S2bxZuBAYAem7EN_9TMkJ1dd__1TDmSZLp0pnI8a8He_jh3w_tbEMISHJjMZaOd-6sgEhQLc8nJ6qCixDJx-0fBSJIe4WzviRSN_QMBnk="

# সিগন্যাল API
API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
# =======================================================

CHANNELS_FILE = "channels.json"
CONFIG_FILE = "dialogue_config.json"

DEFAULT_CONFIG = {
    "welcome": "আসসালামু আলাইকুম, সবাই কেমন আছেন? আমি আপনাদের সিগন্যাল এআই। এখন উইনগো ১ মিনিটে সিগন্যাল শুরু হচ্ছে, সবাই রেডি থাকুন।",
    "signal_template": "সবাই উইনগো ১ মিনিটে ট্রেড করুন {signal}-এ! পিরিয়ড নাম্বার {period}। কনফিডেন্স {confidence} পার্সেন্ট! শুভকামনা সবাইকে!",
    "song": "একবার বলি, বারবার বলি, বলি যে লক্ষবার... তুমি আমার প্রিয়তমা, তুমি যে আমার...",
    "win": "পিরিয়ড নাম্বার {period} বিগ উইন! আমাদের সিগন্যাল ডিরেক্ট উইন হয়েছে! অভিনন্দন সবাইকে!",
    "loss": "কোনো সমস্যা নেই বন্ধুরা, নেক্সট সিগন্যালে রিকভারি করে নিবো ইনশাআল্লাহ!"
}

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_channels(data):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ================= ডাটাবেস প্যাটার্ন =================
PATTERN_DB = {
    "SSBSSBSBB": "BIG", "BSBSBBSBS": "SMALL", "BSBSBBBSS": "BIG", "SSSBBBSSS": "SMALL", "SSSBSBBBS": "SMALL",
    "SBSSBSSBB": "BIG", "SBSSBSSBS": "BIG", "SBSBSSSBS": "SMALL", "SBBSBSSBS": "BIG", "BBSBBSSBB": "SMALL",
    "BSBBSBSSS": "BIG", "SBSBBSSBB": "SMALL", "BBBSBSSBS": "BIG", "SBSSBBSBS": "SMALL", "BSSBSSSBS": "SMALL",
    "BBSBSBBSB": "BIG", "SBBSBSSSS": "BIG", "SBSBBBSBB": "SMALL", "BSBBBBSBB": "BIG", "BSBSSBSBB": "SMALL",
    "BBBBBBBBB": "BIG", "BSBSBBSBB": "BIG", "SSSBBBBBB": "BIG", "BSSBBBSBB": "SMALL", "SBBSBBBSB": "SMALL",
    "BSSBBBSBS": "SMALL", "SSBSBBBBS": "SMALL", "SSBBSBBSB": "BIG", "SSBSSBSSS": "SMALL", "SBSBSSBSB": "BIG",
    "BSBBSSSSS": "SMALL", "SSSBBBSBB": "SMALL", "SBSBBSBSS": "SMALL", "SBSSBSSSS": "SMALL", "BBSBBSBBB": "SMALL",
    "SSSSBBSSB": "BIG", "BBSSBSBSS": "BIG", "SSBBBSBSB": "BIG", "SBBBSBBBS": "SMALL", "SBBBBBBSS": "BIG",
    "SBBSSSSSB": "BIG", "SBSBBSBBS": "SMALL", "BBSSSSBSB": "SMALL", "BSSBSBBSB": "SMALL", "BBBBSSBSS": "SMALL",
    "BBBSSBBSB": "BIG", "BSBSSBBBS": "BIG", "SSBBSBSBB": "BIG", "SBBBSBSBS": "SMALL", "BSBBSSBBB": "SMALL",
    "BSSSBSBSB": "SMALL", "BBBBBSBSB": "BIG", "BSSSSSBBS": "BIG", "SSBSBBBSB": "SMALL", "SSSSSBSSB": "SMALL",
    "BSSSSBBBB": "SMALL", "BBBBBBBSB": "BIG", "BSSSBSSSB": "SMALL", "SBBSBSBBB": "SMALL", "SSSBBBBSS": "SMALL",
    "BBBSSBSBB": "BIG", "SSBSBSBBB": "BIG", "BBBBSSSBB": "BIG", "SBSSBBSSB": "SMALL", "BBSSBSBBS": "BIG",
    "SSSBBSBSS": "SMALL", "BBSBBBSSB": "BIG", "BBBBSSBBS": "BIG", "BBBSBBSSS": "BIG", "SBBSBBBBS": "BIG",
    "BBBSSBBBS": "BIG", "BSSBBSSBB": "BIG", "SBBBSBSSB": "BIG", "BSSBBSSBS": "BIG", "SSBBSBBBB": "SMALL",
    "BSBBSBBSS": "BIG", "BBSSBBBBB": "BIG", "SBBSBBBSS": "BIG", "BSBSBSSSB": "SMALL", "SSBBSBSSS": "BIG",
    "SBBSSSBBS": "BIG", "SBSSBBSBB": "SMALL", "BSSBBSSSS": "BIG", "SSSBBSSBB": "SMALL", "BBSSBSSSB": "SMALL",
    "SBSBSBBSS": "BIG", "BSBSSSBBS": "SMALL", "SSBSBSSBS": "SMALL", "BBBSBBBBB": "BIG", "BBBBSBSSB": "BIG",
    "BSSSSBBSB": "BIG", "SSSBBSBBB": "BIG", "BBSBBBSBS": "SMALL", "SBSBBBSSS": "BIG", "SBBSSBSBB": "BIG",
    "BBSSBBSSS": "SMALL", "SBBBSSSBS": "SMALL", "BBBBBBSSB": "BIG", "SBSBBBSBS": "BIG", "BSSBBSBBB": "SMALL",
    "SSBSSSSBB": "SMALL", "BBSBBBBBS": "SMALL", "BSSBSSSSB": "SMALL", "SBBBSSSSS": "BIG", "BSBBBBSBS": "BIG",
    "BSBSSSSBS": "BIG", "BBBSSSSBB": "BIG", "BSBSSBBSS": "BIG", "SSSSBSBSS": "BIG", "SSBBSSBBS": "SMALL",
    "SSBSSSBSB": "BIG", "SSSBSSBSB": "BIG", "SSBBBSSBB": "BIG", "BSSSSBSBS": "SMALL", "SBBSSBBSS": "SMALL",
    "SSSSSSBSB": "BIG", "BSBBSBBBB": "SMALL", "SSSSBSBBS": "BIG", "SSBBSSBSS": "BIG", "BBSBSSBSB": "SMALL",
    "SSBSSBBSB": "BIG", "BBSSSBBSB": "SMALL", "SBBSSBBBS": "SMALL", "SBBBSSBBB": "BIG", "SBSSBSBSB": "BIG",
    "SBSSSSBBS": "BIG", "BBSBBSBSB": "SMALL", "SSSSSBBSS": "SMALL", "BSSSBBBSB": "BIG", "BBBSBSBSS": "BIG",
    "BBBSSSBSS": "BIG", "BSBBBBBBS": "BIG", "BSSBBBBBS": "BIG", "SSBSBBSBS": "SMALL", "BBBBSBSBS": "SMALL",
    "BSSSSBSSB": "BIG", "BSBSBBBSB": "BIG", "BSBBBSSBS": "SMALL", "SSSBBBSSB": "SMALL", "BSSSSSBSB": "SMALL",
    "BSSBBBBSS": "BIG", "SSBSBBSSS": "BIG", "SSBSSBBBS": "BIG", "SBSBBSSBS": "BIG", "BBBSBSSBB": "BIG",
    "BSBSSBSBS": "SMALL", "SSSSBBBBB": "BIG", "BBSSBSSBS": "SMALL", "SBBSBSSSB": "SMALL", "BBBBBSSBB": "BIG",
    "BSBBBSSSS": "SMALL", "SBBSSSBSB": "SMALL", "SSBBBBSBS": "BIG", "BBBSBBSBB": "BIG", "BSBBBBBSB": "BIG",
    "BSSSSSSBS": "BIG", "SSBSBBBBB": "BIG", "SBSBSSSBB": "BIG", "BSBSSBSSS": "BIG", "SBBBSBBSS": "BIG",
    "BSBBSSSSB": "SMALL", "SSSBBBSBS": "SMALL", "SSSBSSBSS": "SMALL", "BSBBBSBBB": "BIG", "BSSSSSSSS": "BIG",
    "BSSBSSSBB": "BIG", "SSSSBBSSS": "BIG", "BBSSSBBSS": "SMALL", "SSBBBBSSB": "BIG", "SBBSSSSSS": "SMALL",
    "SBSBBSBBB": "SMALL", "BBSSBBSBS": "SMALL", "SSSSBBSBS": "SMALL", "BSSBSBBSS": "BIG", "BBBBSSBSB": "BIG",
    "SBBSBBSBS": "BIG", "BBBBSSSBS": "BIG", "BBSSSSSSB": "SMALL", "BBBBBSBBS": "BIG", "BSBSSBBBB": "SMALL",
    "SBBBSBSBB": "BIG", "SSBSBSBBS": "SMALL", "BSSBSBBBS": "BIG", "SBSSSBSBS": "BIG", "BSSSSSBBB": "BIG",
    "SSBSBBBSS": "SMALL", "BBSBSBSBS": "SMALL", "BSBBSSSBS": "SMALL", "SSBBSBSSB": "BIG", "SBSSSSSBS": "SMALL",
    "SSSSSBBSB": "SMALL", "SBBBSSBBS": "BIG", "BBBBBSBSS": "BIG", "SBSBSSSSB": "SMALL", "SSSBBSBSB": "SMALL",
    "SSBBSBSBS": "BIG", "BBSSBSSBB": "BIG", "SBSSBBBSB": "SMALL", "SSBSBSBSS": "SMALL", "BBBSBBSSB": "SMALL",
    "SBBBBBBBS": "SMALL", "SBSBBBBBS": "SMALL", "SBSBSBSBB": "SMALL", "BBSSBBBBS": "BIG", "BSSSSSBSS": "SMALL",
    "SBBBBBSBB": "BIG", "SBBBBSBSS": "SMALL", "BBBSBBSBS": "SMALL", "BBSBSBSSB": "BIG", "SBSBBBBSS": "SMALL",
    "BSSBBSSSB": "SMALL", "BBSSBSBBB": "BIG", "BBBSBSBBS": "BIG", "BSBSBSBSB": "SMALL", "BSBBBSSSB": "SMALL",
    "BSBSSSSSS": "SMALL", "SBBBSBSSS": "SMALL", "BSSSSBBBS": "SMALL", "SSBSBSSBB": "SMALL", "SSSBSBSSB": "BIG",
    "SSSSBSSBS": "SMALL", "SSSBBSBBS": "BIG", "SSBSBSSSB": "BIG", "BSSSSBBSS": "BIG", "SBBSSBSBS": "SMALL",
    "BSBBSBBSB": "SMALL", "BSBBBSBSB": "BIG", "SSSSBSSSS": "SMALL", "BBBBBBSSS": "BIG", "SSSBSBBSS": "SMALL",
    "BBSSSBSBB": "BIG", "SBBSSBSSS": "BIG", "BBSSBSSSS": "SMALL", "BBSSBBSBB": "BIG", "SBBBSSSSB": "BIG",
    "BBSBSBBSS": "BIG", "SBBBBSBBB": "BIG", "BSBSSSSBB": "SMALL", "SSBSBBSBB": "SMALL", "SSBBBSBSS": "BIG",
    "SSBSBSSSS": "BIG", "SBSBSSSSS": "SMALL", "BSBBBBSSS": "BIG", "SSSSBSBBB": "SMALL", "SSBBSSBSB": "SMALL",
    "BBSBSSBSS": "SMALL", "SBBBSBBBB": "SMALL", "SSSSSSSSB": "BIG", "SSBBBSBBS": "SMALL", "SBBSSBBBB": "BIG",
    "SSBBBBBSB": "SMALL", "BBBBSBBSB": "SMALL", "SBSBSBBBS": "SMALL", "SBSSSSBBB": "SMALL", "BBSSSBBBS": "BIG",
    "SSSBSBSBS": "SMALL", "BBSBSSBBB": "BIG", "BBBSBSBSB": "SMALL", "SSBBBSSSS": "BIG", "SBBBBSSBS": "SMALL",
    "BSBBBBBBB": "SMALL", "BBSBSSSBB": "SMALL", "BSSSSBSSS": "SMALL", "SBSBBSSSS": "SMALL", "SBBBSSBSB": "SMALL",
    "BBBSBBBSS": "BIG", "BSSBBBBSB": "BIG", "SBSBBSBSB": "BIG", "SSBSBBSSB": "BIG", "BSBSBBSSB": "BIG",
    "BSBBSSBSB": "BIG", "SBSBBBBBB": "SMALL", "SBBSBBSBB": "SMALL", "SSSSBBBBS": "BIG", "SBSSSSBSS": "BIG",
    "SSBBBBBBB": "BIG", "BBBBBSSBS": "BIG", "SBSBBSSSB": "BIG", "SBBSBSBSB": "BIG", "SSSSBBBSS": "SMALL",
    "BSBBBBBSS": "BIG", "SBSSSBBBS": "BIG", "BBSSSSBBB": "SMALL", "SBBSSSBSS": "BIG", "BSBSSBSSB": "BIG",
    "SBBBSBBSB": "SMALL", "BSSBSBSSS": "BIG", "SBBSSSSBB": "BIG", "SBSSSBBSS": "BIG", "BSSSSSSSB": "SMALL",
    "BSSSBSBBB": "BIG", "SSBBBBSSS": "SMALL", "BSBBBSBSS": "SMALL", "SSSSBBSBB": "BIG", "BBSSSSSSS": "BIG",
    "BBBBBSBBB": "BIG", "SBBSBBBBB": "BIG", "BBBBSSSSB": "SMALL", "SSSBSSSSS": "BIG", "BSSBSBBBB": "SMALL",
    "SBSSSBSBB": "BIG", "SBSBSSBBB": "SMALL", "BBSSSSSBS": "SMALL", "SBBBBBSSS": "SMALL", "SBBSBSBBS": "BIG",
    "BBSBSBSBB": "SMALL", "BBBBBSSSS": "BIG", "BBBSSBSBS": "SMALL", "BSBBBSSBB": "SMALL", "SSBBBBSBB": "BIG",
    "BBBSSSBBS": "SMALL", "BSSBSBSBB": "BIG", "BSSSBSSBS": "SMALL", "SSBBSBBSS": "SMALL", "BSBSBSSBB": "SMALL",
    "SSSSSBBBS": "SMALL", "SSSBSSBBB": "SMALL", "SSBSBSBSB": "SMALL", "SSBSSSBBS": "BIG", "SBBBBBBBB": "SMALL",
    "SBSBSBBSB": "SMALL", "SSSBSSSBB": "BIG", "SBSSBBBBS": "SMALL", "SBSSBSBBS": "BIG", "SBSSBSSSB": "BIG",
    "SBSBSBSBS": "BIG", "BBBBBBBBS": "SMALL", "SBSBBBBSB": "BIG", "SBBSBBSSB": "SMALL", "BBBSSBSSB": "SMALL",
    "BBSSBBBSB": "SMALL", "SSSSSBBBB": "BIG", "BSSBBSBSB": "SMALL", "BBBBBBBSS": "BIG", "BSBSSSBSB": "BIG",
    "BSSBBBSSS": "BIG", "BSBSBSBBS": "BIG", "BSSBSSBSS": "BIG", "BSBBSBSBB": "SMALL", "SSBBBSSBS": "SMALL",
    "BBBBBBSBS": "SMALL", "BSBSBSSBS": "BIG", "SSSBBSSSB": "BIG", "SSSSBSSSB": "SMALL", "BSSBSBSBS": "SMALL",
    "SSSSSSBBB": "SMALL", "BBSSSBSBS": "SMALL", "SBBSSBSSB": "SMALL", "BBSBBSSSB": "BIG", "BSSSBBBSS": "SMALL",
    "SBBBBBSBS": "SMALL", "SBSBSBSSS": "SMALL", "BBBBBBSBB": "BIG", "SBSSSSSSB": "BIG", "SSSSBSBSB": "BIG",
    "BBSSSBSSS": "SMALL", "SBSSBSBBB": "BIG", "BSSSBBSBS": "BIG", "SSSSSSBSS": "BIG", "BBSBSBSSS": "SMALL",
    "BBBSSSSSS": "SMALL", "BSBBBBSSB": "SMALL", "BBBSBSSSS": "BIG", "BSSSBBSSS": "BIG", "SSSSSSSSS": "BIG",
    "SSBBBSBBB": "BIG", "BSBBSBSSB": "SMALL", "SSBBSSSSB": "BIG", "BBBBSBBSS": "SMALL", "SBSBSBBBB": "BIG",
    "BBSBBSBBS": "SMALL", "BSSSSSSBB": "SMALL", "BSBSBBBBB": "BIG", "SSSSSSSBS": "BIG", "BBSSSBBBB": "SMALL",
    "SSBBSSSBB": "BIG", "SSSBSBSBB": "BIG", "BBSSBBBSS": "SMALL", "BBBBSBBBS": "BIG", "SSBSSBSBS": "SMALL",
    "BBBSSSBBB": "SMALL", "SSSBBBBSB": "BIG", "SSSBSBBBB": "BIG", "BBSBSSSBS": "SMALL", "BSSSBBBBB": "SMALL",
    "SBBSBSSBB": "SMALL", "BBSBBSSBS": "BIG", "BSBSBBSSS": "BIG", "BSSSBBSBB": "BIG", "BSSBBBSSB": "SMALL",
    "SBBBBBBSB": "SMALL", "BSBBSSSBB": "BIG", "SSSBBBBBS": "SMALL", "SSSBSBSSS": "SMALL", "SBSSBBBSS": "BIG",
    "SSBSSBSSB": "SMALL", "SBBBBSSSS": "BIG", "BBBSBSSSB": "SMALL", "SSBBBBBSS": "SMALL", "BBSBSSSSS": "BIG",
    "BBSSSSBBS": "SMALL", "BBBBBSSSB": "SMALL", "BSBBSSBSS": "SMALL", "BBSSBSBSB": "SMALL", "BBBBSSBBB": "SMALL",
    "SBSBSSBSS": "SMALL", "BSSBSBSSB": "SMALL", "BSSBSSBBB": "BIG", "SBSSSBBSB": "SMALL", "BSBSSBBSB": "SMALL",
    "BBSSSSBSS": "SMALL", "BSSSBSBBS": "SMALL", "BBBSSBBSS": "BIG", "SSSSSBSBS": "SMALL", "BSSSSBSBB": "SMALL",
    "SSBBBBBBS": "SMALL", "BSBBSSBBS": "SMALL", "BSSSBSBSS": "SMALL", "SSBSSSSBS": "BIG", "SSSSSBSSS": "BIG",
    "SBSSSBSSB": "SMALL", "BBBBSSSSS": "SMALL", "SSSBSSSSB": "SMALL", "SSBSSSSSS": "BIG", "SBBBBBSSB": "SMALL",
    "SBBSSSBBB": "SMALL", "SBSSBBSSS": "SMALL", "SSSBSSBBS": "SMALL", "SBSSSSSSS": "BIG", "BBSBBBSSS": "BIG",
    "BBSBSBBBS": "BIG", "BSSSBSSBB": "SMALL", "BSBSSSBBB": "BIG", "BBSBSSBBS": "BIG", "BBBSSBBBB": "SMALL",
    "BSBBBSBBS": "BIG", "SBSSSSSBB": "BIG", "BBSSSSSBB": "BIG", "SBBSBSBSS": "SMALL", "SSBBSBBBS": "SMALL",
    "SBSBSSBBS": "SMALL", "SBBSSSSBS": "SMALL", "SSBSSSBBB": "BIG", "BSBSBSSSS": "BIG", "SSSBSSSBS": "BIG",
    "SBSSBBBBB": "BIG", "BSSBSSBBS": "SMALL", "SBBSSBBSB": "BIG", "SSSBBSSBS": "SMALL", "BBSBBBBBB": "BIG",
    "SSBSSBBBB": "SMALL", "SSSSBBBSB": "SMALL", "SBBBBSBBS": "BIG", "BBBSBBBBS": "BIG", "SBBSBBSSS": "BIG",
    "BBBSSBSSS": "SMALL", "BBSBSSSSB": "SMALL", "BBSBBBSBB": "BIG", "SBSBBBSSB": "BIG", "BSSBBSBSS": "BIG",
    "BSSSBSSSS": "BIG", "BBSSBBSSB": "SMALL", "SBBBSSSBB": "BIG", "BSBSBSBBB": "BIG", "BSSBSSBSB": "BIG",
    "BSBSBSBSS": "SMALL", "BSBSSSSSB": "BIG", "BSSBBSBBS": "BIG", "SBBBBSSBB": "SMALL", "SSBSSSBSS": "SMALL",
    "SSSSSSBBS": "BIG", "SSBBBSSSB": "BIG", "BSBBSBSBS": "SMALL", "SSBBSSBBB": "BIG", "BBSBBBBSS": "SMALL",
    "SBSBSBSSB": "BIG", "BBBSSSBSB": "BIG", "BBBSBBBSB": "SMALL", "BBSSSBSSB": "SMALL", "SSSSSBSBB": "SMALL",
    "SSSBSBBSB": "SMALL", "BBSBSBBBB": "BIG", "BBBBSBSSS": "SMALL", "SBSSSSBSB": "BIG", "SSBSSBBSS": "SMALL",
    "BBBSSSSSB": "BIG", "SSSBBSSSS": "BIG", "BBBSBSBBB": "BIG", "SBSSBSBSS": "SMALL", "BSSSBBSSB": "SMALL",
    "BBSBBSBSS": "SMALL", "BBSBBSSSS": "BIG", "SSBBSSSSS": "SMALL", "SSSSBSSBB": "SMALL", "SBBBBSSSB": "BIG",
    "BSBSBBBBS": "SMALL", "SSSSSSSBB": "BIG", "BBBSSSSBS": "SMALL", "BSSBBBBBB": "SMALL", "SSBBSSSBS": "SMALL",
    "BBBBSBBBB": "SMALL"
}

def algo_sum3(numbers):
    if len(numbers) < 3: return 'BIG'
    return 'SMALL' if (numbers[0] + numbers[1] + numbers[2]) > 14 else 'BIG'

def algo_cth(numbers):
    if len(numbers) < 2: return 'SMALL'
    calc = (numbers[1] + numbers[0] + 3) % 10
    return 'BIG' if calc >= 5 else 'SMALL'

def algo_joe_gojo(sizes):
    if len(sizes) < 5: return 'BIG'
    streak = 1
    for i in range(1, len(sizes)):
        if sizes[i] == sizes[0]: streak += 1
        else: break
    if streak >= 3:
        return 'SMALL' if sizes[0] == 'BIG' else 'BIG'
    else:
        big_count = sizes[:5].count('BIG')
        return 'BIG' if big_count >= 3 else 'SMALL'

def algo_adtyx(sizes):
    if len(sizes) < 5: return 'BIG'
    r1, r2, r3, r4, r5 = sizes[0], sizes[1], sizes[2], sizes[3], sizes[4]
    if r1 == r2 == r3: pred = r1
    elif r1 == r2: pred = r1
    elif r1 != r2 and r2 != r3 and r3 != r4 and r4 != r5: pred = r1
    else: pred = 'SMALL' if r1 == 'BIG' else 'BIG'

    big_count = sizes[:5].count('BIG')
    if big_count >= 4: pred = 'SMALL'
    elif (5 - big_count) >= 4: pred = 'BIG'
    return pred

def algo_prosperly(sizes, numbers):
    if len(sizes) < 10: return 'SMALL'
    last10_big = sum(1 for n in numbers[:10] if n >= 5)
    is_big_trend = last10_big > 6
    is_small_trend = (10 - last10_big) > 6

    counts = {'BIG': sizes[:3].count('BIG'), 'SMALL': sizes[:3].count('SMALL')}
    pred = 'BIG' if counts['BIG'] > counts['SMALL'] else 'SMALL'

    if is_big_trend and pred == 'SMALL': pred = 'BIG'
    if is_small_trend and pred == 'BIG': pred = 'SMALL'
    return pred

def algo_tamil_vip(numbers):
    if len(numbers) < 10: return 'BIG'
    ma5 = sum(numbers[:5]) / 5.0
    ma10 = sum(numbers[:10]) / 10.0
    momentum = ma5 - ma10
    if momentum > 0.5: return 'BIG'
    if momentum < -0.5: return 'SMALL'
    return 'BIG' if numbers[0] >= 5 else 'SMALL'

def algo_neural_sum(numbers):
    if len(numbers) < 5: return 'SMALL'
    return 'BIG' if (sum(numbers[:5]) % 10) >= 5 else 'SMALL'

def process_ensemble_prediction(history_list):
    if not history_list or len(history_list) < 10:
        return 'BIG', 80

    numbers = [int(item["number"]) for item in history_list]
    sizes = ['BIG' if n >= 5 else 'SMALL' for n in numbers]

    pat_str = "".join(['B' if s == 'BIG' else 'S' for s in reversed(sizes[:9])])
    db_match = PATTERN_DB.get(pat_str, None)

    if db_match:
        return db_match, 99

    models = [
        algo_sum3(numbers),
        algo_cth(numbers),
        algo_joe_gojo(sizes),
        algo_adtyx(sizes),
        algo_prosperly(sizes, numbers),
        algo_tamil_vip(numbers),
        algo_neural_sum(numbers)
    ]

    big_votes = models.count('BIG')
    small_votes = models.count('SMALL')

    final_pred = 'BIG' if big_votes > small_votes else 'SMALL'
    max_votes = max(big_votes, small_votes)
    confidence = int(round((max_votes / 7.0) * 100))

    return final_pred, confidence

# ================= নতুন ও মিষ্টি বাংলাদেশি ফিমেল ভয়েস =================
async def generate_sweet_girl_voice(text, filename=None, pitch="+1Hz", rate="+0%"):
    if not filename:
        filename = f"voice_{uuid.uuid4().hex[:8]}.mp3"
    try:
        comm = edge_tts.Communicate(
            text, voice="bn-BD-NabanitaNeural", rate=rate, pitch=pitch
        )
        await comm.save(filename)
        return filename
    except Exception as e:
        print(f"[TTS Error]: {e}")
        return None

# ================= ক্লায়েন্ট ইনিশিয়ালাইজেশন =================
bot = TelegramClient("bot_session", API_ID, API_HASH)
assistant = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
call_py = PyTgCalls(assistant)

is_running = False
active_chat_id = None
active_chat_title = "None"
last_period = None
current_pred = None
pending_check = False

user_states = {}

async def play_in_live(audio_file_path):
    global call_py, active_chat_id
    if not active_chat_id or not audio_file_path or not os.path.exists(audio_file_path):
        return
    try:
        await call_py.join_group_call(
            int(active_chat_id),
            AudioPiped(audio_file_path)
        )
    except Exception:
        try:
            await call_py.change_stream(
                int(active_chat_id),
                AudioPiped(audio_file_path)
            )
        except Exception as err:
            print(f"[Audio Stream Warning]: {err}")

async def fetch_lottery_history():
    try:
        timeout = aiohttp.ClientTimeout(total=4)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            url = f"{API_URL}?pageNo=1&pageSize=20&t={int(asyncio.get_event_loop().time() * 1000)}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    return data.get("data", {}).get("list", [])
    except Exception as err:
        print(f"[API Fetch Error]: {err}")
    return []

# ================= লাইভ সিগন্যাল লুপ =================
async def wingo_1min_live_engine():
    global last_period, current_pred, pending_check, is_running, active_chat_id
    print(f">> Signal Engine চালু: {active_chat_title} ({active_chat_id})")

    while is_running and active_chat_id:
        try:
            cfg = load_config()
            history = await fetch_lottery_history()

            if history:
                latest = history[0]
                actual_period = str(latest["issueNumber"])
                actual_num = int(latest["number"])
                actual_size = "BIG" if actual_num >= 5 else "SMALL"

                # ১. উইন / লস চেক
                if pending_check and last_period and last_period != actual_period:
                    last_3_digits_prev = last_period[-3:]
                    if current_pred:
                        if current_pred == actual_size:
                            win_speech = cfg.get("win", DEFAULT_CONFIG["win"]).format(
                                period=last_3_digits_prev,
                                number=actual_num
                            )
                            v_file = await generate_sweet_girl_voice(win_speech, "win.mp3", pitch="+2Hz")
                            await play_in_live(v_file)
                            await asyncio.sleep(6)
                        else:
                            loss_speech = cfg.get("loss", DEFAULT_CONFIG["loss"]).format(
                                period=last_3_digits_prev,
                                number=actual_num
                            )
                            v_file = await generate_sweet_girl_voice(loss_speech, "loss.mp3", pitch="+1Hz")
                            await play_in_live(v_file)
                            await asyncio.sleep(5)
                    pending_check = False

                # ২. নতুন সিগন্যাল
                if last_period != actual_period:
                    last_period = actual_period
                    pred_val, confidence = process_ensemble_prediction(history)
                    current_pred = pred_val
                    pending_check = True

                    next_period_full = str(int(actual_period) + 1)
                    last_3_digits = next_period_full[-3:]
                    pred_bangla = "বিগ" if current_pred == "BIG" else "স্মল"

                    signal_speech = cfg.get("signal_template", DEFAULT_CONFIG["signal_template"]).format(
                        signal=pred_bangla,
                        period=last_3_digits,
                        confidence=confidence
                    )

                    print(f"[🚨 Signal] Period: {last_3_digits} | Pred: {current_pred} | Conf: {confidence}%")
                    v_file = await generate_sweet_girl_voice(signal_speech, "signal.mp3", pitch="+2Hz")
                    await play_in_live(v_file)

                    await asyncio.sleep(15)
                    if is_running and pending_check:
                        song_speech = cfg.get("song", DEFAULT_CONFIG["song"])
                        if song_speech.strip():
                            song_file = await generate_sweet_girl_voice(song_speech, "song.mp3", pitch="+2Hz", rate="-2%")
                            await play_in_live(song_file)

        except Exception as e:
            print(f"[Engine Loop Warning]: {e}")

        await asyncio.sleep(2)

# ================= মেনু প্যানেল UI =================
def get_main_menu():
    status = "🟢 রানিং (LIVE ON)" if is_running else "🔴 বন্ধ (OFF)"
    text = (
        "╔════════════════════════╗\n"
        "   👑 **REAL PAPA VIP CONTROL PANEL** 👑\n"
        "╚════════════════════════╝\n\n"
        f"📊 **বট স্ট্যাটাস:** {status}\n"
        f"🎯 **সিলেক্টেড চ্যানেল:** `{active_chat_title}`\n"
        f"🆔 **চ্যানেল আইডি:** `{active_chat_id or 'None'}`\n\n"
        "নিচের বাটনগুলো দিয়ে সহজে বট পরিচালনা করুন:"
    )

    buttons = [
        [
            Button.inline("▶️ স্টার্ট লাইভ সিগন্যাল", b"btn_start_signal"),
            Button.inline("🛑 স্টপ সিগন্যাল", b"btn_stop_signal")
        ],
        [
            Button.inline("📢 লাইভে বার্তা বলুন", b"btn_speak_custom"),
            Button.inline("📝 ডায়লগ এডিটর", b"btn_edit_dialogues")
        ],
        [
            Button.inline("📋 চ্যানেল সিলেক্ট করুন", b"btn_select_channel"),
            Button.inline("➕ নতুন চ্যানেল অ্যাড", b"btn_add_channel")
        ],
        [
            Button.inline("🗑️ চ্যানেল ডিলিট", b"btn_delete_channel"),
            Button.inline("🔄 রিফ্রেশ প্যানেল", b"btn_refresh")
        ]
    ]
    return text, buttons

# ================= ইভেন্ট হ্যান্ডলার =================
@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    text, buttons = get_main_menu()
    await event.respond(text, buttons=buttons)

@bot.on(events.CallbackQuery())
async def callback_handler(event):
    global is_running, active_chat_id, active_chat_title, call_py
    data = event.data.decode("utf-8")
    sender_id = event.sender_id

    if data in ["btn_refresh", "btn_back_main"]:
        text, buttons = get_main_menu()
        await event.edit(text, buttons=buttons)

    elif data == "btn_speak_custom":
        if not is_running or not active_chat_id:
            await event.answer("⚠️ আগে সিগন্যাল চালু করুন!", alert=True)
            return
        user_states[sender_id] = "WAITING_CUSTOM_SPEECH"
        await event.edit(
            "📢 **লাইভে যা বলতে চান বাংলায় লিখে মেসেজ পাঠান:**",
            buttons=[[Button.inline("🔙 মূল মেনু", b"btn_back_main")]]
        )

    elif data == "btn_edit_dialogues":
        cfg = load_config()
        text = (
            "📝 **ডায়লগ এডিটর প্যানেল**\n\n"
            f"1️⃣ **Welcome:** `{cfg.get('welcome')[:35]}...`\n"
            f"2️⃣ **Signal:** `{cfg.get('signal_template')[:35]}...`\n"
            f"3️⃣ **Song:** `{cfg.get('song')[:35]}...`\n"
            f"4️⃣ **Win:** `{cfg.get('win')[:35]}...`\n"
            f"5️⃣ **Loss:** `{cfg.get('loss')[:35]}...`"
        )
        buttons = [
            [Button.inline("✏️ Welcome", b"edit_welcome"), Button.inline("✏️ Signal", b"edit_signal")],
            [Button.inline("✏️ Song", b"edit_song"), Button.inline("✏️ Win", b"edit_win")],
            [Button.inline("✏️ Loss", b"edit_loss"), Button.inline("🔄 রিসেট", b"edit_reset")],
            [Button.inline("🔙 মূল মেনু", b"btn_back_main")]
        ]
        await event.edit(text, buttons=buttons)

    elif data.startswith("edit_"):
        action = data.replace("edit_", "")
        if action == "reset":
            save_config(DEFAULT_CONFIG)
            await event.answer("✅ ডিফল্ট ডায়লগ রিস্টোর হয়েছে!", alert=True)
            text, buttons = get_main_menu()
            await event.edit(text, buttons=buttons)
            return

        user_states[sender_id] = f"SETTING_DIALOGUE_{action.upper()}"
        hint = ""
        if action == "signal":
            hint = "\n⚠️ `{signal}`, `{period}`, `{confidence}` কোডগুলো ব্যবহার করবেন।"
        elif action in ["win", "loss"]:
            hint = "\n⚠️ `{period}` কোডটি ব্যবহার করবেন।"

        await event.edit(
            f"✍️ **নতুন {action.upper()} ডায়লগটি লিখে পাঠান:**{hint}",
            buttons=[[Button.inline("🔙 ব্যাকে যান", b"btn_edit_dialogues")]]
        )

    elif data == "btn_add_channel":
        user_states[sender_id] = "WAITING_CHANNEL_DATA"
        await event.edit(
            "➕ **নতুন চ্যানেল যোগ করার নিয়ম:**\n\n"
            "ফরম্যাট: `নাম | আইডি`\n"
            "উদাহরণ:\n`VIP Group | -1004378457331`",
            buttons=[[Button.inline("🔙 মূল মেনু", b"btn_back_main")]]
        )

    elif data == "btn_select_channel":
        channels = load_channels()
        if not channels:
            await event.edit("❌ কোনো চ্যানেল লিস্ট নেই! আগে চ্যানেল অ্যাড করুন।", buttons=[[Button.inline("🔙 মূল মেনু", b"btn_back_main")]])
            return

        buttons = []
        for name, cid in channels.items():
            mark = "✅ " if str(cid) == str(active_chat_id) else ""
            buttons.append([Button.inline(f"{mark}{name}", f"set_chan_{cid}".encode())])
        buttons.append([Button.inline("🔙 মূল মেনু", b"btn_back_main")])
        await event.edit("🎯 **চ্যানেল সিলেক্ট করুন:**", buttons=buttons)

    elif data.startswith("set_chan_"):
        cid = data.replace("set_chan_", "")
        channels = load_channels()
        for name, c_id in channels.items():
            if str(c_id) == str(cid):
                active_chat_id = str(cid)
                active_chat_title = name
                break
        text, buttons = get_main_menu()
        await event.edit(f"✅ **সিলেক্টেড চ্যানেল:** `{active_chat_title}`", buttons=buttons)

    elif data == "btn_delete_channel":
        channels = load_channels()
        if not channels:
            await event.edit("❌ কোনো চ্যানেল নেই!", buttons=[[Button.inline("🔙 মূল মেনু", b"btn_back_main")]])
            return

        buttons = []
        for name, cid in channels.items():
            buttons.append([Button.inline(f"🗑️ {name}", f"del_chan_{name}".encode())])
        buttons.append([Button.inline("🔙 মূল মেনু", b"btn_back_main")])
        await event.edit("🗑️ **যে চ্যানেলটি মুছতে চান ক্লিক করুন:**", buttons=buttons)

    elif data.startswith("del_chan_"):
        name_to_del = data.replace("del_chan_", "")
        channels = load_channels()
        if name_to_del in channels:
            del channels[name_to_del]
            save_channels(channels)
            if active_chat_title == name_to_del:
                active_chat_id = None
                active_chat_title = "None"
        text, buttons = get_main_menu()
        await event.edit(f"🗑️ `{name_to_del}` রিমুভ করা হয়েছে!", buttons=buttons)

    elif data == "btn_start_signal":
        if not active_chat_id:
            await event.answer("⚠️ আগে চ্যানেল সিলেক্ট করুন!", alert=True)
            return
        if is_running:
            await event.answer("⚠️ সিগন্যাল ইতিমধ্যে চালু আছে!", alert=True)
            return

        is_running = True
        await event.answer("🚀 সিগন্যাল চালু হচ্ছে...", alert=True)
        text, buttons = get_main_menu()
        await event.edit(text, buttons=buttons)

        try:
            cfg = load_config()
            welcome_intro = cfg.get("welcome", DEFAULT_CONFIG["welcome"])
            welcome_audio = await generate_sweet_girl_voice(welcome_intro, "welcome.mp3", pitch="+2Hz")
            await play_in_live(welcome_audio)
        except Exception as e:
            print(f"[Live Start Error]: {e}")

        asyncio.create_task(wingo_1min_live_engine())

    elif data == "btn_stop_signal":
        if not is_running:
            await event.answer("⚠️ সিগন্যাল বন্ধ আছে!", alert=True)
            return

        is_running = False
        try:
            if active_chat_id:
                await call_py.leave_group_call(int(active_chat_id))
        except Exception as e:
            print(f"[Stop Call Error]: {e}")

        await event.answer("🛑 সিগন্যাল বন্ধ করা হয়েছে!", alert=True)
        text, buttons = get_main_menu()
        await event.edit(text, buttons=buttons)

@bot.on(events.NewMessage(func=lambda e: e.is_private and not e.text.startswith("/")))
async def text_handler(event):
    sender_id = event.sender_id
    state = user_states.get(sender_id)

    if not state:
        return

    text = event.text.strip()

    if state == "WAITING_CUSTOM_SPEECH":
        user_states[sender_id] = None
        await event.respond("🎙️ লাইভে বলা হচ্ছে...")
        v_file = await generate_sweet_girl_voice(text, "custom_speech.mp3", pitch="+2Hz")
        await play_in_live(v_file)
        await event.respond("✅ **বার্তা বাজানো হয়েছে!**")
        m_text, buttons = get_main_menu()
        await event.respond(m_text, buttons=buttons)

    elif state == "WAITING_CHANNEL_DATA":
        if "|" in text:
            try:
                parts = text.split("|")
                name = parts[0].strip()
                cid_raw = parts[1].strip()
                cid = int(cid_raw)
                
                channels = load_channels()
                channels[name] = str(cid)
                save_channels(channels)
                
                user_states[sender_id] = None
                await event.respond(f"✅ **চ্যানেল সফলভাবে অ্যাড হয়েছে:**\n🏷️ নাম: `{name}`\n🆔 আইডি: `{cid}`")
                m_text, buttons = get_main_menu()
                await event.respond(m_text, buttons=buttons)
            except ValueError:
                await event.respond("❌ ভুল আইডি ফরম্যাট! চ্যানেল আইডি অবশ্যই নাম্বার হতে হবে (যেমন: `-1004378457331`)।")
        else:
            await event.respond("❌ ফরম্যাট ভুল! নাম এবং আইডির মাঝে `|` চিহ্ন দিন।\nউদাহরণ: `VIP | -1004378457331`")

    elif state.startswith("SETTING_DIALOGUE_"):
        key = state.replace("SETTING_DIALOGUE_", "").lower()
        if key == "signal":
            key = "signal_template"
        cfg = load_config()
        cfg[key] = text
        save_config(cfg)
        user_states[sender_id] = None
        await event.respond(f"✅ **{key.upper()} ডায়লগ সেভ হয়েছে!**")
        m_text, buttons = get_main_menu()
        await event.respond(m_text, buttons=buttons)

# ================= Render Web Server =================
async def keep_alive():
    server = web.Application()
    server.router.add_get("/", lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ================= মেইন ফাংশন =================
async def main():
    await keep_alive()

    # ১. টেলিগ্রাম বট ও অ্যাসিস্ট্যান্ট ক্লায়েন্ট চালু
    await bot.start(bot_token=BOT_TOKEN)
    await assistant.start()
    
    # ২. ভয়েস কল ক্লায়েন্ট শুরু
    try:
        await call_py.start()
    except Exception as e:
        print(f"[PyTgCalls Start Notice]: {e}")
    
    print("==================================================")
    print(" 🎛️ REAL PAPA VIP CONTROLLER ONLINE & READY!")
    print("==================================================")

    # বটকে সার্বক্ষণিক চালু রাখা
    await bot.run_until_disconnected()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
