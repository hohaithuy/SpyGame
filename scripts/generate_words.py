#!/usr/bin/env python3
"""
One-time script to generate word clusters for Spy Game using MiniMax API.
Run once: python3 scripts/generate_words.py
Output: data/words.json
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

TOKEN = "sk-cp-_9h4LgwYFcjeirroIp0lGx8ktjtGyC_vlShyUkMvCj_qF82khGuzvYiyXKXwgBHTxYZCfSH7UNms5iOO8XUMAXQ6UaTkkD9bp6mLAK56hC3-qBxRNo_39Ys"
URL = "https://api.minimax.io/anthropic"
MODEL = "MiniMax-M2.7"

# Define all categories with specific prompts for high-quality Vietnamese word clusters
CATEGORIES = [
    {
        "id": "food_vn",
        "name": "Món Việt",
        "icon": "🍜",
        "prompt": "Tạo 8 nhóm từ (cluster) về CHỦ ĐỀ: Món ăn Việt Nam. Mỗi nhóm gồm 5-7 từ LIÊN QUAN, CÙNG LOẠI nhưng KHÁC NHAU đủ để mô tả. Ví dụ nhóm 'Nước lèo': [Phở, Bún bò, Hủ tiếu, Bún riêu, Mì Quảng, Bún mắm]. Các nhóm: món nước, món cuốn, các loại cơm, các loại bánh mặn, các loại bánh ngọt/chè, món nướng/chiên, đồ ăn vặt đường phố, các loại xôi/cháo.",
    },
    {
        "id": "drinks",
        "name": "Đồ uống",
        "icon": "🥤",
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Đồ uống. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: các loại cà phê, các loại trà, nước trái cây/sinh tố, các loại sữa, đồ uống có cồn, nước ngọt có ga, đồ uống mới trend (trà sữa, nước ép detox...).",
    },
    {
        "id": "fruits",
        "name": "Trái cây",
        "icon": "🍎",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Trái cây. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: trái cây nhiệt đới Việt Nam, cam/quýt/bưởi, trái cây ôn đới, các loại dưa, các loại berry/mọng nước, trái cây mùa hè Việt Nam.",
    },
    {
        "id": "animals",
        "name": "Động vật",
        "icon": "🐾",
        "prompt": "Tạo 10 nhóm từ về CHỦ ĐỀ: Động vật. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: họ mèo lớn, họ chó/sói, động vật dưới nước, côn trùng, các loại chim, gặm nhấm nhỏ, bò sát, gia súc nuôi, linh trưởng/khỉ, động vật biển.",
    },
    {
        "id": "places",
        "name": "Địa điểm",
        "icon": "🏖️",
        "prompt": "Tạo 9 nhóm từ về CHỦ ĐỀ: Địa điểm. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: nơi học tập, y tế, mua sắm, lưu trú/du lịch, ăn uống, giải trí/vui chơi, cơ quan hành chính, làm đẹp/chăm sóc, tôn giáo/tâm linh.",
    },
    {
        "id": "transport",
        "name": "Phương tiện",
        "icon": "🚗",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Phương tiện giao thông. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: xe đường bộ cá nhân, dịch vụ gọi xe, phương tiện đường dài, đường thủy, xe khẩn cấp/đặc biệt.",
    },
    {
        "id": "objects",
        "name": "Đồ vật",
        "icon": "🔧",
        "prompt": "Tạo 9 nhóm từ về CHỦ ĐỀ: Đồ vật hàng ngày. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: dụng cụ viết, đồ nhà bếp/ăn uống, đồ nằm/ngồi, đồ đội/đeo trên người, đồ tắm rửa, dụng cụ cắt, đồ chiếu sáng, túi/hộp chứa đồ, đồ dọn dẹp nhà cửa.",
    },
    {
        "id": "tech",
        "name": "Công nghệ",
        "icon": "📱",
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Công nghệ & Mạng xã hội. Mỗi nhóm gồm 5-7 từ. Các nhóm: thiết bị cá nhân, thiết bị âm thanh, mạng xã hội, ứng dụng nhắn tin, nền tảng streaming/xem phim, phụ kiện điện thoại, ứng dụng mua sắm online.",
    },
    {
        "id": "professions",
        "name": "Nghề nghiệp",
        "icon": "💼",
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Nghề nghiệp. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: y tế, giáo dục, pháp luật/an ninh, nghệ thuật/biểu diễn, nhà bếp/ẩm thực, xây dựng/kỹ thuật, công nghệ thông tin.",
    },
    {
        "id": "sports",
        "name": "Thể thao",
        "icon": "⚽",
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Thể thao & Vận động. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: môn bóng, môn dùng vợt, thể thao dưới nước, võ thuật/đối kháng, cờ/trí tuệ, hoạt động ngoài trời, thể thao mùa đông/đặc biệt.",
    },
    {
        "id": "entertainment",
        "name": "Giải trí",
        "icon": "🎬",
        "prompt": "Tạo 9 nhóm từ về CHỦ ĐỀ: Giải trí & Văn hóa đại chúng. Mỗi nhóm gồm 5-7 từ. Các nhóm: game mobile phổ biến, game PC, siêu anh hùng Marvel/DC, anime nổi tiếng, boardgame, phim Việt Nam nổi tiếng, phim hoạt hình Disney, nhạc cụ, thể loại nhạc.",
    },
    {
        "id": "people",
        "name": "Con người",
        "icon": "👥",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Con người & Mối quan hệ. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: gia đình ruột thịt, quan hệ xã hội, nhân vật huyền thoại/lịch sử, sinh vật siêu nhiên, người có quyền lực, giai đoạn cuộc đời (em bé, thiếu niên...).",
    },
    {
        "id": "nature",
        "name": "Thiên nhiên",
        "icon": "🌿",
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Thiên nhiên & Thời tiết. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: hiện tượng thời tiết, thiên thể trên trời, các dạng nước tự nhiên, địa hình, các loại hoa, cây cối, thiên tai.",
    },
    {
        "id": "clothing",
        "name": "Thời trang",
        "icon": "👗",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Thời trang & Phụ kiện. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: các loại áo, các loại quần/váy, giày dép, phụ kiện trang sức, loại vải/chất liệu.",
    },
    {
        "id": "school",
        "name": "Trường học",
        "icon": "📚",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Trường học. Mỗi nhóm gồm 5-8 từ tiếng Việt. Các nhóm: môn học, dụng cụ học tập, hoạt động ở trường, con người ở trường, phòng/khu vực trong trường.",
    },
    {
        "id": "emotions",
        "name": "Cảm xúc",
        "icon": "😊",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Cảm xúc & Tính cách. Mỗi nhóm gồm 5-7 từ tiếng Việt. Các nhóm: cảm xúc vui/hạnh phúc, cảm xúc buồn/tiêu cực, cảm xúc sợ hãi/lo lắng, tính cách tích cực, tính cách tiêu cực.",
    },
    {
        "id": "vegetables",
        "name": "Rau củ",
        "icon": "🥬",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Rau củ quả. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: rau lá xanh (cải bó, rau muống...), củ (khoai tây, cà rốt...), quả dùng nấu ăn (cà chua, bí đỏ...), rau thơm/gia vị tươi (húng quế, rau mùi...), đậu/hạt (đậu xanh, đậu đỏ...), nấm các loại (nấm rơm, nấm mèo...).",
    },
    {
        "id": "spices",
        "name": "Gia vị & Nước chấm",
        "icon": "🧂",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Gia vị & Nước chấm Việt Nam. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: gia vị khô (tiêu đen, bột ngọt...), nước chấm/sốt (nước mắm, tương ớt...), đường/muối/dầu, gia vị Tết/đặc biệt.",
    },
    {
        "id": "countries",
        "name": "Quốc gia",
        "icon": "🌍",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Quốc gia trên thế giới. Mỗi nhóm gồm 5-7 tên nước (dùng tên tiếng Việt 2 âm tiết, ví dụ: Nhật Bản, Hàn Quốc, Thái Lan). Các nhóm: Đông Nam Á, Đông Á, châu Âu phổ biến, châu Mỹ, Trung Đông/Nam Á, châu Phi.",
    },
    {
        "id": "vn_cities",
        "name": "Địa danh Việt Nam",
        "icon": "🇻🇳",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Địa danh & Thành phố Việt Nam. Mỗi nhóm gồm 5-7 từ 2 âm tiết. Các nhóm: thành phố lớn (Hà Nội, Đà Nẵng...), địa điểm du lịch biển (Nha Trang, Phú Quốc...), vùng cao/núi (Đà Lạt, Sa Pa...), miền Tây (Cần Thơ, Bến Tre...), di tích/danh lam (Huế, Hội An...).",
    },
    {
        "id": "holidays",
        "name": "Lễ hội & Ngày lễ",
        "icon": "🎊",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Lễ hội & Ngày lễ. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: ngày lễ Việt Nam (Tết nguyên, Giỗ tổ...), ngày lễ quốc tế (Giáng sinh, Valentine...), lễ hội truyền thống VN (Hội chùa, Lễ hội...), sự kiện đời người (Đám cưới, sinh nhật...).",
    },
    {
        "id": "appliances",
        "name": "Đồ gia dụng",
        "icon": "🏠",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Đồ gia dụng & Thiết bị trong nhà. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: thiết bị nhà bếp (nồi cơm, lò vi...), thiết bị giặt/sấy, thiết bị phòng khách (ti vi, quạt trần...), thiết bị phòng ngủ, thiết bị nhà tắm.",
    },
    {
        "id": "rooms",
        "name": "Phòng & Không gian",
        "icon": "🚪",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Phòng & Không gian sống. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: phòng trong nhà (phòng ngủ, nhà bếp...), không gian ngoài trời (sân vườn, ban công...), phòng trong trường/công ty (hội trường, căn tin...), phòng trong khách sạn/bệnh viện.",
    },
    {
        "id": "brands",
        "name": "Thương hiệu",
        "icon": "🏷️",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Thương hiệu phổ biến ở Việt Nam. Mỗi nhóm gồm 5-7 tên thương hiệu (chọn tên 2 âm tiết). Các nhóm: xe máy/ô tô (Honda, Toyota...), thời trang (Nike, Adidas...), đồ ăn nhanh (McDonald, KFC...), điện thoại/laptop (Apple, Samsung...), thương hiệu Việt (Vinamilk, Viettel...), mỹ phẩm/chăm sóc.",
    },
    {
        "id": "colors_shapes",
        "name": "Màu sắc & Hình dạng",
        "icon": "🎨",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Màu sắc & Hình dạng. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: màu nóng (đỏ tươi, cam đất...), màu lạnh (xanh biển, tím than...), hình dạng (hình tròn, hình vuông...), chất liệu bề mặt (bóng loáng, sần sùi...).",
    },
    {
        "id": "space",
        "name": "Vũ trụ & Khoa học",
        "icon": "🚀",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Vũ trụ & Khoa học. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: hành tinh/thiên thể (Sao Hỏa, Mặt Trăng...), phương tiện vũ trụ/khoa học (tên lửa, kính viễn...), nhà khoa học/phát minh nổi tiếng, hiện tượng khoa học (từ trường, trọng lực...).",
    },
    {
        "id": "body",
        "name": "Cơ thể người",
        "icon": "🫀",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Bộ phận cơ thể người. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: bộ phận trên mặt (đôi mắt, cái mũi...), bộ phận tay/chân, nội tạng (trái tim, lá gan...), xương/khớp, tóc/da/móng.",
    },
    {
        "id": "daily_activities",
        "name": "Hoạt động hàng ngày",
        "icon": "🏃",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Hoạt động hàng ngày. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết (động từ/cụm động từ). Các nhóm: buổi sáng (đánh răng, tập thể...), nấu ăn (xào rau, kho cá...), dọn dẹp (lau nhà, giặt đồ...), giải trí (xem phim, đọc sách...), di chuyển (đi bộ, chạy xe...), giao tiếp (gọi điện, nhắn tin...).",
    },
    {
        "id": "music",
        "name": "Âm nhạc",
        "icon": "🎵",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Âm nhạc. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: thể loại nhạc (nhạc pop, nhạc rock...), nhạc cụ dây (đàn tranh, guitar...), nhạc cụ gõ/thổi (trống cơm, sáo trúc...), hoạt động âm nhạc (hát hò, soạn nhạc...), sự kiện âm nhạc (hòa nhạc, lễ hội...).",
    },
]

SYSTEM_PROMPT = """Bạn là trợ lý tạo dữ liệu cho trò chơi "Ai là Gián Điệp" (Who is the Spy).

