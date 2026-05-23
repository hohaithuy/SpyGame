# 🕵️ Spy Game (Ai Là Gián Điệp?) - Web Host & AI Word Generator

Một ứng dụng web hosting cao cấp, responsive, mượt mà dành cho trò chơi board game phổ biến **"Ai là Gián Điệp"** (Who is the Spy). Trò chơi được tối ưu hóa để chơi trên một thiết bị di động duy nhất (điện thoại hoặc máy tính bảng) truyền tay nhau giữa các người chơi.

Dự án đi kèm một script Python tích hợp gọi API **MiniMax** để tự động tạo cơ sở dữ liệu các cặp từ tiếng Việt 2 âm tiết đa dạng và cực kỳ chất lượng.

👉 **Chơi ngay tại bản Live (GitHub Pages)**: [https://hohaithuy.github.io/SpyGame/](https://hohaithuy.github.io/SpyGame/)

---

## 🌟 Các tính năng nổi bật

### 📱 1. Web Host cao cấp (Single-Device Passing)
*   **Giao diện Midnight sang trọng**: Lớp nền mờ kính (Glassmorphic) sang xịn mịn, hỗ trợ hoàn hảo hiển thị từ màn hình điện thoại (iPhone SE đến Pro Max), máy tính bảng (iPad) cho tới máy tính cá nhân.
*   **Thẻ 3D Reveal chân thực**: Lật mở vai trò bí mật bằng hiệu ứng 3D xoay Y mượt mà, giúp bảo mật thông tin tối đa khi truyền tay máy cho người chơi tiếp theo.
*   **Thuật toán an toàn cho Dân Trắng (3% Blank Rule)**: Khi game có người chơi là Dân Trắng, hệ thống áp dụng tỷ lệ ngẫu nhiên 3% người nói đầu tiên là Dân Trắng (tránh việc Dân Trắng gặp khó khăn do chưa có bất cứ dữ liệu từ nào để mô tả). 97% còn lại lượt nói đầu tiên sẽ là Dân thường hoặc Gián điệp.
*   **Phục hồi & Đồng bộ dữ liệu**: Tự động lưu danh sách tên người chơi vào `localStorage` của trình duyệt để bạn không phải nhập lại mỗi lần tải lại trang. Các vòng chơi sẽ lưu lịch sử từ đã chơi để không bị lặp lại đề bài.
*   **Âm thanh Haptic bằng Web Audio API**: Các nút ấn và thẻ lật phát ra âm thanh sinh động, phản hồi thời gian thực trực tiếp từ trình duyệt mà không cần tải thêm các tệp âm thanh MP3 nặng nề.
*   **Dữ liệu từ dự phòng (Offline Fallback)**: Tích hợp sẵn danh sách hơn 40 nhóm từ tiếng Việt 2 âm tiết chuẩn chỉnh chất lượng cao trong mã nguồn, ứng dụng hoạt động hoàn hảo ngoại tuyến ngay cả khi chưa có tệp cơ sở dữ liệu AI.

### 🤖 2. Trình tạo từ AI (`scripts/generate_words.py`)
*   **Tạo từ thông minh bằng AI**: Sử dụng API MiniMax (`MiniMax-M2.7`) để tạo 30 chủ đề phong phú với quy tắc bắt buộc 2 âm tiết tiếng Việt tự nhiên cho mỗi từ chơi.
*   **Nhật ký trực quan (Progress Log)**: Hiển thị thanh tiến trình %, thời gian chạy, thống kê số lượng nhóm từ và tổ hợp cặp từ khả thi trực tiếp trên terminal.
*   **Chế độ checkpoint thông minh (`data/checkpoint.json`)**: Tự động lưu tiến độ sau mỗi lần gọi API thành công. Nếu bị ngắt kết nối mạng hoặc lỗi giữa chừng, bạn chỉ cần chạy lại script, hệ thống sẽ tự động tải checkpoint và tiếp tục tạo tiếp từ phần bị lỗi mà không bị mất chi phí gọi API từ trước.
*   **Tự động thử lại không giới hạn (Exponential Backoff)**: Tự động phát hiện lỗi timeout/kết nối mạng và thử lại với thời gian chờ tăng dần (3s -> 6s -> 12s -> ... tối đa 60s) cho tới khi hoàn tất.

---

## 🛠️ Hướng dẫn cài đặt & Chạy ứng dụng

### 🚀 1. Chạy Web Host (Trực tiếp)
Không cần cài đặt, không cần build phức tạp. Bạn chỉ cần mở tệp [index.html](index.html) trực tiếp bằng trình duyệt trên điện thoại hoặc máy tính là có thể bắt đầu chơi ngay lập tức!

Nếu bạn muốn tạo một máy chủ web nội bộ trên Mac để người chơi khác cùng kết nối qua mạng Wifi:
```bash
python3 -m http.server 8000
```
Sau đó mở địa chỉ `http://localhost:8000` trên máy tính hoặc `http://<ip-mac-cua-ban>:8000` trên điện thoại của các bạn bè cùng chơi.

---

### 🤖 2. Sử dụng trình tạo từ AI (`generate_words.py`)

#### Bước 1: Thiết lập khóa API bảo mật
1. Tạo một tệp `.env` trong thư mục gốc của dự án (tệp này đã được đưa vào `.gitignore` để tránh bị lộ khóa API lên Git):
```bash
cp .env.example .env
```
2. Mở tệp `.env` và nhập khóa MiniMax API của bạn:
```env
MINIMAX_API_KEY=sk-cp-cua_ban_o_day...
```

#### Bước 2: Chạy Script tạo dữ liệu
Chạy lệnh sau trên terminal của bạn:
```bash
python3 scripts/generate_words.py
```

Sau khi hoàn tất, script sẽ xuất ra tệp dữ liệu sạch [data/words.json](data/words.json) chứa 30 chủ đề từ phong phú để tích hợp thẳng vào ứng dụng web!

---

## 👥 Thứ tự & Quy tắc chơi Spy Game cơ bản

1.  **Nhập tên**: Nhập tên của những người chơi tham gia (mỗi dòng một người).
2.  **Cấu hình vai trò**: Thiết lập số lượng Gián Điệp và Dân Trắng (Mặc định: 1 Gián Điệp, 0 Dân Trắng).
3.  **Lật thẻ bảo mật**: Truyền tay nhau máy, mỗi người chơi ấn vào thẻ bài để lật xem Vai trò & Từ bí mật của mình, sau đó bấm xác nhận để che thẻ đi và chuyển cho người kế tiếp.
    *   **Dân thường**: Nhận được Từ thường (ví dụ: *Bánh mì*).
    *   **Gián điệp**: Nhận được Từ gián điệp - rất giống từ thường (ví dụ: *Bánh bao*).
    *   **Dân trắng**: Không nhận được từ nào cả.
4.  **Vòng mô tả**: Mọi người lần lượt mô tả từ của mình theo **Thứ Tự Nói Chuyện** ngẫu nhiên trên màn hình. Mỗi người chỉ được dùng 1 câu ngắn gọn mô tả gián tiếp từ của mình, tránh nói từ thẳng ra.
5.  **Bỏ phiếu loại**: Sau khi mọi người mô tả xong vòng đầu, cả bàn cùng thảo luận và bỏ phiếu loại bỏ người nghi ngờ là Gián Điệp nhất. Người bị loại sẽ rời trò chơi.
6.  **Kết thúc game**: Ấn nút **"Kết Thúc & Công Bố"** để tiết lộ toàn bộ vai trò và đáp án từ của mỗi người để phân định thắng thua!
    *   **Dân thường thắng**: Nếu tìm ra và loại bỏ tất cả Gián Điệp.
    *   **Gián điệp thắng**: Nếu số lượng Gián điệp còn sống bằng hoặc nhiều hơn số Dân thường còn lại, HOẶC nếu Gián điệp bị loại nhưng đoán đúng từ của Dân thường.
    *   **Dân trắng thắng**: Nếu sống sót đến cuối cùng của lượt chơi.
