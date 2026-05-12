# Hướng Dẫn Kỹ Thuật: Matrix Testing trên GitHub Actions

Tài liệu này giải thích chi tiết cấu hình chiến lược kiểm thử đa chiều (Matrix Testing) đã được triển khai cho dự án, bao gồm các thiết lập kiểm soát luồng thực thi và cách loại trừ các tổ hợp không mong muốn.

---

## 1. Cấu hình Matrix hiện tại

Chiến lược Matrix cho phép chạy cùng một Job `test` song song trên nhiều môi trường khác nhau. Dự án hiện tại kiểm thử chéo với tổng cộng **6 tổ hợp (2 OS × 3 Python versions)**:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.10", "3.11", "3.12"]
  fail-fast: false
```

### Giải thích chi tiết:
- **`os`**: Chạy toàn bộ bộ test trên hai hệ điều hành phổ biến nhất là Linux (`ubuntu-latest`) và macOS (`macos-latest`).
- **`python-version`**: Đảm bảo mã nguồn tương thích hoàn toàn với 3 phiên bản Python đang được hỗ trợ tích cực nhất (3.10, 3.11 và 3.12).
- **`fail-fast: false`**: 
  - **Mặc định (`true`)**: Nếu bất kỳ một tổ hợp nào (ví dụ: `ubuntu-latest` + `Python 3.10`) bị thất bại, GitHub Actions sẽ ngay lập tức hủy toàn bộ các job song song còn lại đang chạy.
  - **Tối ưu hóa (`false`)**: Cho phép tất cả các tổ hợp tiếp tục chạy đến cùng dù có tổ hợp bị lỗi. Điều này giúp bạn có cái nhìn toàn diện (complete visibility) xem code bị lỗi trên những môi trường cụ thể nào mà không phải chạy đi chạy lại nhiều lần.

---

## 2. Khi nào nên sử dụng `exclude`?

Trong thực tế, không phải lúc nào bạn cũng muốn chạy toàn bộ các tổ hợp chéo. Thuộc tính **`exclude`** được sử dụng để **loại bỏ các tổ hợp cụ thể** ra khỏi ma trận kiểm thử.

### Các trường hợp sử dụng điển hình:

**1. Tiết kiệm chi phí CI/CD (Runner Minutes)**
> macOS runner trên GitHub Actions tốn chi phí (số phút sử dụng) cao gấp 10 lần so với Linux runner. Nếu một phiên bản Python cũ (như 3.10) hoạt động ổn định trên Linux và không có logic đặc thù cho OS, bạn có thể bỏ qua nó trên macOS để tiết kiệm tài nguyên.

**2. Thư viện không tương thích**
> Một số thư viện máy học hoặc giao diện đồ họa (GUI) có thể chưa hỗ trợ phiên bản Python mới nhất (ví dụ 3.12) trên một hệ điều hành cụ thể (như Windows hoặc macOS).

### Ví dụ minh họa cấu hình `exclude`:

Giả sử bạn muốn loại bỏ tổ hợp **macOS chạy Python 3.10** ra khỏi luồng CI, bạn cấu hình như sau:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.10", "3.11", "3.12"]
    exclude:
      - os: macos-latest
        python-version: "3.10"
  fail-fast: false
```

Khi áp dụng cấu hình trên, số lượng Job thực tế được kích hoạt sẽ giảm từ **6 xuống còn 5 job**, giúp quy trình CI chạy nhanh hơn và tiết kiệm tài nguyên hệ thống.