LUẬT CHƠI: Mỗi lượt, app chọn ngẫu nhiên 2 từ từ cùng 1 nhóm (cluster). 1 từ cho dân thường, 1 từ cho gián điệp. Các từ trong cùng nhóm phải:

1. CÙNG LOẠI / CÙNG CHỨC NĂNG (ví dụ: đều là đồ uống nóng, đều là phương tiện 2 bánh)
2. ĐỦ GIỐNG để khi mô tả có thể nhầm lẫn
3. ĐỦ KHÁC để người chơi giỏi có thể phân biệt qua cách mô tả
4. PHỔ BIẾN - người Việt Nam ai cũng biết
5. Dùng tiếng Việt tự nhiên, có thể dùng tên riêng quốc tế nếu phổ biến

⚠️ QUY TẮC BẮT BUỘC VỀ ĐỘ DÀI TỪ:
- MỖI TỪ PHẢI ĐÚNG 2 ÂM TIẾT (2 từ tiếng Việt), KHÔNG ĐƯỢC 1 từ đơn, KHÔNG ĐƯỢC 3 từ trở lên.
- ✅ ĐÚNG: "Bánh mì", "Xe máy", "Cà phê", "Trà sữa", "Bóng đá", "Hoa hồng"
- ❌ SAI 1 từ: "Phở", "Bia", "Kem", "Cam", "Nho", "Chuối"
- ❌ SAI 3+ từ: "Cà phê sữa", "Nước hoa quả", "Xe cứu thương", "Bánh tráng trộn"
- Nếu từ phổ biến chỉ có 1 âm tiết, hãy thêm từ bổ nghĩa để thành 2 âm tiết (ví dụ: "Phở" → "Phở bò", "Bia" → "Bia lon", "Kem" → "Kem ốc")
- Luôn luôn là từ tiếng việt, tuyệt đối tránh tiếng Anh để user không bị hiểu nhầm.

