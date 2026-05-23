#!/usr/bin/env python3
"""智谱AI 多模态 — 视觉(GLM-5V) / 绘图 / 视频 / 对话  v5.1 — 稳健执行引擎"""

import sys, os, base64, json, argparse, time, mimetypes, re, textwrap, subprocess
import io, threading
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
ENHANCE_SUFFIX = "，高质量，细节丰富，专业构图，精美"
RETRY_MAX = 4
RETRY_DELAYS = [1, 2, 4, 8]

# ----- helpers -----
def load_key():
    """返回主 API Key（向后兼容）。"""
    return load_keys()[0]

def load_keys():
    """加载所有可用的 API Key（环境变量 + .env 文件），去重。"""
    keys = []
    # 环境变量：ZHIPU_API_KEY, ZHIPU_API_KEY_2, ...
    for i in range(10):
        var = "ZHIPU_API_KEY" if i == 0 else f"ZHIPU_API_KEY_{i}"
        val = os.environ.get(var)
        if val:
            val = val.strip().strip('"').strip("'")
            if val and val not in keys:
                keys.append(val)
    # .env 文件
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if os.path.exists(env_file):
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k.startswith("ZHIPU_API_KEY") and not k.endswith("_PAID") and v and v not in keys:
                    keys.append(v)
    return keys if keys else [""]

def load_paid_key():
    """加载付费 API Key（单 key，用于 GLM-5V-Turbo 视觉）。"""
    key = os.environ.get("ZHIPU_API_KEY_PAID", "")
    if key:
        key = key.strip().strip('"').strip("'")
    if not key:
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
        if os.path.exists(env_file):
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("ZHIPU_API_KEY_PAID="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    return key or ""


# ----- 智能 Key 调度器 -----
_SCHED_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".key_state.json")

