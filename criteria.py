"""Anh xa nguyen van cac nhan trong ke hoach thuc tap sang code.

Nguon: Ke hoach thuc tap Web Media 08-09/2026
  - Muc II.4  : 20 tieu chi nhan ban ve (01-08 cu, 09-20 bo sung)
  - Muc II.4b : danh sach "Loai ngay"
  - Muc II.5  : 10 cot Excel + cong chat luong
  - Muc II.3a : 6 yeu cau chat luong du lieu

Moi tieu chi ghi ro AI TRIEU:
  "code"  - may tu quyet duoc, mien phi
  "meta"  - suy tu metadata trang nguon (tieu de, alt, caption)
  "nguoi" - PHAI mat nguoi nhin, xem QC_HUONG_DAN.md

Tool khong goi AI. 6/20 tieu chi co buoc may check, 16/20 can mat nguoi
nhin (tieu chi 02 va 06 co ca hai). Chay `python main.py map` de xem bang.
"""
from __future__ import annotations

import config as C

# ===================================================================
# II.4 - TIEU CHI NHAN BAN VE (phai du TAT CA moi duoc tinh)
# ===================================================================
CRITERIA = {
    # --- tieu chi cu 01-08 -----------------------------------------
    "01": {
        "text": "Dung nha Viet Nam (ong/pho · cap 4 NT · biet thu VN · tho ho VN)",
        "by": "meta+nguoi",
        "impl": "config.VN_HINT quet dia danh; config.REJECT_PROJECT loai "
                "biet thu pho; nguoi xac nhan theo QC buoc 2",
        "field": "house_type",
    },
    "02": {
        "text": "La mat bang cong nang 2D - nhin tu tren xuong, nhin ro phong; "
                "khong mat dung / mat cat / 3D",
        "by": "code+nguoi",
        "impl": "imgcheck.white_ratio() + imgcheck.axis_line_score() chan "
                "render va phoi canh; nguoi xac nhan theo QC buoc 1",
        "field": "is_2d_floorplan",
    },
    "03": {
        "text": "Thay ro tuong bao + tuong ngan",
        "by": "nguoi",
        "impl": "QC dieu kien REPLAN (a)",
        "field": "dung_cho_REPLAN",
    },
    "04": {
        "text": "Nhan dien duoc cua / cua so (hoac vi tri lo mo)",
        "by": "nguoi",
        "impl": "QC dieu kien REPLAN (b)",
        "field": "dung_cho_REPLAN",
    },
    "05": {
        "text": "Co nhan cong nang phong, hoac du ro de suy ra",
        "by": "nguoi",
        "impl": "QC dieu kien REPLAN (c)",
        "field": "dung_cho_REPLAN",
    },
    "06": {
        "text": "Do net du dung - khong mo, khong choi, khong cat nua nha",
        "by": "code+nguoi",
        "impl": "imgcheck contrast_std + MIN_SHORT_EDGE + watermark; "
                "nguoi cham lai cot do_net",
        "field": "do_net",
    },
    "07": {
        "text": "Uu tien co noi that - quan trong voi HC_REPLAN",
        "by": "nguoi",
        "impl": "nguoi dien cot co_noi_that (uu tien, KHONG bat buoc)",
        "field": "co_noi_that",
    },
    "08": {
        "text": "Moi file = 1 tang mat bang; nhieu tang thi tach file",
        "by": "meta+nguoi",
        "impl": "config.ALT_TANG doc so tang tu alt/caption -> hau to _t2; "
                "nguoi tach file khi anh ghep nhieu tang",
        "field": "so_tang_tren_anh",
    },
    # --- tieu chi bo sung 09-20 ------------------------------------
    "09": {
        "text": "Goc nhin vuong goc 2D - khong meo phoi canh / isometric / "
                "chup man hinh nghieng",
        "by": "code",
        "impl": "imgcheck.axis_line_score() - ban ve 2D co nhieu doan thang "
                "ngang/doc; anh nghieng thi diem thap -> loai thang",
        "field": "is_2d_floorplan",
    },
    "10": {
        "text": "Khung bao khep kin - tuong bao khong dut, tach duoc ranh nha",
        "by": "nguoi",
        "impl": "nguoi dien cot co_boundary_ro",
        "field": "co_boundary_ro",
    },
    "11": {
        "text": "Loi vao chinh nhan dien duoc",
        "by": "nguoi",
        "impl": "QC buoc 2 (sanh don / tien sanh) -> ghi_chu",
        "field": "ghi_chu",
    },
    "12": {
        "text": "Phong uot (bep / WC) tach duoc voi phong o neu co tren ban",
        "by": "nguoi",
        "impl": "QC quy tac dem phong -> so_phong_uoc",
        "field": "so_phong_uoc",
    },
    "13": {
        "text": "Cau thang / gieng troi / san trong thay duoc neu nha co",
        "by": "nguoi",
        "impl": "QC buoc 2 - cung la dau hieu phan biet ongpho",
        "field": "house_type",
    },
    "14": {
        "text": "Chu / nhan doc duoc - khong lat guong, khong xoay lech",
        "by": "nguoi",
        "impl": "QC buoc 2 - nhan tieng Anh -> ban ngoai nhap, loai",
        "field": "nhan_phong_ngon_ngu",
    },
    "15": {
        "text": "Noi that khong che khuat tuong bao va tuong ngan",
        "by": "nguoi",
        "impl": "QC dieu kien REPLAN (d)",
        "field": "dung_cho_REPLAN",
    },
    "16": {
        "text": "Dung mat bang cong nang - khong lay ban ket cau / dien / nuoc / "
                "PCCC / chi tiet thi cong",
        "by": "code+meta",
        "impl": "config.REJECT_TEXT chan tu alt/caption truoc khi tai anh",
        "field": "is_2d_floorplan",
    },
    "17": {
        "text": "Do phan giai du: canh ngan >= 800 px, khong nen vo net tuong",
        "by": "code",
        "impl": "imgcheck.inspect() do SAU crop_drawing_area(); "
                "640-800px -> soft_fail -> 'tam' (tranh loai oan mau tot)",
        "field": "do_net",
    },
    "18": {
        "text": "Contrast du de tach tuong khoi nen - khong gan trang / gan den",
        "by": "code",
        "impl": "imgcheck contrast_std >= MIN_CONTRAST_STD",
        "field": "do_net",
    },
    "19": {
        "text": "Khong chong nhieu tang hoac nhieu ban tren cung mot anh",
        "by": "nguoi",
        "impl": "nguoi cat anh ghep thanh tung file _t1/_t2 roi tach dong Excel",
        "field": "so_tang_tren_anh",
    },
    "20": {
        "text": "Mau GEPLAN = dat: bo cuc 1 tang, <= 8 phong cong nang",
        "by": "nguoi",
        "impl": "QC buoc 3; config.MAX_ROOMS_GEPLAN = 8. "
                "BIET THU thuong vuot 8 phong - KHONG phai ly do loai mau",
        "field": "dung_cho_GEPLAN",
    },
}