QUAN TRỌNG: Trả về ĐÚNG định dạng JSON, không thêm text giải thích.

Định dạng trả về:
{
  "clusters": [
    { "id": "xxx_01", "theme": "Tên nhóm ngắn", "words": ["từ 1", "từ 2", "từ 3", "từ 4", "từ 5"] },
    ...
  ]
}"""


def log(msg):
    """Print with timestamp and flush immediately."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


def progress_bar(current, total, width=30):
    """Generate a text progress bar."""
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = current / total * 100
    return f"[{bar}] {pct:.0f}%"


def extract_json(text):
    """Extract and parse a JSON object from text with high robustness."""
    text_clean = text.strip()

    # 1. Try direct parsing
    try:
        return json.loads(text_clean)
    except json.JSONDecodeError:
        pass

    # 2. Try handling common markdown code block variants
    for marker in ["```json", "```JSON", "```"]:
        if marker in text_clean:
            try:
                parts = text_clean.split(marker)
                if len(parts) > 1:
                    candidate = parts[1].split("```")[0].strip()
                    if candidate:
                        return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    # 3. Fallback: Find outermost curly braces to extract raw JSON block
    first_brace = text_clean.find("{")
    last_brace = text_clean.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text_clean[first_brace : last_brace + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # Raise decode error if all parsing attempts fail
    raise json.JSONDecodeError(
        "Could not find or parse any valid JSON object in text", text_clean, 0
    )


def call_api(category):
    """Call MiniMax API for a single category."""
    payload = {
        "model": MODEL,
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": category["prompt"]}],
        "system": SYSTEM_PROMPT,
    }

    headers = {"Content-Type": "application/json", "x-api-key": TOKEN}

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        URL + "/v1/messages", data=data, headers=headers, method="POST"
    )

    # Keep a fallback text variable so error logging always has access to the raw response
    text = ""

    try:
        start = time.time()
        log(f"    📡 Calling API...")
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw_body = resp.read().decode("utf-8")

        try:
            result = json.loads(raw_body)
        except json.JSONDecodeError as e:
            log(f"    ❌ API returned non-JSON HTTP response body: {e}")
            log(f"    Response snippet: {raw_body[:300]}")
            return None

        elapsed = time.time() - start
        log(f"    📥 Response received ({elapsed:.1f}s)")

        # Check for API level error responses
        if "error" in result:
            log(f"    ❌ API Error block in response: {result['error']}")
            return None

        base_resp = result.get("base_resp", {})
        if base_resp and base_resp.get("status_code", 0) != 0:
            log(
                f"    ❌ API base_resp Error ({base_resp.get('status_code')}): {base_resp.get('status_msg')}"
            )
            return None

        # Extract text content from the response content blocks
        content_blocks = result.get("content", [])
        if not content_blocks:
            log(
                f"    ❌ No content blocks in response. Response keys: {list(result.keys())}"
            )
            log(f"    Full result: {json.dumps(result, ensure_ascii=False)[:500]}")
            return None

        for block in content_blocks:
            if block.get("type") == "text":
                text += block["text"]

        if not text.strip():
            log(f"    ❌ Text content blocks are empty. Content: {content_blocks}")
            return None

        # Parse JSON using the robust extraction helper
        parsed = extract_json(text)
        clusters = parsed.get("clusters", [])

        # Fix IDs to use the category prefix
        prefix = category["id"]
        for i, cluster in enumerate(clusters):
            cluster["id"] = f"{prefix}_{i + 1:02d}"

        return clusters

    except urllib.error.HTTPError as e:
        log(f"    ❌ HTTP Error {e.code}: {e.read().decode()[:200]}")
        return None
    except json.JSONDecodeError as e:
        log(f"    ❌ JSON parse error: {e}")
        log(f"    Raw text (first 500 chars): {text[:500]}")
        return None
    except Exception as e:
        log(f"    ❌ Error: {e}")
        return None


