# Tool dataset mặt bằng biệt thự — Nhóm N3 Công nghệ Thông tin

Thu thập mặt bằng công năng 2D loại `bietthu`, quota 3.000 mẫu, mentor Mr. Phúc.

**Tool không gọi AI, không tốn một đồng nào.** Toàn bộ chạy bằng regex và OpenCV.

## Tool làm gì, người làm gì

6 trong 20 tiêu chí ở mục II.4 có bước máy check được. 16 tiêu chí cần mắt người — tường bao có rõ không, nhãn phòng đọc được không, có đúng là biệt thự không — không có cách nào đo bằng code. Hai tiêu chí (02 và 06) có cả hai bước: máy lọc thô, người chốt.

Nên phân công như sau:

| Tool làm | Người làm |
|---|---|
| Tìm và tải ảnh ứng viên từ nguồn | Xem ảnh trong `output/_tam/` |
| Loại phối cảnh, render, ảnh chụp nghiêng, bản kỹ thuật | Điền 5 cột: `co_noi_that`, `co_boundary_ro`, `so_phong_uoc`, `dung_cho_REPLAN`, `dung_cho_GEPLAN` |
| Loại ảnh vỡ nét, contrast thấp, tỷ lệ bất thường | Đổi `_trang_thai` từ `tam` sang `dat` khi qua cổng |
| Chống trùng bằng pHash và mã dự án | |
| Điền sẵn 5 cột: `ten_file`, `loai_nha`, `nguon`, `do_net`, `ghi_chu` | |

**Tool không bao giờ tự đánh dấu mẫu nào là `dat`.** Mẫu sống sót đều ở trạng thái `tam`. Cách chấm nằm trong [QC_HUONG_DAN.md](QC_HUONG_DAN.md).

## Cài đặt

```bash
pip install -r requirements.txt
```

Mở `config.py`, tìm `USER_AGENT` và thay email cho đúng người phụ trách. Không cần khóa API, không cần đăng ký gì.

## Lệnh

| Lệnh | Mạng | Chi phí |
|---|---|---|
| `python main.py map` | không | 0 |
| `python main.py report` | không | 0 |
| `python main.py check --dir ./anh_cua_ban` | không | 0 |
| `python main.py calib --dir ./bo_test --labels nhan.csv` | không | 0 |
| `python main.py probe --source neohouse --limit 10` | chỉ đọc HTML | 0 |
| `python main.py crawl --source neohouse --limit 50` | có | 0 |

## Quy trình 6 bước

1. **Cài đặt** — như mục trên. Đừng quên sửa email trong `USER_AGENT`.
2. **Xem bảng đối chiếu** — `python main.py map`. In 20 tiêu chí II.4 kèm ai làm từng tiêu chí, 10 cột Excel, 9 mục loại ngay. Đây cũng là thứ đưa cho nhóm trưởng và mentor xem.
3. **Chấm thử ảnh có sẵn** — `python main.py check --dir ./anh_cua_ban`. Xem tool loại đúng chưa. Chạy bao nhiêu lần cũng được, không tốn gì.
4. **Probe nguồn** — `python main.py probe --source neohouse --limit 10`. Cho biết crawler bắt đúng link dự án không và tỷ lệ lọc alt text bao nhiêu. Ra 0 trang dự án thì sửa `project_url_pattern`; ra 0 ứng viên thì bổ sung từ khóa vào `ACCEPT_TEXT`.
5. **Hiệu chỉnh trên bộ test 50 ảnh** — bước không được bỏ qua, xem mục *Quy trình hiệu chỉnh bắt buộc* bên dưới.
6. **Mở van** — `python main.py crawl --source neohouse --limit 100`. Với delay 2.5 giây và khoảng 10–13 request mỗi dự án, 100 dự án mất **50–70 phút**, chạy nền được. Dừng giữa chừng rồi chạy lại an toàn: tool đánh số tiếp và đọc lại pHash từ Excel để không xử lý trùng. Lưu ý Excel chỉ ghi mỗi 25 dòng, nên Ctrl+C có thể mất tối đa 24 dòng cuối.

