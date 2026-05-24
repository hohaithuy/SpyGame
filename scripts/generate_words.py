#!/usr/bin/env python3
"""
One-time script to generate word clusters for Spy Game using MiniMax API.
Run once: python3 scripts/generate_words.py
Output: data/words.json
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

TOKEN = None
URL = "https://api.minimax.io/anthropic"
MODEL = "MiniMax-M2.7"
MIN_WORDS_PER_CLUSTER = 4
MAX_RETRY_FEEDBACK_ITEMS = 20
MAX_GENERATION_ATTEMPTS = 5
VIETNAMESE_LETTERS_PATTERN = re.compile(r"^[A-Za-zÀ-ỹĐđ]+ [A-Za-zÀ-ỹĐđ]+$")


def load_token():
    """Load the MiniMax token only when generation is requested."""
    token = os.environ.get("MINIMAX_API_KEY") or os.environ.get("TOKEN")
    if token:
        return token

    env_path = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )
    if not os.path.exists(env_path):
        return None

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line_clean = line.strip()
                if line_clean and not line_clean.startswith("#") and "=" in line_clean:
                    key, value = line_clean.split("=", 1)
                    if key.strip() in ["MINIMAX_API_KEY", "TOKEN"]:
                        return value.strip().strip('"').strip("'")
    except OSError:
        return None

    return None

# Define all categories with specific prompts for high-quality Vietnamese word clusters
CATEGORIES = [
    {
        "id": "food_vn",
        "name": "Món Việt",
        "icon": "🍜",
        "prompt": "Tạo 8 nhóm từ (cluster) về CHỦ ĐỀ: Món ăn Việt Nam. Mỗi nhóm gồm 5-7 cụm tiếng Việt đúng 2 từ, LIÊN QUAN, CÙNG LOẠI nhưng KHÁC NHAU đủ để mô tả. Ví dụ nhóm 'Nước lèo': [Phở bò, Bún bò, Hủ tiếu, Bún riêu, Mì Quảng, Bún mắm]. Các nhóm: món nước, món cuốn, các loại cơm, các loại bánh mặn, các loại bánh ngọt/chè, món nướng/chiên, đồ ăn vặt, món nếp/cháo.",
    },
    {
        "id": "drinks",
        "name": "Đồ uống",
        "icon": "🥤",
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Đồ uống. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: các loại cà phê, các loại trà, sinh tố, các loại sữa, đồ uống có cồn, nước giải khát, đồ uống thịnh hành (trà sữa, trà đào...).",
    },
    {
        "id": "fruits",
        "name": "Trái cây",
        "icon": "🍎",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Trái cây. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ (ví dụ: xoài cát, thanh long). Các nhóm: trái cây nhiệt đới Việt Nam, quả họ cam, trái cây ôn đới, các loại dưa, quả mọng nước, trái cây mùa hè Việt Nam.",
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
        "prompt": "Tạo 7 nhóm từ về CHỦ ĐỀ: Công nghệ & Cuộc sống số. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt. Các nhóm: thiết bị cá nhân, thiết bị âm thanh, hoạt động nhắn tin, nội dung trực tuyến, phụ kiện điện thoại, mua sắm trực tuyến, bảo mật số. Không dùng tên app hoặc thương hiệu.",
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
        "prompt": "Tạo 9 nhóm từ về CHỦ ĐỀ: Giải trí. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt. Các nhóm: thể loại phim, hoạt động xem phim, trò chơi dân gian, trò chơi bàn, sân khấu, nhạc cụ, thể loại nhạc, chương trình truyền hình, địa điểm vui chơi. Không dùng tên riêng hoặc tiếng Anh.",
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
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Rau củ quả. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: rau lá xanh (cải xanh, rau muống...), củ (khoai tây, cà rốt...), quả dùng nấu ăn (cà chua, bí đỏ...), rau thơm (húng quế, rau mùi...), đậu/hạt (đậu xanh, đậu đỏ...), nấm các loại (nấm rơm, nấm mèo...).",
    },
    {
        "id": "spices",
        "name": "Gia vị & Nước chấm",
        "icon": "🧂",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Gia vị & Nước chấm Việt Nam. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: gia vị khô (tiêu đen, bột ngọt...), nước chấm (nước mắm, tương ớt...), gia vị tạo vị, gia vị ngày Tết.",
    },
    {
        "id": "scenery",
        "name": "Danh thắng",
        "icon": "🏞️",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Danh thắng & Cảnh quan. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt tự nhiên đúng 2 từ. Các nhóm: bãi biển, thác nước, đồi núi, hang động, hồ nước, vườn hoa.",
    },
    {
        "id": "vn_cities",
        "name": "Địa danh Việt Nam",
        "icon": "🇻🇳",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Địa danh Việt Nam. Mỗi nhóm gồm 5-7 địa danh tiếng Việt tự nhiên đúng 2 từ. Các nhóm: thành phố, du lịch biển, vùng cao, miền Tây, di tích. Không dùng địa danh một từ.",
    },
    {
        "id": "holidays",
        "name": "Lễ hội & Ngày lễ",
        "icon": "🎊",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Lễ hội & Ngày lễ. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: ngày lễ Việt Nam, mùa lễ hội, nghi thức truyền thống, sự kiện đời người. Không dùng tên lễ tiếng Anh.",
    },
    {
        "id": "appliances",
        "name": "Đồ gia dụng",
        "icon": "🏠",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Đồ gia dụng & Thiết bị trong nhà. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: thiết bị nấu nướng (nồi cơm, chảo điện...), thiết bị giặt giũ, thiết bị làm mát (quạt trần, quạt đứng...), thiết bị phòng ngủ, thiết bị nhà tắm.",
    },
    {
        "id": "rooms",
        "name": "Phòng & Không gian",
        "icon": "🚪",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Phòng & Không gian sống. Mỗi nhóm gồm 5-7 từ tiếng Việt 2 âm tiết. Các nhóm: phòng trong nhà (phòng ngủ, nhà bếp...), không gian ngoài trời (sân vườn, ban công...), phòng trong trường/công ty (hội trường, căn tin...), phòng trong khách sạn/bệnh viện.",
    },
    {
        "id": "shopping",
        "name": "Mua sắm",
        "icon": "🛍️",
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Mua sắm & Dịch vụ. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt. Các nhóm: khu mua sắm, loại cửa hàng, đồ khuyến mãi, cách thanh toán, dịch vụ giao hàng, trải nghiệm mua hàng. Không dùng tên thương hiệu.",
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
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Vũ trụ & Khoa học. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: thiên thể, dụng cụ quan sát, thí nghiệm, hiện tượng khoa học. Không dùng tên riêng.",
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
        "prompt": "Tạo 6 nhóm từ về CHỦ ĐỀ: Hoạt động hàng ngày. Mỗi nhóm gồm 5-7 cụm động từ tiếng Việt tự nhiên đúng 2 từ. Các nhóm: buổi sáng (đánh răng, rửa mặt...), nấu ăn (xào rau, kho cá...), dọn dẹp (lau nhà, giặt đồ...), giải trí (xem phim, đọc sách...), di chuyển (đi bộ, chạy xe...), giao tiếp (gọi điện, nhắn tin...).",
    },
    {
        "id": "music",
        "name": "Âm nhạc",
        "icon": "🎵",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Âm nhạc. Mỗi nhóm gồm 5-7 cụm tiếng Việt tự nhiên đúng 2 từ. Các nhóm: thể loại nhạc Việt, nhạc cụ dây, nhạc cụ gõ/thổi, hoạt động âm nhạc, sự kiện âm nhạc. Không dùng tên nhạc cụ hoặc thể loại bằng tiếng Anh.",
    },
    {
        "id": "travel",
        "name": "Du lịch",
        "icon": "🧳",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Du lịch. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt đúng 2 từ. Các nhóm: hành lý, đặt phòng, tham quan, trải nghiệm biển, trải nghiệm miền núi.",
    },
    {
        "id": "office",
        "name": "Văn phòng",
        "icon": "🗂️",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Văn phòng & Công việc. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt đúng 2 từ. Các nhóm: bàn làm việc, cuộc họp, giấy tờ, đồng nghiệp, thói quen công sở.",
    },
    {
        "id": "health",
        "name": "Sức khỏe",
        "icon": "🩺",
        "prompt": "Tạo 5 nhóm từ về CHỦ ĐỀ: Sức khỏe & Chăm sóc cơ thể. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt đúng 2 từ. Các nhóm: triệu chứng nhẹ, khám bệnh, thuốc men, tập luyện, nghỉ ngơi.",
    },
    {
        "id": "gardening",
        "name": "Làm vườn",
        "icon": "🪴",
        "prompt": "Tạo 4 nhóm từ về CHỦ ĐỀ: Làm vườn. Mỗi nhóm gồm 5-7 cụm từ tiếng Việt đúng 2 từ. Các nhóm: dụng cụ vườn, loại cây, công việc chăm cây, khu vực trồng cây.",
    },
]

SYSTEM_PROMPT = """Bạn là trợ lý tạo dữ liệu cho trò chơi "Ai là Gián Điệp" (Who is the Spy).

