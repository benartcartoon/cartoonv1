#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path

NEGATIVE="extra arms, extra legs, extra feet, extra fingers, missing limbs, merged limbs, duplicate character, crossed eyes, eye drift, deformed face, identity drift, inconsistent colors, inconsistent costume, prop teleportation, environment continuity error"

def plan(topic,duration):
    n=math.ceil(duration/5)
    shots=[]
    for i in range(n):
        start=i*5; end=min((i+1)*5,duration)
        shots.append({
          "shot":i+1,"start_sec":start,"end_sec":end,
          "story_goal":f"{topic} — bölüm {i+1}/{n}",
          "start_state":"previous_end_state" if i else "establish_from_reference",
          "action":"WRITE_ACTION_AUTOMATICALLY_FROM_STORY",
          "end_state":"carry_forward_to_next_shot",
          "character_refs":"REQUIRED","environment_ref":"REQUIRED",
          "prompt_rules":["exact character identity","natural anatomy","single clear action","continuity with previous shot"],
          "negative_prompt":NEGATIVE,
          "audio_events":[]
        })
    return {"topic":topic,"duration_sec":duration,"shot_seconds":5,"shot_count":n,"shots":shots}

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--topic",required=True); ap.add_argument("--duration",type=int,default=60); ap.add_argument("--out",default="episode_plan.json")
    a=ap.parse_args()
    Path(a.out).write_text(json.dumps(plan(a.topic,a.duration),ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"Tamamlandı: {math.ceil(a.duration/5)} adet 5 saniyelik shot -> {a.out}")
