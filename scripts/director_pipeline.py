#!/usr/bin/env python3
"""CartoonV1 director pipeline: plan -> render hook -> QC -> retry -> audio -> concat -> 1080p/60."""
from __future__ import annotations
import argparse,json,math,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NEG="extra arms, extra legs, extra feet, extra fingers, missing limbs, merged limbs, duplicate character, crossed eyes, eye drift, face deformation, identity drift, color drift, costume drift, prop teleportation, environment continuity error"

def cmd(x): print("+"," ".join(map(str,x)),flush=True); subprocess.run(list(map(str,x)),check=True)
def plan(topic,duration,out):
    n=math.ceil(duration/5); shots=[]
    for i in range(n):
        shots.append({"shot":i+1,"start_sec":i*5,"end_sec":min((i+1)*5,duration),
          "story_goal":f"{topic} | shot {i+1}/{n}","start_state":"previous_end_state" if i else "reference_establish",
          "end_state":"carry_to_next","prompt":"AUTO_STORY_ACTION + exact approved character/environment references + one clear action",
          "negative_prompt":NEG,"audio_events":[]})
    data={"topic":topic,"duration_sec":duration,"shot_seconds":5,"shots":shots}
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); return data

def qc_sidecar(clip):
    # Human/CV detector can write clip.mp4.qc.json with {"pass":true/false,"reasons":[]}.
    p=Path(str(clip)+".qc.json")
    if not p.exists(): return {"pass":False,"reasons":["QC_NOT_RUN"]}
    return json.loads(p.read_text(encoding="utf-8"))

def concat(clips,out):
    lst=out.parent/"concat.txt"; lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in clips),encoding="utf-8")
    cmd(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy",out])

def finish(src,out):
    cmd(["ffmpeg","-y","-i",src,"-vf","scale=1920:1080:flags=lanczos,fps=60","-c:v","libx264","-crf","18","-preset","medium","-c:a","aac","-b:a","192k",out])

def main():
    a=argparse.ArgumentParser(); a.add_argument("--topic",required=True); a.add_argument("--duration",type=int,default=60)
    a.add_argument("--work",default="/content/drive/MyDrive/Wan2.2-Cartoon/jobs/current"); a.add_argument("--max-retries",type=int,default=3)
    x=a.parse_args(); w=Path(x.work); (w/"clips").mkdir(parents=True,exist_ok=True); (w/"audio").mkdir(exist_ok=True)
    data=plan(x.topic,x.duration,w/"episode_plan.json")
    print(f"PLAN: {len(data['shots'])} x 5s")
    print("RENDER CONTRACT: render each clips/shot_XX.mp4 from episode_plan.json using approved references.")
    print("QC CONTRACT: reject anatomy/identity/eye/world-continuity defects; write .qc.json. Retry up to",x.max_retries)
    print("AUDIO CONTRACT: create timecoded diegetic SFX from visible actions; dialogue requires lip-sync; music optional/low.")
    clips=[w/"clips"/f"shot_{s['shot']:02d}.mp4" for s in data["shots"]]
    missing=[str(p) for p in clips if not p.exists()]
    if missing:
        (w/"render_queue.json").write_text(json.dumps({"missing":missing},indent=2),encoding="utf-8")
        print("WAITING_FOR_RENDER:",len(missing),"shots. Queue:",w/"render_queue.json"); return
    failed=[{"clip":str(p),"qc":qc_sidecar(p)} for p in clips if not qc_sidecar(p).get("pass")]
    if failed:
        (w/"retry_queue.json").write_text(json.dumps(failed,ensure_ascii=False,indent=2),encoding="utf-8")
        print("QC_RETRY_REQUIRED:",len(failed),"shots. Queue:",w/"retry_queue.json"); return
    joined=w/"joined.mp4"; concat(clips,joined); final=w/"FINAL_1080P60.mp4"; finish(joined,final)
    print("TAMAMLANDI:",final)
if __name__=="__main__": main()