def call_api_with_retry(category):
    """Call API with infinite retry and exponential backoff."""
    attempt = 0
    wait = 3  # initial wait seconds

    while True:
        attempt += 1
        clusters = call_api(category)

        if clusters is not None:
            return clusters

        log(f"    ⚠️  Attempt {attempt} failed. Retrying in {wait}s...")
        time.sleep(wait)
        wait = min(wait * 2, 60)  # exponential backoff, cap at 60s


# ─── Checkpoint helpers ─────────────────────────────────────

CHECKPOINT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "checkpoint.json"
)
CHECKPOINT_PATH = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "checkpoint.json"
    )
)


def load_checkpoint():
    """Load checkpoint if exists. Returns dict of category_id -> cat_entry."""
    if not os.path.exists(CHECKPOINT_PATH):
        return {}
    try:
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        completed = {cat["id"]: cat for cat in data.get("categories", [])}
        log(f"💾 Checkpoint loaded: {len(completed)} categories already done")
        for cat_id, cat in completed.items():
            n_c = len(cat["clusters"])
            n_w = sum(len(c["words"]) for c in cat["clusters"])
            log(f"    ⏩ {cat['icon']}  {cat['name']} — {n_c} clusters, {n_w} words")
        return completed
    except Exception as e:
        log(f"⚠️  Could not load checkpoint: {e}")
        return {}