# ===================================================================
# II.4 - LOAI NGAY
# ===================================================================
HARD_REJECT = {
    "ngoai_nhap": ("Ban ngoai nhap khong dung kieu Viet Nam",
                   "nguoi: nhan phong tieng Anh, don vi ft/inch"),
    "sketch_roi": ("Sketch qua roi / chi khung tho khong cong nang",
                   "imgcheck.axis_line_score() thap + nguoi xac nhan"),
    "scan_loi": ("Scan loi nang, thieu tuong, thieu phong chinh",
                 "imgcheck contrast_std + nguoi cham cot do_net"),
    "cat_cut_watermark": ("Anh cat cut, watermark che tuong/phong",
                          "imgcheck.gray_center_ratio() gan co + nguoi soi ky"),
    "mat_dung": ("Mat dung, phoi canh, mat cat dung",
                 "config.REJECT_TEXT + imgcheck.white_ratio()"),
    "render_3d": ("Render 3D, isometric, BIM/SketchUp goc nghieng",
                  "imgcheck.white_ratio() < 0.55 + it duong thang ngang/doc"),
    "anh_chup_giay": ("Anh chup giay meo, bong den, tay/vat che ban ve",
                      "imgcheck.axis_line_score() - duong bi cong/nghieng"),
    "ban_ky_thuat_khac": ("Ban dien / nuoc / ket cau / PCCC",
                          "config.REJECT_TEXT tu alt/caption"),
    "trung_layout": ("Trung layout cung can (doi mau/crop/resize/doi ten)",
                     "imgcheck.phash() + DedupIndex, Hamming <= 8"),
}

# ===================================================================
# II.5 - 10 COT EXCEL
# ===================================================================
EXCEL_MAP = {
    "ten_file": {
        "bat_buoc": True,
        "gia_tri": "Dung ten file da nop",
        "nguon_gia_tri": "TOOL: main._filename() -> bietthu_001.jpg | _015_t2.jpg",
    },
    "loai_nha": {
        "bat_buoc": True,
        "gia_tri": "ongpho / cap4 / bietthu / thoho",
        "nguon_gia_tri": "TOOL: config.HOUSE_TYPE = 'bietthu' (co dinh cho N3)",
    },
    "nguon": {
        "bat_buoc": True,
        "gia_tri": "Link · sach · don vi · 'noi bo'",
        "nguon_gia_tri": "TOOL: ctx['project_url']; thu cong -> 'thu_cong'",
    },
    "co_noi_that": {
        "bat_buoc": True,
        "gia_tri": "co / khong",
        "nguon_gia_tri": "NGUOI cham - QC_HUONG_DAN.md",
    },
    "do_net": {
        "bat_buoc": True,
        "gia_tri": "dat / tam / loai",
        "nguon_gia_tri": "TOOL dien 'dat'/'tam' theo phan giai+contrast, NGUOI cham lai",
    },
    "dung_cho_REPLAN": {
        "bat_buoc": True,
        "gia_tri": "dat / tam / loai",
        "nguon_gia_tri": "NGUOI cham - du ca 4 dieu kien a-b-c-d (TC 03/04/05/15)",
    },
    "dung_cho_GEPLAN": {
        "bat_buoc": True,
        "gia_tri": "dat / tam / loai",
        "nguon_gia_tri": "NGUOI cham - 1 tang VA <= 8 phong (TC 20)",
    },
    "so_phong_uoc": {
        "bat_buoc": True,
        "gia_tri": "So phong cong nang uoc luong",
        "nguon_gia_tri": "NGUOI dem - chi dem trong khung bao khep kin",
    },
    "co_boundary_ro": {
        "bat_buoc": True,
        "gia_tri": "co / khong",
        "nguon_gia_tri": "NGUOI cham (TC 10)",
    },
    "ghi_chu": {
        "bat_buoc": False,
        "gia_tri": "Tang · thieu cua so · ban tho…",
        "nguon_gia_tri": "TOOL: so tang + co imgcheck + ma du an; NGUOI bo sung",
    },
}

