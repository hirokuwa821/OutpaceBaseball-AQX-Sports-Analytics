# 3D Spinning Baseball Component for Outpace Baseball
# Emulates Rapsodo / TrackMan 3D pitch spin visualizer

try:
    from src import i18n
except Exception:
    try:
        import i18n
    except Exception:
        i18n = None

def get_baseball_html_template():
    return """<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{margin:0;overflow:hidden;background:transparent;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;user-select:none;}
#c{width:100%;height:285px;position:relative;display:flex;justify-content:center;align-items:center;}
canvas{outline:none;cursor:grab;}canvas:active{cursor:grabbing;}
.hud{position:absolute;bottom:8px;left:50%;transform:translateX(-50%);background:rgba(15,23,42,0.92);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,0.20);border-radius:12px;padding:3px 8px;font-size:10px;font-weight:700;color:#f8fafc;display:flex;align-items:center;justify-content:center;gap:6px;max-width:96%;box-sizing:border-box;box-shadow:0 4px 12px rgba(0,0,0,0.5);pointer-events:none;z-index:10;}
.hud span{white-space:nowrap;}
.grip-tip{position:absolute;bottom:35px;left:50%;transform:translateX(-50%);background:rgba(2,132,199,0.94);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,0.30);border-radius:10px;padding:3px 10px;font-size:9.5px;font-weight:700;color:#ffffff;white-space:nowrap;max-width:94%;overflow:hidden;text-overflow:ellipsis;pointer-events:none;z-index:10;display:none;box-shadow:0 4px 12px rgba(0,0,0,0.4);}
.spd{position:absolute;top:4px;right:6px;background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.25);color:#94a3b8;border-radius:10px;padding:2px 7px;font-size:10px;cursor:pointer;font-weight:700;z-index:10;}
.spd:hover{color:#00d2ff;border-color:#00d2ff;}
.rst{position:absolute;top:4px;left:58px;background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.25);color:#94a3b8;border-radius:10px;padding:2px 6px;font-size:10px;cursor:pointer;font-weight:700;z-index:10;}
.rst:hover{color:#00d2ff;border-color:#00d2ff;}
.mag-btn{position:absolute;top:4px;right:78px;background:rgba(15,23,42,0.75);border:1px solid rgba(0,255,255,0.35);color:#00ffff;border-radius:10px;padding:2px 6px;font-size:10px;cursor:pointer;font-weight:700;z-index:10;}
.mag-btn:hover{color:#38bdf8;border-color:#38bdf8;}
.grip-btn{position:absolute;top:4px;right:132px;background:rgba(15,23,42,0.75);border:1px solid rgba(255,255,255,0.25);color:#38bdf8;border-radius:10px;padding:2px 6px;font-size:10px;cursor:pointer;font-weight:700;z-index:10;}
.grip-btn:hover{color:#67e8f9;border-color:#67e8f9;}
.clk{position:absolute;top:4px;left:6px;font-size:10px;font-weight:700;color:#64748b;background:rgba(15,23,42,0.5);border-radius:6px;padding:2px 5px;pointer-events:none;z-index:10;}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head><body><div id="c">
<div class="clk">12:00 ↑</div>
<button class="rst" onclick="resetCam()" title="Reset Camera">↺</button>
<button class="grip-btn" id="gripBtn" onclick="toggleGrip()" title="Grip Guide: 4S/2S/SL/CH/FS">✋ 4-Seam</button>
<button class="mag-btn" id="magBtn" onclick="toggleMagnus()" title="Magnus Lift Force Vector">__LIFT_BTN_TEXT__</button>
<button class="spd" id="btn" onclick="toggleSpd()">0.1x (Slow)</button>
<div class="grip-tip" id="gripTip"></div>
<div class="hud"><span>🌀 __RPM__ rpm</span><span>⏰ __AXIS__</span><span>📐 __GYRO__° Gyro</span></div>
</div>
__SCRIPT__
</body></html>"""


