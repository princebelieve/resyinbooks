// Check reflow at phone/tablet widths with actual Chromium device emulation.
import {spawn} from 'node:child_process';
import {writeFile,mkdir,mkdtemp,rm} from 'node:fs/promises';
import {resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
const base=resolve(import.meta.dirname);
const production=resolve(base,'Production');
const preview=resolve(production,'EPUB_Preview');
const output=resolve(production,'Previews/EPUB');
const reportDir=resolve(production,'EPUB_Validation');
await mkdir(output,{recursive:true}); await mkdir(reportDir,{recursive:true});
const profile=await mkdtemp(resolve(tmpdir(),'givers-epub-chrome-'));
const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless','--no-sandbox','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'
],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let ws;
try {
  const endpoint=await new Promise((ok,fail)=>{
    let log=''; const timer=setTimeout(()=>fail(new Error('Chrome startup timeout')),25000);
    chrome.stderr.on('data',chunk=>{log+=chunk;const m=log.match(/DevTools listening on (ws:\/\/[^\s]+)/);if(m){clearTimeout(timer);ok(m[1]);}});
    chrome.on('error',fail); chrome.on('exit',code=>fail(new Error('Chrome exited '+code+' '+log.slice(-1000))));
  });
  ws=new WebSocket(endpoint); await new Promise((ok,fail)=>{ws.onopen=ok;ws.onerror=fail;});
  let serial=0;const pending=new Map();
  ws.onmessage=e=>{const msg=JSON.parse(e.data),cb=pending.get(msg.id);if(cb){pending.delete(msg.id);msg.error?cb.reject(new Error(JSON.stringify(msg.error))):cb.resolve(msg.result);}};
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));});
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});const call=(m,p)=>send(m,p,sessionId);
  await call('Page.enable');const checks=[];
  for(const file of ['chapter-01.xhtml','subject-index.xhtml','nav.xhtml']) for(const [width,font] of [[320,16],[390,16],[390,32],[768,16]]){
    await call('Emulation.setDeviceMetricsOverride',{width,height:844,deviceScaleFactor:1,mobile:true});
    await call('Page.navigate',{url:pathToFileURL(resolve(preview,file)).href});
    await call('Runtime.evaluate',{expression:'new Promise(r=>document.readyState==="complete"?r():window.addEventListener("load",r,{once:true}))',awaitPromise:true});
    await call('Runtime.evaluate',{expression:`{document.documentElement.style.fontSize='${font}px';await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));}`});
    const {result}=await call('Runtime.evaluate',{returnByValue:true,expression:'({width:innerWidth,scroll:document.documentElement.scrollWidth,font:getComputedStyle(document.body).fontSize,title:document.title,overflow:[...document.querySelectorAll("body *")].map(e=>({tag:e.tagName,text:(e.innerText||"").slice(0,90),right:e.getBoundingClientRect().right,width:e.getBoundingClientRect().width})).filter(e=>e.right>innerWidth+1).slice(0,5)})'});
    const item={file,viewport:width,rootFont:font,...result.value}; if(item.scroll>width+1)throw new Error('Horizontal overflow '+JSON.stringify(item)); checks.push(item);
    if(file==='chapter-01.xhtml'&&width===390){const shot=await call('Page.captureScreenshot',{format:'png'});await writeFile(resolve(output,font===32?'Mobile_LargeText_Preview.png':'Mobile_Chapter_Preview.png'),Buffer.from(shot.data,'base64'));}
  }
  await writeFile(resolve(reportDir,'Mobile_Reflow_Report.json'),JSON.stringify({status:'passed',checks},null,2));
  console.log(JSON.stringify({status:'passed',checks:checks.length})); await send('Browser.close');
} finally {
  ws?.close();
  if(chrome.exitCode===null){const closed=new Promise(ok=>chrome.once('exit',ok));chrome.kill();await Promise.race([closed,new Promise(ok=>setTimeout(ok,4000))]);}
  try{await rm(profile,{recursive:true,force:true,maxRetries:5,retryDelay:250});}catch{}
}