Sau đó mới tới phần chấm tay theo [QC_HUONG_DAN.md](QC_HUONG_DAN.md), rồi `python main.py report` để xem tiến độ.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `N3_OUT` | `./output` | thư mục kết quả |

## Bộ lọc miễn phí thay AI đến đâu

Bộ lọc mạnh nhất là đếm đoạn thẳng ngang/dọc (`imgcheck.axis_line_score`). Mặt bằng 2D gần như chỉ gồm tường song song với cạnh ảnh, cộng lưới trục và đường kích thước — điểm rất cao. Phối cảnh, render, ảnh chụp giấy nghiêng thì đường bị xoay hoặc cong — điểm thấp. Đo trên ảnh mẫu:

| Loại ảnh | Số đường thẳng | Kết quả |
|---|---|---|
| Mặt bằng CAD | 51 | `tam` — giữ lại |
| Render 3D | 0 | `loai` |
| Ảnh chụp giấy nghiêng 7° | 0 | `loai` |

Ngưỡng nằm ở `config.MIN_AXIS_LINES = 12`. Thấy tool loại oan nhiều bản vẽ thật thì hạ xuống; thấy rác lọt nhiều thì nâng lên.

### Hiệu chỉnh `LINEART_WHITE_RATIO` trên 25 ảnh thật

Đo trên 25 ảnh tải từ 8 nguồn, nhãn tay sau khi xem tận mắt:

| Ngưỡng | Giữ đúng | Loại oan (C) | Rác lọt (G) |
|---|---|---|---|
| 0.55 (cũ) | 13 | **6** | 0 |
| 0.50 | 14 | 5 | 0 |
| **0.42 (đang dùng)** | **18** | **1** | **0** |

Ngưỡng 0.55 loại oan 6/19 bản vẽ thật — toàn **mặt bằng tô màu** (sàn xám, sân xanh, WC xanh dương) nên tỷ lệ pixel trắng chỉ 0.45–0.50. Hạ xuống 0.42 cứu được 5 mẫu mà **không cho render nào lọt**, vì bộ lọc đếm đường thẳng chặn tiếp: render có `lines` thấp hoặc không phải trục giao.

Bộ lọc đường thẳng chính là thứ cho phép nới `white_ratio` an toàn. Hai bộ lọc bù nhau: `white_ratio` bắt ảnh chụp và render tối, `axis_line_score` bắt phối cảnh sáng màu.

Cái bộ lọc này **không** làm được: phân biệt biệt thự với nhà ống, đánh giá tường bao, đọc nhãn phòng, đếm phòng. Đó là lý do vẫn cần người chấm.

## Pipeline

Mười bước, tất cả miễn phí. Thứ tự có chủ đích: bước rẻ nhất chạy trước, bước tốn băng thông chạy sau.

| # | Bước | Loại được |
|---|---|---|
| 1 | Lọc alt/caption bằng regex | 60–70% |
| 2 | Thử URL bản gốc | cứu mẫu phân giải thấp |
| 3 | Tải ảnh | |
| 4 | Crop khung bản vẽ | vành marketing, logo, hotline |
| 5 | Đo phân giải (sau crop) | ảnh vỡ nét |
| 6 | Lineart + contrast | render, ảnh chụp |
| 7 | Tỷ lệ cạnh | banner, dải băng dọc |
| 8 | Đếm đường thẳng ngang/dọc | phối cảnh, ảnh chụp nghiêng |
| 9 | Watermark chìm + pHash chống trùng | ảnh đăng lại |
| 10 | Ghi Excel để người chấm | |

## Hai trạng thái máy, một trạng thái người

Cổng máy nằm trong `assess.gate()`. Nó chỉ trả về `tam` hoặc `loai` — **không bao giờ trả `dat`**.

| Tình huống | Trạng thái | Ai đặt |
|---|---|---|
| Không phải bản vẽ lineart, contrast thấp, ít đường thẳng, tỷ lệ lạ, trùng pHash, alt/caption nói rõ là phối cảnh | `loai` | tool |
| Qua hết bộ lọc máy | `tam` | tool |
| `do_net=dat` và (REPLAN=dat hoặc GEPLAN=dat) | `dat` | **người**, sau khi điền 5 cột |

