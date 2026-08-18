# Bảng đối chiếu — Kế hoạch thực tập → Code

Ánh xạ nguyên văn mọi nhãn trong kế hoạch Web Media 08–09/2026 sang tool của nhóm N3. Chạy `python main.py map` để in bảng này trong terminal.

**Tool không gọi AI, không tốn chi phí.** 6 tiêu chí có bước máy check bằng OpenCV; 16 tiêu chí cần mắt người, chấm tay theo [QC_HUONG_DAN.md](QC_HUONG_DAN.md). Tiêu chí 02 và 06 có cả hai bước.

## II.4 — 20 tiêu chí nhận bản vẽ

| TC | Nội dung | Ai làm | Cột Excel | Hàm xử lý |
|---|---|---|---|---|
| 01 | Đúng nhà Việt Nam | meta + người | `house_type` | `VN_HINT` + `REJECT_PROJECT`, người xác nhận |
| 02 | Mặt bằng công năng 2D | **code** + người | `is_2d_floorplan` | `white_ratio()` + `axis_line_score()` |
| 03 | Thấy rõ tường bao + tường ngăn | người | `dung_cho_REPLAN` | điều kiện (a) |
| 04 | Nhận diện cửa / cửa sổ | người | `dung_cho_REPLAN` | điều kiện (b) |
| 05 | Có nhãn công năng phòng | người | `dung_cho_REPLAN` | điều kiện (c) |
| 06 | Độ nét đủ dùng | **code** + người | `do_net` | `contrast_std` + `MIN_SHORT_EDGE` |
| 07 | Ưu tiên có nội thất | người | `co_noi_that` | ưu tiên, không bắt buộc |
| 08 | Mỗi file = 1 tầng | meta + người | `so_tang_tren_anh` | `ALT_TANG` → hậu tố `_t2` |
| 09 | Góc nhìn vuông góc 2D | **code** | `is_2d_floorplan` | `axis_line_score()` — ảnh nghiêng thì điểm thấp |
| 10 | Khung bao khép kín | người | `co_boundary_ro` | |
| 11 | Lối vào chính nhận diện được | người | `ghi_chu` | sảnh đón / tiền sảnh |
| 12 | Phòng ướt tách được với phòng ở | người | `so_phong_uoc` | quy tắc đếm phòng |
| 13 | Cầu thang / giếng trời / sân trong | người | `house_type` | dấu hiệu phân biệt `ongpho` |
| 14 | Chữ / nhãn đọc được | người | `nhan_phong_ngon_ngu` | nhãn tiếng Anh → loại |
| 15 | Nội thất không che tường | người | `dung_cho_REPLAN` | điều kiện (d) |
| 16 | Không lấy bản kết cấu / điện / nước / PCCC | **code** + meta | `is_2d_floorplan` | `REJECT_TEXT` trên alt/caption |
| 17 | Cạnh ngắn ≥ 800px | **code** | `do_net` | đo sau `crop_drawing_area()` |
| 18 | Contrast đủ tách tường khỏi nền | **code** | `do_net` | `contrast_std` |
| 19 | Không chồng nhiều tầng trên một ảnh | người | `so_tang_tren_anh` | người cắt file `_t1`/`_t2` |
| 20 | GEPLAN: 1 tầng · ≤ 8 phòng | người | `dung_cho_GEPLAN` | `MAX_ROOMS_GEPLAN` |

Sáu tiêu chí có bước máy chạy trước, miễn phí, loại rác hàng loạt. Mười sáu tiêu chí còn lại do người chấm.

## II.4b — Loại ngay

| Mục trong kế hoạch | Chặn bởi |
|---|---|
| Bản ngoại nhập không đúng kiểu VN | người: nhãn tiếng Anh, đơn vị ft/inch |
| Sketch quá rối, chỉ khung thô | `axis_line_score()` thấp + người xác nhận |
| Scan lỗi nặng, thiếu tường | `contrast_std` + người chấm `do_net` |
| Ảnh cắt cụt, watermark che tường/phòng | `gray_center_ratio()` gắn cờ + người soi kỹ |
| Mặt đứng, phối cảnh, mặt cắt đứng | `REJECT_TEXT` + `white_ratio()` |
| Render 3D, isometric, BIM/SketchUp | `white_ratio() < 0.55` + ít đường thẳng trục giao |
| Ảnh chụp giấy méo, bóng đèn, tay che | `axis_line_score()` — đường bị cong/nghiêng |
| Bản điện / nước / kết cấu / PCCC | `REJECT_TEXT` trên alt/caption |
| Trùng layout cùng căn | `phash()` Hamming ≤ 8 + mã dự án |

## II.5 — 10 cột Excel

