"""Cau hinh trung tam cho tool thu thap mat bang (nhom N3)."""
import os
import re

# ---------------------------------------------------------------- nhom / quota
GROUP = "N3"

# Loai nha dang thu thap. Doi bang bien moi truong de chay mot loai khac vao
# mot thu muc rieng, vi du:
#   $env:N3_HOUSE_TYPE = "thoho";  $env:N3_OUT = "./output_thoho"
# Gia tri hop le theo ke hoach: ongpho | cap4 | bietthu | thoho
HOUSE_TYPE = os.environ.get("N3_HOUSE_TYPE", "bietthu")
QUOTA = 3000
MENTOR = "Mr. Phuc"

MILESTONES = {"d1_3": 900, "d4_5": 1500, "d6_8": 2250, "d9": 2700, "final": 3000}
TARGET_PASS_RATE = 0.90

# ---------------------------------------------------------------- nguong may check
MIN_SHORT_EDGE = 800          # tieu chi 17, do SAU khi crop khung ban ve
SOFT_SHORT_EDGE = 640         # duoi nguong nay moi loai thang; 640-800 -> 'tam'
PHASH_THRESHOLD = 8           # Hamming distance <= 8 coi la trung
LINEART_WHITE_RATIO = 0.55    # ban ve CAD nen trang chiem > 55%
WATERMARK_GRAY_RATIO = 0.06   # ty le pixel xam nhat o vung trung tam
MIN_CONTRAST_STD = 25         # do lech chuan xam, tranh anh gan trang/gan den

# Ban ve mat bang co rat nhieu doan thang ngang/doc (tuong, truc, kich thuoc).
# Phoi canh va anh chup thi khong. Day la bo loc mien phi manh nhat con lai
# sau khi bo AI - no thay the mot phan viec "day co phai ban ve 2D khong".
MIN_AXIS_LINES = 12
ASPECT_MIN = 0.35             # loai banner ngang va dai bang doc
ASPECT_MAX = 2.80

MAX_ROOMS_GEPLAN = 8          # tieu chi 20
ALLOWED_EXT = (".jpg", ".jpeg", ".png")

# ---------------------------------------------------------------- loc alt/caption
# Dau phan cach linh hoat: khop ca "mat bang", "mặt bằng" lan "mat-bang" trong
# ten file. Ten file la tin hieu manh nhat tren neohouse va nhieu site WordPress.
_S = r"[\s\-_]*"

# CHI nhan khi co tu chi ban ve. KHONG nhan rieng "N tang" - moi tieu de biet
# thu deu chua "1 tang", nen bat rieng no se keo ve toan bo anh phoi canh.
ACCEPT_TEXT = re.compile(
    rf"(mat{_S}bang|mặt{_S}bằng|"
    rf"cong{_S}nang|công{_S}năng|"
    rf"ban{_S}ve|bản{_S}vẽ|"
    rf"vat{_S}dung|vật{_S}dụng|"
    rf"layout|floor{_S}plan|"
    rf"\bmb{_S}(tang|tầng|\d))",
    re.I,
)

REJECT_TEXT = re.compile(
    rf"(phoi{_S}canh|phối{_S}cảnh|ngoai{_S}that|ngoại{_S}thất|"
    rf"noi{_S}that|nội{_S}thất|mat{_S}tien|mặt{_S}tiền|"
    rf"mat{_S}dung|mặt{_S}đứng|mat{_S}cat|mặt{_S}cắt|"
    rf"khong{_S}gian|không{_S}gian|goc{_S}nhin|góc{_S}nhìn|"
    rf"ho{_S}boi|hồ{_S}bơi|3d|render|sketchup|"
    rf"anh{_S}bia|ảnh{_S}bìa|anh{_S}dai{_S}dien|thumbnail|"
    rf"mat{_S}bang{_S}mai|mặt{_S}bằng{_S}mái|mat{_S}bang{_S}tong{_S}the|"
    rf"ket{_S}cau|kết{_S}cấu|dien{_S}nuoc|điện{_S}nước|pccc|"
    rf"thi{_S}cong|thi{_S}công|hoan{_S}thien|hoàn{_S}thiện)",
    re.I,
)

# Xac nhan cong trinh Viet Nam qua dia danh trong tieu de / bai viet
VN_HINT = re.compile(
    r"(tai\s+|tại\s+)?(ha\s*noi|hà\s*nội|hcm|ho\s*chi\s*minh|hồ\s*chí\s*minh|"
    r"da\s*nang|đà\s*nẵng|hai\s*phong|hải\s*phòng|can\s*tho|cần\s*thơ|"
    r"nghe\s*an|nghệ\s*an|ha\s*tinh|hà\s*tĩnh|thanh\s*hoa|thanh\s*hóa|"
    r"quang\s*(ninh|binh|nam|ngai)|quảng\s*(ninh|bình|nam|ngãi)|"
    r"dong\s*nai|đồng\s*nai|binh\s*duong|bình\s*dương|long\s*an|"
    r"tien\s*giang|tiền\s*giang|ben\s*tre|bến\s*tre|an\s*giang|"
    r"vung\s*tau|vũng\s*tàu|ba\s*ria|bà\s*rịa|tay\s*ninh|tây\s*ninh|"
    r"bac\s*giang|bắc\s*giang|bac\s*ninh|bắc\s*ninh|phu\s*quoc|phú\s*quốc|"
    r"da\s*lat|đà\s*lạt|gia\s*lai|ca\s*mau|cà\s*mau|soc\s*trang|sóc\s*trăng|"
    r"vinh\s*long|vĩnh\s*long|hue|huế|binh\s*thuan|bình\s*thuận|"
    r"gia\s*chu|gia\s*chủ|cong\s*trinh\s*tai|công\s*trình\s*tại)",
    re.I,
)

