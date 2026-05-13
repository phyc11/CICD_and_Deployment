# Building a Complete CI/CD Pipeline with GitHub Actions

**Project Name:** `cicd-pipeline-demo`  
**Repository URL:** [https://github.com/phyc11/CICD_and_Deployment.git](https://github.com/phyc11/CICD_and_Deployment.git)  
**Course:** Basic DevOps Essentials for Developer  
**Estimated Time:** 150 minutes  
**Frameworks:** GitHub Actions, Python 3.11+, Docker, FastAPI, Trivy

---

## Bảng Mục Lục (Table of Contents)
1. [Giới thiệu Dự án](#1-giới-thiệu-dự-án)
2. [Cấu trúc Thư mục](#2-cấu-trúc-thư-mục)
3. [Chi tiết Các Tác Vụ (Tasks Implementation)](#3-chi-tiết-các-tác-vụ-tasks-implementation)
   - [Task 1: Basic CI Workflow](#task-1-create-basic-ci-workflow)
   - [Task 2: Matrix Testing & Tối ưu hóa](#task-2-implement-matrix-testing)
   - [Task 3: Caching & Artifacts](#task-3-add-caching-and-artifacts)
   - [Task 4: Docker Build, Push & Quét Bảo Mật](#task-4-build-and-push-docker-image)
   - [Task 5: Chiến Lược Triển Khai (Deployment Strategy)](#task-5-implement-deployment-strategy)
4. [Kết quả & Minh chứng (Screenshots & Artifacts)](#4-kết-quả--minh-chứng-screenshots--artifacts)

---

## 1. Giới thiệu Dự án
Dự án này xây dựng một hệ thống CI/CD hoàn chỉnh và tự động hóa quy trình phát triển phần mềm bằng **GitHub Actions** cho một ứng dụng web viết bằng **Python (FastAPI)**.

Hệ thống tích hợp đầy đủ các tiêu chuẩn thực hành DevOps hiện đại:
- **Kiểm tra chất lượng mã (Linting & Formatting):** Sử dụng `Ruff` và `Black`.
- **Kiểm thử tự động (Automated Testing):** Sử dụng `pytest` với báo cáo độ phủ mã (Code Coverage).
- **Kiểm thử đa chiều (Matrix Testing):** Kiểm tra chéo trên nhiều hệ điều hành (`ubuntu-latest`, `macos-latest`) và các phiên bản Python (3.10, 3.11, 3.12).
- **Tối ưu hóa hiệu năng (Caching):** Lưu bộ đệm các thư viện phụ thuộc dựa trên băm của `pyproject.toml`.
- **Đóng gói & Phân phối (Containerization):** Tự động xây dựng hình ảnh Docker, gắn thẻ (semantic tagging) và đẩy lên **GitHub Container Registry (ghcr.io)**.
- **Quét lỗ hổng bảo mật (Vulnerability Scanning):** Tích hợp công cụ **Trivy** để rà soát các rủi ro bảo mật trong Docker image.
- **Chiến lược triển khai (Deployment Strategy):** Triển khai tự động lên môi trường `staging` và yêu cầu phê duyệt thủ công (Manual Approval) trước khi triển khai lên môi trường `production` kèm cơ chế kiểm tra sức khỏe (Health Check).

---

## 2. Cấu trúc Thư mục
```text
.
├── .github/
│   └── workflows/
│       ├── ci.yml          # Luồng CI: Lint, Test, Matrix, Caching, Codecov
│       ├── docker.yml      # Luồng Docker: Build, Tag, Scan (Trivy), Push ghcr.io
│       └── deploy.yml      # Luồng Triển khai: Staging (Auto) & Production (Manual Approval)
├── src/
│   ├── __init__.py
│   └── app.py              # Mã nguồn ứng dụng FastAPI
├── tests/
│   └── test_app.py         # Kịch bản kiểm thử pytest
├── screenshot/             # Thư mục chứa hình ảnh minh chứng kết quả
│   ├── coverage.png
│   ├── successful_workflow.png
│   └── test_result.png
├── caching_benchmark_results.md # Báo cáo chi tiết đo lường hiệu năng Caching
├── matrix_testing_guide.md      # Hướng dẫn và giải thích kỹ thuật Matrix Testing
├── deploy.sh               # Kịch bản triển khai tự động & Health check
├── Dockerfile              # Cấu hình tối ưu hóa Docker Multi-stage build
├── pyproject.toml          # Quản lý phụ thuộc và cấu hình công cụ (Ruff, Black, Pytest)
└── README.md               # Tài liệu tổng quan dự án
```

---

## 3. Chi tiết Các Tác Vụ (Tasks Implementation)

### Task 1: Create Basic CI Workflow
- **Vị trí file:** `.github/workflows/ci.yml`
- **Sự kiện kích hoạt (Triggers):** Kích hoạt khi có sự kiện `push` vào các nhánh `main`, `develop` hoặc khi tạo `pull_request` nhắm vào nhánh `main`.
- **Jobs & Phụ thuộc:**
  - **`lint`**: Chạy công cụ kiểm tra chất lượng mã nhanh nhất hiện nay là `Ruff` (`ruff check .`) và kiểm tra định dạng chuẩn với `Black` (`black --check .`).
  - **`test`**: Chỉ được kích hoạt sau khi job `lint` thành công hoàn toàn (`needs: lint`). Thực thi các kịch bản kiểm thử bằng `pytest` với tùy chọn xuất báo cáo bao phủ mã.

### Task 2: Implement Matrix Testing
- **Cấu hình đa chiều (Matrix Strategy):** Job `test` được mở rộng để chạy song song trên 6 môi trường chéo:
  - **Hệ điều hành:** `ubuntu-latest` và `macos-latest`.
  - **Phiên bản Python:** `3.10`, `3.11`, `3.12`.
- **Cơ chế Fail-Fast:** Thiết lập `fail-fast: false` nhằm đảm bảo nếu một tổ hợp môi trường bị lỗi, các luồng kiểm thử trên các môi trường còn lại vẫn tiếp tục thực thi đến cùng. Điều này giúp lập trình viên thu thập đầy đủ thông tin về khả năng tương thích của mã nguồn trên từng nền tảng.
- **Tài liệu hóa & Thuộc tính `exclude`:**
  - Thuộc tính `exclude` được sử dụng để loại bỏ các tổ hợp cụ thể không cần thiết hoặc không tương thích ra khỏi ma trận nhằm tiết kiệm tài nguyên (Runner Minutes).
  - *Ví dụ:* Có thể loại trừ tổ hợp `macos-latest` chạy Python `3.10` nếu môi trường này tốn kém chi phí và không mang lại giá trị kiểm thử bổ theo. Chi tiết xem tại file [matrix_testing_guide.md](./matrix_testing_guide.md).

### Task 3: Add Caching and Artifacts
- **Chiến lược Caching:** Sử dụng `actions/cache@v4` để lưu trữ thư mục bộ đệm của `pip` và `uv`. Khóa cache (Cache Key) được tạo động dựa trên hệ điều hành và hàm băm của file `pyproject.toml` (`${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}`).
- **Quản lý Artifacts:** Sau khi kiểm thử hoàn tất, hệ thống tự động tải lên các tệp kết quả:
  - Báo cáo độ phủ mã: `coverage.xml`
  - Kết quả kiểm thử chuẩn JUnit XML: `test-results.xml`
- **Tích hợp Codecov:** Tự động gửi dữ liệu bao phủ mã đến Codecov thông qua `codecov/codecov-action@v4` để trực quan hóa các chỉ số chất lượng trên bảng điều khiển.
- **Đo lường thời gian tiết kiệm (Caching Benchmark):**

| Run Type | Build Time |
| :--- | :--- |
| **Without cache** (Lần đầu tiên) | ~35 seconds |
| **With cache** (Các lần sau) | ~5 seconds |

> **Kết luận:** Việc áp dụng Caching giúp tiết kiệm trung bình **30 giây** cho mỗi Job. Trên toàn bộ 6 luồng ma trận chạy song song, tổng thời gian xử lý tiết kiệm được lên tới khoảng **3 phút** cho mỗi lần đẩy mã nguồn. Chi tiết đo lường xem tại [caching_benchmark_results.md](./caching_benchmark_results.md).

### Task 4: Build and Push Docker Image
- **Vị trí file:** `.github/workflows/docker.yml`
- **Xây dựng & Đánh thẻ (Tagging):** Tự động đóng gói Docker image khi mã nguồn trên nhánh `main` hoặc `develop` có sự thay đổi. Sử dụng `docker/metadata-action` để tự động gán nhãn tệp với commit SHA (`${{ github.sha }}`) và thẻ `latest`.
- **Xác thực & Lưu trữ:** Tự động đăng nhập và đẩy hình ảnh lên **GitHub Container Registry (ghcr.io)** sử dụng biến mật khẩu an toàn mặc định `${{ secrets.GITHUB_TOKEN }}`.
- **Tối ưu hóa điều kiện kích hoạt (Path Filters):** Cấu hình `paths-ignore` để bỏ qua việc xây dựng Docker image không cần thiết nếu các thay đổi chỉ thuộc về tài liệu (`**.md`, `docs/**`), tệp `.gitignore` hoặc `LICENSE`.
- **Quét lỗ hổng bảo mật (Image Scanning):** Tích hợp công cụ **Trivy** (`aquasecurity/trivy-action`) để rà soát toàn bộ các gói hệ điều hành và thư viện trong image trước khi đẩy lên registry. Nếu phát hiện lỗ hổng mức độ `CRITICAL` hoặc `HIGH`, quy trình có thể cảnh báo kịp thời.

### Task 5: Implement Deployment Strategy
- **Vị trí file:** `.github/workflows/deploy.yml`
- **Phân tách Môi trường Triển khai:**
  - **Môi trường `staging`:** Triển khai tự động (Auto-deploy) ngay khi tệp hình ảnh mới được tạo thành công từ nhánh `develop`.
  - **Môi trường `production`:** Yêu cầu phê duyệt thủ công (**Manual Approval**) thông qua tính năng bảo vệ môi trường (Environment Protection Rules) của GitHub trước khi thực thi lệnh triển khai từ nhánh `main`.
- **Kịch bản Triển khai & Health Check (`deploy.sh`):**
  - Tải về (pull) hình ảnh Docker mới nhất từ `ghcr.io`.
  - Dọn dẹp các container cũ đang chạy và khởi tạo container mới.
  - Thực hiện vòng lặp kiểm tra trạng thái hoạt động (Health Check) liên tục trong 15 giây bằng lệnh `docker inspect` để đảm bảo dịch vụ đã khởi động thành công.
  - Trả về mã lỗi và nhật ký hệ thống (logs) nếu dịch vụ thất bại, hoặc gửi thông báo thành công thông qua tính năng chú thích của GitHub Actions (`::notice`).

---

## 4. Kết quả & Minh chứng (Screenshots & Artifacts)
Các minh chứng về việc chạy thành công toàn bộ hệ thống CI/CD được lưu trữ sẵn trong thư mục `screenshot/`:
- **Giao diện luồng Actions thành công:** [`screenshot/successful_workflow.png`](./screenshot/successful_workflow.png)
- **Báo cáo kết quả kiểm thử (Pytest Results):** [`screenshot/test_result.png`](./screenshot/test_result.png)
- **Báo cáo độ phủ mã (Coverage Report):** [`screenshot/coverage.png`](./screenshot/coverage.png)

---
*Dự án hoàn thành 100% các tiêu chí đánh giá của bài tập CI/CD and Deployment Assignment.*
