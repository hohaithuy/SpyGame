# 🕵️ Ai Là Gián Điệp? (Spy Game Web Host)

Một ứng dụng web hosting mượt mà, sang trọng dành cho trò chơi board game phổ biến **"Ai là Gián Điệp"** (Who is the Spy). Trò chơi được tối ưu hóa để chơi trên một thiết bị di động duy nhất (điện thoại hoặc máy tính bảng) truyền tay nhau giữa các người chơi.

👉 **CHƠI NGAY TẠI BẢN LIVE (GitHub Pages)**: **[https://hohaithuy.github.io/SpyGame/](https://hohaithuy.github.io/SpyGame/)**

---

## 👥 Hướng dẫn cách chơi (Truyền tay điện thoại)

1.  **Nhập tên**: Nhập tên các người chơi tham gia ở màn hình chính (mỗi dòng một người).
2.  **Thiết lập game**: Chọn số lượng Gián Điệp và Dân Trắng tùy ý (mặc định: 1 Gián Điệp, 0 Dân Trắng).
3.  **Lật thẻ bảo mật**: Lần lượt truyền tay nhau điện thoại. Mỗi người chơi nhấp vào thẻ bài bí mật để xem Vai trò & Từ bí mật của mình, sau đó bấm xác nhận để che thẻ lại rồi truyền máy cho người kế tiếp.
    *   **Dân thường**: Nhận được Từ thường (ví dụ: *Bánh mì*).
    *   **Gián điệp**: Nhận được Từ gián điệp - rất giống từ thường (ví dụ: *Bánh bao*).
    *   **Dân trắng**: Không nhận được từ nào cả (trống trơn).
4.  **Vòng mô tả**: Mọi người lần lượt mô tả từ của mình bằng một câu ngắn gọn, gián tiếp theo **Thứ Tự Nói Chuyện** ngẫu nhiên hiển thị trên màn hình.
5.  **Biện luận & Bỏ phiếu**: Sau khi mô tả xong vòng chơi, cả bàn cùng thảo luận và bỏ phiếu loại bỏ người chơi bị nghi ngờ là Gián Điệp nhất.
6.  **Kết thúc game**: Ấn nút **"Kết Thúc & Công Bố"** để tiết lộ toàn bộ vai trò, đáp án từ của mỗi người chơi và bắt đầu vòng chơi mới!

---

## 🛠️ Trình tạo từ AI (Tùy chọn nâng cao)
Nếu bạn muốn tự tạo tệp cơ sở dữ liệu các cặp từ tiếng Việt mới bằng AI:
1. Sao chép `.env.example` thành `.env` và điền khóa API MiniMax của bạn: `MINIMAX_API_KEY=sk-cp-...`
2. Chạy lệnh:
```bash
python3 scripts/generate_words.py
```
*Tệp dữ liệu từ mới sẽ tự động lưu vào `data/words.json` để tích hợp thẳng vào web game của bạn.*
