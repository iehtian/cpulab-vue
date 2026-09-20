import time
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import FloatRect, Locator, Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from requests.utils import dict_to_sequence

# --- 配置 ---
TARGET_URL = "https://dygx1.cpu.edu.cn/lims/!equipments/equipment/index.386.reserv"
SSO_LOGIN_URL = (
    "https://id.cpu.edu.cn/sso/login"
    "?service=https%3A%2F%2Fdygx1.cpu.edu.cn%2Fgateway%2Flogin"
    "%3Ffrom%3Dcpu%26redirect%3Dhttps%253A%252F%252Fdygx1.cpu.edu.cn"
    "%252Flims%252F%2521people%252Fcpu%252Flogin"
)
STORAGE_STATE_FILE = Path(__file__).parent / "playwright_state.json"
OUTPUT_FILE = Path(__file__).parent / "output_origin.html"
OUTPUT_CLICKED_FILE = Path(__file__).parent / "output_clicked.html"
OUTPUT_SCREENSHOT = Path(__file__).parent / "output_clicked.png"

TIMEOUT = 30_000  # 网络空闲等待超时（毫秒）
CLICK_TIMEOUT = 15_000  # 点击后等待弹窗超时（毫秒）

EXTRA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


# =============================================================================
# 页面日历结构说明
# =============================================================================
# 页面使用双层叠加布局实现仪器预约日历：
#
#   底层: <tbody class="hour_grid">
#         ├── 每行 = 半小时，每列 = 一周中的某天
#         ├── <td class="hour_cell R{row}C{col}"> 是空的，无 innerHTML
#         └── 这些 td 的白色背景透出来就是"可预约空块"
#
#   顶层: <div class="hour_components">
#         ├── 绝对定位的 <div class="block block_*"> 覆盖在底层格子上
#         ├── block_fixed  (class="block_7")  = 非工作时间（灰色，不可预约）
#         ├── block_default(class="block_0~5") = 已有预约（彩色，含用户信息）
#         ├── block_hover                      = 鼠标悬停时 JS 临时创建，离开即销毁
#         └── 没有被任何 block 覆盖的 hour_cell 区域 = 可预约时段（视觉上是白色空块）
#
#   关键认知:
#   - 可预约空块不是 DOM 元素！在 DevTools 里找不到它们
#   - 它们是底层 hour_cell 没有被顶层 block 遮住的"负空间"
#   - 鼠标悬停时 JS 根据坐标计算时段，临时插入 block_hover 显示高亮
#   - 点击/拖拽时 JS 根据坐标计算起止时间，弹出预约表单
#
#   模拟点击某时段的方法:
#   1. 定位到 hour_cell td（通过 class R{row}C{col}）
#   2. 获取其 bounding box
#   3. 在 box 内计算目标时间的 y 坐标（每半小时 = 1 row, 高度 = box.height）
#   4. page.mouse.click(x, y) 在该坐标点击
#   5. 等待弹出的预约表单出现
#
#   示例: 点击周一(今天) 10:00-10:30 的格子
#   cell = page.locator("td.hour_cell.today.R20C1")  # row 20 = 10:00
#   box = cell.bounding_box()
#   page.mouse.click(box.x + box.width/2, box.y + box.height/2)
# =============================================================================


def _needs_login(page_or_resp) -> bool:
    """判断是否需要登录：被重定向到 CAS 或返回 401。"""
    url = page_or_resp.url if hasattr(page_or_resp, "url") else page_or_resp
    return "id.cpu.edu.cn" in url or "/error/" in url


def _create_context(browser):
    """创建 browser context，如有 storage_state 则加载。"""
    kwargs = {
        "viewport": {"width": 1920, "height": 1080},
        "extra_http_headers": EXTRA_HEADERS,
    }
    if STORAGE_STATE_FILE.exists():
        try:
            kwargs["storage_state"] = str(STORAGE_STATE_FILE)
            print(f"[INFO] 已加载 storage_state: {STORAGE_STATE_FILE}")
        except (OSError, ValueError) as e:
            print(f"[WARN] storage_state 加载失败: {e}")
    return browser.new_context(**kwargs)