# Loai bo du an that ra la nha ong (quota cua N1)
REJECT_PROJECT = re.compile(
    r"(biet\s*thu\s*pho|biệt\s*thự\s*phố|"
    r"nha\s*pho|nhà\s*phố|nha-pho|"
    r"mat\s*tien\s*[4-7](\.\d)?\s*m|mặt\s*tiền\s*[4-7](\.\d)?\s*m|"
    r"\b[4-7](\.\d)?\s*x\s*\d{2}\s*m|"
    r"[-/]np\d+/?$)",                  # ma du an NP.. = nha pho
    re.I,
)

# Trich metadata tu tieu de du an neohouse.
# Tach lam 2 regex: nhom optional dat sau `.*?` trong MOT regex se luon
# khop rong (regex ket thuc som), khien ma_du_an mai mai bang None.
TITLE_META = re.compile(
    r"(?P<tang>\d+)\s*[Tt]ầng"
    r"(?:.*?(?P<pn>\d+)\s*[Pp]hòng\s*[Nn]gủ)?",
    re.S,
)

TITLE_CODE = re.compile(r"\b(BT[VB]?\s?\d+)\b", re.I)

# Lay so tang tu alt/caption cua chinh tam anh: "mat bang tang 2", "MB tang tret"
#
# Tieng Viet co HAI cach dat so quanh chu "tang":
#   "1 tang 2 phong ngu"  -> so DUNG TRUOC = so tang cua CAN NHA
#   "mat bang tang 2"     -> so DUNG SAU  = tang cua BAN VE nay
# Chi cai thu hai moi la thu ta can. Khong co lookahead thi "1 tầng 2 phòng ngủ"
# se bi doc thanh "tang 2" - ghep chu "tầng" cua ve nay voi so "2" cua ve kia.
ALT_TANG = re.compile(
    r"(?:tang|tầng)[\s_.-]*(\d)(?![\s_.-]*(?:phong|phòng|pn\b|nguoi|người))",
    re.I,
)
ALT_TRET = re.compile(r"(tret|trệt|tang\s*1|tầng\s*1)", re.I)
ALT_TUM = re.compile(r"(tum|mai|mái)", re.I)

# ---------------------------------------------------------------- nguon
SOURCES = {
    "neohouse": {
        "name": "NEOHouse",
        "listing": [
            "https://neohouse.vn/du-an/biet-thu-1-tang/",   # uu tien: GEPLAN
            "https://neohouse.vn/du-an/biet-thu-dep/",
            "https://neohouse.vn/du-an/biet-thu-nha-vuon/",
            "https://neohouse.vn/du-an/biet-thu-2-tang/",
            "https://neohouse.vn/du-an/biet-thu-3-tang/",
        ],
        "project_url_pattern": r"/portfolio/[^/]+/?$",
        "max_pages": 5,
    },
    # Nguon dung SITEMAP thay vi duyet listing. Bat buoc voi nhung site chan
    # phan trang trong robots.txt - vietnamarch co "Disallow: */page/*", nen
    # duyet listing chi lay duoc trang 1. Sitemap la danh sach chinh chu site
    # cong bo cho crawler, dung no vua day du vua dung phep.
    "vietnamarch_thoho": {
        "name": "Vietnamarch - nha tho ho",
        "sitemap": "https://vietnamarch.com.vn/sitemap_index.xml",
        "project_url_pattern": r"(nha-tho-ho|tu-duong|nha-tho-tu)",
        "listing": [],
        "max_pages": 1,
    },
    # Them nguon moi o day sau khi da kiem tra khong co watermark de len tuong.
    # KHONG dung shac.vn: watermark chay ngang giua ban ve tren MOI anh.
    # KHONG dung sbsvilla.vn: robots.txt khai bao ai-train=no.
}

BLACKLIST_DOMAINS = {"shac.vn", "www.shac.vn"}

# ---------------------------------------------------------------- lich su / IO
USER_AGENT = (
    "N3-InternResearchBot/1.0 (dataset mat bang VN; "
    "lien he: duoghuutri1202@gmail.com)"
)
REQUEST_DELAY = 2.5      # giay giua moi request toi cung 1 domain
REQUEST_TIMEOUT = 20

EXCEL_COLUMNS = [
    "ten_file", "loai_nha", "nguon", "co_noi_that", "do_net",
    "dung_cho_REPLAN", "dung_cho_GEPLAN", "so_phong_uoc",
    "co_boundary_ro", "ghi_chu",
]
