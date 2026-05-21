#!/usr/bin/env python3
"""智谱AI 免费模型 — 视觉 / 绘图 / 视频 / 对话  v3"""

import sys, os, base64, json, argparse, time, mimetypes, re, textwrap, subprocess
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
ENHANCE_SUFFIX = "，高质量，细节丰富，专业构图，精美"
RETRY_MAX = 4
RETRY_DELAYS = [1, 2, 4, 8]

# ----- helpers -----
def load_key():
    for var in ["ZHIPU_API_KEY"]:
        if os.environ.get(var):
            return os.environ[var]
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ZHIPU_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

def _req(endpoint, data=None, method="POST"):
    if data is None:
        data = {}
    key = load_key()
    if not key:
        print("请先设置 ZHIPU_API_KEY", file=sys.stderr)
        print("注册 bigmodel.cn → API Key → 写入 ~/skills/glm-vision/.env", file=sys.stderr)
        sys.exit(1)
    url = f"{BASE_URL}{endpoint}"
    headers = {"Authorization": f"Bearer {key}"}
    body = None
    if method != "GET":
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode("utf-8")

    last_err = None
    for attempt in range(RETRY_MAX):
        try:
            with urlopen(Request(url, data=body, headers=headers, method=method), timeout=120) as r:
                return json.loads(r.read().decode("utf-8"))
        except HTTPError as e:
            code = e.code
            err_body = e.read().decode()
            # 内容审核拦截
            try:
                err_data = json.loads(err_body)
                err_code = err_data.get("error", {}).get("code", "")
                if err_code in ("1301", "1310"):
                    print("API 调用被内容安全审核拦截。请尝试修改提示词。", file=sys.stderr)
                    sys.exit(1)
            except json.JSONDecodeError:
                pass
            # 429 / 5xx → 重试
            if code in (429, 500, 502, 503) and attempt < RETRY_MAX - 1:
                wait = RETRY_DELAYS[attempt]
                print(f"  [API {code}] 重试 {attempt+1}/{RETRY_MAX} ({wait}s)...", file=sys.stderr)
                time.sleep(wait)
                last_err = err_body
                continue
            print(f"API 错误 ({code}): {err_body[:200]}", file=sys.stderr)
            sys.exit(1)
        except URLError as e:
            if attempt < RETRY_MAX - 1:
                wait = RETRY_DELAYS[attempt]
                print(f"  [连接失败] 重试 {attempt+1}/{RETRY_MAX} ({wait}s)...", file=sys.stderr)
                time.sleep(wait)
                last_err = str(e)
                continue
            print(f"API 连接失败: {last_err or e}", file=sys.stderr)
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

def _call_model(model, content):
    """调 chat/completions，返回回复文本。"""
    data = {"model": model, "messages": [{"role": "user", "content": content}]}
    r = _req("/chat/completions", data)
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
def do_vision(image_args, question, thinking=False):
    if not question:
        question = "请详细描述这张图片的内容，不要遗漏任何文字、数据、元素或细节。"
    paths = _resolve_images(image_args)
    content = [_encode_image(p) for p in paths]
    content.append({"type": "text", "text": question})
    model = "glm-4.1v-thinking-flash" if thinking else "glm-4v-flash"
    print(_call_model(model, content))

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

        # 自动选模型
        intent = _detect_intent(q)
        model = "glm-4.1v-thinking-flash" if intent == "deep" else "glm-4v-flash"

        try:
            ans = _call_model(model, content)
            label = "智谱分析" if intent == "deep" else "智谱视觉"
            print(f"\n[{label}] {ans}\n")
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

# ----- cli -----
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="智谱 AI 免费模型")
    sp = p.add_subparsers(dest="cmd")

    vp = sp.add_parser("vision", help="图片理解（支持路径或 URL）")
    vp.add_argument("images", nargs="+")
    vp.add_argument("-q", "--question", default=None)
    vp.add_argument("--thinking", action="store_true")

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

    args = p.parse_args()
    if args.cmd == "vision":
        do_vision(args.images, args.question, args.thinking)
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
    else:
        p.print_help()
