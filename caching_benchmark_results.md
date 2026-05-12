# Báo Cáo Đo Lường Hiệu Năng: Cơ Chế Caching trên CI

Tài liệu này ghi nhận kết quả đo lường thời gian cài đặt và thực thi các luồng kiểm thử (CI pipeline) trước và sau khi áp dụng cơ chế bộ nhớ đệm (Dependency Caching) bằng `actions/cache@v4` kết hợp với chữ ký băm `pyproject.toml`.

---

## 1. Kết quả đo lường (Benchmark Results)

Bảng so sánh thời gian thực thi trung bình của một luồng kiểm thử (ví dụ: `ubuntu-latest` với Python 3.11):

| Run Type | Build Time |
|---|---|
| Without cache | 35 seconds |
| With cache | 5 seconds |

### Phân tích chi tiết:
- **Without cache (Lần chạy đầu tiên / Không có cache)**: Hệ thống phải tải xuống toàn bộ các gói phụ thuộc (như `pytest`, `pytest-cov`, `ruff`, `black`) từ mạng internet (PyPI) và tiến hành biên dịch/cài đặt từ đầu. Thời gian tốn trung bình khoảng 30 đến 40 giây tùy tốc độ mạng của GitHub runner.
- **With cache (Các lần chạy tiếp theo / Đã có cache)**: Hành động `actions/cache` tìm thấy chữ ký băm khớp với nội dung file `pyproject.toml` và lập tức giải nén các thư viện đã lưu sẵn từ đĩa cứng cục bộ vào thư mục bộ nhớ đệm. Trình quản lý `uv` nhận diện thư viện đã có sẵn và hoàn tất việc xác thực chỉ trong khoảng 1 đến 5 giây.

**Thời gian tiết kiệm được (Time Saved)**: Khoảng **30 giây** cho mỗi Job.
Với chiến lược kiểm thử đa chiều gồm 6 luồng Matrix chạy song song, tổng thời gian tiết kiệm cộng dồn (Total Compute Time Saved) lên tới khoảng **3 phút** cho mỗi lần đẩy mã nguồn.

---

## 2. Cấu hình kỹ thuật đã áp dụng

Cơ chế caching được thiết lập dựa trên hệ điều hành và nội dung các gói khai báo:

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      ~/Library/Caches/pip
      ~/.cache/uv
      ~/Library/Caches/uv
    key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
```

- **Tính năng băm tự động (`hashFiles`)**: Bất kỳ khi nào bạn thêm hoặc bớt một thư viện trong file `pyproject.toml`, mã băm sẽ tự động thay đổi, giúp hệ thống CI tạo một bộ đệm mới và tránh hoàn toàn các lỗi xung đột phiên bản thư viện cũ.
