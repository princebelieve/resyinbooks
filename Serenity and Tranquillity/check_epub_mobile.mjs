// Check actual mobile viewport reflow using Chrome's device emulation.
import {spawn} from 'node:child_process';
import {writeFile, mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const base=resolve(import.meta.dirname);
const preview=resolve(base,'.tools/epub-preview');
const chrome=spawn('C:/Program Files/Google/Chrome/Application/chrome.exe',[
  '--headless','--no-sandbox','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0','--user-data-dir='+resolve(base,'.tools/chrome_epub_emulation'),
  'about:blank'],{windowsHide:true,stdio:['ignore','ignore','pipe']});
let ws;
try {
  const endpoint=await new Promise((ok,fail)=>{
    let log=''; const timer=setTimeout(()=>fail(new Error('Browser startup timeout')),20000);
    chrome.stderr.on('data',chunk=>{
      log+=chunk;
      const m=log.match(/DevTools listening on (ws:\/\/[^\s]+)/);
      if(m){clearTimeout(timer);ok(m[1]);}
    });
    chrome.on('error',fail);
  });
  ws=new WebSocket(endpoint);
  await new Promise((ok,fail)=>{ws.onopen=ok;ws.onerror=fail;});
  let serial=0; const pending=new Map();
  ws.onmessage=event=>{
    const msg=JSON.parse(event.data);
    const cb=pending.get(msg.id);
    if(cb){pending.delete(msg.id);msg.error?cb.reject(new Error(JSON.stringify(msg.error))):cb.resolve(msg.result);}
  };
  const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
    const id=++serial;pending.set(id,{resolve,reject});
    ws.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
  });
  const {targetId}=await send('Target.createTarget',{url:'about:blank'});
  const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
  const call=(method,params)=>send(method,params,sessionId);
  await call('Page.enable');
  const results=[];
  for(const file of ['chapter-01.xhtml','subject-index.xhtml','nav.xhtml']){
    for(const [width,font] of [[320,16],[390,16],[390,32],[768,16]]){
      await call('Emulation.setDeviceMetricsOverride',{width,height:844,deviceScaleFactor:1,mobile:true});
      await call('Page.navigate',{url:pathToFileURL(resolve(preview,file)).href});
      await call('Runtime.evaluate',{expression:'new Promise(resolve => { if(document.readyState === "complete") resolve(); else window.addEventListener("load", resolve, {once:true}); })',awaitPromise:true});
      // Explicit viewport width prevents the mobile browser's legacy 980px
      // desktop fallback; reading systems already supply their own viewport.
      await call('Runtime.evaluate',{expression:`{
        let m=document.createElement('meta');m.name='viewport';m.content='width=device-width, initial-scale=1';document.head.append(m);
        document.documentElement.style.fontSize='${font}px';
      }`});
      const {result}=await call('Runtime.evaluate',{returnByValue:true,expression:'({width:innerWidth,scroll:document.documentElement.scrollWidth,font:getComputedStyle(document.body).fontSize,title:document.title})'});
      if(result.value.scroll>width+1) throw new Error('Horizontal overflow '+JSON.stringify({file,width,font,...result.value}));
      results.push({file,viewport:width,rootFont:font,...result.value});
      if(file==='chapter-01.xhtml' && width===390){
        const shot=await call('Page.captureScreenshot',{format:'png'});
        await writeFile(resolve(base,'Previews/EPUB',font===32?'Mobile_LargeText_Preview.png':'Mobile_Chapter_Preview.png'),Buffer.from(shot.data,'base64'));
      }
    }
  }
  await writeFile(resolve(base,'EPUB_Validation/Mobile_Reflow_Report.json'),JSON.stringify({status:'passed',checks:results},null,2));
  console.log(JSON.stringify({status:'passed',mobileAndTabletChecks:results.length}));
  await send('Browser.close');
} finally {
  ws?.close();chrome.kill();
}
