#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
poem-ink 預生成語音管線（Gate 1-2）
- TTS：macOS `say -v Meijia`（zh_TW 女聲，免費可重現；GitHub Actions 可換 edge-tts 同名 voice）
- 精準句時間軸：逐句獨立合成 → ffprobe 量每段秒數 → ffmpeg concat，start/end 用累加算出
  （by-construction forced alignment，誤差 < 50ms，比 Whisper 後對齊更準；若改用單檔 TTS，可再跑 Whisper 重對齊）
- 輸出：audio/NN_read.mp3 + audio/NN_explain.mp3（共 48 檔）+ timings.json + results.tsv
用法：python3 gen_audio.py [--only-timing] [--limit N]
"""
import re, json, subprocess, os, sys, pathlib

BASE = pathlib.Path(__file__).parent
AUD = BASE / "audio"
TMP = BASE / ".tmp_audio"
VOICE = os.environ.get("TTS_VOICE", "Meijia")
RATE = os.environ.get("TTS_RATE", "170")  # 對應前端「適中 .8」
BITRATE = os.environ.get("MP3_BITRATE", "80k")
GAP_READ = 0.35
GAP_EX = 0.45

def sh(*a):
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def dur(p):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(p)],capture_output=True,text=True,check=True)
    return float(r.stdout.strip())

def synth(text, out_mp3):
    aiff = str(out_mp3) + ".aiff"
    subprocess.run(["say","-v",VOICE,"-r",RATE,text,"-o",aiff],check=True)
    subprocess.run(["ffmpeg","-y","-v","error","-i",aiff,"-codec:a","libmp3lame","-b:a",BITRATE,str(out_mp3)],check=True)
    os.remove(aiff)
    return dur(out_mp3)

def silence(sec, out_mp3):
    subprocess.run(["ffmpeg","-y","-v","error","-f","lavfi","-i","anullsrc=r=44100:cl=mono",
        "-t",str(sec),"-codec:a","libmp3lame","-b:a",BITRATE,str(out_mp3)],check=True)

def parse_index():
    t = (BASE/"index.html").read_text(encoding="utf-8")
    # 取 P：用第一個 "const P=[" 到 "\n];\n" 之間（P 陣列結尾是 \n];）
    i = t.find("const P=[")
    j = t.find("\n];", i)
    p_src = t[i:j+3]
    # 取 EX：從 const EX=[ 到 "]];"（EX 結尾是 ]];）
    i2 = t.find("const EX=[")
    j2 = t.find("]];", i2) + 3
    ex_src = t[i2:j2]
    # 用簡易掃描抽字串：P 每首 [標題,詩人,全文,...]
    titles = re.findall(r"\['([^']+)','([^']+)','([^']+)',", p_src)
    exs = re.findall(r'\["((?:[^"\\]|\\.)*)", "((?:[^"\\]|\\.)*)", "((?:[^"\\]|\\.)*)"\]', ex_src)
    assert len(titles) == 24, f"P 解析到 {len(titles)} 首"
    assert len(exs) == 24, f"EX 解析到 {len(exs)} 組"
    return titles, exs

def split_sentences(full):
    return re.findall(r"[^，。；？]+[，。；？]", full)

def explain_tx(e):
    e0, e1, e2 = e
    parts = e1.split("。")
    conv = "".join(["「"+w.split("：")[0]+"」的意思是"+"：".join(w.split("：")[1:])+"。" for w in parts if w.strip() and "：" in w])
    return [e0, "詩裡有幾個詞，我們先來認識一下。" + conv, "簡單來說，" + e2]

def main():
    only_timing = "--only-timing" in sys.argv
    limit = None
    for a in sys.argv:
        if a.startswith("--limit"):
            limit = int(a.split("=")[1] if "=" in a else sys.argv[sys.argv.index(a)+1])
    AUD.mkdir(exist_ok=True); TMP.mkdir(exist_ok=True)
    titles, exs = parse_index()
    timings = []
    results = ["commit\tval_bpb\tmemory_gb\tstatus\tdescription"]
    total_bytes = 0
    n = len(titles) if limit is None else min(limit, len(titles))
    for idx in range(n):
        title, poet, full = titles[idx]
        sents = split_sentences(full)
        read_lines = [f"{title}，{poet.replace('・','，')}"] + sents
        ex_lines = explain_tx(exs[idx])
        for kind, lines, gap in (("read", read_lines, GAP_READ), ("explain", ex_lines, GAP_EX)):
            segs, cur, entries = [], 0.0, []
            for s_i, line in enumerate(lines):
                seg = TMP / f"{idx:02d}_{kind}_{s_i}.mp3"
                if not only_timing or not seg.exists():
                    synth(line, seg)
                d = dur(seg)
                entries.append({"text": line, "start": round(cur,2), "end": round(cur+d,2)})
                segs.append(seg); cur += d
                if s_i < len(lines)-1:
                    g = TMP / f"{idx:02d}_{kind}_gap{s_i}.mp3"
                    if not g.exists():
                        silence(gap, g)
                    segs.append(g); cur += gap
            # concat
            lst = TMP / f"{idx:02d}_{kind}.txt"
            lst.write_text("".join(f"file '{s}'\n" for s in segs), encoding="utf-8")
            out = AUD / f"{idx:02d}_{kind}.mp3"
            subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(lst),
                "-codec:a","libmp3lame","-b:a",BITRATE,str(out)],check=True)
            total_bytes += out.stat().st_size
            # 存 entries（去掉 title 行給前端對應詩句時用 offset；完整保留）
            if kind == "read":
                read_entries, read_total = entries, cur
            else:
                ex_entries, ex_total = entries, cur
        timings.append({"poem_id": idx, "title": title, "read": read_entries,
            "read_total": round(read_total,2), "explain": ex_entries, "explain_total": round(ex_total,2),
            "files": {"read": f"audio/{idx:02d}_read.mp3", "explain": f"audio/{idx:02d}_explain.mp3"}})
        print(f"[{idx+1:02d}/24] {title} read={read_total:.1f}s explain={ex_total:.1f}s")
    (BASE/"timings.json").write_text(json.dumps(timings, ensure_ascii=False, indent=1), encoding="utf-8")
    # results.tsv（autoresearch 改編：baseline 對比）
    with open(BASE/"results.tsv","w",encoding="utf-8") as f:
        f.write("\n".join(results+[
            f"gen-{VOICE}-{RATE}\t-\t-\tkeep\t48 mp3 + timings.json, total {total_bytes/1e6:.1f}MB"]) + "\n")
    # 需要驗證的項目（confidence signaling）：找出end-start異常短/長的句
    low = []
    for t in timings:
        for k in ("read","explain"):
            for s in t[k]:
                dd = s["end"]-s["start"]
                if dd < 1.0 or dd > 15.0:
                    low.append({"poem":t["title"],"kind":k,"text":s["text"][:12],"dur":dd})
    (BASE/"needs_check.json").write_text(json.dumps(low, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK: {n} 首，timings.json + needs_check.json（{len(low)} 項待複聽）")

if __name__ == "__main__":
    main()
