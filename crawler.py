"""Crawler WordPress: listing -> trang du an -> anh mat bang.

Nguyen tac: ton trong robots.txt, delay giua request, ghi ro nguon.
"""
from __future__ import annotations

import re
import time
import urllib.parse as up
import urllib.robotparser as rp

import requests
from bs4 import BeautifulSoup

import config as C

_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": C.USER_AGENT})
_ROBOTS: dict[str, rp.RobotFileParser] = {}
_LAST_HIT: dict[str, float] = {}


# ------------------------------------------------------------------ lich su
def _polite(url: str) -> None:
    host = up.urlparse(url).netloc
    wait = C.REQUEST_DELAY - (time.time() - _LAST_HIT.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _LAST_HIT[host] = time.time()


_SIGNAL: dict[str, str | None] = {}


def ai_train_signal(url: str) -> str | None:
    """Doc Content-Signal trong robots.txt -> gia tri cua 'ai-train'.

    Chuan Content Signals cho phep chu site noi ro tung muc dich su dung.
    'ai-train=no' = khong duoc dung noi dung de huan luyen mo hinh, va ho ghi
    ro day la express reservation of rights theo Dieu 4 Chi thi EU 2019/790.
    Dataset nay sinh ra de huan luyen HC_REPLAN va HC_GEPLAN, dung vao muc do.
    Tra ve 'no' | 'yes' | None (khong khai bao).
    """
    host = up.urlparse(url).netloc
    if host in _SIGNAL:
        return _SIGNAL[host]

    val = None
    try:
        r = _SESSION.get(f"https://{host}/robots.txt", timeout=15)
        if r.status_code == 200:
            for dong in re.findall(r"^\s*Content-Signal:\s*(.+)$", r.text,
                                   re.I | re.M):
                m = re.search(r"ai-train\s*=\s*(\w+)", dong, re.I)
                if m:
                    val = m.group(1).lower()
    except requests.RequestException:
        pass

    _SIGNAL[host] = val
    if val == "no":
        print(f"  [!] {host} khai bao ai-train=no trong robots.txt.")
        print("      Chu site tu choi cho dung noi dung de huan luyen mo hinh.")
        print("      Bo qua nguon nay.")
    return val


def allowed(url: str) -> bool:
    host = up.urlparse(url).netloc
    if host in C.BLACKLIST_DOMAINS:
        return False
    if ai_train_signal(url) == "no":
        return False
    if host not in _ROBOTS:
        parser = rp.RobotFileParser()
        parser.set_url(f"{up.urlparse(url).scheme}://{host}/robots.txt")
        try:
            parser.read()
        except Exception:  # noqa: BLE001
            parser = None
        _ROBOTS[host] = parser
    parser = _ROBOTS[host]
    return True if parser is None else parser.can_fetch(C.USER_AGENT, url)


def get(url: str) -> requests.Response | None:
    if not allowed(url):
        return None
    _polite(url)
    try:
        r = _SESSION.get(url, timeout=C.REQUEST_TIMEOUT)
        return r if r.status_code == 200 else None
    except requests.RequestException:
        return None


# ------------------------------------------------------------------ ban goc
def try_original(url: str) -> str:
    """WordPress sinh nhieu bien the kich thuoc tu 1 file goc.

    Bo hau to -700x557 de lay ban day du -> cuu duoc rat nhieu mau
    bi loai oan vi phan giai thap.
    """
    stripped = re.sub(r"-\d{2,4}x\d{2,4}(?=\.\w+$)", "", url)

    # Chi thu nhung bien the KHAC url ban dau. Thu lai chinh url la vo nghia
    # (that bai thi van tra ve no) ma ton them 1 HEAD + 2.5 giay delay.
    cands: list[str] = []
    for cand in (stripped, re.sub(r"(?=\.\w+$)", "-scaled", stripped, count=1)):
        if cand != url and "-scaled-scaled" not in cand and cand not in cands:
            cands.append(cand)

    for cand in cands:
        if not allowed(cand):
            continue
        _polite(cand)
        try:
            if _SESSION.head(cand, timeout=10).status_code == 200:
                return cand
        except requests.RequestException:
            continue
    return url


# ------------------------------------------------------------------ thu thap
def sitemap_links(sitemap_url: str, pattern: re.Pattern, limit: int) -> list[str]:
    """Liet ke trang du an tu sitemap thay vi duyet listing.

    Dung cho site chan phan trang trong robots.txt. Sitemap la danh sach do
    chinh chu site cong bo cho crawler nen day la duong dung phep va day du.
    """
    resp = get(sitemap_url)
    if resp is None:
        return []

    # sitemap_index tro toi nhieu sitemap con; sitemap thuong chua URL trang.
    con = re.findall(r"<loc>\s*([^<\s]+\.xml)\s*</loc>", resp.text)
    nguon = con or [sitemap_url]

    found: list[str] = []
    seen: set[str] = set()
    for sm in nguon:
        r = get(sm) if sm != sitemap_url else resp
        if r is None:
            continue
        for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text):
            if u.endswith(".xml") or u in seen:
                continue
            if not pattern.search(u):
                continue
            if C.REJECT_PROJECT.search(u):
                continue
            seen.add(u)
            found.append(u)
            if len(found) >= limit:
                return found
    return found