class KeyScheduler:
    """多 Key 智能调度：跨进程持久化健康追踪 + round-robin 公平分发。"""
    def __init__(self):
        self.keys = load_keys()
        self._lock = threading.Lock()
        self._state = self._load_state()
        self._health = self._state.get("health", {})
        self._rr = self._state.get("rr", 0)
        for k in self.keys:
            if k not in self._health:
                self._health[k] = {"ok": 0, "err": 0, "last_429": 0.0}

    def _load_state(self):
        try:
            with open(_SCHED_STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_state(self):
        try:
            os.makedirs(os.path.dirname(_SCHED_STATE_FILE), exist_ok=True)
            with open(_SCHED_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({"rr": self._rr, "health": self._health}, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def pick(self):
        """Round-robin 选择，优先健康 key，冷却 key 自动降权。"""
        with self._lock:
            now = time.time()
            healthy = [k for k in self.keys if now - self._health[k]["last_429"] > 30]
            cooling = [k for k in self.keys if now - self._health[k]["last_429"] <= 30]
            pool = healthy if healthy else sorted(cooling, key=lambda k: -self._health[k]["last_429"])
            key = pool[self._rr % len(pool)]
            self._rr = (self._rr + 1) % max(len(pool), 1)
            self._save_state()
            return key

    def ok(self, key):
        with self._lock:
            self._health[key]["ok"] += 1
            self._save_state()

    def fail(self, key):
        with self._lock:
            self._health[key]["err"] += 1
            self._health[key]["last_429"] = time.time()
            self._save_state()

    def best_worker_count(self):
        """根据健康状态推荐并行数。"""
        with self._lock:
            now = time.time()
            healthy = sum(1 for k in self.keys if now - self._health[k]["last_429"] > 30)
            return max(1, min(healthy, len(self.keys)))

    def status(self):
        """返回各 key 状态摘要。"""
        with self._lock:
            lines = []
            for i, k in enumerate(self.keys):
                h = self._health[k]
                cd = max(0, 30 - (time.time() - h["last_429"]))
                tag = "❄️冷却" if cd > 0 else "✅正常"
                lines.append(f"  key{i+1}: {h['ok']}ok/{h['err']}err {tag} ({cd:.0f}s)")
            return "\n".join(lines)

_scheduler = None
def get_scheduler():
    global _scheduler
    if _scheduler is None:
        _scheduler = KeyScheduler()
    return _scheduler


def _req(endpoint, data=None, method="POST"):
    if data is None:
        data = {}
    keys = load_keys()
    if not keys or not keys[0]:
        print("请先设置 ZHIPU_API_KEY", file=sys.stderr)
        print("注册 bigmodel.cn → API Key → 写入 .env", file=sys.stderr)
        sys.exit(1)
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode("utf-8") if method != "GET" else None
    sched = get_scheduler()

    total = RETRY_MAX * len(keys)
    last_err = None
    for attempt in range(total):
        key = sched.pick()
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        try:
            with urlopen(Request(url, data=body, headers=headers, method=method), timeout=120) as r:
                sched.ok(key)
                return json.loads(r.read().decode("utf-8"))
        except HTTPError as e:
            code = e.code
            err_body = e.read().decode()
            try:
                err_data = json.loads(err_body)
                err_code = err_data.get("error", {}).get("code", "")
                if err_code in ("1301", "1310"):
                    print("API 调用被内容安全审核拦截。请尝试修改提示词。", file=sys.stderr)
                    sys.exit(1)
            except json.JSONDecodeError:
                pass
            if code in (429, 500, 502, 503) and attempt < total - 1:
                sched.fail(key)
                wait = RETRY_DELAYS[attempt % len(RETRY_DELAYS)]
                print(f"  [API {code}] 重试 {attempt+1}/{total} ({wait}s)...", file=sys.stderr)
                time.sleep(wait)
                last_err = err_body
                continue
            print(f"API 错误 ({code}): {err_body[:200]}", file=sys.stderr)
            sys.exit(1)
        except URLError as e:
            if attempt < total - 1:
                wait = RETRY_DELAYS[attempt % len(RETRY_DELAYS)]
                print(f"  [连接失败] 重试 {attempt+1}/{total} ({wait}s)...", file=sys.stderr)
                time.sleep(wait)
                last_err = str(e)
                continue
            print(f"API 连接失败: {last_err or e}", file=sys.stderr)
            sys.exit(1)

PAID_RETRY_DELAYS = [1, 2, 4, 8, 16]

def _req_paid(endpoint, data=None, method="POST"):
    """付费 API 请求——单 key 直连，5 次重试 + 1302 限流等待，无调度器开销。"""
    if data is None:
        data = {}
    key = load_paid_key()
    if not key:
        print("请先设置 ZHIPU_API_KEY_PAID", file=sys.stderr)
        sys.exit(1)
    url = f"{BASE_URL}{endpoint}"
    body = json.dumps(data).encode("utf-8") if method != "GET" else None

    for attempt in range(len(PAID_RETRY_DELAYS)):
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        try:
            with urlopen(Request(url, data=body, headers=headers, method=method), timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except HTTPError as e:
            code = e.code
            err_body = e.read().decode()
            try:
                err_data = json.loads(err_body)
                err_code = err_data.get("error", {}).get("code", "")
                if err_code in ("1301", "1310"):
                    print("API 调用被内容安全审核拦截。请尝试修改提示词。", file=sys.stderr)
                    sys.exit(1)
                if err_code == "1302" and attempt < 3:
                    # 账户级限流，等待 30s 再重试
                    wait = 30
                    print(f"  [账户限流 1302] 等待 {wait}s 后重试 ({attempt+1}/3)...", file=sys.stderr)
                    time.sleep(wait)
                    continue
            except json.JSONDecodeError:
                pass
            if code in (429, 500, 502, 503) and attempt < len(PAID_RETRY_DELAYS) - 1:
                wait = PAID_RETRY_DELAYS[attempt]
                print(f"  [付费API {code}] 重试 {attempt+1}/{len(PAID_RETRY_DELAYS)} ({wait}s)...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"付费API 错误 ({code}): {err_body[:200]}", file=sys.stderr)
            sys.exit(1)
        except URLError as e:
            if attempt < len(PAID_RETRY_DELAYS) - 1:
                wait = PAID_RETRY_DELAYS[attempt]
                print(f"  [连接失败] 重试 {attempt+1}/{len(PAID_RETRY_DELAYS)} ({wait}s)...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"API 连接失败: {str(e)}", file=sys.stderr)
            sys.exit(1)

def _download_file(url, timeout=60):
    """下载远程文件到临时路径，返回本地路径。"""
    req = Request(url, headers={"User-Agent": "glm-vision"})
    try:
        with urlopen(req, timeout=timeout) as r:
            suffix = ".png"
            ct = r.headers.get("Content-Type", "")
            if "gif" in ct: suffix = ".gif"
            elif "jpeg" in ct or "jpg" in ct: suffix = ".jpg"
            elif "webp" in ct: suffix = ".webp"
            tmp = f"glm-output/_dl_{int(time.time())}{suffix}"
            os.makedirs("glm-output", exist_ok=True)
            with open(tmp, "wb") as f:
                f.write(r.read())
        return os.path.abspath(tmp)
    except HTTPError as e:
        print(f"下载失败: URL 返回 HTTP {e.code}", file=sys.stderr)
        sys.exit(1)

def _resolve_images(args):
    """args 可以是路径列表或单个 URL → 都返回本地路径列表。"""
    paths = []
    for a in args:
        if a.startswith(("http://", "https://")):
            local = _download_file(a)
            print(f"  已下载: {local}", file=sys.stderr)
            paths.append(local)
        else:
            if not os.path.isfile(a):
                print(f"找不到文件: {a}", file=sys.stderr)
                sys.exit(1)
            paths.append(a)
    return paths

def _encode_image(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    mime, _ = mimetypes.guess_type(path)
    if not mime or not mime.startswith("image/"):
        mime = "image/png"
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}

def _call_model(model, content, paid=False):
    """调 chat/completions，返回回复文本。"""
    data = {"model": model, "messages": [{"role": "user", "content": content}]}
    r = _req_paid("/chat/completions", data) if paid else _req("/chat/completions", data)
    return r["choices"][0]["message"]["content"]

def _open_file(path):
    """用默认程序打开文件（Windows）。
    图片 → 默认查看器打开（已暂停状态）;
    视频 → 定位到文件夹，不自动播放。"""
    try:
        abspath = os.path.abspath(path)
        if path.lower().endswith(".mp4"):
            subprocess.run(["explorer", f"/select,{abspath}"], check=False)
        else:
            os.startfile(abspath)
    except Exception:
        pass

def _detect_intent(question):
    """简单意图识别：自动选模型。"""
    q = question.lower()
    deep = ["分析", "评价", "对比", "区别", "问题", "改进", "建议", "判断",
            "advantage", "disadvantage", "compare", "evaluate", "analyze",
            "怎么样", "如何", "为什么", "原因"]
    if any(d in q for d in deep):
        return "deep"  # 用 thinking 模型
    return "simple"

# ----- commands -----
def do_vision(image_args, question, thinking=False, json_output=False):
    if not question:
        question = "请详细描述这张图片的内容，不要遗漏任何文字、数据、元素或细节。"
    paths = _resolve_images(image_args)
    content = [_encode_image(p) for p in paths]
    content.append({"type": "text", "text": question})
    result = _call_model("glm-5v-turbo", content, paid=True)
    if json_output:
        print(json.dumps({"success": True, "result": result, "model": "glm-5v-turbo", "images": image_args}, ensure_ascii=False))
    else:
        print(result)

def do_chat(image_args):
    """交互式视觉对话模式"""
    paths = _resolve_images(image_args)
    print(textwrap.dedent(f"""\
    ╔══════════════════════════════════════╗
    ║  视觉对话模式                        ║
    ║  输入问题开始对话，输入 exit 退出     ║
    ╚══════════════════════════════════════╝
    图片: {', '.join(os.path.basename(p) for p in paths)}
    """))

    # 会话历史（用于上下文传递，但每次仍传图以保证视觉精度）
    history = []

    while True:
        try:
            q = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n退出对话模式。")
            break

        if not q:
            continue
        if q in ("exit", "quit", "退出"):
            print("退出对话模式。")
            break

        # 构建 content
        content = [_encode_image(p) for p in paths]
        # 如果有多轮上下文，追加
        for h in history[-4:]:  # 保留最近 2 轮上下文
            content.append({"type": "text", "text": h["q"]})
            content.append({"type": "text", "text": h["a"]})
        content.append({"type": "text", "text": q})

        try:
            ans = _call_model("glm-5v-turbo", content, paid=True)
            print(f"\n[智谱视觉] {ans}\n")
            history.append({"q": q, "a": ans})
        except SystemExit:
            print("\n[错误] API 调用失败，可重试或输入 exit 退出。")

def do_draw(prompt, output_path, size="1024x1024", enhance=False):
    if enhance:
        prompt = prompt.rstrip("。，,;；") + ENHANCE_SUFFIX
    data = {"model": "cogview-3-flash", "prompt": prompt, "size": size, "watermark": False}
    r = _req("/images/generations", data)
    if "data" not in r or not r["data"] or "url" not in r["data"][0]:
        print(f"绘图 API 返回异常: {json.dumps(r, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)
    img_url = r["data"][0]["url"]
    if not output_path:
        os.makedirs("glm-output", exist_ok=True)
        output_path = f"glm-output/image_{int(time.time())}.png"
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    try:
        with urlopen(Request(img_url, headers={"User-Agent": "glm-vision"}), timeout=60) as rp:
            with open(output_path, "wb") as f:
                f.write(rp.read())
        abspath = os.path.abspath(output_path)
        print(f"IMAGE_SAVED:{abspath}")
        _open_file(abspath)
    except URLError as e:
        code = getattr(e, "code", "?")
        err = e.read().decode()[:200] if hasattr(e, "read") else str(e)
        print(f"图片下载失败 (HTTP {code}): {err}", file=sys.stderr)
        sys.exit(1)

def do_video_submit(prompt, image_path=None):
    data = {"model": "cogvideox-flash", "prompt": prompt}
    if image_path:
        if os.path.isfile(image_path):
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            data["image_url"] = f"data:image/png;base64,{b64}"
        else:
            print(f"找不到图片: {image_path}", file=sys.stderr)
            sys.exit(1)
    r = _req("/videos/generations", data)
    task_id = r.get("id") or r.get("task_id")
    if not task_id:
        print("VIDEO_ERROR:任务提交失败", file=sys.stderr)
        print(json.dumps(r, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    print(f"TASK_ID:{task_id}")

def do_video_poll(task_id):
    try:
        sr = _req(f"/async-result/{task_id}", method="GET")
    except SystemExit:
        return
    ts = sr.get("task_status", "")
    if ts == "SUCCESS":
        url = sr.get("video_result", [{}])[0].get("url", "")
        if url: print(f"VIDEO_READY:{url}")
        else: print("VIDEO_ERROR:结果无链接", file=sys.stderr)
    elif ts == "FAIL": print("VIDEO_FAILED")
    else: print("VIDEO_PENDING")

def _progress_bar(current, total, width=20):
    """生成简易进度条字符串。"""
    ratio = current / total if total > 0 else 0
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {int(ratio * 100)}%"

def do_video(prompt, image_path=None):
    """一站式视频生成：自动重试提交 → 轮询 → 下载打开"""
    poll_interval = 15
    max_polls = 60

    # --- 提交阶段：负载高时自动重试 ---
    data = {"model": "cogvideox-flash", "prompt": prompt}
    if image_path:
        if os.path.isfile(image_path):
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            data["image_url"] = f"data:image/png;base64,{b64}"
        else:
            print(f"找不到图片: {image_path}", file=sys.stderr)
            sys.exit(1)

    task_id = None
    print("提交视频任务...", file=sys.stderr)
    for idx, wait in enumerate([10, 30, 60, 120, 120]):
        try:
            r = _req("/videos/generations", data)
            task_id = r.get("id") or r.get("task_id")
            if task_id:
                break
            print("VIDEO_ERROR:任务提交失败", file=sys.stderr)
            print(json.dumps(r, ensure_ascii=False), file=sys.stderr)
            sys.exit(1)
        except SystemExit:
            print(f"  [重试 {idx+1}/5] 模型负载高，{wait}秒后重试...", file=sys.stderr)
            time.sleep(wait)

    if not task_id:
        print("VIDEO_FAILED:提交失败，模型持续负载过高", file=sys.stderr)
        sys.exit(1)

    print(f"TASK_ID:{task_id}")
    print("等待视频生成...", file=sys.stderr)

    # --- 轮询阶段 ---
    for i in range(max_polls):
        bar = _progress_bar(i, max_polls)
        print(f"\r  生成中 {bar}  已等待 {i*poll_interval}s/{max_polls*poll_interval}s", end="", file=sys.stderr)
        try:
            sr = _req(f"/async-result/{task_id}", method="GET")
        except SystemExit:
            time.sleep(poll_interval)
            continue

        ts = sr.get("task_status", "")
        if ts == "SUCCESS":
            url = sr.get("video_result", [{}])[0].get("url", "")
            if not url:
                print("VIDEO_ERROR:结果无链接", file=sys.stderr)
                sys.exit(1)
            os.makedirs("glm-output", exist_ok=True)
            path = f"glm-output/video_{int(time.time())}.mp4"
            print("\r  ✓ 生成完成，下载视频...                          ", file=sys.stderr)
            try:
                with urlopen(Request(url, headers={"User-Agent": "glm-vision"}), timeout=300) as rp:
                    with open(path, "wb") as f:
                        f.write(rp.read())
                abspath = os.path.abspath(path)
                print(f"VIDEO_SAVED:{abspath}")
                _open_file(abspath)
                return
            except URLError as e:
                code = getattr(e, "code", "?")
                err = e.read().decode()[:200] if hasattr(e, "read") else str(e)
                print(f"下载失败 (HTTP {code}): {err}", file=sys.stderr)
                sys.exit(1)
        elif ts == "FAIL":
            print("\r  VIDEO_FAILED                                 ", file=sys.stderr)
            sys.exit(1)

        time.sleep(poll_interval)

    print("\r  VIDEO_TIMEOUT:生成超时                              ", file=sys.stderr)
    sys.exit(1)

def do_video_download(url, output_path):
    if not output_path:
        os.makedirs("glm-output", exist_ok=True)
        output_path = f"glm-output/video_{int(time.time())}.mp4"
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    try:
        with urlopen(Request(url, headers={"User-Agent": "glm-vision"}), timeout=300) as rp:
            with open(output_path, "wb") as f:
                f.write(rp.read())
        print(f"VIDEO_SAVED:{os.path.abspath(output_path)}")
        _open_file(os.path.abspath(output_path))
    except URLError as e:
        code = getattr(e, "code", "?")
        err = e.read().decode()[:200] if hasattr(e, "read") else str(e)
        print(f"下载失败 (HTTP {code}): {err}", file=sys.stderr)
        sys.exit(1)

def do_keys_status():
    """显示所有 key 的健康状态。"""
    sched = get_scheduler()
    print(f"免费 API Key（{len(sched.keys)} 个），推荐并行数 {sched.best_worker_count()}：")
    print(sched.status())
    paid = load_paid_key()
    if paid:
        masked = paid[:8] + "..." + paid[-4:]
        print(f"付费 API Key（GLM-5V-Turbo）: {masked} ✅")
    else:
        print("付费 API Key（GLM-5V-Turbo）: 未设置 ❌")

def do_queue(prompt_file, workers=None, size="1024x1024", enhance=False):
    """从文件逐行读取提示词，多 Key 并行生成图片。"""
    with open(prompt_file, encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]

    if not prompts:
        print("队列为空")
        return

    print(f"队列共 {len(prompts)} 条提示词")
    do_batch_draw(prompts, size=size, enhance=enhance, workers=workers)

def do_batch_draw(prompts, size="1024x1024", enhance=False, workers=None):
    """并行生成多张图片——每个子进程独立调度，自动调节并行数。"""
    script = os.path.abspath(__file__)
    base = ["python", script, "draw"]
    if enhance: base.append("--enhance")
    if size != "1024x1024": base.extend(["--size", size])
    if workers is None:
        workers = get_scheduler().best_worker_count()

    with ThreadPoolExecutor(max_workers=min(workers, len(prompts))) as ex:
        futures = {ex.submit(subprocess.run, base + [p], capture_output=True, encoding="utf-8", errors="replace", timeout=180): p for p in prompts}
        for f in as_completed(futures):
            p = futures[f][:40]
            r = f.result()
            if r.returncode == 0:
                out = (r.stdout or "").strip()
                print(f"✅ {p[:40]} → {out}")
            else:
                err = (r.stderr or "").strip()[:120]
                print(f"❌ {p[:40]} → {err}")

def do_batch_vision(images, question=None, thinking=False, workers=None, json_output=False):
    """串行多图理解——付费 key 并发为 1，逐张处理，显示进度。"""
    if not question:
        question = "请详细描述这张图片的内容，不要遗漏任何文字、数据、元素或细节。"
    resolved = _resolve_images(images)
    total = len(resolved)
    results = []
    ok_count = 0
    fail_count = 0

    for idx, path in enumerate(resolved, 1):
        name = os.path.basename(path)
        print(f"[{idx}/{total}] {name} ...", file=sys.stderr)
        content = [_encode_image(path)]
        content.append({"type": "text", "text": question})
        try:
            ans = _call_model("glm-5v-turbo", content, paid=True)
            ok_count += 1
            if json_output:
                results.append({"image": name, "success": True, "result": ans})
            else:
                print(f"[OK] {name}: {ans[:200]}")
        except BaseException as e:
            fail_count += 1
            err_msg = str(e).strip()[:200]
            if json_output:
                results.append({"image": name, "success": False, "error": err_msg})
            else:
                print(f"[FAIL] {name}: {err_msg}")

    if json_output:
        print(json.dumps({"success": ok_count > 0, "total": total, "ok": ok_count, "fail": fail_count, "results": results}, ensure_ascii=False))
    else:
        print(f"\n完成: {ok_count}/{total} 成功, {fail_count}/{total} 失败", file=sys.stderr)

# ----- cli -----
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="智谱 AI 多模态模型")
    sp = p.add_subparsers(dest="cmd")

    vp = sp.add_parser("vision", help="图片理解（支持路径或 URL）")
    vp.add_argument("images", nargs="+")
    vp.add_argument("-q", "--question", default=None)
    vp.add_argument("--thinking", action="store_true")
    vp.add_argument("--json", action="store_true", help="输出 JSON 格式")

    cp = sp.add_parser("chat", help="交互式视觉对话（支持路径或 URL）")
    cp.add_argument("images", nargs="+")

    dp = sp.add_parser("draw", help="AI 绘图")
    dp.add_argument("prompt")
    dp.add_argument("output_path", nargs="?", default=None)
    dp.add_argument("--size", default="1024x1024", choices=["1024x1024", "1280x720", "720x1280"])
    dp.add_argument("--enhance", action="store_true", help="自动增强 prompt 质量")

    vs = sp.add_parser("video-submit", help="提交视频任务")
    vs.add_argument("prompt")
    vs.add_argument("--image", default=None, help="参考图片路径（图生视频）")
    sp.add_parser("video-poll", help="查询视频状态").add_argument("task_id")
    vd = sp.add_parser("video-download", help="下载视频")
    vd.add_argument("url")
    vd.add_argument("output_path", nargs="?", default=None)

    v = sp.add_parser("video", help="一站式生成视频（自动提交 → 轮询 → 下载打开）")
    v.add_argument("prompt")
    v.add_argument("--image", default=None, help="参考图片路径（图生视频）")

    kp = sp.add_parser("keys", help="查看 API Key 健康状态")

    qp = sp.add_parser("queue", help="从文件逐行读取提示词并行生成")
    qp.add_argument("file", help="提示词文件（每行一个）")
    qp.add_argument("--workers", type=int, default=None, help="并行数")
    qp.add_argument("--size", default="1024x1024", choices=["1024x1024", "1280x720", "720x1280"])
    qp.add_argument("--enhance", action="store_true")

    bdp = sp.add_parser("batch-draw", help="并行生成多张图片")
    bdp.add_argument("prompts", nargs="+")
    bdp.add_argument("--size", default="1024x1024", choices=["1024x1024", "1280x720", "720x1280"])
    bdp.add_argument("--enhance", action="store_true")
    bdp.add_argument("--workers", type=int, default=None, help="并行数（默认 auto）")

    bvp = sp.add_parser("batch-vision", help="并行图片理解")
    bvp.add_argument("images", nargs="+")
    bvp.add_argument("-q", "--question", default=None)
    bvp.add_argument("--thinking", action="store_true")
    bvp.add_argument("--workers", type=int, default=None, help="保留兼容，付费 key 实际串行")
    bvp.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = p.parse_args()
    if args.cmd == "vision":
        do_vision(args.images, args.question, args.thinking, getattr(args, "json", False))
    elif args.cmd == "chat":
        do_chat(args.images)
    elif args.cmd == "draw":
        do_draw(args.prompt, args.output_path, args.size, args.enhance)
    elif args.cmd == "video-submit":
        do_video_submit(args.prompt, args.image)
    elif args.cmd == "video-poll":
        do_video_poll(args.task_id)
    elif args.cmd == "video-download":
        do_video_download(args.url, args.output_path)
    elif args.cmd == "video":
        do_video(args.prompt, args.image)
    elif args.cmd == "keys":
        do_keys_status()
    elif args.cmd == "queue":
        do_queue(args.file, args.workers, args.size, args.enhance)
    elif args.cmd == "batch-draw":
        do_batch_draw(args.prompts, args.size, args.enhance, args.workers)
    elif args.cmd == "batch-vision":
        do_batch_vision(args.images, args.question, args.thinking, args.workers, getattr(args, "json", False))
    else:
        p.print_help()
