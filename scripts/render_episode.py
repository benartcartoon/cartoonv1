#!/usr/bin/env python3
"""Resumable 10-minute WAN2.2 batch renderer for Google Colab.
40 logical scenes x 15s = 120 continuity shots x ~5s.
Each successful shot is saved to Drive and its last frame seeds the next shot.
"""
import json, os, subprocess, time, shutil
from pathlib import Path

DRIVE=Path("/content/drive/MyDrive/MiniMax-H3")
EP=DRIVE/"episodes"/"episode_001"
SHOTS=EP/"shots"; FRAMES=EP/"frames"; FINAL=EP/"final"; STATE=EP/"state.json"
MODEL=Path("/content/drive/MyDrive/Wan2.2-Cartoon/models/Wan2.2-TI2V-5B")
WAN=Path("/content/Wan2.2")
REPO=Path("/content/cartoonv1")
for p in (SHOTS,FRAMES,FINAL): p.mkdir(parents=True,exist_ok=True)

LOCK="""STRICT CHARACTER LOCK. Use the approved reference identity exactly. No human speech. Characters communicate only with facial expression, body language and their fixed species/character vocal sounds. Miyav: mischievous orange-white kitten. Damla: serious cleanliness-loving blue-white female puppy. Pofu: innocent clumsy white-brown puppy. Yaprak: nature-loving sleepy gray-white green-eyed kitten with green leaf accessory. Canta: intelligent orderly teacher anthropomorphic brown backpack. Preserve colors, face, proportions and accessories. Family-friendly cinematic 3D cartoon. No morphing, no duplicate characters, no extra limbs, no identity drift, no text, no camera cuts."""
NEG="extra limbs, duplicate character, deformed face, crossed eyes, identity drift, color drift, costume drift, morphing, human speech, subtitles, text"

def load_plan():
    p=EP/"plan.json"
    if not p.exists(): raise SystemExit(f"Plan yok: {p}")
    return json.loads(p.read_text(encoding="utf-8"))

def state():
    if STATE.exists():
        try:return json.loads(STATE.read_text())
        except:pass
    return {"completed":[],"attempts":{}}

def save_state(s):
    tmp=STATE.with_suffix(".tmp"); tmp.write_text(json.dumps(s,indent=2)); tmp.replace(STATE)

def valid_video(p):
    if not p.exists() or p.stat().st_size<100000:return False
    q=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)],capture_output=True,text=True)
    try:return float(q.stdout.strip())>3
    except:return False

def last_frame(video,out):
    subprocess.run(["ffmpeg","-y","-sseof","-0.08","-i",str(video),"-frames:v","1",str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def first_reference():
    for name in ("miyav.png","Miyav.png"):
        p=DRIVE/"characters"/name
        if p.exists():return p
    raise SystemExit("Miyav referansi bulunamadi: MiniMax-H3/characters/miyav.png")

def render(idx,prompt,image,out):
    seed=3193264261+idx
    cmd=["python",str(WAN/"generate.py"),"--task","ti2v-5B","--size","1280*704","--ckpt_dir",str(MODEL),
         "--image",str(image),"--prompt",prompt+"\n\n"+LOCK,"--frame_num","121","--sample_steps","40",
         "--base_seed",str(seed),"--save_file",str(out)]
    return subprocess.run(cmd,cwd=WAN).returncode==0 and valid_video(out)

def concat(plan):
    clips=[SHOTS/f"shot_{i:03d}.mp4" for i in range(1,len(plan["shots"])+1)]
    lst=EP/"concat.txt"; lst.write_text("".join(f"file '{x.as_posix()}'\n" for x in clips))
    joined=EP/"joined.mp4"
    subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(joined)],check=True)
    out=FINAL/"episode_001_1080p60.mp4"
    subprocess.run(["ffmpeg","-y","-i",str(joined),"-vf","scale=1920:1080:flags=lanczos,fps=60","-c:v","libx264","-crf","18","-preset","medium","-an",str(out)],check=True)
    return out

plan=load_plan(); s=state(); ref=first_reference()
print(f"START: {len(plan['shots'])} continuity shots, target 10 minutes")
for shot in plan["shots"]:
    i=shot["shot"]; out=SHOTS/f"shot_{i:03d}.mp4"; frame=FRAMES/f"shot_{i:03d}_last.png"
    if valid_video(out):
        if not frame.exists(): last_frame(out,frame)
        if i not in s["completed"]: s["completed"].append(i); save_state(s)
        ref=frame; print(f"SKIP PASS {i:03d}"); continue
    if i>1:
        prev=FRAMES/f"shot_{i-1:03d}_last.png"
        if prev.exists(): ref=prev
    ok=False
    for attempt in range(1,4):
        s["attempts"][str(i)]=attempt; save_state(s)
        print(f"RENDER {i:03d}/{len(plan['shots'])} attempt {attempt}/3")
        if render(i,shot["prompt"],ref,out):
            last_frame(out,frame); ref=frame; s["completed"].append(i); save_state(s); ok=True; break
        if out.exists(): out.unlink()
    if not ok: raise SystemExit(f"SHOT {i:03d} 3 denemede basarisiz. Yeniden calistirinca buradan devam eder.")
final=concat(plan)
print("TAMAMLANDI:",final)