def seed_links(seeds: list[str], pattern: re.Pattern, limit: int) -> list[str]:
    """Di tu vai trang goc, gom cac trang cung chu de tren cung ten mien.

    Dung cho TRANG TONG HOP - kieu bai "15+ mau mat bang biet thu" gom san
    hang chuc ban ve trong mot trang. Mot trang nhu vay bang 15-20 trang du an,
    va nhieu site khong co sitemap nen khong liet ke duong khac duoc.
    Ban than cac seed cung la trang co anh, nen chung nam trong ket qua.
    """
    found: list[str] = []
    seen: set[str] = set()

    for seed in seeds:
        if seed not in seen:
            seen.add(seed)
            found.append(seed)
        resp = get(seed)
        if resp is None:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        host = up.urlparse(seed).netloc
        for a in soup.select("a[href]"):
            href = up.urljoin(seed, a["href"]).split("#")[0].split("?")[0]
            p = up.urlparse(href)
            if p.netloc != host or href in seen:
                continue
            if not pattern.search(p.path) or C.REJECT_PROJECT.search(p.path):
                continue
            seen.add(href)
            found.append(href)
            if len(found) >= limit:
                return found
    return found


def project_links(source_key: str, limit: int = 200) -> list[str]:
    src = C.SOURCES[source_key]
    pattern = re.compile(src["project_url_pattern"])

    if src.get("sitemap"):
        return sitemap_links(src["sitemap"], pattern, limit)

    if src.get("seeds"):
        return seed_links(src["seeds"], pattern, limit)

    found: list[str] = []
    seen: set[str] = set()

    for listing in src["listing"]:
        for page in range(1, src["max_pages"] + 1):
            url = listing if page == 1 else f"{listing.rstrip('/')}/page/{page}/"
            resp = get(url)
            if resp is None:
                break
            soup = BeautifulSoup(resp.text, "html.parser")
            khop = 0          # so link du an tren trang, ke ca da thay roi
            for a in soup.select("a[href]"):
                href = up.urljoin(url, a["href"])
                if not pattern.search(up.urlparse(href).path):
                    continue
                khop += 1
                if href in seen:
                    continue
                # CHI loc theo slug URL. Chu trong the <a> khong dang tin: nhieu
                # the boc ca khoi card nen get_text() quet luon tieu de cua du an
                # ben canh, lam loai oan nhung du an hoan toan hop le.
                slug = up.urlparse(href).path
                if C.REJECT_PROJECT.search(slug):
                    continue          # nha pho / nha ong = quota cua nhom N1
                seen.add(href)
                found.append(href)
                if len(found) >= limit:
                    return found

            # Dung khi trang KHONG CON link du an nao. Truoc day dung khi khong
            # co link MOI nao - nhung cac danh muc cua neohouse trung nhau rat
            # nhieu, nen trang 1 cua danh muc thu ba tro di toan link da thay,
            # lam vong lap thoat ngay va bo mat trang 2-3 cua ba danh muc cuoi.
            if khop == 0:
                break
    return found