def sso_login(page: Page, username: str, password: str) -> bool:
    """在 headless 浏览器中完成 CAS SSO 登录，返回是否成功。"""

    if not username:
        print("[ERROR] 用户名为空")
        return False
    if not password:
        print("[ERROR] 密码为空")
        return False

    print("[步骤2] 正在打开登录页面...")
    page.goto(SSO_LOGIN_URL)
    page.wait_for_load_state("networkidle")

    page.fill("#username", username)
    page.fill("#password", password)

    print("[步骤2] 提交登录...")
    page.click("#submit")

    # 等待离开 CAS 域名（跟随重定向）
    try:
        page.wait_for_url(lambda u: "id.cpu.edu.cn" not in u, timeout=15_000)
    except PlaywrightTimeout:
        print("[ERROR] 登录超时，仍在 CAS 页面")
        print(f"  当前 URL: {page.url}")
        return False

    page.wait_for_load_state("networkidle")

    if "id.cpu.edu.cn" in page.url:
        print(f"[ERROR] 登录失败，当前 URL: {page.url}")
        return False

    print("[INFO] 登录成功")
    return True


def _sso_login(page) -> bool:
    """在 headless 浏览器中完成 CAS SSO 登录，返回是否成功。"""
    import os

    username = os.environ.get("LIMS_USER", "")
    password = os.environ.get("LIMS_PASS", "")

    if not username:
        username = input("请输入用户名: ").strip()
    if not password:
        password = input("请输入密码: ").strip()

    if not username:
        print("[ERROR] 用户名为空")
        return False
    if not password:
        print("[ERROR] 密码为空")
        return False

    print("[步骤2] 正在打开登录页面...")
    page.goto(SSO_LOGIN_URL)
    page.wait_for_load_state("networkidle")

    page.fill("#username", username)
    page.fill("#password", password)

    print("[步骤2] 提交登录...")
    page.click("#submit")

    # 等待离开 CAS 域名（跟随重定向）
    try:
        page.wait_for_url(lambda u: "id.cpu.edu.cn" not in u, timeout=15_000)
    except PlaywrightTimeout:
        print("[ERROR] 登录超时，仍在 CAS 页面")
        print(f"  当前 URL: {page.url}")
        return False

    page.wait_for_load_state("networkidle")

    if "id.cpu.edu.cn" in page.url:
        print(f"[ERROR] 登录失败，当前 URL: {page.url}")
        return False

    print("[INFO] 登录成功")
    return True


from flask import jsonify
from playwright.sync_api import StorageState


@dataclass
class DygxRunResponse:
    ok: bool = True
    storage_state: StorageState | None = None
    error: str | None = ""


# LIMS 预约块的 block_N 类别 → 前端显示用色（与 LIMS 原始颜色不完全一致，占位可调）。
BLOCK_COLOR_MAP = {
    0: "#FDE68A",  # 黄
    1: "#93C5FD",  # 蓝
    2: "#86EFAC",  # 绿
    3: "#F9A8D4",  # 粉
    4: "#C4B5FD",  # 紫
    5: "#FCA5A5",  # 红
}

# 编辑弹窗中「删除」按钮的候选 selector（真实 DOM 需实测确认，按序尝试第一个命中者）。
DELETE_BUTTON_SELECTORS = (
    'input[name="delete"]',
    'input.button_delete',
    'a[name="delete"]',
    'button.button_delete',
)