LUẬT CHƠI: Mỗi lượt, app chọn ngẫu nhiên 2 từ từ cùng 1 nhóm (cluster). 1 từ cho dân thường, 1 từ cho gián điệp. Các từ trong cùng nhóm phải:

1. CÙNG LOẠI / CÙNG CHỨC NĂNG (ví dụ: đều là đồ uống nóng, đều là phương tiện 2 bánh)
2. ĐỦ GIỐNG để khi mô tả có thể nhầm lẫn
3. ĐỦ KHÁC để người chơi giỏi có thể phân biệt qua cách mô tả
4. PHỔ BIẾN - người Việt Nam ai cũng biết
5. Dùng tiếng Việt tự nhiên, không dùng tên thương hiệu hoặc từ tiếng Anh

⚠️ QUY TẮC BẮT BUỘC VỀ ĐỘ DÀI TỪ:
- MỖI MỤC TRONG "words" PHẢI ĐÚNG 2 TỪ, đếm bằng `len(value.split()) == 2`.
- Mỗi mục phải là cụm tiếng Việt tự nhiên; không dùng chữ số, ký hiệu, tiếng Anh hoặc tên riêng quốc tế.
- Mỗi cluster phải có ít nhất 4 mục hợp lệ, không trùng nhau.
- ✅ ĐÚNG: "Bánh mì", "Xe máy", "Cà phê", "Trà sữa", "Bóng đá", "Hoa hồng"
- ❌ SAI 1 từ: "Phở", "Bia", "Kem", "Cam", "Nho", "Chuối"
- ❌ SAI 3+ từ: "Cà phê sữa", "Nước hoa quả", "Xe cứu thương", "Bánh tráng trộn"
- Nếu từ phổ biến chỉ có 1 từ, hãy thêm từ bổ nghĩa để thành 2 từ (ví dụ: "Phở" → "Phở bò", "Bia" → "Bia lạnh", "Kem" → "Kem lạnh")
- Một cụm đúng có thể không chứa ký tự mang dấu, ví dụ "Canh chua" hoặc "Thanh long"; tuyệt đối tránh tiếng Anh để user không bị hiểu nhầm.

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