def parse_title_meta(title: str) -> dict:
    title = title or ""
    meta = {"so_tang": None, "so_phong_ngu": None, "ma_du_an": None}
    m = C.TITLE_META.search(title)
    if m:
        meta["so_tang"] = int(m.group("tang")) if m.group("tang") else None
        meta["so_phong_ngu"] = int(m.group("pn")) if m.group("pn") else None
    code = C.TITLE_CODE.search(title)
    if code:
        meta["ma_du_an"] = code.group(1).replace(" ", "").upper()
    return meta


_LAZY_ATTR = ("src", "data-src", "data-lazy-src", "data-original",
              "data-lazy", "data-echo")


def _src_that(img) -> str:
    """Lay URL anh THAT tu the <img>, ke ca khi site dung lazy-load.

    Rat nhieu site Viet Nam nap luoi: thuoc tinh `src` chi la anh placeholder
    (hoac trong), con URL that nam o `data-src`. Chi doc `src` la mat trang
    nguon - vinavic.vn co 89 anh nam ngoai `src`, doc thieu thanh 0 ung vien.
    """
    for k in _LAZY_ATTR:
        v = (img.get(k) or "").strip()
        if v and not v.startswith("data:"):
            return v

    # srcset: "anh-480.jpg 480w, anh-1200.jpg 1200w" -> lay ban rong nhat
    for k in ("srcset", "data-srcset"):
        v = (img.get(k) or "").strip()
        if not v:
            continue
        ung = []
        for phan in v.split(","):
            m = phan.strip().split()
            if not m:
                continue
            rong = int(m[1][:-1]) if len(m) > 1 and m[1].endswith("w") else 0
            ung.append((rong, m[0]))
        if ung:
            return max(ung)[1]
    return ""


def scan_project(project_url: str) -> tuple[list[dict], dict]:
    """Nhu candidate_images() nhung tra ve them thong ke tung buoc loc.

    Dung cho lenh `probe`: chi doc HTML, khong tai anh, khong goi AI.
    """
    st = {"the_img": 0, "sai_duoi": 0, "bi_reject_text": 0,
          "khong_khop_accept": 0, "ung_vien": 0, "loi_tai_trang": 0}

    resp = get(project_url)
    if resp is None:
        st["loi_tai_trang"] = 1
        return [], st
    soup = BeautifulSoup(resp.text, "html.parser")

    title = (soup.title.get_text(strip=True) if soup.title else "")
    body_text = soup.get_text(" ", strip=True)[:6000]
    loc = C.VN_HINT.search(title) or C.VN_HINT.search(body_text)
    meta = parse_title_meta(title)

    out: list[dict] = []
    for img in soup.find_all("img"):
        st["the_img"] += 1
        src = up.urljoin(project_url, _src_that(img))
        if not src.lower().split("?")[0].endswith(C.ALLOWED_EXT):
            st["sai_duoi"] += 1
            continue
        alt = img.get("alt", "") or ""
        cap = ""
        fig = img.find_parent("figure")
        if fig and fig.figcaption:
            cap = fig.figcaption.get_text(" ", strip=True)
        # Ten file la tin hieu manh nhat: "mat-bang-...jpg" vs "phoi-canh-...jpg".
        # Alt text cua neohouse thuong chi la tieu de du an, khong ta noi dung anh.
        ten_file = src.rsplit("/", 1)[-1]
        blob = f"{alt} {cap} {ten_file}"

        if C.REJECT_TEXT.search(blob):
            st["bi_reject_text"] += 1
            continue
        if not C.ACCEPT_TEXT.search(blob):
            st["khong_khop_accept"] += 1
            continue

        st["ung_vien"] += 1
        out.append(
            {
                "url": src,
                "alt": alt,
                "caption": cap,
                "title": title,
                "location": loc.group(0) if loc else "",
                "project_url": project_url,
                **meta,
            }
        )
    return out, st


def candidate_images(project_url: str) -> list[dict]:
    """Tra ve danh sach anh UNG VIEN da qua loc alt/caption (chua tai)."""
    return scan_project(project_url)[0]


def download(url: str, dest: str) -> bool:
    if not allowed(url):
        return False
    _polite(url)
    try:
        r = _SESSION.get(url, timeout=C.REQUEST_TIMEOUT, stream=True)
        if r.status_code != 200:
            return False
        with open(dest, "wb") as fh:
            for chunk in r.iter_content(65536):
                fh.write(chunk)
        return True
    except requests.RequestException:
        return False
