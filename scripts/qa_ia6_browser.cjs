// Assignment 6 browser checks. The Python harness supplies a disposable database/server.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.QA_URL;
assert(base && new URL(base).hostname === '127.0.0.1', 'Use the isolated local QA harness');
const password = process.env.QA_PASSWORD;
const output = process.env.QA_OUTPUT_DIR || '/tmp/myportofolio-ia6';
fs.mkdirSync(output, { recursive: true });
const checks = [];
function check(condition, label) { assert(condition, label); checks.push(label); }
function gate() { let release; const promise = new Promise(resolve => { release = resolve; }); return { promise, release }; }

(async () => {
 const browser = await chromium.launch({headless:true, executablePath:process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
 const errors = [];
 const writes = [];
 const contexts = [];
 async function session(username) {
  const context = await browser.newContext({viewport:{width:1440,height:1000}});
  contexts.push(context);
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => {
   if (request.url().includes('/api/v1/experiences/') && request.method() !== 'GET') writes.push(request);
  });
  if (username) {
   await page.goto(base+'/login/?next=/experience/');
   await page.locator('#id_username').fill(username); await page.locator('#id_password').fill(password);
   await page.getByRole('button', {name:'Login',exact:true}).click();
   await page.waitForURL(base+'/experience/');
  } else await page.goto(base+'/experience/');
  await page.waitForSelector('.timeline-item');
  return {context,page};
 }
 const publicData = async context => {
  const response = await context.request.get(base+'/api/v1/experiences/', {headers:{Accept:'application/json'}});
  assert.equal(response.status(),200); return response.json();
 };
 const token = async context => (await context.cookies()).find(cookie=>cookie.name==='csrftoken')?.value;
 const form = page => page.locator('#experience-form');
 const fill = async (page, values) => {
  for (const [name,value] of Object.entries(values)) {
   const control = form(page).locator(`[name="${name}"]`);
   if (name==='category') await control.selectOption(value); else await control.fill(value);
  }
 };
 const save = page => form(page).locator('button[type=submit]').click();
 const loaded = page => page.waitForSelector('#experience-loading.hide', {state:'attached'});
 const card = (page,title) => page.locator('.timeline-item').filter({has:page.locator('.timeline-role',{hasText:title})});
 try {
  const {context:guestContext,page:guest} = await session();
  const data = await publicData(guestContext);
  check(data.length>0 && !('fields' in data[0]),'Experience renders the flat DRF contract');
  check(await guest.locator('[data-new-experience], [data-action=edit], [data-action=delete]').count()===0,'Guests have no management controls');
  await guest.locator('summary').first().click();
  check(await guest.locator('.timeline-item').first().getByRole('link',{name:/Login to star/}).count()===1,'Guest star prompts login');
  for (const suffix of ['',data[0].id+'/']) {
   const response = await guestContext.request.get(base+'/api/v1/experiences/'+suffix,{headers:{Accept:'text/html'}});
   check(response.status()===200 && (await response.text()).includes('Django REST framework'),'Browsable Experience API renders '+(suffix?'detail':'list'));
  }
  // An unsanitized legacy title returned from storage must still render as text.
  await guest.route('**/api/v1/experiences/**', async route => {
   const response = await route.fetch(); const rows = await response.json();
   rows[0].title = '<img src=x onerror="window.ia6Xss=1"> Legacy title';
   await route.fulfill({response,json:rows});
  });
  await guest.reload(); await guest.waitForSelector('.timeline-item');
  check((await guest.locator('.timeline-role').first().textContent()).includes('<img'),'Legacy markup remains visible plain text');
  check(await guest.locator('.timeline-role img').count()===0 && !await guest.evaluate(()=>window.ia6Xss),'Legacy title cannot execute markup');
  await guest.unroute('**/api/v1/experiences/**'); await guest.reload(); await guest.waitForSelector('.timeline-item');
  const reads=[]; guest.on('request',r=>{if(r.url().includes('/api/v1/experiences/')&&r.method()==='GET')reads.push(r.url());});
  const search=guest.locator('#experience-search-input');
  await search.pressSequentially('no-match-ia6',{delay:15});
  await guest.waitForSelector('#experience-empty:not(.hide)');
  check(reads.length===1,'Experience search debounces to one request');
  check(new URL(guest.url()).searchParams.get('title')==='no-match-ia6','Search is retained in the page URL');
  await guest.locator('#experience-clear-filters').click(); await guest.waitForSelector('.timeline-item'); await loaded(guest);
  check(await search.inputValue()==='' && !new URL(guest.url()).searchParams.has('title'),'Clear filters restores the list and URL');
  await guest.route('**/api/v1/experiences/**',route=>route.abort());
  await search.fill('offline'); await search.press('Enter'); await guest.waitForSelector('#experience-error:not(.hide)');
  check(true,'Experience shows a recoverable network error');
  await guest.unroute('**/api/v1/experiences/**'); await search.fill(''); await guest.locator('#experience-retry').click();
  await guest.waitForSelector('.timeline-item'); await loaded(guest); check(true,'Retry reloads Experience');
  const slow=gate(), sawSlow=gate();
  await guest.route('**/api/v1/experiences/**',async route=>{
   if(new URL(route.request().url()).searchParams.get('title')==='slow-ia6') {
    sawSlow.release(); await slow.promise;
    try {await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify([{...data[0],title:'STALE IA6 RESULT'}])});} catch { /* Aborted requests need not accept fulfillment. */ }
   } else await route.continue();
  });
  await search.fill('slow-ia6'); await sawSlow.promise;
  await search.fill('newest-empty-ia6'); await search.press('Enter'); await guest.waitForSelector('#experience-empty:not(.hide)');
  slow.release(); await guest.unroute('**/api/v1/experiences/**');
  check(!await guest.locator('#experience-list').textContent().then(text=>text.includes('STALE IA6 RESULT')),'An aborted search cannot replace the newest results');
  await guest.locator('#experience-clear-filters').click(); await guest.waitForSelector('.timeline-item');

  const {context:ownerContext,page:owner}=await session('qa-owner');
  let navigations=0; owner.on('request',request=>{if(request.resourceType()==='document')navigations++;});
  await owner.locator('[data-new-experience]').click();
  const values={title:'<b></b>',location:'<i></i>',description:'<svg></svg>',category:'research',started_at:'2026-09-01',ended_at:''};
  await fill(owner,values);
  const invalidResponse=owner.waitForResponse(r=>r.url().endsWith('/api/v1/experiences/')&&r.request().method()==='POST');
  await save(owner); check((await invalidResponse).status()===400,'Invalid create returns HTTP 400');
  await owner.waitForSelector('#experience-form [aria-invalid=true]');
  check(await form(owner).locator('[aria-invalid=true]').count()===3,'All three invalid fields have inline feedback');
  check(await form(owner).locator('[name=title]').inputValue()==='<b></b>','Invalid input is retained');
  check(await owner.locator('#toast-title').textContent()==='Could not save experience','Validation also appears in a toast');
  check(await form(owner).locator('[name=title]').evaluate(el=>el===document.activeElement),'Focus moves to the first invalid field');
  check(await form(owner).locator('[name=title]').getAttribute('aria-describedby')!==null,'Invalid fields reference their error text accessibly');
  const title='IA6 Browser '+Date.now();
  await fill(owner,{...values,title,location:'Depok',description:'Assignment 6 browser QA'});
  const paused=gate(), sawCreate=gate(); let postCount=0;
  await owner.route('**/api/v1/experiences/',async route=>{
   if(route.request().method()==='POST') {postCount++; sawCreate.release(); await paused.promise;}
   await route.continue();
  });
  await save(owner); await sawCreate.promise;
  check(await form(owner).getAttribute('aria-busy')==='true','Form announces a pending save');
  check(await form(owner).locator('[name=title]').isDisabled(),'Fields are stable while saving');
  await owner.keyboard.press('Escape');
  check(await owner.locator('#add-experience-modal').evaluate(el=>el.open),'Escape cannot discard a pending save');
  check(await owner.locator('#add-experience-modal .project-form-modal__close').isDisabled(),'Close control is disabled while saving');
  await form(owner).evaluate(el=>el.requestSubmit());
  const createdResponse=owner.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/api/v1/experiences/'));
  paused.release(); await createdResponse; await owner.unroute('**/api/v1/experiences/');
  await owner.waitForFunction(t=>document.querySelector('#experience-list').textContent.includes(t),title); await loaded(owner);
  check(postCount===1,'Repeated submit creates only one request');
  check(await form(owner).locator('[data-api-error]').count()===0,'Successful correction clears stale errors');
  const created=(await publicData(ownerContext)).find(item=>item.title===title); assert(created);
  await owner.locator('#experience-search-input').fill(title); await owner.locator('#experience-search-input').press('Enter');
  await loaded(owner); await owner.locator('label[for=experience-filter-research]').click(); await loaded(owner);
  await card(owner,title).locator('summary').click(); await card(owner,title).locator('[data-action=edit]').click();
  check(await form(owner).locator('[name=title]').inputValue()===title,'Edit modal is populated from the selected Experience');
  await fill(owner,{location:'Lombok',ended_at:'2026-10-01'});
  const patch=owner.waitForResponse(r=>r.request().method()==='PATCH'); await save(owner);
  check((await patch).status()===200,'Owner updates through PATCH');
  await owner.waitForFunction(()=>!document.querySelector('#add-experience-modal').open); await loaded(owner);
  check((await publicData(ownerContext)).find(item=>item.id===created.id).location==='Lombok','PATCH persists the changed field');
  check(new URL(owner.url()).searchParams.get('category')==='research' && await owner.locator('#experience-search-input').inputValue()===title,'Search and category survive editing');
  check(navigations===0,'Experience create/search/edit do not reload the document');
  // Real expired session: backend returns 403 while the already-rendered owner form remains.
  await card(owner,title).locator('[data-action=edit]').click(); await fill(owner,{title:title+' Unsaved'});
  await ownerContext.clearCookies();
  const denied=owner.waitForResponse(r=>r.request().method()==='PATCH'); await save(owner);
  check((await denied).status()===403,'Expired session is rejected by the actual API');
  await owner.waitForFunction(()=>!document.querySelector('#experience-form button[type=submit]').disabled);
  check(await owner.locator('#add-experience-modal').evaluate(el=>el.open),'403 preserves the open modal');
  check(await form(owner).locator('[name=title]').inputValue()===title+' Unsaved','403 preserves the unsaved draft');
  check(await owner.locator('#toast-message').textContent().then(text=>text.length>0),'403 is shown through a toast');
  check(await form(owner).locator('[data-form-feedback]').isVisible(),'403 also has persistent in-form feedback');
  check((await publicData(ownerContext)).find(item=>item.id===created.id).title===title,'Rejected update leaves the stored title unchanged');
  await owner.waitForFunction(()=>getComputedStyle(document.getElementById('toast-component')).borderLeftColor==='rgb(180, 35, 24)');
  await owner.screenshot({path:path.join(output,'experience-403-desktop.png'),fullPage:true});

  const {context:editorContext,page:editor}=await session('qa-editor');
  check(await editor.locator('[data-new-experience], [data-action=delete]').count()===0,'Editor sees no create/delete controls');
  const editorCard=card(editor,title); await editorCard.locator('summary').click(); await editorCard.locator('[data-action=edit]').click();
  await fill(editor,{description:'Editor update from IA6 QA'});
  const editorPatch=editor.waitForResponse(r=>r.request().method()==='PATCH'); await save(editor);
  check((await editorPatch).status()===200,'Editor can PATCH from the page');
  await editor.waitForFunction(()=>!document.querySelector('#add-experience-modal').open); await loaded(editor);
  const editorBefore=await publicData(editorContext);
  const csrf=await token(editorContext);
  const headers={'X-CSRFToken':csrf,Accept:'application/json'};
  check((await editorContext.request.post(base+'/api/v1/experiences/',{headers,data:{title:'Blocked'}})).status()===403,'Editor create is denied even with a valid CSRF token');
  check((await editorContext.request.delete(base+'/api/v1/experiences/'+created.id+'/',{headers})).status()===403,'Editor delete is denied by the server');
  assert.deepEqual(await publicData(editorContext),editorBefore); check(true,'Editor denied writes preserve the public database representation');
  // Simulated transport failure leaves editable form data intact.
  await card(editor,title).locator('[data-action=edit]').click(); await fill(editor,{location:'Unsaved offline location'});
  await editor.route('**/api/v1/experiences/'+created.id+'/',route=>route.abort()); await save(editor);
  await editor.waitForFunction(()=>!document.querySelector('#experience-form button[type=submit]').disabled);
  check(await form(editor).locator('[name=location]').inputValue()==='Unsaved offline location','Network failure preserves draft data');
  check(await form(editor).locator('[data-form-feedback]').isVisible(),'Network failure produces accessible feedback');
  await editor.unroute('**/api/v1/experiences/'+created.id+'/'); await editor.keyboard.press('Escape');

  const {context:userContext,page:user}=await session('qa-visitor');
  check(await user.locator('[data-action=edit], [data-action=delete], [data-new-experience]').count()===0,'Ordinary users only have read/star controls');
  let userCard=card(user,title); await userCard.locator('summary').click();
  const starPause=gate(), sawStar=gate(); let starCount=0;
  await user.route('**/api/v1/experiences/'+created.id+'/star/',async route=>{
   starCount++; sawStar.release(); await starPause.promise; await route.continue();
  });
  await userCard.locator('[data-action=star]').click(); await sawStar.promise;
  check(await userCard.locator('[data-action=star]').isDisabled(),'Star button is disabled during its request');
  await user.locator('#experience-search-input').press('Enter'); await loaded(user);
  userCard=card(user,title);
  check(await userCard.locator('[data-action=star]').isDisabled(),'Pending star stays disabled after a list refresh');
  await userCard.locator('[data-action=star]').evaluate(el=>el.click());
  const starResponse=user.waitForResponse(r=>r.request().method()==='POST'&&r.url().endsWith('/star/'));
  starPause.release(); await starResponse; await user.unroute('**/api/v1/experiences/'+created.id+'/star/');
  await user.waitForFunction(id=>document.querySelector(`[data-id="${id}"] button[data-action=star]`)?.getAttribute('aria-pressed')==='true',created.id);
  check(starCount===1,'Double activation cannot send a second star toggle');
  check(await card(user,title).evaluate(el=>el.open),'Timeline expansion survives star refresh');
  await card(user,title).locator('[data-action=star]').click();
  await user.waitForFunction(id=>document.querySelector(`[data-id="${id}"] button[data-action=star]`)?.getAttribute('aria-pressed')==='false',created.id);
  check(true,'Ordinary user can unstar via AJAX');
  const userBefore=await publicData(userContext);
  const forbidden=await userContext.request.patch(base+'/api/v1/experiences/'+created.id+'/',{headers:{'X-CSRFToken':await token(userContext)},data:{title:'Blocked'}});
  check(forbidden.status()===403,'Ordinary user cannot PATCH by bypassing the UI');
  assert.deepEqual(await publicData(userContext),userBefore); check(true,'Ordinary user denied PATCH preserves stored data');

  // Return to an authorized owner session for confirmation, deletion and mobile QA.
  const {context:finalContext,page:final}=await session('qa-owner');
  await final.locator('label[for=theme-toggle]').click();
  await final.waitForFunction(()=>getComputedStyle(document.body).color==='rgb(247, 231, 196)');
  check(await final.locator('.timeline-role').first().evaluate(el=>getComputedStyle(el).color==='rgb(247, 231, 196)'),'Dark theme text reaches its readable final color');
  await final.screenshot({path:path.join(output,'experience-desktop-dark.png'),fullPage:true});
  let finalCard=card(final,title); await finalCard.locator('summary').click(); await finalCard.locator('[data-action=delete]').click();
  await final.locator('#delete-confirmation button[data-dialog-close]').last().click();
  check((await publicData(finalContext)).some(item=>item.id===created.id),'Cancel delete preserves the Experience');
  await finalCard.locator('[data-action=delete]').click();
  const deleted=final.waitForResponse(r=>r.request().method()==='DELETE'); await final.locator('#delete-confirmation button[type=submit]').click();
  const deleteResponse=await deleted;
  check(deleteResponse.status()===204 && (await deleteResponse.body()).length===0,'Owner delete returns an empty HTTP 204');
  await final.waitForFunction(t=>!document.querySelector('#experience-list').textContent.includes(t),title);
  check(!(await publicData(finalContext)).some(item=>item.id===created.id),'Deleted Experience is absent from the API and page');
  await final.setViewportSize({width:390,height:844});
  await final.locator('[data-new-experience]').click();
  await fill(final,{...values,title:'<b></b>',location:'Lombok',description:'Mobile validation'}); await save(final);
  await final.waitForSelector('#experience-form [aria-invalid=true]');
  check(await final.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile Experience has no horizontal overflow');
  check(await final.locator('#add-experience-modal .project-form-modal__content').evaluate(el=>{const r=el.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1;}),'Mobile edit/create modal fits the viewport');
  check(await form(final).locator('button[type=submit]').evaluate(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight+1;}),'Mobile save action remains visible while editing');
  check(await final.locator('#toast-component').evaluate(el=>el.matches(':popover-open')),'Toast can appear above the active modal');
  await final.screenshot({path:path.join(output,'experience-mobile-validation.png')});
  await final.keyboard.press('Escape');
  await final.locator('label[for=theme-toggle]').click();
  await final.waitForFunction(()=>getComputedStyle(document.body).color==='rgb(43, 27, 20)');
  check(await final.locator('.timeline-role').first().evaluate(el=>getComputedStyle(el).color==='rgb(43, 27, 20)'),'Light theme text reaches its readable final color');
  await final.screenshot({path:path.join(output,'experience-mobile-light.png'),fullPage:true});
  for(const request of writes) {
   const headers=await request.allHeaders();
   // Expired-session request deliberately lacks a cookie but still uses the write helper.
   check('x-csrftoken' in headers && headers.accept==='application/json','AJAX '+request.method()+' sends CSRF and JSON Accept headers');
  }
  check(errors.length===0,'No JavaScript exceptions across all roles');
  const result={suite:'IA6 Experience',passed:checks.length,checks,screenshots:output};
  fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result,null,2));
 } catch(error) {
  for(let i=0;i<contexts.length;i++) {
   const page=contexts[i].pages()[0]; if(page) await page.screenshot({path:path.join(output,`failure-${i}.png`)}).catch(()=>{});
  }
  throw error;
 } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