def normalize_phrase(value):
    """Normalize model spacing while keeping visible Vietnamese content unchanged."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())


def phrase_validation_error(value):
    """Return why a phrase is invalid, or None when it is accepted."""
    normalized = normalize_phrase(value)
    if len(normalized.split()) != 2:
        return "không đúng 2 từ"
    if not all(char.isalpha() or char == " " for char in normalized):
        return "chứa ký tự không phải chữ tiếng Việt"
    if not VIETNAMESE_LETTERS_PATTERN.fullmatch(normalized):
        return "chứa ký tự không phải chữ tiếng Việt"
    return None


def expected_cluster_count(category):
    """Read the requested count from the category prompt."""
    match = re.search(r"Tạo\s+(\d+)\s+nhóm", category["prompt"])
    return int(match.group(1)) if match else 1


def clean_generated_cluster(category, cluster_number, clusters, rejection_reasons=None):
    """Return the first valid generated cluster for one requested cluster id."""
    if not isinstance(clusters, list):
        log("    ❌ 'clusters' must be a JSON array")
        if rejection_reasons is not None:
            rejection_reasons.append("Trường 'clusters' không phải là một mảng JSON.")
        return None

    for index, cluster in enumerate(clusters):
        if not isinstance(cluster, dict) or not isinstance(cluster.get("words"), list):
            log(f"    ⚠️  Dropping cluster #{index + 1}: invalid structure")
            if rejection_reasons is not None:
                rejection_reasons.append(
                    f"Nhóm #{index + 1} bị loại vì thiếu mảng 'words' hợp lệ."
                )
            continue

        words = []
        seen = set()
        for value in cluster["words"]:
            normalized = normalize_phrase(value)
            reason = phrase_validation_error(normalized)
            key = normalized.casefold()
            if reason:
                log(f"    ⚠️  Rejecting {value!r}: {reason}")
                if rejection_reasons is not None:
                    rejection_reasons.append(f"Từ {value!r} bị loại: {reason}.")
            elif key in seen:
                log(f"    ⚠️  Rejecting duplicate {normalized!r}")
                if rejection_reasons is not None:
                    rejection_reasons.append(f"Từ {normalized!r} bị loại: bị trùng.")
            else:
                seen.add(key)
                words.append(normalized)

        if len(words) < MIN_WORDS_PER_CLUSTER:
            theme = cluster.get("theme", f"#{index + 1}")
            log(
                f"    ⚠️  Dropping cluster {theme!r}: only {len(words)} valid words "
                f"(need {MIN_WORDS_PER_CLUSTER})"
            )
            if rejection_reasons is not None:
                rejection_reasons.append(
                    f"Nhóm {theme!r} bị loại: chỉ còn {len(words)} từ hợp lệ, "
                    f"cần ít nhất {MIN_WORDS_PER_CLUSTER}."
                )
            continue

        return {
            "id": f"{category['id']}_{cluster_number:02d}",
            "theme": normalize_phrase(cluster.get("theme")) or f"Nhóm {cluster_number}",
            "words": words,
        }

    if rejection_reasons is not None:
        rejection_reasons.append(
            f"Không có dữ liệu hợp lệ cho id {category['id']}_{cluster_number:02d}."
        )
    return None


def clean_checkpoint_clusters(category, clusters):
    """Retain individually valid clusters from a saved topic entry."""
    if not isinstance(clusters, list):
        return []

    expected = expected_cluster_count(category)
    cleaned = []
    used_numbers = set()
    for fallback_number, cluster in enumerate(clusters, start=1):
        match = re.fullmatch(
            rf"{re.escape(category['id'])}_(\d+)",
            str(cluster.get("id", "")) if isinstance(cluster, dict) else "",
        )
        cluster_number = int(match.group(1)) if match else fallback_number
        if cluster_number < 1 or cluster_number > expected or cluster_number in used_numbers:
            continue

        cleaned_cluster = clean_generated_cluster(category, cluster_number, [cluster])
        if cleaned_cluster is not None:
            cleaned.append(cleaned_cluster)
            used_numbers.add(cluster_number)

    return cleaned


def validate_word_data(data, source):
    """Check that every stored phrase follows the runtime generation contract."""
    violations = []
    total_words = 0
    categories = data.get("categories", [])
    if not isinstance(categories, list) or not categories:
        violations.append("file does not contain any generated topics")
        categories = []

    for category in categories:
        clusters = category.get("clusters", [])
        if not isinstance(clusters, list) or not clusters:
            violations.append(f"{category.get('id')}: topic does not contain any clusters")
            continue
        for cluster in clusters:
            words = cluster.get("words", [])
            if len(words) < MIN_WORDS_PER_CLUSTER:
                violations.append(
                    f"{category.get('id')}/{cluster.get('id')}: "
                    f"cluster has fewer than {MIN_WORDS_PER_CLUSTER} words"
                )
            seen = set()
            for value in words:
                total_words += 1
                normalized = normalize_phrase(value)
                reason = phrase_validation_error(normalized)
                if reason:
                    violations.append(
                        f"{category.get('id')}/{cluster.get('id')}: {value!r} ({reason})"
                    )
                elif normalized.casefold() in seen:
                    violations.append(
                        f"{category.get('id')}/{cluster.get('id')}: "
                        f"{normalized!r} (bị trùng)"
                    )
                else:
                    seen.add(normalized.casefold())

    if violations:
        log(f"❌ {source} failed validation: {len(violations)} issue(s)")
        for violation in violations[:30]:
            log(f"    {violation}")
        if len(violations) > 30:
            log(f"    ... and {len(violations) - 30} more")
        return False

    log(f"✅ {source} is valid ({total_words} Vietnamese two-word phrases)")
    return True


def validate_word_file(path):
    """Validate an existing JSON file without calling the generation API."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return validate_word_data(json.load(f), path)
    except OSError as error:
        log(f"❌ Could not read {path}: {error}")
    except json.JSONDecodeError as error:
        log(f"❌ {path} is not valid JSON: {error}")
    return False


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


