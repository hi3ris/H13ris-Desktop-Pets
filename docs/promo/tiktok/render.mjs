import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const ROOT=process.cwd();
const FPS=30, TOTAL=parseFloat(process.env.TOTAL||'38'), START=parseFloat(process.env.START||'0');
const OUT=process.env.OUT||'video_raw.mp4';
const FF=process.env.FFMPEG||'ffmpeg';
const mime={'.html':'text/html','.png':'image/png','.webp':'image/webp','.css':'text/css','.woff2':'font/woff2','.js':'text/javascript'};
const server=http.createServer((req,res)=>{const p=path.join(ROOT,decodeURIComponent(req.url.split('?')[0]));fs.readFile(p,(e,d)=>{if(e){res.writeHead(404);res.end();return;}res.writeHead(200,{'content-type':mime[path.extname(p)]||'application/octet-stream'});res.end(d);});});
await new Promise(r=>server.listen(8765,r));
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
await page.goto('http://127.0.0.1:8765/'+(process.env.PAGE||'pets.html'));
await page.evaluate(()=>window.ready());
const stills=process.env.STILLS; // "0,2.5,5" -> png stills only
if(stills){for(const t of stills.split(',').map(Number)){await page.evaluate(t=>window.seek(t),t);await page.screenshot({path:`still_${t}.png`});}await browser.close();server.close();process.exit(0);}
const ff=spawn(FF,['-y','-v','error','-f','image2pipe','-vcodec','png','-r',String(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-r',String(FPS),OUT],{stdio:['pipe','inherit','inherit']});
const N=Math.round((TOTAL-START)*FPS);
for(let i=0;i<N;i++){const t=START+i/FPS;await page.evaluate(t=>window.seek(t),t);const buf=await page.screenshot({type:'png'});
  if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150===0)console.log('frame',i,'/',N);}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await browser.close();server.close();console.log('done',OUT);