def parse_week_bookings(page: Page) -> dict:
    """
    解析 LIMS 预约页当前显示的周视图，返回结构化预约数据。

    结构说明（见文件顶部注释）：
      - 顶层 .hour_components 下有一组 .block.block_default 绝对定位块
      - block_fixed / block_7 = 非工作时间（type=off_hour，无 user_name）
      - block_0 ~ block_5        = 已有预约（type=booking，含预约人）
      - 列映射：left / 237.281  → C0(周日)..C6(周六)
      - 时间映射：top / 25      → 半小时行号；height / 25 → 半小时数

    返回：
      {
        "days": ["2026-08-23", ...],   # LIMS 顺序（周日→周六），7 项
        "bookings": [
          {
            "date": "2026-08-23",       # 绝对日期，前端按此匹配列
            "start_row": 28,            # 起始半小时行号（0-47）
            "half_hours": 4,            # 持续半小时数
            "type": "booking"|"off_hour",
            "color": "#F9A8D4",         # 显示色（十六进制）
            "color_class": 3,           # 原始 block_N
            "user_name": "宋名格",       # 仅 booking 有，off_hour 为 None
          },
          ...
        ],
      }
    """
    result = page.evaluate(
        """
        () => {
          const COL_W = 237.281;   // 每列像素宽
          const HALF_H = 25;       // 每半小时像素高

          // 1) 读取 7 天表头日期（周日→周六）
          const headerCells = document.querySelectorAll(
            'table.calendar_week thead th.header'
          );
          const days = [];
          headerCells.forEach((th) => {
            const small = th.querySelector('small');
            const txt = small ? small.textContent.trim() : '';
            days.push(txt.replace(/\\//g, '-'));
          });
          if (days.length !== 7) {
            throw new Error('未找到 7 天表头，实际 ' + days.length);
          }

          // 2) 读取所有预约/非工作 block
          const bookings = [];
          document.querySelectorAll('.hour_components .block.block_default')
            .forEach((b) => {
              const cls = b.className || '';
              const isFixed = cls.indexOf('block_fixed') >= 0;
              const m = cls.match(/block_(\\d+)/);
              const colorClass = m ? parseInt(m[1], 10) : -1;

              const st = b.style;
              const left = parseFloat(st.left) || 0;
              const top = parseFloat(st.top) || 0;
              const height = parseFloat(st.height) || 0;

              const col = Math.round(left / COL_W);
              const date = days[col];
              if (date === undefined || col < 0 || col > 6) return;

              const start_row = Math.round(top / HALF_H);
              const half_hours = Math.max(1, Math.round(height / HALF_H));

              let user_name = null;
              if (!isFixed) {
                const a = b.querySelector('.content a.prevent_default');
                if (a) {
                  // 形如「宋名格-18266165762」，去掉尾部手机号
                  user_name = a.textContent.trim().replace(/-\\d{6,}$/, '');
                }
              }

              bookings.push({
                date: date,
                start_row: start_row,
                half_hours: half_hours,
                type: isFixed ? 'off_hour' : 'booking',
                color_class: colorClass,
                user_name: user_name,
              });
            });

          // 3) 读取当前登录人真实姓名（侧边栏）
          const nameEl = document.querySelector('.sidebar_current_user .name a');
          const current_user_name = nameEl ? nameEl.textContent.trim() : null;

          return { days: days, bookings: bookings, current_user_name: current_user_name };
        }
        """
    )
    # 在 Python 侧补上十六进制颜色，前端直接用
    for b in result["bookings"]:
        b["color"] = BLOCK_COLOR_MAP.get(b["color_class"], "#CBD5E1")
    return result


def _click_target_cell(page) -> DygxRunResponse | None:
    """
    切换到下周并点击周四 10:00-11:00 的格子触发预约弹窗。
    成功返回 None，失败返回带 error 的 DygxRunResponse。
    """
    print("[步骤5] 等待日历 JS 完全初始化...")
    # networkidle 后 Q.Calendar 可能还在通过 setTimeout/RAF 创建 block，
    # 等待 hour_components 容器内的 block 数量稳定
    try:
        page.wait_for_load_state("networkidle")
    except PlaywrightTimeout:
        pass
    page.wait_for_timeout(3_000)  # 给 JS 初始化留足时间
    next_week_a = page.get_by_role("link", name="下周 »")
    next_week_a.first.click()
    page.wait_for_timeout(3_000)  # 给 JS 初始化留足时间
    # 周四 = C4, 10:00 = R20 (每行半小时, 20*0.5=10)
    target_selector = "td.hour_cell.R20C4"
    print(f"[步骤5] 定位周四 10:00 格子: {target_selector}")
    target_cell = page.locator(target_selector)

    if target_cell.count() == 0:
        print("[ERROR] 未找到目标格子，可能列映射有误")
        return DygxRunResponse(ok=False, error="未找到目标格子")

    # 直接点击目标格子触发预约弹窗
    target_cell.dblclick(force=True)
    return None


def _do_booking(page) -> tuple[str, DygxRunResponse | None]:
    """
    内部辅助函数：执行核心预约流程（等待页面、切换下周、点击格子、保存结果）。
    返回 (初始 html, 失败时的 DygxRunResponse；成功时第二个值为 None)
    """
    # --- 等待动态内容加载 ---
    print("[步骤4] 等待页面数据加载...")
    try:
        page.wait_for_load_state("networkidle")
    except PlaywrightTimeout:
        print("[WARN] networkidle 超时，使用当前页面内容")

    # --- 保存初始页面 ---
    print(f"[OK] 最终 URL: {page.url}")
    html = page.content()
    print(f"[OK] 内容长度: {len(html)} 字符")

    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"[OK] 已保存到 {OUTPUT_FILE}")

    # --- 模拟点击周四 10:00-11:00 ---
    # err_resp = _click_target_cell(page)
    # if err_resp is not None:
    #     return html, err_resp

    # try:
    #     page.wait_for_selector(".dialog_border", timeout=5_000)
    # except PlaywrightTimeout:
    #     print("[ERROR] 预约弹窗超时未出现")

    # # --- 保存点击后结果 ---
    # clicked_html = page.content()
    # print(
    #     f"[OK] 点击后内容长度: {len(clicked_html)} 字符"
    #     f"（初始: {len(html)} 字符, "
    #     f"增量: {len(clicked_html) - len(html)} 字符）"
    # )

    # OUTPUT_CLICKED_FILE.write_text(clicked_html, encoding="utf-8")
    # print(f"[OK] 点击后 HTML 已保存到 {OUTPUT_CLICKED_FILE}")

    # page.screenshot(path=str(OUTPUT_SCREENSHOT), full_page=False)
    # print(f"[OK] 截图已保存到 {OUTPUT_SCREENSHOT}")
    return html, None