# ===================================================================
# II.5 - CONG CHAT LUONG
# ===================================================================
GATE_RULE = (
    "do_net == 'dat' AND (dung_cho_REPLAN == 'dat' OR dung_cho_GEPLAN == 'dat')"
    "  ->  duoc tinh"
)
GATE_STATES = {
    "dat": "Duoc tinh vao quota - CHI NGUOI dat duoc, tool khong tu dat",
    "tam": "Tool da loc sach, dang cho nguoi cham 5 cot con lai",
    "loai": "Tool loai chac chan (khong phai ban ve / trung / vo net)",
}

# ===================================================================
# II.3a - 6 YEU CAU CHAT LUONG DU LIEU
# ===================================================================
QUALITY_REQ = {
    "dung_kieu_VN": "config.VN_HINT + REJECT_PROJECT; NGUOI xac nhan",
    "mat_bang_2D": "imgcheck.white_ratio + axis_line_score; NGUOI xac nhan",
    "du_cong_nang": "NGUOI cham REPLAN a-b-c + co_boundary_ro",
    "do_net_dung_duoc": "imgcheck MIN_SHORT_EDGE / contrast_std / watermark",
    "duy_nhat": "imgcheck.phash + DedupIndex.seen_code (ma du an)",
    "dung_cho_2_thuat_toan": "NGUOI cham dung_cho_REPLAN + dung_cho_GEPLAN",
}


def criteria_note(v: dict, flags: list[str]) -> str:
    """Sinh chuoi ma tieu chi bi vi pham, de ghi vao cot ghi_chu.

    CHI ghi nhung tieu chi may da ket luan duoc. Cot de trong (nguoi chua
    cham) khong tinh la vi pham - neu khong thi moi mau deu dinh day ma.
    """
    bad: list[str] = []

    if v.get("is_2d_floorplan") is False:
        bad += ["02", "09", "16"]
    if v.get("house_type") and v["house_type"] != C.HOUSE_TYPE:
        bad.append("01")
    if v.get("co_boundary_ro") == "khong":
        bad.append("10")
    if v.get("nhan_phong_ngon_ngu") == "en":
        bad.append("14")
    if v.get("dung_cho_REPLAN") in ("tam", "loai"):
        bad += ["03", "04", "05", "15"]
    if v.get("dung_cho_GEPLAN") in ("tam", "loai"):
        bad.append("20")
    if any(f.startswith("phan_giai") for f in flags):
        bad.append("17")
    if "nghi_watermark_trung_tam" in flags:
        bad.append("06")
    if v.get("needs_split"):
        bad += ["08", "19"]

    return "TC:" + ",".join(sorted(set(bad))) if bad else ""


def coverage_report() -> None:
    """In bang doi chieu tieu chi -> code."""
    print(f"\n{'TC':<5}{'AI LAM':<14}{'COT EXCEL':<20}NOI DUNG")
    print("-" * 100)
    for code, c in CRITERIA.items():
        print(f"{code:<5}{c['by']:<14}{c['field']:<20}{c['text'][:52]}")

    may = sum(1 for c in CRITERIA.values() if "code" in c["by"])
    nguoi = sum(1 for c in CRITERIA.values() if "nguoi" in c["by"])
    print(f"\nTong: {len(CRITERIA)} tieu chi | {may} co buoc may check | "
          f"{nguoi} can mat nguoi nhin")
    print("Tool KHONG goi AI, khong ton phi. Xem QC_HUONG_DAN.md de cham tay.")

    print(f"\nCong chat luong: {GATE_RULE}")
    for k, val in GATE_STATES.items():
        print(f"  {k:<6}{val}")

    print(f"\n{'COT EXCEL':<20}{'BAT BUOC':<11}NGUON GIA TRI")
    print("-" * 100)
    for col, m in EXCEL_MAP.items():
        print(f"{col:<20}{'co' if m['bat_buoc'] else 'khong':<11}{m['nguon_gia_tri'][:58]}")

    print(f"\n{'LOAI NGAY':<22}CHAN BOI")
    print("-" * 100)
    for key, (text, impl) in HARD_REJECT.items():
        print(f"{key:<22}{impl[:70]}")


if __name__ == "__main__":
    coverage_report()
