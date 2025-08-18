import os
import webbrowser
import re
import json
import base64
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = "terminal.html"
HTML_PATH = os.path.join(PROJECT_DIR, HTML_FILE)

_output_lines = []  # প্রাইভেট লিস্ট, ডাটা জমার জন্য
_browser_opened = False  # ট্র্যাক করবে ব্রাউজার ওপেন হয়েছে কিনা

def add_to_terminal(item)-> None:
    """
    🟩 Adds a message, image, map, or data to the terminal output.

    :param item: Can be a string, image path, URL, map location (map:lat,lon), dict, or bytes.
    :return: None
    """
    global _output_lines

    timestamp = datetime.now().strftime("[%I:%M:%S]")

    content = ""

    if isinstance(item, (bytes, bytearray)):
        encoded_str = base64.b64encode(item).decode("utf-8")
        content = f'<img src="data:image/png;base64,{encoded_str}" alt="image" style="max-width:50%;height:auto;">'

    elif isinstance(item, str):
        lower = item.lower()

        # ম্যাপ লোকেশন detect করা (format: map:lat,long)
        if lower.startswith("map:"):
            try:
                coords = lower[4:].strip()
                lat, lon = map(str.strip, coords.split(","))
                content = f'''
<iframe
    src="https://maps.google.com/maps?q={lat},{lon}&z=15&output=embed"
    style="width:100%; height:400px; border:none; border-radius:8px; margin-top:10px;">
</iframe>'''
            except Exception as e:
                content = f"[Invalid map coordinates] {e}"

        # ইমেজ ফাইল detect করা
        elif lower.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg")):
            content = f'<img src="{item}" alt="image" style="max-width:50%;height:auto;">'

        # URL detect করা (http, https, www)
        elif re.match(r"^(https?://|www\.)[^\s]+$", lower):
            url = item if item.startswith("http") else f"https://{item}"
            content = f'<a href="{url}" target="_blank" rel="noopener noreferrer">🔗 Visit: {url}</a>'

        else:
            # সাধারণ টেক্সট
            safe_text = item.replace("<", "&lt;").replace(">", "&gt;")
            content = safe_text




    elif isinstance(item, dict):
        content = json.dumps(item, ensure_ascii=False, indent=2).replace("<", "&lt;").replace(">", "&gt;")

    else:
        content = str(item).replace("<", "&lt;").replace(">", "&gt;")

    # Timestamp সহ ডাটা লাইন হিসেবে যোগ করা
    line = f'<div class="message-line"><span class="timestamp">{timestamp}</span>{content}</div>'
    _output_lines.append(line)

def clear_from_terminal()->None:
    """
    🧹 Clears all previously added terminal messages.

    :param: no parameter
    :return: None
    """
    global _output_lines
    _output_lines = []


def _generate_html():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    output_html = "\n".join(_output_lines)

    pattern = r'(<div class="terminal-output" id="terminal-output">)(.*?)(<span class="cursor"></span>)(.*?</div>)'
    new_html = re.sub(
        pattern,
        lambda m: f'{m.group(1)}{output_html}{m.group(3)}{m.group(4)}',
        html,
        flags=re.DOTALL
    )
    return new_html

def show_terminal()->None:
    """
    📺 Opens (or refreshes) the terminal HTML in browser with current output.

    :param: no parameter
    :return: None
    """
    global _browser_opened
    html_content = _generate_html()
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    if not _browser_opened:
        webbrowser.open(f"file://{HTML_PATH}")
        _browser_opened = True