def dygx_run_with_login(username: str, password: str) -> DygxRunResponse:
    """
    使用用户名密码登录后执行预约操作。
    返回包含 storage_state 的 DygxRunResponse，供后续调用复用登录态。
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=EXTRA_HEADERS,
        )
        page = context.new_page()
        status: StorageState | None = None
        try:
            # --- 登录 ---
            if not sso_login(page, username, password):
                return DygxRunResponse(ok=False, error="登录失败")

            # --- 访问目标页面 ---
            print("[步骤3] 访问目标页面...")
            page.goto(TARGET_URL, wait_until="domcontentloaded")

            # 持久化 storage_state
            status = context.storage_state()
            print(f"[INFO] storage_state 已获取")

            # --- 核心预约操作 ---
            _html, err_resp = _do_booking(page)
            if err_resp is not None:
                err_resp.storage_state = status
                return err_resp

            return DygxRunResponse(storage_state=status)
        finally:
            context.close()
            browser.close()


def _compute_week_offset(target_date: str, current_sunday: str) -> int:
    """计算目标日期所在 LIMS 周（周日起始）相对当前周的偏移（单位：周）。"""
    from datetime import date, timedelta

    t = date.fromisoformat(target_date)
    target_sunday = t - timedelta(days=(t.weekday() + 1) % 7)
    cur = date.fromisoformat(current_sunday)
    return (target_sunday - cur).days // 7


def _goto_week(page: Page, target_date: str) -> None:
    """把页面导航到包含 target_date 的那一周（LIMS 周为周日→周六）。"""
    # 当前周日（header days[0]）
    current = parse_week_bookings(page)
    current_sunday = current["days"][0]

    offset = _compute_week_offset(target_date, current_sunday)
    if offset == 0:
        return

    # 只点击可见表格里的「上周/下周」链接（隐藏的 calendar_week_header 里也有一份）
    visible = page.locator('table[id^="calweek_"]')
    if offset > 0:
        link = visible.get_by_role("link", name="下周 »")
    else:
        link = visible.get_by_role("link", name="« 上周")

    for i in range(abs(offset)):
        print(f"[步骤4] 切换周 {i + 1}/{abs(offset)} ...")
        link.first.click()
        page.wait_for_timeout(3_000)  # 给 JS 重新渲染留足时间


def _delete_local_state() -> None:
    """删除本地缓存的 storage_state 文件（登录态已过期时调用）。"""
    try:
        if STORAGE_STATE_FILE.exists():
            STORAGE_STATE_FILE.unlink()
            print(f"[INFO] 已删除过期 storage_state: {STORAGE_STATE_FILE}")
    except OSError as e:
        print(f"[WARN] 删除 storage_state 失败: {e}")


def dygx_fetch_with_state(
    storage_state: StorageState, date: str | None = None
) -> tuple[dict | None, str | None]:
    """
    使用已有 storage_state 打开 LIMS 预约页，一次性完成：
      1. 刷新登录态（返回新的 storage_state）
      2. 抓取并解析当前周预约情况

    若登录态已过期（被重定向到 CAS/401），返回 error="expired" 并删除本地缓存文件。

    参数：
      storage_state: Playwright 登录态
      date: 目标日期（YYYY-MM-DD），None 表示当前周

    返回 (result, error)：
      成功 result: {"storage_state", "days", "bookings", "current_user_name"}
      过期 error: "expired"
      其他失败 error: 具体错误信息
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=EXTRA_HEADERS,
            storage_state=storage_state,
        )
        page = context.new_page()
        try:
            print("[步骤3] 访问目标页面...")
            page.goto(TARGET_URL, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle")
            except PlaywrightTimeout:
                print("[WARN] networkidle 超时，使用当前页面内容")
            page.wait_for_timeout(3_000)  # 给 Q.Calendar 初始化留足时间

            # 登录态过期检测：storage_state 失效时会被重定向到 CAS 或 /error/ 页
            if _needs_login(page):
                print(f"[ERROR] 登录态已过期，当前 URL: {page.url}")
                _delete_local_state()
                return None, "expired"

            # 刷新登录态（延长 cookie 有效期）
            status = context.storage_state()

            # 保存初始页面（调试用）
            html = page.content()
            OUTPUT_FILE.write_text(html, encoding="utf-8")
            print(f"[OK] 最终 URL: {page.url}，内容长度: {len(html)} 字符")

            if date:
                _goto_week(page, date)

            bookings = parse_week_bookings(page)
            print(
                f"[OK] 解析到 {len(bookings['bookings'])} 个预约块，"
                f"日期范围 {bookings['days'][0]} ~ {bookings['days'][-1]}"
            )
            return {
                "storage_state": status,
                "days": bookings["days"],
                "bookings": bookings["bookings"],
                "current_user_name": bookings["current_user_name"],
            }, None
        except Exception as e:
            print(f"[ERROR] 抓取预约失败: {e}")
            return None, str(e)
        finally:
            context.close()
            browser.close()


def _set_lims_select(page: Page, name: str, value: str) -> None:
    """设置 LIMS 自定义下拉框（隐藏 <select>）的值并触发 change 事件。"""
    page.evaluate(
        """
        ([name, value]) => {
          const sel = document.querySelector(`select[name="${name}"]`);
          if (!sel) return false;
          sel.value = value;
          sel.dispatchEvent(new Event('change', { bubbles: true }));
          return true;
        }
        """,
        [name, value],
    )


def _read_select_options(page: Page, name: str) -> list[dict]:
    """读取 LIMS 表单中指定 <select name=...> 的所有选项，返回 [{value, text}]。"""
    return page.evaluate(
        """
        (name) => Array.from(
          document.querySelectorAll(`select[name="${name}"] option`)
        ).map((o) => ({ value: o.value, text: o.textContent.trim() }))
        """,
        name,
    )


def _first_real_option(options: list[dict]) -> tuple[str, str] | None:
    """取第一个有效项（value 非空且非占位符 "0"），无则返回 None。"""
    for o in options or []:
        value = o.get("value")
        if value and value != "0":
            return (value, o.get("text", ""))
    return None


def _pick_option(page: Page, name: str) -> tuple[str, str] | None:
    """读取下拉并选中第一个有效项；读取失败或为空时返回 None（调用方回退 "0"）。"""
    try:
        return _first_real_option(_read_select_options(page, name))
    except Exception as e:
        print(f"[WARN] 读取下拉 {name} 失败，将不选择: {e}")
        return None


def _drag_select(
    start_cell: Locator,
    end_cell: Locator,
    sbox: FloatRect,
    ebox: FloatRect,
) -> None:
    """用 locator.drag_to 从起始格顶部拖到结束格底部，覆盖完整整半点。"""
    start_cell.drag_to(
        end_cell,
        source_position={
            "x": sbox["width"] / 2,
            "y": max(1.0, sbox["height"] * 0.15),
        },
        target_position={
            "x": ebox["width"] / 2,
            "y": ebox["height"] - max(1.0, ebox["height"] * 0.15),
        },
    )


def dygx_book(
    storage_state: StorageState,
    date: str,
    start_row: int,
    half_hours: int,
    name: str = "仪器使用预约",
    description: str = "",
    count: str = "1",
) -> tuple[dict | None, str | None]:
    """在 LIMS 上提交一条预约。

    参数：
      date: 目标日期（YYYY-MM-DD）
      start_row: 起始半小时行号（0-47）
      half_hours: 持续半小时数
      name: 预约主题（默认「仪器使用预约」）
      description: 备注
      count: 样品数

    「关联项目 / 经费卡号」由后端读取下拉并自动选择第一个有效项（空则不选，
    提交 "0"），无需调用方传入。

    返回 (result, error)：成功 result 含 success/name/description/count 及
    project/fund_card_no（各为 {value, text} 或 null），失败 error 为错误信息。
    """
    from datetime import date as _date

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=EXTRA_HEADERS,
            storage_state=storage_state,
        )
        page = context.new_page()
        try:
            print("[步骤3] 访问目标页面...")
            page.goto(TARGET_URL, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle")
            except PlaywrightTimeout:
                print("[WARN] networkidle 超时，使用当前页面内容")
            page.wait_for_timeout(3_000)

            _goto_week(page, date)

            # 计算日期在 LIMS 周中的列索引（周日=0 .. 周六=6）
            t = _date.fromisoformat(date)
            col = (t.weekday() + 1) % 7

            end_row = start_row + half_hours - 1
            start_selector = f"td.hour_cell.R{start_row}C{col}"
            end_selector = f"td.hour_cell.R{end_row}C{col}"

            print(f"[步骤5] 拖拽选中 {date} 行{start_row}~{end_row} (列{col})")
            start_cell = page.locator(start_selector)
            if start_cell.count() == 0:
                return None, f"未找到目标格子 {start_selector}"
            end_cell = page.locator(end_selector)
            if end_cell.count() == 0:
                return None, f"未找到目标格子 {end_selector}"

            # 关键：bounding_box 不负责把元素滚进视口。目标格可能在视口下方
            # （如 row25 → y≈1107 > 视口高 1080），导致坐标/鼠标事件全部落空。
            # 必须先显式滚到视口中心，再取坐标。
            start_cell.evaluate(
                "el => el.scrollIntoView({ block: 'center', behavior: 'instant' })"
            )
            page.wait_for_timeout(300)

            sbox = start_cell.bounding_box()
            ebox = end_cell.bounding_box()
            if sbox is None or ebox is None:
                return None, "目标格子不可见，无法定位坐标"

            # 日历 JS 可能尚未就绪，拖拽后弹窗偶发不出现，做少量重试
            dialog_opened = False
            for attempt in range(1, 4):
                _drag_select(start_cell, end_cell, sbox, ebox)
                try:
                    page.wait_for_selector(".dialog_border", timeout=5_000)
                    dialog_opened = True
                    break
                except PlaywrightTimeout:
                    print(f"[WARN] 第 {attempt} 次拖拽未弹出预约窗口")
                    # 清除可能残留的选中块，稍作等待后重试
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(2_000)

            if not dialog_opened:
                return None, "拖拽后预约弹窗未出现（日历可能未就绪）"
            print("[OK] 预约窗口已出现")

            # 等待表单体（AJAX）加载完成。
            # LIMS 用自定义下拉控件，原生 <select> 被 display:none 隐藏（可见的是
            # 旁边的 .dropdown_container），因此这里必须用 state="attached"（等它
            # 出现在 DOM 中），不能用默认的 state="visible"，否则永远超时。
            page.wait_for_selector(
                'select[name="fund_card_no"]', state="attached", timeout=CLICK_TIMEOUT
            )

            print("[步骤6] 读取下拉选项并填充预约表单...")
            project_pick = _pick_option(page, "project")
            fund_pick = _pick_option(page, "fund_card_no")
            project_val = project_pick[0] if project_pick else "0"
            fund_val = fund_pick[0] if fund_pick else "0"

            if name:
                page.fill('input[name="name"]', name)
            page.fill('textarea[name="description"]', description or "")
            page.fill('input[name="count"]', str(count or "1"))
            _set_lims_select(page, "project", project_val)
            _set_lims_select(page, "fund_card_no", fund_val)

            print("[步骤7] 提交预约...")
            page.click('input[name="save"]')

            # 等待页面反应（弹窗关闭/成功提示），随后由调用方决定是否刷新。
            page.wait_for_timeout(2_000)
            return {
                "success": True,
                "name": name or "仪器使用预约",
                "description": description or "",
                "count": str(count or "1"),
                "project": (
                    {"value": project_pick[0], "text": project_pick[1]}
                    if project_pick else None
                ),
                "fund_card_no": (
                    {"value": fund_pick[0], "text": fund_pick[1]}
                    if fund_pick else None
                ),
            }, None
        except Exception as e:
            print(f"[ERROR] 提交预约失败: {e}")
            return None, str(e)
        finally:
            context.close()
            browser.close()


def _open_booking_dialog(page: Page, date: str, start_row: int, half_hours: int) -> bool:
    """点击原预约最后一个块，打开 LIMS 编辑弹窗。返回是否成功打开。"""
    from datetime import date as _date

    t = _date.fromisoformat(date)
    col = (t.weekday() + 1) % 7
    end_row = start_row + half_hours - 1
    cell_selector = f"td.hour_cell.R{end_row}C{col}"

    cell = page.locator(cell_selector)
    if cell.count() == 0:
        print(f"[ERROR] 未找到原预约最后一块 {cell_selector}")
        return False

    cell.evaluate("el => el.scrollIntoView({ block: 'center', behavior: 'instant' })")
    page.wait_for_timeout(300)
    box = cell.bounding_box()
    if box is not None:
        # 点击最后一块几何中心（命中覆盖其上的 .block，打开编辑弹窗）
        page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        try:
            page.wait_for_selector(".dialog_border", timeout=5_000)
            return True
        except PlaywrightTimeout:
            print("[WARN] 点击最后一块未打开编辑弹窗，尝试 fallback")

    # fallback：用 JS 定位匹配 (col, start_row, half_hours) 的 .block，点其底边
    rect = page.evaluate(
        """
        ([col, startRow, halfHours]) => {
          const COL_W = 237.281, HALF_H = 25;
          const blocks = document.querySelectorAll('.hour_components .block.block_default');
          for (const b of blocks) {
            const st = b.style;
            const left = parseFloat(st.left) || 0;
            const top = parseFloat(st.top) || 0;
            const height = parseFloat(st.height) || 0;
            const c = Math.round(left / COL_W);
            const r = Math.round(top / HALF_H);
            const h = Math.max(1, Math.round(height / HALF_H));
            if (c === col && r === startRow && h === halfHours) {
              b.scrollIntoView({ block: 'center', behavior: 'instant' });
              const rect = b.getBoundingClientRect();
              return { x: rect.left + rect.width / 2, y: rect.bottom - 1 };
            }
          }
          return null;
        }
        """,
        [col, start_row, half_hours],
    )
    if rect is None:
        print("[ERROR] 未找到匹配的预约块")
        return False
    page.wait_for_timeout(300)
    page.mouse.click(rect["x"], rect["y"])
    try:
        page.wait_for_selector(".dialog_border", timeout=5_000)
        return True
    except PlaywrightTimeout:
        print("[ERROR] 编辑弹窗超时未出现")
        return False


def _set_datetime_range(
    page: Page, start_row: int, half_hours: int, new_start_row: int, new_half_hours: int
) -> None:
    """读取编辑弹窗预填的 dtstart/dtend，按差值推算新值并写回（避免时区问题）。"""
    old_start, old_end = page.evaluate(
        """
        () => {
          const s = document.querySelector('input[name="dtstart"]');
          const e = document.querySelector('input[name="dtend"]');
          return [parseInt(s.value, 10), parseInt(e.value, 10)];
        }
        """
    )
    end_row = start_row + half_hours - 1
    new_end_row = new_start_row + new_half_hours - 1
    new_start = old_start + (new_start_row - start_row) * 1800
    new_end = old_end + (new_end_row - end_row) * 1800
    page.evaluate(
        """
        ([startTs, endTs]) => {
          const s = document.querySelector('input[name="dtstart"]');
          const e = document.querySelector('input[name="dtend"]');
          s.value = String(startTs);
          e.value = String(endTs);
          s.dispatchEvent(new Event('change', { bubbles: true }));
          e.dispatchEvent(new Event('change', { bubbles: true }));
        }
        """,
        [new_start, new_end],
    )


def dygx_modify(
    storage_state: StorageState,
    date: str,
    start_row: int,
    half_hours: int,
    new_start_row: int,
    new_half_hours: int,
) -> tuple[dict | None, str | None]:
    """修改一条已有预约的起止时间（只改 dtstart/dtend，其余字段沿用弹窗预填值）。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=EXTRA_HEADERS,
            storage_state=storage_state,
        )
        page = context.new_page()
        try:
            print("[步骤3] 访问目标页面...")
            page.goto(TARGET_URL, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle")
            except PlaywrightTimeout:
                print("[WARN] networkidle 超时，使用当前页面内容")
            page.wait_for_timeout(3_000)

            if _needs_login(page):
                _delete_local_state()
                return None, "expired"

            _goto_week(page, date)

            if not _open_booking_dialog(page, date, start_row, half_hours):
                return None, "未打开编辑弹窗"

            print("[步骤6] 改写起止时间...")
            _set_datetime_range(page, start_row, half_hours, new_start_row, new_half_hours)

            print("[步骤7] 提交修改...")
            page.click('input[name="save"]')
            page.wait_for_timeout(2_000)
            return {
                "success": True,
                "new_start_row": new_start_row,
                "new_half_hours": new_half_hours,
            }, None
        except Exception as e:
            print(f"[ERROR] 修改预约失败: {e}")
            return None, str(e)
        finally:
            context.close()
            browser.close()


def dygx_delete(
    storage_state: StorageState,
    date: str,
    start_row: int,
    half_hours: int,
) -> tuple[dict | None, str | None]:
    """删除一条已有预约。"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            extra_http_headers=EXTRA_HEADERS,
            storage_state=storage_state,
        )
        page = context.new_page()
        try:
            print("[步骤3] 访问目标页面...")
            page.goto(TARGET_URL, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle")
            except PlaywrightTimeout:
                print("[WARN] networkidle 超时，使用当前页面内容")
            page.wait_for_timeout(3_000)

            if _needs_login(page):
                _delete_local_state()
                return None, "expired"

            _goto_week(page, date)

            if not _open_booking_dialog(page, date, start_row, half_hours):
                return None, "未打开编辑弹窗"

            print("[步骤7] 点击删除...")
            delete_clicked = False
            for selector in DELETE_BUTTON_SELECTORS:
                btn = page.locator(selector)
                if btn.count() > 0:
                    btn.first.click()
                    delete_clicked = True
                    break
            if not delete_clicked:
                return None, "未找到删除按钮"
            page.wait_for_timeout(2_000)
            return {"success": True}, None
        except Exception as e:
            print(f"[ERROR] 删除预约失败: {e}")
            return None, str(e)
        finally:
            context.close()
            browser.close()


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # --- 尝试复用 storage_state ---
        context = _create_context(browser)

        page = context.new_page()

        # 监听 JS 控制台输出和未捕获异常
        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

        print("[步骤1] 先访问sso，再访问目标页面...")

        page.goto(SSO_LOGIN_URL)
        page.wait_for_load_state("networkidle")

        page.goto(TARGET_URL)
        page.wait_for_load_state("networkidle")
        # --- 检查是否需要登录 ---
        if _needs_login(page):
            print("[INFO] 需要登录，storage_state 无效或已过期")
            context.close()

            # 用干净 context 登录
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                extra_http_headers=EXTRA_HEADERS,
            )
            page = context.new_page()

            if not _sso_login(page):
                browser.close()
                return

            # 访问目标页面
            print("[步骤3] 访问目标页面...")
            page.goto(TARGET_URL, wait_until="domcontentloaded")

            # 持久化 storage_state
            context.storage_state(path=str(STORAGE_STATE_FILE))

            print(f"[INFO] storage_state 已保存到 {STORAGE_STATE_FILE}")

        # --- 等待动态内容加载 ---
        print("[步骤4] 等待页面数据加载...")
        try:
            page.wait_for_load_state("networkidle")
        except PlaywrightTimeout:
            print("[WARN] networkidle 超时，使用当前页面内容")

        # --- 保存初始页面 ---
        print(f"[OK] 最终 URL: {page.url}")
        html = page.content()
        print(f"[OK] 内容长度: {len(html)} 字符")

        OUTPUT_FILE.write_text(html, encoding="utf-8")
        print(f"[OK] 已保存到 {OUTPUT_FILE}")

        # --- 模拟点击周三 13:00-13:30 ---
        print("[步骤5] 等待日历 JS 完全初始化...")
        # networkidle 后 Q.Calendar 可能还在通过 setTimeout/RAF 创建 block，
        # 等待 hour_components 容器内的 block 数量稳定
        try:
            page.wait_for_load_state("networkidle")
        except PlaywrightTimeout:
            pass
        page.wait_for_timeout(3_000)  # 给 JS 初始化留足时间
        # next_week_a = page.get_by_role("link", name="下周 »")
        # next_week_a.first.click()
        # page.wait_for_timeout(3_000)  # 给 JS 初始化留足时间
        # 周三 = C3, 9:00 = R18 (每行半小时, 18*0.5=9)
        target_selector = "td.hour_cell.R18C3"
        print(f"[步骤5] 定位周三 9:00 格子: {target_selector}")
        target_cell = page.locator(target_selector)

        if target_cell.count() == 0:
            print("[ERROR] 未找到目标格子，可能列映射有误")
            return

        # 直接点击目标格子触发预约弹窗
        target_cell.dblclick(force=True)
        try:
            page.wait_for_selector(".dialog_border", timeout=10_000)
        except PlaywrightTimeout:
            print("[ERROR] 预约弹窗超时未出现")

        # --- 保存点击后结果 ---
        clicked_html = page.content()
        print(
            f"[OK] 点击后内容长度: {len(clicked_html)} 字符"
            f"（初始: {len(html)} 字符, "
            f"增量: {len(clicked_html) - len(html)} 字符）"
        )

        OUTPUT_CLICKED_FILE.write_text(clicked_html, encoding="utf-8")
        print(f"[OK] 点击后 HTML 已保存到 {OUTPUT_CLICKED_FILE}")

        page.screenshot(path=str(OUTPUT_SCREENSHOT), full_page=False)
        print(f"[OK] 截图已保存到 {OUTPUT_SCREENSHOT}")
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