def save_checkpoint(categories_done):
    """Save current progress to checkpoint file."""
    os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
    data = {"categories": list(categories_done.values())}
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def delete_checkpoint():
    """Remove checkpoint file after successful completion."""
    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)
        log(f"🗑️  Checkpoint deleted (all done!)")


# ─── Main ────────────────────────────────────────────────────


def main():
    from math import comb

    start_time = time.time()
    total_cats = len(CATEGORIES)

    log(f"🚀 Starting word generation for Spy Game")
    log(f"📋 Categories to process: {total_cats}")
    log(f"🔗 API: {URL}")
    log(f"🤖 Model: {MODEL}")
    print(f"{'═' * 60}", flush=True)

    # Load checkpoint
    completed = load_checkpoint()
    skipped = len(completed)
    if skipped > 0:
        log(f"⏩ Resuming — skipping {skipped} already completed categories")
    print(f"{'═' * 60}", flush=True)

    total_clusters = sum(len(c["clusters"]) for c in completed.values())
    total_words = sum(
        sum(len(cl["words"]) for cl in c["clusters"]) for c in completed.values()
    )

    for i, cat in enumerate(CATEGORIES):
        # Skip if already in checkpoint
        if cat["id"] in completed:
            continue

        print(f"\n{'─' * 60}", flush=True)
        log(f"📂 [{i + 1}/{total_cats}] {cat['icon']}  {cat['name']}")
        log(f"    {progress_bar(i, total_cats)}")

        cat_start = time.time()
        clusters = call_api_with_retry(cat)

        # Log results
        n_clusters = len(clusters)
        n_words = sum(len(c["words"]) for c in clusters)
        total_clusters += n_clusters
        total_words += n_words

        cat_elapsed = time.time() - cat_start
        log(f"    ✅ {n_clusters} clusters, {n_words} words ({cat_elapsed:.1f}s)")

        for c in clusters:
            words_preview = ", ".join(c["words"][:4])
            extra = f"... +{len(c['words']) - 4}" if len(c["words"]) > 4 else ""
            log(f"       • {c['theme']}: [{words_preview}{extra}]")

        cat_entry = {
            "id": cat["id"],
            "name": cat["name"],
            "icon": cat["icon"],
            "clusters": clusters,
        }
        completed[cat["id"]] = cat_entry

        # Save checkpoint after each category
        save_checkpoint(completed)
        log(f"    💾 Checkpoint saved ({len(completed)}/{total_cats})")
        log(f"    📊 Running total: {total_clusters} clusters, {total_words} words")

        # Small delay to avoid rate limits
        if i < len(CATEGORIES) - 1:
            time.sleep(1)

    # Build final output preserving CATEGORIES order
    output = {
        "version": "2.0",
        "language": "vi",
        "description": "Mỗi cluster chứa 4-8 từ liên quan. App random chọn 2 từ từ cluster — 1 cho dân, 1 cho gián điệp.",
        "categories": [
            completed[cat["id"]] for cat in CATEGORIES if cat["id"] in completed
        ],
    }

    # Write final output
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "data", "words.json"
    )
    output_path = os.path.normpath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Delete checkpoint — all done!
    delete_checkpoint()

    # Final summary
    elapsed_total = time.time() - start_time
    total_combos = sum(
        comb(len(c["words"]), 2)
        for cat in output["categories"]
        for c in cat["clusters"]
    )

    print(f"\n{'═' * 60}", flush=True)
    log(f"🏁 GENERATION COMPLETE")
    print(f"{'═' * 60}", flush=True)
    print(f"", flush=True)
    print(f"  📦 Output file  : {output_path}", flush=True)
    print(
        f"  ⏱️  Total time   : {elapsed_total:.1f}s ({elapsed_total / 60:.1f} min)",
        flush=True,
    )
    print(
        f"  ✅ Succeeded    : {len(output['categories'])}/{total_cats} categories",
        flush=True,
    )
    print(f"  📂 Categories   : {len(output['categories'])}", flush=True)
    print(f"  🗂️  Clusters     : {total_clusters}", flush=True)
    print(f"  📝 Total words  : {total_words}", flush=True)
    print(f"  🎯 Possible pairs: {total_combos}", flush=True)
    print(f"", flush=True)
    print(f"  {'─' * 50}", flush=True)
    print(f"  {'Category':<28} {'Clusters':<10} {'Words':<8} {'Pairs':<8}", flush=True)
    print(f"  {'─' * 50}", flush=True)
    for cat in output["categories"]:
        n_c = len(cat["clusters"])
        n_w = sum(len(c["words"]) for c in cat["clusters"])
        n_p = sum(comb(len(c["words"]), 2) for c in cat["clusters"])
        print(
            f"  {cat['icon']} {cat['name']:<25} {n_c:<10} {n_w:<8} {n_p:<8}", flush=True
        )
    print(f"  {'─' * 50}", flush=True)
    print(
        f"  {'TOTAL':<28} {total_clusters:<10} {total_words:<8} {total_combos:<8}",
        flush=True,
    )
    print(f"\n✅ Done!", flush=True)


if __name__ == "__main__":
    main()
