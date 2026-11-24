const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROMIUM || '/usr/bin/chromium', args:['--no-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
  try {
    const page = await browser.newPage({viewport:{width:1200,height:850}});
    const errors=[]; page.on('pageerror', e=>errors.push(e.message));
    await page.route(/^https?:/, route=>route.abort());
    await page.goto('file://'+path.resolve(__dirname,'../index.html'),{timeout:120000});
    await page.waitForFunction(()=>document.getElementById('notice').hidden,{timeout:120000});
    const pixel=await page.evaluate(()=>{const c=document.getElementById('globe'),gl=c.getContext('webgl2'),p=new Uint8Array(4);gl.readPixels(c.width/2,c.height/2,1,1,gl.RGBA,gl.UNSIGNED_BYTE,p);return [...p]});
    assert(pixel[3]>0 && pixel.slice(0,3).some(v=>v>10),`Globe center ${pixel}`);
    await page.locator('#elevation').click(); assert.match(await page.locator('#tag').textContent(),/MOLA elevation/);
    await page.locator('#shade').click(); assert.match(await page.locator('#tag').textContent(),/shaded relief/);
    await page.locator('#location').selectOption('0'); assert.match(await page.locator('#info').textContent(),/Olympus Mons/);
    await page.locator('#plus').click(); await page.waitForFunction(()=>document.getElementById('coords').textContent.includes('1.25×'));
    await page.locator('#reset').click(); await page.waitForFunction(()=>document.getElementById('coords').textContent.includes('1.00×'));
    await page.screenshot({path:path.resolve(__dirname,'../preview.png')});
    assert.deepEqual(errors,[]); console.log('Offline render and interactive controls passed; center pixel:',pixel);
  } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