Ảnh được xếp vào ba thư mục:

| Thư mục | Chứa | Ghi chú |
|---|---|---|
| `output/_tam/` | mẫu chờ chấm | **đây là thư mục bạn mở để chấm tay** |
| `output/bietthu/` | mẫu `dat` | thư mục nộp — bạn tự chuyển sang sau khi chấm |
| `output/_loai/` | mẫu bị loại | giữ để đối chiếu khi hiệu chỉnh, xóa được |

Mẫu `tam` và `dat` cùng dùng dải số `bietthu_NNN`; mẫu `loai` đặt tên theo pHash (`loai_<hash>.jpg`) nên không tiêu số thứ tự và không ghi đè lên nhau.

## Quy ước đặt tên tầng

```
bietthu_042_t2.jpg     tầng 2
bietthu_069_th.jpg     tầng hầm
bietthu_104_tum.jpg    tum
```

| Hậu tố | Tầng |
|---|---|
| `_t1` `_t2` `_t3`… | tầng đánh số |
| `_th` | tầng hầm |
| `_tl` | tầng lửng |
| `_tst` | sân thượng |
| `_tap` | áp mái |
| `_tum` | tum |

Bản vẽ Việt Nam có nhiều tầng không đánh số được. Gộp chúng vào `_t1` là sai, bỏ trống thì mất thông tin, nên mỗi loại có nhãn riêng.

**Quy tắc "lầu" tính theo từng dự án.** Dự án **có** bản vẽ trệt: trệt là tầng 1, lầu 1 là tầng 2. Dự án **không có** bản vẽ trệt: lầu 1 chính là tầng 1. Nếu áp một quy tắc cứng cho cả hai, 32/95 dự án sẽ có hai bản vẽ khác nhau cùng mang nhãn `_t1`.

**Nhãn đọc từ chủ đề bản vẽ, không phải cả tên file.** `assess.nhan_tang()` chỉ đọc phần ngay sau cụm "mặt bằng" / "bản vẽ". Quét cả tên file thì `mat-bang-ham-biet-thu-tren-doi-ban-ham-1-tret.jpg` bị đọc thành *trệt* — mô tả căn nhà lấn át chủ đề bản vẽ.

Ảnh cũ gắn lại bằng `python main.py retag --that`, đánh số lại liên tục bằng `python main.py danhso --that`.

## Bảo trì

| Lệnh | Việc |
|---|---|
| `python main.py danhso --that` | đánh số lại liên tục 001..N |
| `python main.py retag --that` | gắn lại hậu tố tầng cho ảnh đã có |
| `python doi_sang_jpg.py --that` | đổi webp/jpeg sang jpg |
| `python doi_soat.py --that` | đối chiếu Excel với thư mục ảnh bằng pHash |

**Không chạy các lệnh này khi đang có mẻ cào chạy nền.** Cả hai bên đều mở, sửa rồi lưu cùng file Excel nên sẽ ghi đè lẫn nhau. Đã từng làm mất liên kết của 27 dòng vì lỗi này — `doi_soat.py` sinh ra để dọn hậu quả đó.

Lý do cụ thể nằm ở cột `ghi_chu`. Cuối tuần 1 lọc `output/_tam/` theo mã TC và xử lý hàng loạt — một lần sửa cấu hình thường cứu được vài trăm mẫu.

## Lưu ý riêng của biệt thự

`dung_cho_GEPLAN=dat` chỉ khi 1 tầng và ≤ 8 phòng. Biệt thự thường 10–14 phòng nên phần lớn mẫu sẽ `GEPLAN=loai` — **đó là bình thường, không phải lý do loại mẫu**. Trục chính của nhóm N3 là REPLAN. Mặt bằng tầng 2, tầng 3, tầng tum mới là nguồn GEPLAN tốt nhất.

## Nguồn

`neohouse.vn` đã kiểm tra: ảnh mặt bằng không watermark, metadata tiêu đề rất tốt. Ưu tiên `/du-an/biet-thu-1-tang/` vì nhà 1 tầng dễ đạt GEPLAN.