| Cột | Bắt buộc | Ai điền |
|---|---|---|
| `ten_file` | có | **tool** — `bietthu_001.jpg`, `bietthu_015_t2.jpg` |
| `loai_nha` | có | **tool** — `HOUSE_TYPE = 'bietthu'` cố định |
| `nguon` | có | **tool** — `ctx['project_url']`, thủ công → `thu_cong` |
| `co_noi_that` | có | người |
| `do_net` | có | **tool** điền `dat`/`tam` theo phân giải + contrast, người chấm lại |
| `dung_cho_REPLAN` | có | người — đủ cả 4 điều kiện a–b–c–d (TC 03/04/05/15) |
| `dung_cho_GEPLAN` | có | người — 1 tầng và ≤ 8 phòng (TC 20) |
| `so_phong_uoc` | có | người — chỉ đếm trong khung bao khép kín |
| `co_boundary_ro` | có | người (TC 10) |
| `ghi_chu` | không | **tool** ghi số tầng + cờ + mã dự án; người bổ sung |

Bốn cột phụ ngoài chuẩn nằm bên phải để nhóm tự dùng, xóa trước khi nộp: `_trang_thai`, `_url_nguon`, `_phash`, `_ma_du_an`.

## Mã tiêu chí trong cột ghi_chu

Tool chỉ ghi mã của những tiêu chí **máy đã kết luận được**. Cột người chưa chấm để trống thì không tính là vi phạm — nếu không thì mọi mẫu đều dính đầy mã và cột `ghi_chu` mất tác dụng lọc.

```
bietthu_001   tang 1 · duong_thang=51 · TC:17
bietthu_002   tang 2 · BTV12 · duong_thang=46
ảnh nghi watermark   nghi_watermark_trung_tam · TC:06
```

Cuối tuần 1, lọc cột `ghi_chu` theo mã. Nếu thấy `TC:17` chiếm đa số mẫu `tam` thì đó là vấn đề phân giải — sửa bước tìm bản gốc là cứu được hàng loạt, không phải sửa từng mẫu.

## II.5 — Cổng chất lượng

```
do_net == 'dat' AND (dung_cho_REPLAN == 'dat' OR dung_cho_GEPLAN == 'dat')
```

| Trạng thái | Ai đặt | Cách tính theo kế hoạch |
|---|---|---|
| `dat` | **người**, sau khi điền 5 cột | Được tính vào quota |
| `tam` | tool | Tool đã lọc sạch, đang chờ người chấm |
| `loai` | tool | Không đếm |

Cổng máy nằm trong `assess.gate()` và **không bao giờ trả về `dat`** — nó chỉ tách rác khỏi ứng viên. Việc quyết định một mẫu có dùng được cho HC_REPLAN hay HC_GEPLAN đòi hỏi nhìn tường, nhìn nhãn phòng, đếm phòng; không có cách nào đo bằng code.

## II.3a — 6 yêu cầu chất lượng dữ liệu

| Yêu cầu | Thực thi |
|---|---|
| Đúng kiểu Việt Nam | `VN_HINT` + `REJECT_PROJECT`; người xác nhận |
| Mặt bằng công năng 2D | `white_ratio` + `axis_line_score`; người xác nhận |
| Đủ công năng | người chấm REPLAN a–b–c + `co_boundary_ro` |
| Độ nét dùng được | `MIN_SHORT_EDGE` / `contrast_std` / watermark |
| Duy nhất | `phash` + `DedupIndex.seen_code` |
| Dùng được cho 2 thuật toán | người chấm `dung_cho_REPLAN` + `dung_cho_GEPLAN` |

## II.7 — Mốc lũy kế `bietthu`

`report` in tiến độ theo đúng mốc trong kế hoạch: ngày 1–3 → 900, ngày 4–5 → 1.500, ngày 6–8 → 2.250, ngày 9 → 2.700, cuối tuần 2 → 3.000, tỷ lệ đạt ≥ 90%.

Con số này đếm cột `_trang_thai = dat` trong Excel, tức là đếm công chấm tay chứ không phải công crawl. Crawl 3.000 ảnh mất khoảng một ngày; chấm 3.000 ảnh mới là phần chiếm lịch.

## Điểm cần nhớ về TC 20

Biệt thự thường 10–14 phòng nên phần lớn mẫu sẽ có `dung_cho_GEPLAN = loai`. **Đây không phải lý do loại mẫu** — cổng chất lượng chỉ cần một trong hai thuật toán đạt. Trục chính của N3 là REPLAN. Nếu ai đó sửa code thành loại bỏ mẫu vượt 8 phòng, nhóm sẽ mất khoảng 80% dataset.
