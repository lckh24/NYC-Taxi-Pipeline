# NYC Taxi Pipeline - Implementation Plan

Tài liệu này lưu trữ kế hoạch triển khai chi tiết cho toàn bộ các module trong dự án. Các module tiếp theo sẽ được bổ sung (append) liên tục vào file này.

---

# Module 1: Ingestion (Data Download)

Tài liệu này tổng hợp toàn bộ các quyết định thiết kế đã thống nhất trong phiên phỏng vấn (/grill-me) và phác thảo các bước triển khai cụ thể cho module tải dữ liệu (`ingestion/download.py`).

---

## 1. Tóm tắt các quyết định thiết kế (Agreed Design Decisions)

| Hạng mục | Quyết định đã thống nhất | Lợi ích trong Data Engineering |
| :--- | :--- | :--- |
| **Phạm vi dữ liệu** | 3 tháng đầu năm 2024 (`2024-01`, `2024-02`, `2024-03`) + `taxi_zone_lookup.csv` | Đủ lớn để test hiệu năng (~10 triệu dòng, ~150MB), không gây nghẽn mạng/ổ cứng khi dev |
| **Giao diện thực thi** | Chạy đơn giản: `python -m ingestion.download` | Dễ dàng tích hợp vào Airflow / Script runner sau này |
| **Idempotency** | Tự động kiểm tra: nếu file đã tồn tại và hợp lệ thì bỏ qua (skip) | Tiết kiệm băng thông, an toàn khi chạy lại nhiều lần (re-run) |
| **Atomic Download** | Tải vào file tạm (`.tmp`), tải thành công 100% mới đổi tên sang file chính | Tránh tình trạng file tải dở bị lỗi mạng làm hỏng pipeline downstream |
| **Giao diện tiến trình** | Dùng `tqdm` kết hợp streaming `requests` | Hiển thị tiến trình trực quan (% hoàn thành, tốc độ MB/s, thời gian còn lại) |
| **Kiểm tra toàn vẹn** | Đọc thử schema/metadata bằng `polars` / `pyarrow` ngay sau khi tải | Phát hiện sớm file hỏng (corrupted) trước khi nạp vào DuckDB |

---

## 2. Các thay đổi dự kiến (Proposed Changes)

### Tầng Dependencies & Config

#### [MODIFY] [requirements.txt](file:///d:/Projects/nyc-taxi-pipeline/requirements.txt)
* Thêm thư viện `tqdm>=4.66.0` để hỗ trợ hiển thị progress bar khi download.

#### [MODIFY] [ingestion/config.py](file:///d:/Projects/nyc-taxi-pipeline/ingestion/config.py)
* Bổ sung hằng số cấu hình danh sách tháng cần tải (`MONTHS_TO_INGEST = ["2024-01", "2024-02", "2024-03"]`).
* Đảm bảo các thư mục đích (`RAW_DATA_DIR`, `SEED_DIR`) được tạo tự động nếu chưa có.

---

### Tầng Ingestion

#### [NEW] [ingestion/download.py](file:///d:/Projects/nyc-taxi-pipeline/ingestion/download.py)
Xây dựng script chính gồm các hàm chức năng:
1. `download_file_atomic(url, destination_path)`:
   * Kiểm tra nếu file đích đã tồn tại $\rightarrow$ in thông báo bỏ qua (idempotency).
   * Mở stream tải HTTP theo từng chunk (1MB).
   * Sử dụng `tqdm` hiển thị thanh tiến trình tải.
   * Ghi vào `destination_path.with_suffix(".tmp")`.
   * Đổi tên atomic sang `destination_path` khi hoàn thành.
   * Tự động dọn dẹp file `.tmp` nếu có ngoại lệ ngắt mạng.
2. `verify_parquet_integrity(file_path)`:
   * Dùng `polars.scan_parquet(file_path)` hoặc `pyarrow.parquet.ParquetFile(file_path)` để đọc schema và số hàng/metadata, đảm bảo file nguyên vẹn.
3. `verify_csv_integrity(file_path)`:
   * Dùng `polars.read_csv(file_path, n_rows=5)` để đảm bảo file CSV bảng tra cứu hợp lệ.
4. `main()`:
   * Điều phối tải `taxi_zone_lookup.csv` về `data/seed/`.
   * Lần lượt tải các file `yellow_tripdata_2024-0X.parquet` về `data/raw/`.
   * Tiến hành verify toàn bộ dữ liệu.

---

### Cập nhật tài liệu & ngữ cảnh

#### [MODIFY] [context.md](file:///d:/Projects/nyc-taxi-pipeline/context.md)
* Cập nhật quyết định thiết kế và đánh dấu hoàn thành bước Ingestion sau khi thực hiện xong.

---

## 3. Kế hoạch xác minh (Verification Plan)

### Kiểm thử thực tế (Execution & Integrity Test)
1. **Cài đặt thư viện**:
   ```powershell
   .\.venv\Scripts\pip.exe install tqdm
   ```
2. **Chạy script tải dữ liệu**:
   ```powershell
   .\.venv\Scripts\python.exe -m ingestion.download
   ```
3. **Xác minh kết quả**:
   * Kiểm tra thư mục `data/seed/taxi_zone_lookup.csv` có tồn tại và đọc được.
   * Kiểm tra thư mục `data/raw/` có 3 file parquet (`yellow_tripdata_2024-01.parquet`, `02.parquet`, `03.parquet`) với kích thước ~45MB–55MB/file.
   * Chạy lại lệnh lần 2 để kiểm chứng tính chất **Idempotency** (script phải báo file đã tồn tại và không tải lại).
