#!/usr/bin/env python3
import json, os, shutil, subprocess, time, urllib.request
from pathlib import Path

BASE=Path("/content/drive/MyDrive/MiniMax-H3")
COMFY=BASE/"ComfyUI"; EP=BASE/"episodes"/"episode_001"
SHOTS=EP/"shots"; FRAMES=EP/"frames"; FINAL=EP/"final"; STATE=EP/"state.json"
for p in (SHOTS,FRAMES,FINAL): p.mkdir(parents=True,exist_ok=True)
API="http://127.0.0.1:8188"

LOCK="""Family-friendly cinematic 3D cartoon. Preserve the exact approved character identities, proportions, colors, faces and accessories from the reference pictures. Miyav is the mischievous orange-white kitten. Damla is the serious cleanliness-loving blue-white female puppy. Pofu is the innocent clumsy white-brown puppy. Yaprak is the sleepy nature-loving gray-white green-eyed kitten with green leaf accessory. Canta is the intelligent orderly anthropomorphic backpack teacher. No human speech. Communication is facial expression, body language and natural character sounds only. No subtitles or text. Keep environment and object continuity. No morphing, duplicate characters, extra limbs, identity drift or color drift."""

def req(path,data=None):
    body=None if data is None else json.dumps(data).encode()
    r=urllib.request.Request(API+path,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(r,timeout=30) as x:return json.loads(x.read())

def wait_server():
    for _ in range(180):
        try:req("/system_stats"); return
        except:time.sleep(2)
    raise RuntimeError("ComfyUI API acilmadi")

def valid(p):
    if not p.exists() or p.stat().st_size<100000:return False
    q=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)],capture_output=True,text=True)
    try:return float(q.stdout.strip())>3
    except:return False

def last_frame(v,p):
    subprocess.run(["ffmpeg","-y","-sseof","-0.08","-i",str(v),"-frames:v","1",str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def copy_input(src,name):
    dst=COMFY/"input"/name; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst); return name

def refs_for(i):
    refs=[]
    if i>1:
        p=FRAMES/f"shot_{i-1:03d}_last.png"
        if p.exists(): refs.append(p)
    # fixed identity anchors on every shot
    for candidates in [("miyav.png",),("damla.png","damla"),("pofu.png","pofu"),("yaprak.png","yaprak"),("çanta.png","canta.png")]:
        for n in candidates:
            p=BASE/"characters"/n
            if p.exists(): refs.append(p); break
    if not refs: raise RuntimeError("Karakter referanslari bulunamadi")
    return refs[:9]

def workflow(i,prompt,refs):
    w={
      "119":{"class_type":"VAELoader","inputs":{"vae_name":"minimax_h3_video_vae_int8_convrot.safetensors"}},
      "120":{"class_type":"VAELoader","inputs":{"vae_name":"minimax_h3_audio_vae_fp32.safetensors"}},
      "127":{"class_type":"UNETLoader","inputs":{"unet_name":"minimax_h3_ref2va_pruned_int8_convrot.safetensors","weight_dtype":"default"}},
      "128":{"class_type":"CLIPLoader","inputs":{"clip_name":"qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors","type":"minimax","device":"default"}},
      "129":{"class_type":"RandomNoise","inputs":{"noise_seed":3193264261+i}},
      "136":{"class_type":"MiniMaxH3ReferenceToVideo","inputs":{"clip":["128",0],"vae":["119",0],"audio_vae":["120",0],"prompt":prompt+"\n\n"+LOCK,"width":1344,"height":768,"length":124,"ref_image_size":"match"}},
      "126":{"class_type":"BasicGuider","inputs":{"model":["127",0],"conditioning":["136",0]}},
      "123":{"class_type":"KSamplerSelect","inputs":{"sampler_name":"res_multistep"}},
      "124":{"class_type":"BasicScheduler","inputs":{"model":["127",0],"scheduler":"simple","steps":20,"denoise":1.0}},
      "125":{"class_type":"SamplerCustomAdvanced","inputs":{"noise":["129",0],"guider":["126",0],"sampler":["123",0],"sigmas":["124",0],"latent_image":["136",1]}},
      "122":{"class_type":"VAEDecode","inputs":{"samples":["125",0],"vae":["119",0]}},
      "121":{"class_type":"VAEDecodeAudio","inputs":{"samples":["125",0],"vae":["120",0]}},
      "130":{"class_type":"CreateVideo","inputs":{"images":["122",0],"audio":["121",0],"fps":24,"bit_depth":8}},
      "92":{"class_type":"SaveVideo","inputs":{"video":["130",0],"filename_prefix":f"episode_001/shot_{i:03d}","format":"auto","codec":"auto"}}
    }
    for k,src in enumerate(refs):
        nid=str(200+k); name=copy_input(src,f"episode_001_ref_{i:03d}_{k}.png")
        w[nid]={"class_type":"LoadImage","inputs":{"image":name}}
        w["136"]["inputs"][f"ref_images.ref_image_{k}"]=[nid,0]
    return w

def render(i,prompt,refs):
    q=req("/prompt",{"prompt":workflow(i,prompt,refs)})
    pid=q["prompt_id"]
    while True:
        h=req("/history/"+pid)
        if pid in h:
            item=h[pid]
            if item.get("status",{}).get("status_str")=="error": raise RuntimeError(str(item.get("status")))
            outs=item.get("outputs",{}).get("92",{})
            vids=outs.get("videos",[]) or outs.get("gifs",[]) or outs.get("files",[])
            if vids:
                f=vids[0]; src=COMFY/"output"/f.get("subfolder","")/f["filename"]; return src
        time.sleep(5)

plan=json.loads((EP/"plan.json").read_text())
st=json.loads(STATE.read_text()) if STATE.exists() else {"completed":[],"attempts":{}}
wait_server()
for s in plan["shots"]:
    i=s["shot"]; out=SHOTS/f"shot_{i:03d}.mp4"; frame=FRAMES/f"shot_{i:03d}_last.png"
    if valid(out):
        if not frame.exists():last_frame(out,frame)
        continue
    ok=False
    for a in range(1,4):
        st["attempts"][str(i)]=a; STATE.write_text(json.dumps(st,indent=2))
        try:
            made=render(i,s["prompt"],refs_for(i)); shutil.copy2(made,out)
            if valid(out):
                last_frame(out,frame); st["completed"]=sorted(set(st["completed"]+[i])); STATE.write_text(json.dumps(st,indent=2)); ok=True; print(f"PASS {i:03d}/{len(plan['shots'])}"); break
        except Exception as e: print("RETRY",i,a,repr(e))
    if not ok: raise SystemExit(f"Shot {i} basarisiz. Tekrar calistirinca buradan devam edecek.")

lst=EP/"concat.txt"; clips=[SHOTS/f"shot_{i:03d}.mp4" for i in range(1,len(plan["shots"])+1)]
lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips))
joined=EP/"joined.mp4"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(joined)],check=True)
out=FINAL/"episode_001_1080p60.mp4"
subprocess.run(["ffmpeg","-y","-i",str(joined),"-vf","scale=1920:1080:flags=lanczos,fps=60","-c:v","libx264","-crf","18","-preset","medium","-c:a","aac","-b:a","192k",str(out)],check=True)
print("TAMAMLANDI:",out)
