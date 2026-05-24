# 🕵️ Ai Là Gián Điệp? (Spy Game Web Host)

Một ứng dụng web hosting mượt mà, sang trọng dành cho trò chơi board game phổ biến **"Ai là Gián Điệp"** (Who is the Spy). Trò chơi được tối ưu hóa để chơi trên một thiết bị di động duy nhất (điện thoại hoặc máy tính bảng) truyền tay nhau giữa các người chơi.

👉 **CHƠI NGAY TẠI BẢN LIVE (GitHub Pages)**: **[https://hohaithuy.github.io/SpyGame/](https://hohaithuy.github.io/SpyGame/)**

---

## 👥 Hướng dẫn cách chơi (Truyền tay điện thoại)

1.  **Nhập tên**: Nhập tên các người chơi tham gia ở màn hình chính (mỗi dòng một người).
2.  **Thiết lập game**: Mỗi vòng luôn có 1 Gián Điệp. Chọn xác suất xuất hiện tối đa 1 Dân Trắng: `0%`, `20%`, `40%`, `60%`, `80%` hoặc `100%`.
3.  **Lật thẻ bảo mật**: Lần lượt truyền tay nhau điện thoại. Mỗi người chơi nhấp vào thẻ bài bí mật để xem vai trò và thông tin riêng của mình, sau đó bấm xác nhận để che thẻ lại rồi truyền máy cho người kế tiếp.
    *   **Dân thường**: Nhận được Từ thường (ví dụ: *Bánh mì*).
    *   **Gián điệp**: Nhận được Từ gián điệp - rất giống từ thường (ví dụ: *Bánh bao*).
    *   **Dân trắng**: Không nhận được từ. Hãy khiến cả bàn nghi ngờ và bỏ phiếu loại mình.
4.  **Vòng mô tả**: Mọi người lần lượt mô tả từ của mình bằng một câu ngắn gọn, gián tiếp theo **Thứ Tự Nói Chuyện** ngẫu nhiên hiển thị trên màn hình.
5.  **Biện luận & Bỏ phiếu**: Sau khi mô tả xong, cả bàn cùng thảo luận rồi dùng nút **Vote** cạnh người bị loại.
6.  **Tính điểm**:
    *   Vote trúng **Dân Trắng**: Dân Trắng thắng vòng và nhận `+2` điểm.
    *   Vote nhầm **Dân Thường**: Gián Điệp sống sót và nhận `+2` điểm.
    *   Vote trúng **Gián Điệp**: Gián Điệp được đoán từ Dân Thường. Đoán đúng nhận `+1` điểm; đoán sai thì mỗi Dân Thường nhận `+1` điểm.
    *   **Gián Điệp chủ động đoán từ** trước khi bị vote: Đoán đúng nhận `+2` điểm; đoán sai thì mỗi Dân Thường nhận `+1` điểm.
7.  **Công bố**: Sau khi xử lý vote, xem toàn bộ vai trò, icon vai trò và bảng điểm tích lũy trước khi bắt đầu vòng mới.
8.  **Cài đặt giữa trận**: Nhấn nút bánh răng ở góc phải để đổi xác suất Dân Trắng hoặc thêm/xoá người chơi cho vòng kế tiếp. Người đã rời bàn vẫn giữ điểm và tiếp tục hiện trong bảng xếp hạng.
9.  **Khôi phục ván đấu**: Trạng thái ván và bảng điểm được lưu trên trình duyệt của thiết bị. Khi mở lại trang, chọn chơi tiếp ván cũ hoặc bắt đầu game mới.

---

## 🛠️ Trình tạo từ AI (Tùy chọn nâng cao)
Nếu bạn muốn tự tạo tệp cơ sở dữ liệu các cặp từ tiếng Việt mới bằng AI:
1. Sao chép `.env.example` thành `.env` và điền khóa API MiniMax của bạn: `MINIMAX_API_KEY=sk-cp-...`
2. Chạy lệnh:
```bash
python3 scripts/generate_words.py
```
Generator tạo từng nhóm từ riêng biệt trong mỗi chủ đề. Mỗi nhóm được thử tối đa 5 lần; nếu vẫn lỗi, nhóm đó được bỏ qua và generator tiếp tục nhóm kế tiếp, còn các nhóm đã hợp lệ vẫn được giữ. Chỉ các nhóm có tối thiểu 4 cụm đúng 2 từ được ghi; cụm tiếng Việt hợp lệ như `Canh chua` hoặc `Thanh long` không bị loại chỉ vì không có ký tự mang dấu. Để kiểm tra một tệp hiện có mà không gọi API:
```bash
python3 scripts/generate_words.py --validate data/words.json
```
*Tệp dữ liệu từ mới sẽ tự động lưu vào `data/words.json` để tích hợp thẳng vào web game của bạn.*
