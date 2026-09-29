// Démons H13ris en 3D (three.js r128). makeDemon(opts) -> THREE.Group, pieds en y=0, hauteur ~2.4 (adulte).
(function(){
const T=THREE;
const hsl=(h,s,l)=>new T.Color().setHSL(h/360,s,l).convertSRGBToLinear();
const col=c=>(c instanceof T.Color)?c:new T.Color(c).convertSRGBToLinear();
function mat(c,opts={}){if(opts.emissive)opts.emissive=col(opts.emissive);return new T.MeshStandardMaterial(Object.assign({color:col(c),roughness:.55,metalness:.05},opts));}
function sphere(r,c,seg=32,opts){return new T.Mesh(new T.SphereGeometry(r,seg,seg),mat(c,opts));}
function chain(points,r0,r1,c,n=24){ // tube effilé le long d'une courbe (cornes, queue)
  const g=new T.Group();const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)));
  const rs=14;const geo=new T.TubeGeometry(curve,n,1,rs,false);const pos=geo.attributes.position;
  for(let i=0;i<=n;i++){const P=curve.getPointAt(i/n);const r=r0+(r1-r0)*(i/n);
    for(let j=0;j<=rs;j++){const k=i*(rs+1)+j;const v=new T.Vector3(pos.getX(k),pos.getY(k),pos.getZ(k)).sub(P).multiplyScalar(r).add(P);pos.setXYZ(k,v.x,v.y,v.z);}}
  pos.needsUpdate=true;geo.computeVertexNormals();g.add(new T.Mesh(geo,mat(c)));
  const a=sphere(r0,c,16);a.position.copy(curve.getPoint(0));g.add(a);const b=sphere(r1,c,12);b.position.copy(curve.getPoint(1));g.add(b);
  return g;
}
function heartMesh(size,c){const s=new T.Shape();const x=0,y=0;
  s.moveTo(x,y+size*.35);s.bezierCurveTo(x,y+size*.6,x-size*.5,y+size*.6,x-size*.5,y+size*.2);
  s.bezierCurveTo(x-size*.5,y-size*.15,x,y-size*.35,x,y-size*.6);
  s.bezierCurveTo(x,y-size*.35,x+size*.5,y-size*.15,x+size*.5,y+size*.2);
  s.bezierCurveTo(x+size*.5,y+size*.6,x,y+size*.6,x,y+size*.35);
  const g=new T.ExtrudeGeometry(s,{depth:size*.25,bevelEnabled:true,bevelSize:size*.06,bevelThickness:size*.06,bevelSegments:3});
  g.center();return new T.Mesh(g,mat(c));}

const SKINS={
  hybris:{body:[235,.46,.44],belly:[235,.5,.58],horn:'#F6DB8C',hornShape:'crescent',tail:'heart',blush:'#FF9ECF',iris:'#58E1FF',irisTop:'#141338',mark:'H'},
  iblis: {body:[354,.74,.63],belly:[354,.85,.75],horn:'#FFE6D8',hornShape:'bump',tail:'drop',blush:'#E0305F',iris:'#FFB547',irisTop:'#3D0B1C',mark:'13'},
};
function skinFromHue(h){return {body:[h,.62,.58],belly:[h,.7,.72],horn:'#F6DB8C',hornShape:Math.random()<.5?'crescent':'bump',tail:'heart',blush:'#FF9ECF',iris:'#58E1FF',irisTop:'#141338'};}

