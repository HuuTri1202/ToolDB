"""Cac phep kiem tra anh chay bang OpenCV - mien phi, khong goi dich vu nao."""
from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

import config as C


@dataclass
class ImgReport:
    ok: bool = True
    reason: str = ""
    width: int = 0
    height: int = 0
    cropped: bool = False
    white_ratio: float = 0.0
    gray_center_ratio: float = 0.0
    contrast_std: float = 0.0
    axis_lines: int = 0
    aspect: float = 0.0
    phash: int = 0
    soft_fail: bool = False
    flags: list = field(default_factory=list)


# ------------------------------------------------------------------ 1. crop
def crop_drawing_area(img: np.ndarray) -> tuple[np.ndarray, bool]:
    """Cat bo vien marketing (logo, hotline, khung mau) quanh ban ve.

    Bat buoc chay TRUOC khi do phan giai - neu khong se loai nham
    nhung anh co vien branding lon (loi thuong gap nhat).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    _, bw = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return img, False

    H, W = gray.shape[:2]
    x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    if 0.25 < (w * h) / (W * H) < 0.95 and min(w, h) > 200:
        return img[y : y + h, x : x + w], True
    return img, False


# ------------------------------------------------------------------ 2. lineart
def white_ratio(gray: np.ndarray) -> float:
    """Ban ve CAD co nen trang ap dao; phoi canh/render thi khong."""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    return float(hist[235:].sum() / max(hist.sum(), 1))


# ------------------------------------------------------------------ 3. watermark
def gray_center_ratio(gray: np.ndarray) -> float:
    """Do luong pixel xam nhat o vung trung tam -> dau hieu watermark chim.

    Ban ve sach gan nhu chi co 2 tong: trang nen va den net.
    Mot luong pixel xam bat thuong o giua thuong la watermark de len tuong.
    """
    h, w = gray.shape[:2]
    center = gray[int(h * 0.30) : int(h * 0.70), int(w * 0.20) : int(w * 0.80)]
    if center.size == 0:
        return 0.0
    hist = cv2.calcHist([center], [0], None, [256], [0, 256]).flatten()
    return float(hist[190:240].sum() / max(hist.sum(), 1))


# ------------------------------------------------------------------ 4. duong thang
def axis_line_score(gray: np.ndarray) -> int:
    """Dem doan thang DAI nam ngang hoac thang dung.

    Mat bang 2D gan nhu chi gom tuong song song voi canh anh, cong them
    luoi truc va duong kich thuoc -> diem rat cao. Phoi canh, render,
    anh chup giay thi duong bi nghieng hoac cong -> diem thap.
    Day la bo loc thay cho buoc 1 cua AI (co phai mat bang 2D khong).
    """
    h, w = gray.shape[:2]
    min_len = max(int(min(h, w) * 0.15), 40)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=80,
        minLineLength=min_len, maxLineGap=6,
    )
    if lines is None:
        return 0

    n = 0
    for x1, y1, x2, y2 in np.asarray(lines).reshape(-1, 4):
        dx, dy = abs(int(x2) - int(x1)), abs(int(y2) - int(y1))
        if (dy <= 2 and dx >= min_len) or (dx <= 2 and dy >= min_len):
            n += 1
    return n


# ------------------------------------------------------------------ 5. pHash
def phash(gray: np.ndarray, size: int = 32, keep: int = 8) -> int:
    """Perceptual hash 64-bit. Bat duoc ca crop / resize / doi mau."""
    small = cv2.resize(gray, (size, size), interpolation=cv2.INTER_AREA)
    dct = cv2.dct(np.float32(small))
    block = dct[:keep, :keep]
    med = np.median(block[1:, 1:])
    bits = (block > med).flatten()
    out = 0
    for b in bits:
        out = (out << 1) | int(b)
    return out


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


# ------------------------------------------------------------------ pipeline
def inspect(path: str) -> ImgReport:
    """Chay toan bo kiem tra mien phi tren 1 file anh."""
    r = ImgReport()
    img = cv2.imread(path)
    if img is None:
        r.ok, r.reason = False, "khong_doc_duoc_anh"
        return r

    full_short = min(img.shape[:2])
    img, r.cropped = crop_drawing_area(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    r.height, r.width = gray.shape[:2]
    r.phash = phash(gray)

    # --- LOI CUNG: loai thang, khong dua sang cho nguoi cham ----------------
    r.white_ratio = white_ratio(gray)
    if r.white_ratio < C.LINEART_WHITE_RATIO:
        r.ok, r.reason = False, "khong_phai_ban_ve_lineart"
        return r

    r.contrast_std = float(gray.std())          # tieu chi 18
    if r.contrast_std < C.MIN_CONTRAST_STD:
        r.ok, r.reason = False, "contrast_thap"
        return r

    # --- LOI MEM: van giu lai, nhung ha do_net xuong "tam" -----------------
    # Tieu chi 17. Crop co the cat vao phan tieu de nen do ca 2 kich thuoc:
    # neu anh goc du 800 thi chi canh bao, khong loai - de buoc thu ban goc
    # va QC nguoi quyet dinh. Day la cho de loai oan mau tot nhat.
    # So voi SOFT_SHORT_EDGE chu KHONG phai MIN_SHORT_EDGE. Nhieu site dang
    # mat bang o co ~1100x700: anh goc nam trong dai mem 640-800 nhung khong
    # dat 800, con ban sau crop thi tut xuong duoi 640 -> neu so voi 800 thi
    # ca hai deu truot va anh bi loai cung. Day la cho giet quota nang nhat.
    short = min(r.width, r.height)
    if short < C.MIN_SHORT_EDGE:
        if full_short >= C.SOFT_SHORT_EDGE or short >= C.SOFT_SHORT_EDGE:
            r.flags.append(f"phan_giai_sat_nguong_{short}px")
            r.soft_fail = True
        else:
            r.ok, r.reason = False, "do_phan_giai_qua_thap"
            r.flags.append("thu_lai_ban_goc")
            return r

    # Ty le canh: loai banner ngang, dai bang doc, anh bia.
    r.aspect = r.width / max(r.height, 1)
    if not (C.ASPECT_MIN <= r.aspect <= C.ASPECT_MAX):
        r.ok, r.reason = False, f"ty_le_canh_bat_thuong_{r.aspect:.2f}"
        return r

    # Dem duong thang ngang/doc - thay cho buoc "co phai mat bang 2D" cua AI.
    r.axis_lines = axis_line_score(gray)
    if r.axis_lines < C.MIN_AXIS_LINES:
        r.ok, r.reason = False, f"it_duong_thang_{r.axis_lines}"
        return r

    # Watermark chim: chi co y nghia tren anh lineart, nen kiem tra sau cung.
    r.gray_center_ratio = gray_center_ratio(gray)
    if r.gray_center_ratio > C.WATERMARK_GRAY_RATIO:
        r.flags.append("nghi_watermark_trung_tam")
        r.soft_fail = True

    return r


class DedupIndex:
    """Chong trung bang pHash + ma du an."""

    def __init__(self, hashes: list[tuple[int, str]] | None = None,
                 codes: set[str] | None = None) -> None:
        self._hashes: list[tuple[int, str]] = list(hashes or [])
        self._codes: set[str] = set(codes or ())

    def seen_code(self, code: str | None) -> bool:
        """CO SIDE EFFECT: ma chua gap se duoc ghi nho ngay tai day."""
        if not code:
            return False
        if code in self._codes:
            return True
        self._codes.add(code)
        return False

    def seen_hash(self, h: int) -> str | None:
        for known, name in self._hashes:
            if hamming(known, h) <= C.PHASH_THRESHOLD:
                return name
        return None

    def add(self, h: int, name: str) -> None:
        self._hashes.append((h, name))

    def __len__(self) -> int:
        return len(self._hashes)