`shac.vn` nằm trong blacklist: watermark chạy ngang giữa bản vẽ trên mọi ảnh, không cứu được bằng crop.

`betaviet.vn` **đã kiểm tra, không dùng được** — không phải vì watermark mà vì site không đăng mặt bằng. Đo trên 6 trang dự án thật: 196 ảnh nội dung, **0 ảnh mặt bằng**. Chuỗi "mặt bằng", "công năng", "bản vẽ" xuất hiện **0 lần** trong HTML thô. Không có lazy-load (0 ảnh nằm ngoài thuộc tính `src`), nên đây là site thiếu chứ không phải crawler mù. Betaviet là đơn vị thiết kế thi công, trang dự án chỉ trưng phối cảnh và ảnh nội thất hoàn thiện. Ngoài ra listing của họ trộn lẫn khách sạn, lâu đài, nhà phố — kể cả có mặt bằng cũng phải mở rộng `REJECT_PROJECT` khá nhiều.

`sbsvilla.vn` **không dùng được** — robots.txt khai báo `Content-Signal: search=yes,ai-train=no,use=reference`, tức chủ site cho phép lập chỉ mục tìm kiếm nhưng **từ chối cho dùng nội dung để huấn luyện mô hình**, và ghi rõ đây là express reservation of rights theo Điều 4 Chỉ thị EU 2019/790. Dataset này sinh ra để huấn luyện HC_REPLAN và HC_GEPLAN nên rơi đúng vào mục bị từ chối. Đường dẫn vẫn trả HTTP 200 và `robots.txt` không chặn User-Agent của tool — nhưng cho phép truy cập không đồng nghĩa cho phép dùng vào mục đích này.

`vietnamarch.com.vn` **không có mặt bằng** — giống betaviet, là đơn vị thiết kế trưng phối cảnh. Quét 15 trang nhà thờ họ: 441 ảnh, chỉ 8 lần nhắc "mặt bằng" và đều là **2 ảnh lặp lại**, trong đó chữ "mặt bằng" dùng theo nghĩa mô tả (*"mặt bằng chữ Nhị"*, *"mặt bằng 70m2"*) chứ không phải nhãn ảnh bản vẽ. Cạm bẫy riêng của site này: **alt text ghi "Bản vẽ thiết kế…" cho cả ảnh render**, nên lọc theo chữ "bản vẽ" sẽ dính hàng loạt phối cảnh — đã tải về kiểm tra tận mắt, cả hai đều là render 3D có watermark "V SPACE". Bộ lọc `white_ratio` chặn đúng (0.03–0.34, ngưỡng 0.55).

Site cũng chặn phân trang (`Disallow: */page/*`) nên phải liệt kê qua sitemap — xem chế độ `sitemap` trong `config.SOURCES`.

**Tool tự kiểm tra tín hiệu này.** `crawler.ai_train_signal()` đọc `Content-Signal` trong robots.txt; gặp `ai-train=no` thì `allowed()` trả `False` và mọi request tới host đó dừng lại. Không cần nhớ thủ công.

## Bảng nguồn đã kiểm tra

| Nguồn | Kết quả | Ghi chú |
|---|---|---|
| `neohouse.vn` | **dùng được** | 131 dự án + 7 trang tổng hợp. Ảnh 1100x713 |
| `noithaticon.vn` | **dùng được** | Bản vẽ CAD 1280x905 — nguồn duy nhất đạt tiêu chí 17 |
| `tanphatcompany.com` | **dùng được** | Mặt bằng tô màu 2326x1729, cần ngưỡng `white_ratio` ≤ 0.50 |
| `kientructrangkim.com` | **dùng được** | Mặt bằng thật nhưng chỉ 750x531 |
| `nhadepktv.vn` | một phần | Có mặt bằng thật nhưng toàn **nhà phố** — quota N1, không phải N3 |
| `lg.com.vn` | một phần | Bản vẽ thật, ảnh rất nhỏ (cạnh ngắn 279–338px) |
| `betaviet.vn` | không | 5.912 URL, **0 URL nào có "mat-bang"** |
| `vietnamarch.com.vn` | không | 441 ảnh/15 trang, 0 mặt bằng. Alt ghi "Bản vẽ" cho cả render |
| `decoxdesign.com` | không | Nhồi SEO: tên file `mat-bang-...` nhưng là ảnh chụp nội thất |
| `vinavic.vn` | không | Nhồi SEO tương tự, ảnh là phối cảnh mặt đứng |
| `akisa.vn` `nhaxinhdesign.com` | không | Không có URL nào chứa "mat-bang" |
| `sbsvilla.vn` `sbshouse.vn` | **chặn** | robots.txt khai báo `ai-train=no` |
| `shac.vn` | không | Watermark chạy ngang giữa bản vẽ trên mọi ảnh |