window.makeDemon=function(o={}){
  const sk=o.skin?SKINS[o.skin]:skinFromHue(o.hue??290);
  if(o.hornShape)sk.hornShape=o.hornShape;
  const body=hsl(...sk.body),belly=hsl(...sk.belly),line=body.clone().multiplyScalar(.35);
  const g=new T.Group();const inner=new T.Group();g.add(inner);
  // corps
  const b=sphere(1,body);b.scale.set(1,.95,.92);b.position.y=1.05;inner.add(b);
  const bl=sphere(.72,belly);bl.scale.set(1,.85,.45);bl.position.set(0,.78,.72);inner.add(bl);
  // pieds
  for(const s of[-1,1]){const f=sphere(.28,body.clone().multiplyScalar(.85));f.scale.set(1.15,.55,1.2);f.position.set(s*.42,.14,.3);inner.add(f);}
  // bras
  const arms=[];for(const s of[-1,1]){const a=new T.Group();const up=sphere(.18,body);up.scale.set(1,1.5,1);up.position.y=-.2;a.add(up);const hand=sphere(.17,body);hand.position.y=-.5;a.add(hand);a.position.set(s*.95,1.05,.15);a.rotation.z=s*-.35;inner.add(a);arms.push(a);}
  // yeux
  const eyes=[];for(const s of[-1,1]){const e=new T.Group();
    const w=sphere(.24,'#ffffff',24,{roughness:.25});e.add(w);
    const ir=sphere(.15,sk.iris,24,{roughness:.2});ir.position.z=.14;e.add(ir);
    const irt=sphere(.155,sk.irisTop,24,{roughness:.3});irt.position.z=.13;irt.position.y=.06;irt.scale.set(1,.6,1);e.add(irt);
    const pu=sphere(.075,'#1a1230',16,{roughness:.2});pu.position.z=.245;e.add(pu);
    const hl=sphere(.05,'#ffffff',12,{emissive:'#ffffff',emissiveIntensity:.8});hl.position.set(-.06*s,.08,.28);e.add(hl);
    e.position.set(s*.36,1.22,.78);e.lookAt(s*1.2,1.4,4);inner.add(e);eyes.push(e);}
  // joues
  for(const s of[-1,1]){const c=sphere(.16,sk.blush,16,{roughness:.9,transparent:true,opacity:.75});c.scale.set(1,.7,.25);c.position.set(s*.68,.98,.7);c.lookAt(s*2.5,.9,3);inner.add(c);}
  // bouche
  const m=new T.Mesh(new T.TorusGeometry(.13,.035,8,16,Math.PI),mat('#241733'));m.position.set(0,.9,.93);m.rotation.z=Math.PI;m.rotation.x=.3;inner.add(m);
  // cornes
  const hc=col(sk.horn);
  for(const s of[-1,1]){let h;
    if(sk.hornShape==='crescent')h=chain([[s*.3,1.85,.05],[s*.45,2.25,.05],[s*.75,2.45,.05],[s*.9,2.35,.05]],.17,.05,hc,12);
    else h=chain([[s*.32,1.85,.05],[s*.4,2.15,.05],[s*.44,2.3,.05]],.19,.07,hc,8);
    inner.add(h);}
  // queue
  const tail=chain([[-.55,.9,-.6],[-1.05,.75,-.85],[-1.35,1.05,-.85],[-1.45,1.4,-.7]],.09,.06,line,12);inner.add(tail);
  if(sk.tail==='heart'){const hm=heartMesh(.34,hc);hm.position.set(-1.45,1.55,-.7);hm.rotation.y=-.4;inner.add(hm);}
  else{const d=sphere(.15,hc);d.scale.set(1,1.4,1);d.position.set(-1.47,1.55,-.7);inner.add(d);}
  // marque sur le ventre (canvas texture)
  if(sk.mark){const cv=document.createElement('canvas');cv.width=cv.height=128;const cx=cv.getContext('2d');cx.font='bold 72px "Space Grotesk", sans-serif';cx.textAlign='center';cx.textBaseline='middle';cx.fillStyle='rgba(20,15,40,.28)';cx.fillText(sk.mark,64,66);
    const tx=new T.CanvasTexture(cv);const mk=new T.Mesh(new T.PlaneGeometry(.5,.5),new T.MeshBasicMaterial({map:tx,transparent:true}));mk.position.set(0,.72,1.06);inner.add(mk);}
  // accessoires
  const acc=o.acc;
  if(acc==='lunettes'){for(const s of[-1,1]){const r=new T.Mesh(new T.TorusGeometry(.27,.03,8,32),mat('#6A5A80'));r.position.set(s*.36,1.22,1.0);inner.add(r);}const br=new T.Mesh(new T.CylinderGeometry(.025,.025,.2,8),mat('#6A5A80'));br.rotation.z=Math.PI/2;br.position.set(0,1.24,1.0);inner.add(br);}
  if(acc==='soleil'){for(const s of[-1,1]){const r=new T.Mesh(new T.BoxGeometry(.5,.3,.08),mat('#1e1428',{roughness:.2,metalness:.3}));r.position.set(s*.36,1.22,1.02);inner.add(r);}const br=new T.Mesh(new T.CylinderGeometry(.025,.025,.25,8),mat('#1e1428'));br.rotation.z=Math.PI/2;br.position.set(0,1.28,1.02);inner.add(br);}
  if(acc==='noeud'){const bw=new T.Group();for(const s of[-1,1]){const c=new T.Mesh(new T.ConeGeometry(.22,.45,4),mat('#FF7FA0'));c.rotation.z=s*Math.PI/2;c.position.x=s*.24;c.scale.z=.5;bw.add(c);}const k=sphere(.12,'#FF7FA0');bw.add(k);bw.position.set(-.55,2.05,.15);bw.rotation.z=.3;inner.add(bw);}
  if(acc==='helice'){const cap=new T.Mesh(new T.SphereGeometry(.55,24,12,0,Math.PI*2,0,Math.PI/2),mat('#5EE6FF'));cap.position.set(0,1.75,0);inner.add(cap);const st=new T.Mesh(new T.CylinderGeometry(.03,.03,.25,8),mat('#1F7A99'));st.position.set(0,2.4,0);inner.add(st);const pr=new T.Mesh(new T.BoxGeometry(.7,.05,.12),mat('#FFD23F'));pr.position.set(0,2.52,0);inner.add(pr);g.userData.prop=pr;}
  if(acc==='canne'){const c=new T.Mesh(new T.CylinderGeometry(.04,.04,1.1,8),mat('#8a5a2b'));c.position.set(1.25,.55,.3);inner.add(c);const h=new T.Mesh(new T.TorusGeometry(.14,.04,8,16,Math.PI),mat('#8a5a2b'));h.position.set(1.11,1.1,.3);inner.add(h);}
  if(acc==='couronne'){const cr=new T.Mesh(new T.CylinderGeometry(.42,.36,.3,6,1,true),mat('#f4d03f',{metalness:.6,roughness:.3,side:T.DoubleSide}));cr.position.set(0,2.05,0);inner.add(cr);for(let i=0;i<6;i++){const a=i/6*Math.PI*2;const p=new T.Mesh(new T.ConeGeometry(.08,.22,4),mat('#f4d03f',{metalness:.6,roughness:.3}));p.position.set(Math.sin(a)*.4,2.28,Math.cos(a)*.4);inner.add(p);}}
  if(acc==='jetpack'){const jp=new T.Mesh(new T.BoxGeometry(.7,.8,.35),mat('#6b685d',{metalness:.5,roughness:.4}));jp.position.set(0,1.0,-.95);inner.add(jp);for(const s of[-1,1]){const n=new T.Mesh(new T.CylinderGeometry(.1,.14,.3,12),mat('#2a2a25'));n.position.set(s*.22,.5,-.95);inner.add(n);const fl=new T.Mesh(new T.ConeGeometry(.12,.5,12),mat('#ff6b3d',{emissive:'#ff6b3d',emissiveIntensity:1.2}));fl.rotation.x=Math.PI;fl.position.set(s*.22,.1,-.95);inner.add(fl);g.userData.flames=(g.userData.flames||[]).concat(fl);}}
  if(acc==='lightstick'){const st=new T.Mesh(new T.CylinderGeometry(.035,.035,.6,8),mat('#ece8de'));st.position.set(1.2,1.3,.3);inner.add(st);const gl=sphere(.16,'#c58cff',16,{emissive:'#c58cff',emissiveIntensity:1.5});gl.position.set(1.2,1.72,.3);inner.add(gl);}
  if(acc==='casquette'){const cap=new T.Mesh(new T.SphereGeometry(.6,24,12,0,Math.PI*2,0,Math.PI/2),mat('#2a4fd4'));cap.position.set(0,1.7,0);inner.add(cap);const vis=new T.Mesh(new T.CylinderGeometry(.55,.55,.06,24,1,false,-.7,1.4),mat('#2a4fd4'));vis.position.set(0,1.72,.15);inner.add(vis);const st=new T.Mesh(new T.PlaneGeometry(.22,.22),new T.MeshBasicMaterial({color:'#f4d03f'}));st.position.set(0,2.0,.58);inner.add(st);}
  // ombre douce
  const sc=document.createElement('canvas');sc.width=sc.height=128;const scx=sc.getContext('2d');const gr=scx.createRadialGradient(64,64,4,64,64,64);gr.addColorStop(0,'rgba(0,0,0,.55)');gr.addColorStop(1,'rgba(0,0,0,0)');scx.fillStyle=gr;scx.fillRect(0,0,128,128);
  const sh=new T.Mesh(new T.PlaneGeometry(2.6,1.3),new T.MeshBasicMaterial({map:new T.CanvasTexture(sc),transparent:true,depthWrite:false}));sh.rotation.x=-Math.PI/2;sh.position.y=.01;g.add(sh);g.userData.shadow=sh;
  const size=o.size??1;inner.scale.setScalar(size);
  g.userData={...g.userData,inner,arms,eyes,size,name:o.name||o.skin||'demon'};
  return g;
};
// pose/anim déterministe : t en secondes
window.animDemon=function(d,t,opts={}){
  const u=d.userData;const inner=u.inner;
  const br=Math.sin(t*2*Math.PI/3.6)*.022;inner.scale.set(u.size*(1-br*.5),u.size*(1+br),u.size*(1-br*.5));
  inner.rotation.z=(opts.tilt||0)+Math.sin(t*1.7)*.03;
  u.arms.forEach((a,i)=>{const s=i?1:-1;a.rotation.z=s*-.35+Math.sin(t*2.2+i)*.12;if(opts.wave&&i===1)a.rotation.z=-2.4+Math.sin(t*9)*.5;});
  if(u.prop)u.prop.rotation.y=t*30;
  if(u.flames)u.flames.forEach((f,i)=>f.scale.set(1,1+Math.sin(t*40+i)*.35,1));
  if(opts.spin!==undefined)d.rotation.y=opts.spin;
  const bob=opts.bob??Math.abs(Math.sin(t*3))*.06;inner.position.y=bob;
};
})();
