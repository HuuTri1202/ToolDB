"""Cham anh bang QUY TAC - khong goi AI, khong ton mot dong nao.

Chi dien nhung cot ma may quyet duoc chac chan. Cac cot doi mat nguoi
(tuong bao, nhan phong, noi that, so phong) de TRONG cho nguoi cham tay
theo QC_HUONG_DAN.md.

Nguyen tac: tha nham con hon giet nham. Bo loc mien phi khong du tinh te
de loai mau tot mot cach an toan, nen no chi loai nhung gi chac chan la rac
(khong phai lineart, contrast thap, it duong thang, trung lap, alt/caption
noi ro la phoi canh). Phan con lai deu chuyen sang 'tam' cho nguoi quyet.
"""
from __future__ import annotations

import config as C

# Cac cot chi nguoi moi tra loi duoc -> de trong trong Excel.
CHO_NGUOI = ("co_noi_that", "co_boundary_ro", "dung_cho_REPLAN",
             "dung_cho_GEPLAN", "so_phong_uoc")

_MAC_DINH = {
    "is_2d_floorplan": True,
    "house_type": C.HOUSE_TYPE,
    "reject_reason": None,
    "needs_split": False,
    "so_tang_tren_anh": 0,
    "so_phong_uoc": "",
    "co_noi_that": "",
    "co_boundary_ro": "",
    "nhan_phong_ngon_ngu": "",
    "do_net": "tam",
    "dung_cho_REPLAN": "",
    "dung_cho_GEPLAN": "",
    "ghi_chu": "",
}


def _so_tang(ctx: dict) -> int:
    """Doc so tang tu alt/caption cua chinh tam anh, KHONG lay tu tieu de.

    Tieu de du an luon chua "N tang" (so tang cua can nha), khong noi gi ve
    tang cua ban ve nay - dua vao se sinh ra so tang sai.

    TEN FILE anh la tin hieu MANH NHAT va truoc day bi bo qua - don vi thiet ke
    thuong dat ten kieu "mat-bang-tang-2-...jpg" hoac "...-tang-tret-...jpg".
    """
    ten_file = (ctx.get("url", "") or "").split("?")[0].rsplit("/", 1)[-1]
    for blob in (ten_file, f"{ctx.get('alt', '')} {ctx.get('caption', '')}"):
        if not blob:
            continue
        m = C.ALT_TANG.search(blob)
        if m:
            return int(m.group(1))
        m = C.ALT_LAU.search(blob)       # mien Nam: "lau 1" = tang 2
        if m:
            return int(m.group(1)) + 1
        if C.ALT_TRET.search(blob):
            return 1
    return 0


so_tang = _so_tang                       # ten cong khai, dung cho lenh retag


# Tang khong danh so duoc: ten rieng thay cho _tN
TANG_DAC_BIET = (
    ("_th", C.TANG_HAM),
    ("_tum", C.TANG_TUM),
    ("_tl", C.TANG_LUNG),
    ("_tst", C.TANG_SAN_THUONG),
    ("_tap", C.TANG_AP_MAI),
)


def nhan_tang(ten_file: str, co_tret_trong_du_an: bool = True) -> str:
    """Tra ve hau to tang tu ten file anh: '_t2', '_th', '_tum'... hoac ''.

    Chi doc phan NGAY SAU chu "mat bang" / "ban ve" - do moi la chu de cua
    ban ve. Quet ca ten file se sai: "mat-bang-tang-tret-...-ban-ham-1-tret"
    la mat bang TRET cua can nha CO ham, khong phai mat bang ham.
    """
    m = C.CHU_DE_BAN_VE.search(ten_file)
    chu_de = ten_file[m.end():m.end() + 26] if m else ten_file

    for hau_to, pat in TANG_DAC_BIET:
        if pat.search(chu_de):
            return hau_to

    m = C.ALT_TANG.search(chu_de)
    if m:
        return f"_t{m.group(1)}"
    m = C.ALT_LAU.search(chu_de)
    if m:
        # Du an co ban ve tret -> tret la tang 1, lau 1 la tang 2.
        # Du an khong co tret -> lau 1 chinh la tang 1.
        return f"_t{int(m.group(1)) + (1 if co_tret_trong_du_an else 0)}"
    if C.ALT_TRET.search(chu_de):
        return "_t1"
    return ""


def judge(ctx: dict, rep) -> dict:
    """Suy ra nhung gi co the tu metadata trang nguon + ket qua OpenCV."""
    ctx = ctx or {}
    v = dict(_MAC_DINH)
    blob = f"{ctx.get('alt', '')} {ctx.get('caption', '')}"
    tieu_de = ctx.get("title", "") or ""
    ghi: list[str] = []

    # --- tieu chi 02/09/16: co phai mat bang 2D khong -----------------------
    # imgcheck da chan lineart + duong thang. O day chi doc them alt/caption.
    if C.REJECT_TEXT.search(blob):
        v["is_2d_floorplan"] = False
        v["reject_reason"] = "alt_caption_noi_khong_phai_mat_bang"

    # --- tieu chi 01: dung kieu Viet Nam ------------------------------------
    if C.REJECT_PROJECT.search(tieu_de):
        v["house_type"] = "ongpho"
        v["reject_reason"] = "tieu_de_la_biet_thu_pho"
    elif not ctx.get("location"):
        ghi.append("chua_ro_dia_danh")

    # --- tieu chi 08: moi file mot tang -------------------------------------
    tang = _so_tang(ctx)
    v["so_tang_tren_anh"] = tang
    if tang:
        ghi.append(f"tang {tang}")

    # --- tieu chi 06/17/18: do net ------------------------------------------
    v["do_net"] = "tam" if rep.soft_fail else "dat"

    # --- metadata co ich cho nguoi cham -------------------------------------
    if ctx.get("so_phong_ngu"):
        ghi.append(f"tieu de: {ctx['so_phong_ngu']} phong ngu")
    if ctx.get("ma_du_an"):
        ghi.append(ctx["ma_du_an"])

    # So do duong thang de cuoi - la so lieu chan doan, khong phai thong tin
    # nguoi cham can doc truoc.
    ghi.append(f"duong_thang={rep.axis_lines}")
    v["ghi_chu"] = " · ".join(ghi)
    return v


def gate(v: dict, rep) -> str:
    """Tra ve 'tam' | 'loai'. KHONG BAO GIO tra 'dat'.

    Chi nguoi moi dat duoc mau thanh 'dat', sau khi dien 5 cot con lai
    trong Excel. Cong chat luong that (do_net + REPLAN/GEPLAN) can mat
    nguoi nhin, khong co cach nao do bang code.
    """
    if not v.get("is_2d_floorplan"):
        return "loai"
    if v.get("house_type") != C.HOUSE_TYPE:
        return "loai"
    return "tam"
