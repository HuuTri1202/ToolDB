# Hướng dẫn chấm tay — 5 cột tool không tự điền được

Tool đã lọc sạch rác miễn phí và điền sẵn 5 cột. Việc của bạn là mở `output/bietthu_dataset.xlsx`, xem ảnh trong `output/_tam/`, và điền 5 cột còn trống.

| Cột | Tool điền | Bạn điền |
|---|---|---|
| `ten_file` `loai_nha` `nguon` `do_net` `ghi_chu` | ✅ | |
| `co_noi_that` | | `co` / `khong` |
| `co_boundary_ro` | | `co` / `khong` |
| `so_phong_uoc` | | số |
| `dung_cho_REPLAN` | | `dat` / `tam` / `loai` |
| `dung_cho_GEPLAN` | | `dat` / `tam` / `loai` |
| `_trang_thai` | `tam` | đổi thành `dat` nếu qua cổng |

**Cổng chất lượng:** `do_net = dat` **và** (`REPLAN = dat` **hoặc** `GEPLAN = dat`) → đổi `_trang_thai` thành `dat`. Chỉ mẫu `dat` mới tính vào quota 3.000.

---

## Bước 1 — Có phải mặt bằng công năng 2D không?

Mặt bằng công năng 2D là hình chiếu từ trên xuống, tường là các đường thẳng song song với cạnh ảnh, nhìn thấy ranh giới các phòng.

**Loại ngay nếu là:** mặt đứng · mặt cắt đứng · phối cảnh · render 3D · isometric · ảnh nội thất · ảnh ngoại thất · mặt bằng mái (chỉ có đường dốc mái, không có phòng) · mặt bằng tổng thể khu đất (chỉ có khối nhà tô đặc, không có tường ngăn bên trong) · bản kết cấu / điện / nước / PCCC / chi tiết thi công.

## Bước 2 — Có phải biệt thự Việt Nam không?

**Dấu hiệu biệt thự:**

- Khối nhà gần vuông, tỷ lệ ngang:sâu từ 1:1 đến 1:2
- Có khoảng lùi hoặc sân vườn bao quanh ít nhất 2 mặt, không áp ranh
- Có sảnh đón hoặc tiền sảnh, thường có gara ô tô
- Cầu thang đặt ở sảnh trung tâm, không bám sát tường biên
- Phòng khách, phòng ăn, bếp tách bạch; có phòng ngủ master

Nhà có tỷ lệ thon (đến 1:2.5) **vẫn là biệt thự** nếu **có gara trong nhà** và **không có giếng trời**.

**Không phải biệt thự — loại, ghi rõ lý do vào `ghi_chu`:**

| Loại | Dấu hiệu |
|---|---|
| Nhà ống / nhà phố | Dài hẹp, tỷ lệ ngang:sâu từ 1:3 trở lên, tường chung hai bên, có giếng trời, thang bám tường biên. **Quota của nhóm N1** |
| Cấp 4 | Một tầng, bố cục đơn giản, sân trước rộng, không sảnh, không gara |
| Thờ họ | Đối xứng qua trục giữa, gian thờ trung tâm 3 hoặc 5 gian, không có phòng ngủ / bếp hiện đại |
| Ngoại nhập | Nhãn phòng tiếng Anh (Master Bedroom, Walk-in Closet, Mudroom, Basement), đơn vị ft/inch, gara 2–3 xe đấu đầu |

## Bước 3 — Chấm ba cột quyết định

### `do_net`

Tool đã đo phân giải và contrast, nhưng bạn vẫn cần nhìn. Đặt `dat` khi: phóng to lên vẫn phân biệt được tường bao với tường ngăn, không mờ, không chói, không cắt cụt nhà, và watermark (nếu có) **không** đè lên tường hoặc phòng.

Nếu tool ghi `do_net = tam` kèm `phan_giai_sat_nguong` trong `ghi_chu`, hãy tự nhìn — nhiều ảnh 640–800px vẫn dùng tốt.

### `dung_cho_REPLAN` — đặt `dat` khi **đủ cả 4**

- **(a)** Tường bao và tường ngăn đều rõ
- **(b)** Nhận diện được cửa / cửa sổ, hoặc ít nhất vị trí lờ mờ
- **(c)** Phòng có nhãn công năng đọc được, hoặc đủ rõ để suy ra
- **(d)** Nội thất (nếu có) **không** che khuất tường

Thiếu một điều kiện → `tam`. Thiếu hai trở lên → `loai`.

### `dung_cho_GEPLAN` — đặt `dat` **chỉ khi** đúng 1 tầng trên ảnh **và** số phòng công năng ≤ 8

Biệt thự thường 10–14 phòng nên phần lớn mẫu sẽ `GEPLAN = loai`. **Đó là bình thường, không phải lý do loại mẫu** — cổng chất lượng chỉ cần một trong hai thuật toán đạt. Trục chính của nhóm N3 là REPLAN.

---

## Phân biệt hai dạng mặt bằng

| Dạng | Dấu hiệu | Ảnh hưởng |
|---|---|---|
| **Bản vẽ kỹ thuật** | Nền trắng, tường đen đặc, nội thất vẽ nét đơn giản, thường có lưới trục và kích thước | Ưu tiên, dễ đạt REPLAN |
| **Render nội thất top-view** | Sàn có vân gỗ hoặc vân đá, giường có ảnh chăn gối thật, có cây cảnh đổ bóng | Tường khó tách khỏi nền → `dung_cho_REPLAN` tối đa `tam` |

## Quy tắc đếm phòng

Chỉ đếm phòng nằm **trong khung bao khép kín**. Không đếm: sân trước, sân sau, sân vườn, hiên nhà, hồ bơi, tiểu cảnh, ban công, sân thượng, lối đi ngoài nhà.

## Quy tắc watermark

- Watermark ở **góc** ảnh hoặc **ngoài** khung bản vẽ → không ảnh hưởng, vẫn có thể `dat`
- Watermark **đè lên** vùng tường, phòng, hoặc nhãn phòng → **loại ngay**, kể cả khi mờ
- Kiểm tra cả watermark chìm độ mờ thấp chạy ngang giữa bản vẽ

Tool có đo watermark chìm ở vùng trung tâm và ghi cờ `nghi_watermark_trung_tam` vào `ghi_chu` — thấy cờ này thì soi kỹ.

## Ảnh ghép nhiều tầng

Nếu một ảnh chứa nhiều hơn 1 tầng hoặc nhiều bản vẽ ghép chung: cắt thành từng file riêng, đặt tên `bietthu_015_t1.jpg`, `bietthu_015_t2.jpg`, rồi tách thành nhiều dòng trong Excel.

---

## Mẹo chấm nhanh

Đừng chấm từng ảnh một cách rời rạc. Sắp xếp Excel theo cột `nguon` để các ảnh cùng dự án nằm cạnh nhau — cùng một công trình thì kết luận về `house_type` và `co_noi_that` thường giống nhau, chấm theo cụm nhanh hơn nhiều.

Lọc cột `ghi_chu` theo cờ trước: `nghi_watermark_trung_tam` và `phan_giai_sat_nguong` gom lại xử lý một lượt.

Hai người trong nhóm nên chấm chồng 50 ảnh đầu một cách độc lập rồi so nhau. Lệch nhiều nghĩa là hai người đang hiểu tiêu chí khác nhau — thống nhất lại trước khi chia việc, không thì dataset sẽ không đồng nhất.
