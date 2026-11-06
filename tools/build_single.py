# -*- coding: utf-8 -*-
"""把整个项目打成一个可以直接双击、也能直接发给别人的单文件 HTML。

做四件事：
  1. spine/lib/*.js 五个外部脚本全部内联
  2. 背景图 art/backdrop.png 转 JPEG data URI（有 1px 虚焦，压到 85 质量看不出来）
  3. 四条 320kbps 的音轨重编码成 128kbps 后 base64 内嵌（原文件不动）
  4. 输出到 release/ 下

用法：python tools/build_single.py
"""
import base64
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")
OUT_DIR = os.path.join(ROOT, "release")

TRACKS = ["singer.mp3", "guitar.mp3", "bass.mp3", "drums.mp3"]
BITRATE = 128


def inline_scripts(html):
    """把 spine/lib 下的外部脚本换成内联内容"""
    def repl(m):
        path = m.group(1)
        full = os.path.join(ROOT, path)
        with io.open(full, encoding="utf-8") as f:
            body = f.read()
        return "<script>\n/* ---- %s ---- */\n%s\n</script>" % (path, body)

    return re.sub(r'<script src="(spine/lib/[^"]+)"></script>', repl, html)


def backdrop_data_uri():
    from PIL import Image
    im = Image.open(os.path.join(ROOT, "art", "backdrop.png")).convert("RGB")
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85, optimize=True, progressive=True)
    raw = buf.getvalue()
    print("  backdrop: %dx%d -> %.0f KB (jpeg q85)" % (im.size[0], im.size[1], len(raw) / 1024.0))
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")


def encode_track(name):
    """mp3 -> 128kbps mp3 -> base64"""
    import lameenc
    import miniaudio

    path = os.path.join(ROOT, name)
    dec = miniaudio.decode_file(path, output_format=miniaudio.SampleFormat.SIGNED16,
                               nchannels=2, sample_rate=44100)
    pcm = dec.samples.tobytes()

    enc = lameenc.Encoder()
    enc.set_bit_rate(BITRATE)
    enc.set_in_sample_rate(44100)
    enc.set_channels(2)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()

    orig = os.path.getsize(path) / 1024.0 / 1024.0
    print("  %-11s %5.1f MB -> %5.1f MB  (%d kbps, %.0fs)"
          % (name, orig, len(data) / 1024.0 / 1024.0, BITRATE, dec.num_frames / 44100.0))
    return base64.b64encode(data).decode("ascii")


def main():
    with io.open(SRC, encoding="utf-8") as f:
        html = f.read()

    print("内联资源…")
    html = inline_scripts(html)

    print("背景图：")
    html = html.replace('src="art/backdrop.png"', 'src="%s"' % backdrop_data_uri(), 1)

    print("音轨：")
    parts = []
    for t in TRACKS:
        parts.append('"%s":"%s"' % (t, encode_track(t)))
    audio_js = "<script>\nwindow.EMBED_AUDIO = {\n" + ",\n".join(parts) + "\n};\n</script>\n"

    anchor = "<script>\n(function () {"
    if anchor not in html:
        sys.exit("找不到主脚本入口，index.html 结构变了？")
    html = html.replace(anchor, audio_js + anchor, 1)

    # 单文件版不能有外链
    left = re.findall(r'(?:src|href)="(?!data:|#)([^"]+)"', html)
    if left:
        print("警告：还有外链 ->", set(left))

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "GitStudy-AngelBand-v2.5.0.html")
    with io.open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size = os.path.getsize(out) / 1024.0 / 1024.0
    print("\n输出：%s  (%.1f MB)" % (out, size))


if __name__ == "__main__":
    main()