def call_api(
    category,
    cluster_number,
    total_clusters,
    retry_feedback=None,
    rejection_reasons=None,
):
    """Call MiniMax API for one cluster id within a category."""
    cluster_id = f"{category['id']}_{cluster_number:02d}"
    user_prompt = (
        f"{category['prompt']}\n\n"
        f"Lần gọi này CHỈ tạo đúng 1 cluster cho id \"{cluster_id}\" "
        f"(nhóm {cluster_number}/{total_clusters} của chủ đề). "
        f"Nếu đề bài liệt kê các nhóm gợi ý, dùng nhóm ở vị trí số {cluster_number}. "
        "Trả về mảng \"clusters\" có đúng 1 phần tử.\n"
        "Nhắc lại: mọi mục trong mảng words bắt buộc là cụm tiếng Việt tự nhiên "
        "gồm đúng 2 từ cách nhau bằng khoảng trắng; cụm như \"Canh chua\" là hợp lệ."
    )
    if retry_feedback:
        feedback = "\n".join(
            f"- {reason}" for reason in retry_feedback[:MAX_RETRY_FEEDBACK_ITEMS]
        )
        user_prompt += (
            "\n\nKết quả lần trước bị validator từ chối vì các lỗi sau:\n"
            f"{feedback}\n"
            "Hãy thay các mục lỗi bằng cụm mới hợp lệ; không lặp lại lỗi trên."
        )

    payload = {
        "model": MODEL,
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
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
        return clean_generated_cluster(
            category, cluster_number, parsed.get("clusters", []), rejection_reasons
        )

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


def call_api_with_retry(category, cluster_number, total_clusters):
    """Try generating one cluster id a limited number of times."""
    wait = 3  # initial wait seconds
    retry_feedback = []
    cluster_id = f"{category['id']}_{cluster_number:02d}"

    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
        rejection_reasons = []
        cluster = call_api(
            category,
            cluster_number,
            total_clusters,
            retry_feedback,
            rejection_reasons,
        )

        if cluster is not None:
            return cluster

        if rejection_reasons:
            retry_feedback = rejection_reasons
            log(
                f"    📝 Sending {min(len(retry_feedback), MAX_RETRY_FEEDBACK_ITEMS)} "
                "validation reason(s) to the model on retry"
            )

        if attempt == MAX_GENERATION_ATTEMPTS:
            log(
                f"    ❌ {cluster_id} failed after {MAX_GENERATION_ATTEMPTS} "
                "attempts; continuing with the next id"
            )
            return None

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
        configured = {category["id"]: category for category in CATEGORIES}
        completed = {}
        for cat in data.get("categories", []):
            category = configured.get(cat.get("id"))
            if not category:
                continue

            clusters = clean_checkpoint_clusters(category, cat.get("clusters", []))
            if not clusters:
                log(f"    ⚠️  Checkpoint topic {cat['id']} has no valid clusters; regenerating it")
                continue

            completed[cat["id"]] = {
                "id": category["id"],
                "name": category["name"],
                "icon": category["icon"],
                "clusters": clusters,
            }
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
    parser = argparse.ArgumentParser(description="Generate or validate Spy Game words.")
    parser.add_argument(
        "--validate",
        metavar="PATH",
        help="Validate an existing words JSON file without calling the API.",
    )
    args = parser.parse_args()

    if args.validate:
        return 0 if validate_word_file(args.validate) else 1

    global TOKEN
    TOKEN = load_token()
    if not TOKEN:
        print(
            "[ERROR] MiniMax API Token is missing! Please set MINIMAX_API_KEY "
            "or define it in a .env file.",
            file=sys.stderr,
        )
        return 1

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
    restored = len(completed)
    if restored > 0:
        log(f"⏩ Resuming with valid clusters from {restored} saved topics")
    print(f"{'═' * 60}", flush=True)

    total_clusters = sum(len(c["clusters"]) for c in completed.values())
    total_words = sum(
        sum(len(cl["words"]) for cl in c["clusters"]) for c in completed.values()
    )

    for i, cat in enumerate(CATEGORIES):
        cluster_target = expected_cluster_count(cat)
        existing_entry = completed.get(cat["id"])
        clusters_by_id = {
            cluster["id"]: cluster
            for cluster in (existing_entry or {}).get("clusters", [])
        }
        missing_numbers = [
            number
            for number in range(1, cluster_target + 1)
            if f"{cat['id']}_{number:02d}" not in clusters_by_id
        ]

        if not missing_numbers:
            continue

        print(f"\n{'─' * 60}", flush=True)
        log(f"📂 [{i + 1}/{total_cats}] {cat['icon']}  {cat['name']}")
        log(f"    {progress_bar(i, total_cats)}")
        if clusters_by_id:
            log(
                f"    Keeping {len(clusters_by_id)} valid saved cluster(s); "
                f"generating {len(missing_numbers)} missing id(s)"
            )

        cat_start = time.time()
        for cluster_number in missing_numbers:
            cluster_id = f"{cat['id']}_{cluster_number:02d}"
            log(f"    Generating {cluster_id} ({cluster_number}/{cluster_target})")
            cluster = call_api_with_retry(cat, cluster_number, cluster_target)
            if cluster is not None:
                clusters_by_id[cluster_id] = cluster
                log(f"    Accepted {cluster_id}")

            if cluster_number != missing_numbers[-1]:
                time.sleep(1)

        clusters = [
            clusters_by_id[f"{cat['id']}_{number:02d}"]
            for number in range(1, cluster_target + 1)
            if f"{cat['id']}_{number:02d}" in clusters_by_id
        ]
        if not clusters:
            log(f"    No valid clusters generated for {cat['name']}; skipping topic")
            continue

        # Log results
        n_clusters = len(clusters)
        n_words = sum(len(c["words"]) for c in clusters)

        cat_elapsed = time.time() - cat_start
        log(
            f"    ✅ Kept {n_clusters}/{cluster_target} clusters, "
            f"{n_words} words ({cat_elapsed:.1f}s)"
        )

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

        # Save checkpoint after every attempted topic, including partial successes.
        save_checkpoint(completed)
        log(f"    💾 Checkpoint saved ({len(completed)}/{total_cats})")
        total_clusters = sum(len(c["clusters"]) for c in completed.values())
        total_words = sum(
            sum(len(cluster["words"]) for cluster in c["clusters"])
            for c in completed.values()
        )
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

    if not validate_word_data(output, "generated output"):
        log("❌ Generated output unexpectedly failed validation")
        return 1

    # Write final output only after the complete set has passed validation.
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