def get_baseball_script():
    return """<script>
(function(){
  const container=document.getElementById('c'),w=container.clientWidth||240,h=285;
  const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(40,w/h,0.1,100);camera.position.set(0,0,4.2);
  const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});
  renderer.setSize(w,h);renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
  container.appendChild(renderer.domElement);
  scene.add(new THREE.AmbientLight(0xffffff,0.85));
  const l1=new THREE.DirectionalLight(0xffffff,0.9);l1.position.set(3,4,5);scene.add(l1);
  const l2=new THREE.DirectionalLight(0x90b0e0,0.4);l2.position.set(-4,-2,-3);scene.add(l2);

  const worldGroup=new THREE.Group();scene.add(worldGroup);
  const clockRad=(__CLOCK_DEG__*Math.PI)/180.0,axX=Math.sin(clockRad),axY=Math.cos(clockRad);
  const gyroRad=(__GYRO_VAL__*Math.PI)/180.0,sinG=Math.sin(gyroRad),cosG=Math.cos(gyroRad);
  const spinVec=new THREE.Vector3(axX*cosG,axY*cosG,sinG).normalize();
  worldGroup.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),spinVec);

  const rMat=new THREE.MeshStandardMaterial({color:0x2563eb,roughness:0.3}),bkMat=new THREE.MeshStandardMaterial({color:0x0f172a,roughness:0.4}),gMat=new THREE.MeshStandardMaterial({color:0x16a34a,roughness:0.3});
  const rGeom=new THREE.CylinderGeometry(0.035,0.035,0.7,16);
  const mBlue=new THREE.Mesh(rGeom,rMat);mBlue.position.y=1.35;worldGroup.add(mBlue);
  const mBlack=new THREE.Mesh(rGeom,bkMat);mBlack.position.y=-1.35;worldGroup.add(mBlack);

  const capGeom=new THREE.SphereGeometry(0.045,16,16);
  const bCap=new THREE.Mesh(capGeom,rMat);bCap.position.y=1.70;worldGroup.add(bCap);
  const bkCap=new THREE.Mesh(capGeom,bkMat);bkCap.position.y=-1.70;worldGroup.add(bkCap);

  const pGeom=new THREE.CylinderGeometry(0.03,0.03,0.48,16);
  const mGreen=new THREE.Mesh(pGeom,gMat);mGreen.rotation.x=Math.PI/2;mGreen.position.z=1.24;worldGroup.add(mGreen);
  const gCap=new THREE.Mesh(new THREE.SphereGeometry(0.04,16,16),gMat);gCap.position.z=1.48;worldGroup.add(gCap);

  const ball=new THREE.Group();worldGroup.add(ball);
  ball.add(new THREE.Mesh(new THREE.SphereGeometry(1.0,64,64),new THREE.MeshStandardMaterial({color:0xfafaf9,roughness:0.65})));

  // Seam Group in authentic 4-Seam Fastball orientation
  const seamGroup=new THREE.Group();
  ball.add(seamGroup);
  const DEG2RAD = Math.PI / 180.0;
  const rot4S = new THREE.Euler(43.0 * DEG2RAD, 330.0 * DEG2RAD, 15.0 * DEG2RAD);
  seamGroup.rotation.copy(rot4S);

  const seamPts=[];
  for(let i=0;i<=360;i++){
    const t=(i/360)*Math.PI*4.0;
    const phi=Math.PI/2.0-(Math.PI/2.0-0.42)*Math.cos(t);
    const th=t/2.0+0.42*Math.sin(2.0*t);
    const sx=Math.sin(phi)*Math.cos(th),sy=Math.sin(phi)*Math.sin(th),sz=Math.cos(phi);
    seamPts.push(new THREE.Vector3(sx*1.002,sy*1.002,sz*1.002));
  }
  const seamPath=new THREE.CatmullRomCurve3(seamPts,true);
  seamGroup.add(new THREE.Mesh(new THREE.TubeGeometry(seamPath,360,0.013,8,true),new THREE.MeshStandardMaterial({color:0xdc2626,roughness:0.35})));

  const stLines=[];
  for(let j=0;j<108;j++){
    const u=j/108,p=seamPath.getPointAt(u),T=seamPath.getTangentAt(u).normalize(),N=p.clone().normalize();
    const B=new THREE.Vector3().crossVectors(N,T).normalize();
    const p_l=p.clone().add(B.clone().multiplyScalar(0.038)).add(T.clone().multiplyScalar(-0.014)).multiplyScalar(1.004);
    const p_r=p.clone().add(B.clone().multiplyScalar(-0.038)).add(T.clone().multiplyScalar(-0.014)).multiplyScalar(1.004);
    const p_c=p.clone().multiplyScalar(1.004);
    stLines.push(p_l.x,p_l.y,p_l.z,p_c.x,p_c.y,p_c.z);
    stLines.push(p_r.x,p_r.y,p_r.z,p_c.x,p_c.y,p_c.z);
  }
  const stGeom=new THREE.BufferGeometry();stGeom.setAttribute('position',new THREE.Float32BufferAttribute(stLines,3));
  seamGroup.add(new THREE.LineSegments(stGeom,new THREE.LineBasicMaterial({color:0xb91c1c,linewidth:2})));

  // Magnus Lift Vector Arrow (IVB & HB deflection)
  const magnusGroup=new THREE.Group();scene.add(magnusGroup);
  const magArrow=new THREE.Group();magnusGroup.add(magArrow);
  const magMat=new THREE.MeshStandardMaterial({color:0x00ffff,emissive:0x0088bb,roughness:0.2});
  const magCyl=new THREE.Mesh(new THREE.CylinderGeometry(0.024,0.024,0.60,16),magMat);
  magCyl.position.y=1.0+(0.60/2.0);magArrow.add(magCyl);
  const magCone=new THREE.Mesh(new THREE.ConeGeometry(0.065,0.20,16),magMat);
  magCone.position.y=1.0+0.60+0.10;magArrow.add(magCone);
  const liftAngle=Math.atan2(__HB_CM__,__IVB_CM__);
  magArrow.rotation.z=-liftAngle;

  let showMag=true;
  window.toggleMagnus=function(){
    showMag=!showMag;
    magnusGroup.visible=showMag;
    const mb=document.getElementById('magBtn');
    if(mb){mb.style.color=showMag?'#00ffff':'#64748b';mb.style.borderColor=showMag?'rgba(0,255,255,0.4)':'rgba(255,255,255,0.15)';}
  };

  // 3D Grip Guide (Finger placement lines & silhouette overlay)
  const gripGroup=new THREE.Group();ball.add(gripGroup);
  const fMatIdx=new THREE.MeshStandardMaterial({color:0x00e5ff,emissive:0x0088aa,roughness:0.3,transparent:true,opacity:0.85});
  const fMatMid=new THREE.MeshStandardMaterial({color:0x3b82f6,emissive:0x1d4ed8,roughness:0.3,transparent:true,opacity:0.85});
  const fMatThm=new THREE.MeshStandardMaterial({color:0xf97316,emissive:0xc2410c,roughness:0.3,transparent:true,opacity:0.85});

  function buildFingerMesh(ptsArray,mat,tipPadR){
    const vPts=ptsArray.map(p=>new THREE.Vector3(p[0],p[1],p[2]));
    const curve=new THREE.CatmullRomCurve3(vPts);
    const tubeGeom=new THREE.TubeGeometry(curve,16,0.040,8,false);
    const fg=new THREE.Group();fg.add(new THREE.Mesh(tubeGeom,mat));
    const tip=vPts[vPts.length-1];
    const padGeom=new THREE.SphereGeometry(tipPadR||0.065,14,14);padGeom.scale(1.0,0.45,1.1);
    const padMesh=new THREE.Mesh(padGeom,mat);padMesh.position.copy(tip);padMesh.lookAt(0,0,0);
    fg.add(padMesh);
    return fg;
  }

  const grips=[
    {name:'4-Seam',tip:'4-Seam: 馬蹄形(C型)の縫い目を横切るように人差し指と中指を置き、親指は底の革で支える',rot:rot4S,cam:[0,1.8,3.8],idx:[[0.14,0.70,-0.65],[0.15,0.94,-0.22],[0.14,0.98,0.20],[0.12,0.86,0.52]],mid:[[-0.14,0.70,-0.65],[-0.15,0.94,-0.22],[-0.14,0.98,0.20],[-0.12,0.86,0.52]],thm:[[0.0,-0.65,-0.65],[0.0,-0.88,-0.25],[0.0,-0.98,0.15]]},
    {name:'2-Seam',tip:'2-Seam: 狭い平行な2本の縫い目に人差し指と中指を沿わせ、シュート回転を生む',rot:new THREE.Euler(0,0,0),cam:[0,1.8,3.8],idx:[[0.24,0.70,-0.65],[0.25,0.92,-0.20],[0.24,0.96,0.20],[0.23,0.88,0.48]],mid:[[-0.24,0.70,-0.65],[-0.25,0.92,-0.20],[-0.24,0.96,0.20],[-0.23,0.88,0.48]],thm:[[0.0,-0.65,-0.65],[0.0,-0.88,-0.25],[0.0,-0.98,0.10]]},
    {name:'Slider',tip:'Slider: 外側の縫い目に指を寄せ(オフセット)、中指の腹で縫い目の縁を押す',rot:rot4S,cam:[-0.6,1.7,3.8],idx:[[-0.05,0.70,-0.65],[-0.06,0.92,-0.20],[-0.06,0.96,0.20],[-0.06,0.90,0.45]],mid:[[-0.28,0.70,-0.65],[-0.30,0.90,-0.20],[-0.32,0.94,0.20],[-0.33,0.84,0.48]],thm:[[0.20,-0.65,-0.65],[0.22,-0.88,-0.25],[0.25,-0.94,0.15]]},
    {name:'Changeup',tip:'Changeup (サークルチェンジ): 親指と人差し指で側面に輪(OKサイン)を作り中指・薬指で脱力',rot:rot4S,cam:[1.6,1.2,3.8],idx:[[0.45,0.50,0.20],[0.52,0.55,0.40],[0.55,0.45,0.60],[0.50,0.35,0.65]],mid:[[0.0,0.70,-0.65],[0.0,0.94,-0.20],[0.0,0.98,0.20],[0.0,0.88,0.50]],thm:[[0.35,-0.20,0.30],[0.45,-0.05,0.55],[0.50,0.18,0.65],[0.50,0.30,0.65]]},
    {name:'Splitter',tip:'Splitter (フォーク): 縫い目の外側に指を大きく挟み込み、回転を抑えて縦に鋭く落とす',rot:rot4S,cam:[0,1.8,3.8],idx:[[0.48,0.65,-0.55],[0.52,0.80,-0.15],[0.55,0.82,0.15],[0.55,0.75,0.38]],mid:[[-0.48,0.65,-0.55],[-0.52,0.80,-0.15],[-0.55,0.82,0.15],[-0.55,0.75,0.38]],thm:[[0.0,-0.65,-0.65],[0.0,-0.88,-0.25],[0.0,-0.98,0.15]]}
  ];

  let gripStep=0;
  window.toggleGrip=function(){
    gripStep=(gripStep+1)%6;
    const gBtn=document.getElementById('gripBtn'),gTip=document.getElementById('gripTip');
    while(gripGroup.children.length>0){gripGroup.remove(gripGroup.children[0]);}
    if(gripStep===0){
      if(gTip)gTip.style.display='none';
      if(gBtn){gBtn.innerText='__GRIP_OFF_TEXT__';gBtn.style.color='#94a3b8';}
      seamGroup.rotation.copy(rot4S);
    }else{
      const g=grips[gripStep-1];
      seamGroup.rotation.copy(g.rot);
      gripGroup.add(buildFingerMesh(g.idx,fMatIdx,0.070));
      gripGroup.add(buildFingerMesh(g.mid,fMatMid,0.070));
      gripGroup.add(buildFingerMesh(g.thm,fMatThm,0.075));
      if(gTip){gTip.innerText=g.tip;gTip.style.display='block';}
      if(gBtn){gBtn.innerText='✋ '+g.name;gBtn.style.color='#00d2ff';}
      camera.position.set(g.cam[0],g.cam[1],g.cam[2]);
      camera.lookAt(0,0,0);
    }
  };

  let spdFactor=0.1,speeds=[0.1,0.25,0.5,1.0,0.0],labels=['0.1x (Slow)','0.25x','0.5x','1.0x (Real)','⏸ Pause'],sIdx=0;
  window.toggleSpd=function(){sIdx=(sIdx+1)%speeds.length;spdFactor=speeds[sIdx];document.getElementById('btn').innerText=labels[sIdx];};

  window.resetCam=function(){scene.rotation.set(0,0,0);camera.position.set(0,0,4.2);};

  let isDrag=false,px=0,py=0;
  renderer.domElement.addEventListener('mousedown',e=>{isDrag=true;px=e.clientX;py=e.clientY;});
  window.addEventListener('mouseup',()=>{isDrag=false;});
  window.addEventListener('mousemove',e=>{if(!isDrag)return;scene.rotation.y+=(e.clientX-px)*0.015;scene.rotation.x+=(e.clientY-py)*0.015;px=e.clientX;py=e.clientY;});
  renderer.domElement.addEventListener('touchstart',e=>{if(e.touches.length===1){isDrag=true;px=e.touches[0].clientX;py=e.touches[0].clientY;}});
  window.addEventListener('touchend',()=>{isDrag=false;});
  window.addEventListener('touchmove',e=>{if(!isDrag||e.touches.length!==1)return;scene.rotation.y+=(e.touches[0].clientX-px)*0.015;scene.rotation.x+=(e.touches[0].clientY-py)*0.015;px=e.touches[0].clientX;py=e.touches[0].clientY;});
  renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();camera.position.z=Math.min(7,Math.max(2.5,camera.position.z+e.deltaY*0.003));},{passive:false});

  let last=performance.now();
  function animate(now){
    requestAnimationFrame(animate);
    const dt=Math.min((now-last)/1000,0.1);last=now;
    ball.rotation.y+=(__RPM_NUM__/60)*(2*Math.PI)*spdFactor*dt;
    renderer.render(scene,camera);
  }
  requestAnimationFrame(animate);
})();
</script>"""
def generate_3d_spinning_baseball_html(
    spin_axis_str: str,
    spin_rate_rpm: int,
    active_spin_pct: float,
    gyro_angle_deg: float,
    pitch_type: str = "fastball",
    lang: str = "ja",
    ivb_cm: float = 35.0,
    hb_cm: float = 15.0,
) -> str:
    """Rapsodo / TrackMan 風の3Dリアルタイム回転野球ボールHTML（Three.js WebGL）を生成。"""
    try:
        parts = str(spin_axis_str).split(":")
        hrs = int(parts[0])
        mins = int(parts[1]) if len(parts) > 1 else 0
        total_clock_deg = (hrs % 12) * 30.0 + (mins / 60.0) * 30.0
    except Exception:
        total_clock_deg = 0.0

    rpm = int(spin_rate_rpm or 1800)
    eff = float(active_spin_pct or 85.0)
    gyro = float(gyro_angle_deg or 25.0)
    final_ivb = float(ivb_cm if ivb_cm is not None else 35.0)
    final_hb = float(hb_cm if hb_cm is not None else 15.0)

    template = get_baseball_html_template()
    script = get_baseball_script()

    lift_btn_txt = i18n.t("3d_lift_btn", lang) if i18n else "🎯 Lift"
    grip_off_txt = i18n.t("3d_grip_off_btn", lang) if i18n else "✋ Grip OFF"

    script = script.replace("__CLOCK_DEG__", str(total_clock_deg))
    script = script.replace("__GYRO_VAL__", str(gyro))
    script = script.replace("__RPM_NUM__", str(rpm))
    script = script.replace("__IVB_CM__", str(final_ivb))
    script = script.replace("__HB_CM__", str(final_hb))
    script = script.replace("__GRIP_OFF_TEXT__", grip_off_txt)

    html = template.replace("__RPM__", f"{rpm:,}")
    html = html.replace("__AXIS__", str(spin_axis_str))
    html = html.replace("__GYRO__", f"{gyro:.1f}")
    html = html.replace("__LIFT_BTN_TEXT__", lift_btn_txt)
    html = html.replace("__SCRIPT__", script)

    return html