**Bài học chung: tên file và alt text không đáng tin.** Bốn nguồn nhồi từ khóa `mat-bang` vào tên ảnh render để SEO. Cách duy nhất chắc chắn là tải vài ảnh về và nhìn.

## Kiểm tra một nguồn mới

```bash
python main.py probe --url "https://site-nao-do.vn/trang-du-an"
```

Lệnh này chạy được với URL bất kỳ chưa có trong `config.SOURCES`. Nó báo: tín hiệu `ai-train`, robots.txt có chặn không, số ứng viên nếu coi đây là trang dự án, số lần chuỗi `mặt bằng` xuất hiện trong HTML thô, và các tiền tố đường dẫn hay gặp để bạn đoán `project_url_pattern`.

**Phép thử 10 giây:** đếm chuỗi `mặt bằng` trong HTML thô. Bằng 0 thì bỏ ngay, không cần đo gì thêm. neohouse cho 10 lần; betaviet cho 0.

Ước tính một site cỡ neohouse cho 250–350 mẫu. Để đạt 3.000 cần 10–12 site. Trước khi thêm nguồn mới vào `config.SOURCES`: chạy `probe` để xem selector có bắt được không (miễn phí), rồi tải thử 5 ảnh và chạy `check` — nếu dính watermark giữa thì bỏ ngay, đừng crawl.

## Quy trình hiệu chỉnh bắt buộc

Đừng chạy quy mô lớn trước khi làm xong:

1. Lấy 50 ảnh từ ít nhất 3 site
2. Hai người trong nhóm chấm tay độc lập, ghi vào CSV theo mẫu `nhan_mau.csv` (`ten_file,nhan` — nhãn là `dat`/`tam`/`loai`; dòng tiêu đề và dòng nhãn không hợp lệ được bỏ qua)
3. `python main.py calib --dir ./bo_test --labels nhan.csv` — miễn phí, chạy lại bao nhiêu lần cũng được
4. Đọc ma trận: **C** là mẫu dùng được bị tool loại oan, **G** là rác lọt sang khâu chấm tay
5. Sửa cho tới khi **C dưới 3/50**. Hạ `MIN_AXIS_LINES`, nới `ASPECT_MIN`/`ASPECT_MAX`, hoặc bớt từ khóa trong `REJECT_TEXT`
6. Rồi mới mở van

**C và G không cân nhau.** C giết quota — ảnh bị tool loại thì không ai nhìn thấy nó nữa, mất luôn. G chỉ làm bạn tốn thêm vài giây chấm tay rồi bấm `loai`. Nên khi phải chọn, luôn nới lỏng bộ lọc chứ đừng siết.

Nhóm chỉ có 2 người và 6 buổi/tuần — không có cơ hội làm lại lần hai.

## Trước khi crawl

Tool đã đọc `robots.txt`, giới hạn 2.5 giây/request, và khai báo User-Agent trung thực. Bạn cần sửa email liên hệ trong `config.USER_AGENT`.

Các bản vẽ này thuộc bản quyền của đơn vị thiết kế. Hỏi Mr. Phúc trước: công ty đã có thỏa thuận với đơn vị nào chưa, và kho hồ sơ khách hàng nội bộ có dùng được không. Tài liệu xếp nguồn nội bộ ở mức ưu tiên cao nhất — nếu có, đó là dữ liệu sạch pháp lý và thực sự "duy nhất trên thế giới", thứ mà crawl web không tạo ra được.
