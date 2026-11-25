var $=function(i){return document.getElementById(i)},peso=function(n){return '₱'+n.toLocaleString('en-PH')};
var OPT={},TOP=[],PROD=[],CATS=[],PIZ=[],FEE=0,REFP=0,S={},CART=[],EDIT=-1,TAB='Pizza',PV='pick';
var SIDE=['','all','left','right'],SIDELABEL={'':'Tap to add',all:'Whole pizza',left:'Left half',right:'Right half'};
var find=function(g,id){return OPT[g].filter(function(o){return o.id===id})[0]};
var pfind=function(id){return PROD.filter(function(p){return p.id===id})[0]};
var pizza=function(id){return id?PIZ.filter(function(p){return p.id===id})[0]:null};
function h(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e}
function clone(o){return JSON.parse(JSON.stringify(o))}

function rng(str){var h=1779033703^str.length;for(var i=0;i<str.length;i++){h=Math.imul(h^str.charCodeAt(i),3432918353);h=h<<13|h>>>19}
 var a=h>>>0;return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

function pieces(t,side,R){var r=rng(t.id+side),n=side==='all'?t.c:Math.ceil(t.c*.6),out=[],g=0;
 while(out.length<n&&g++<400){var a=r()*6.283,d=Math.sqrt(r())*R,x=Math.cos(a)*d,y=Math.sin(a)*d;
  if(side==='left'&&x>-8)continue;if(side==='right'&&x<8)continue;
  var ok=out.every(function(q){return Math.hypot(q[0]-x,q[1]-y)>(t.id==='pep'?27:19)});if(!ok&&g<300)continue;
  out.push([x,y,r()*360,.85+r()*.3])}
 return out}

function drawPizza(){
 var cr=find('crust',S.crust),sc=find('sauce',S.sauce),R=cr.r,h='';
 h+='<circle r="152" fill="#d9a85c"/><circle r="152" fill="none" stroke="#b9823a" stroke-width="3"/>';
 if(S.crust==='stuffed')h+='<circle r="'+(R+10)+'" fill="none" stroke="#efc67e" stroke-width="7" stroke-dasharray="2 9" stroke-linecap="round"/>';
 h+='<circle r="'+R+'" fill="'+sc.c+'"/>';
 if(S.cheese!=='none'){var cr2=rng('cheese'+S.cheese),extra=S.cheese==='extra';
  h+='<circle r="'+(R-5)+'" fill="'+(extra?'#f3d47a':'#f6e3a1')+'" opacity="'+(extra?.97:.86)+'"/>';
  for(var i=0;i<(extra?34:18);i++){var a=cr2()*6.283,d=Math.sqrt(cr2())*(R-14);h+='<ellipse cx="'+Math.cos(a)*d+'" cy="'+Math.sin(a)*d+'" rx="'+(10+cr2()*12)+'" ry="'+(7+cr2()*8)+'" fill="#fff4c4" opacity=".55" transform="rotate('+cr2()*180+' '+Math.cos(a)*d+' '+Math.sin(a)*d+')"/>'}}
 TOP.forEach(function(t){var side=S.top[t.id];if(!side)return;
  pieces(t,side,R-24).forEach(function(p,i){h+='<g transform="translate('+p[0].toFixed(1)+' '+p[1].toFixed(1)+') rotate('+p[2].toFixed(0)+') scale('+p[3].toFixed(2)+')"><use class="piece" href="#t-'+t.id+'" style="animation-delay:'+(i*18)+'ms"/></g>'})});
 $('pizza').innerHTML=h;
 $('pz').style.transform='scale('+find('size',S.size).k+')'}

function lidOpen(){$('boxwrap').classList.add('open')}
function signed(n){return n?(n>0?' +':' −')+peso(Math.abs(n)):''}

/* Pricing: same rules the server applies. A named pizza is priced for Medium; its own sauce, cheese, crust
   and toppings are included; size changes the price by the gap to Medium; extras cost extra. */
function calc(c){var pr=pizza(c.preset),z=find('size',c.size),parts=[],base=0;
 if(pr){base=pr.p;parts.push([z.n,z.p-REFP])}else parts.push([z.n,z.p]);
 ['crust','sauce','cheese'].forEach(function(g){var o=find(g,c[g]),d=pr&&find(g,pr[g]);parts.push([o.n,pr?Math.max(0,o.p-(d?d.p:0)):o.p])});
 TOP.forEach(function(t){var s=c.top[t.id];if(s)parts.push([t.n+(s==='all'?'':' ('+s+' half)'),pr&&pr.top[t.id]?0:t.p])});
 if(pr)TOP.forEach(function(t){if(pr.top[t.id]&&!c.top[t.id])parts.push(['No '+t.n,0])});
 return{base:base,parts:parts,unit:base+parts.reduce(function(a,p){return a+p[1]},0)}}
function unit(c){return calc(c).unit}
function surcharge(g,o){var pr=pizza(S.preset);if(!pr)return o.p;var d=find(g,pr[g]);return Math.max(0,o.p-(d?d.p:0))}

function seg(g){var el=$('g-'+g);el.innerHTML='';var pr=pizza(S.preset);OPT[g].forEach(function(o){
 var tag=g==='size'?(pr?signed(o.p-REFP):' · '+peso(o.p)):(surcharge(g,o)?' +'+peso(surcharge(g,o)):'');
 var b=h('button','',o.n+tag);b.type='button';b.setAttribute('aria-pressed',S[g]===o.id);b.onclick=function(){S[g]=o.id;lidOpen();render()};el.appendChild(b)})}
function bins(){var el=$('bins'),pr=pizza(S.preset);el.innerHTML='';TOP.forEach(function(t){var s=S.top[t.id]||'',inc=pr&&pr.top[t.id],b=h('button','bin');b.type='button';
 b.setAttribute('aria-pressed',!!s);b.setAttribute('aria-label',t.n+', '+SIDELABEL[s]+', '+(inc?'included':peso(t.p)));
 b.innerHTML='<svg viewBox="-18 -18 36 36" aria-hidden="true"><use href="#t-'+t.id+'"/></svg><span class="n"></span><span class="s"></span>';
 b.querySelector('.n').textContent=t.n;b.querySelector('.s').textContent=SIDELABEL[s]+' · '+(inc?'included':peso(t.p));
 b.onclick=function(){var i=(SIDE.indexOf(s)+1)%SIDE.length;if(SIDE[i])S.top[t.id]=SIDE[i];else delete S.top[t.id];lidOpen();render()};el.appendChild(b)})}
function render(){var pr=pizza(S.preset);['size','crust','sauce','cheese'].forEach(seg);bins();drawPizza();$('pprice').textContent=peso(unit(S));
 $('bname').textContent=pr?pr.n:'Build your own';$('bsub').textContent=pr?pr.d+' · '+peso(pr.p)+' for Medium':'Pick the size, crust, sauce, cheese and every topping.';
 $('addp').textContent=EDIT>=0?'Update pizza':'Add to order';$('canceledit').hidden=EDIT<0}

/* a fresh pizza: from a named pizza's recipe, or from scratch */
function fresh(id){var pr=pizza(id),pref={size:'m',crust:'classic',sauce:'tomato',cheese:'reg'};S={preset:pr?pr.id:null,top:pr?clone(pr.top):{}};
 ['size','crust','sauce','cheese'].forEach(function(g){var want=pr&&pr[g]?pr[g]:pref[g],o=OPT[g];S[g]=o.some(function(x){return x.id===want})?want:(o[0]&&o[0].id)})}

/* cart */
function save(){try{localStorage.setItem('forno-cart',JSON.stringify(CART))}catch(e){}}
function valid(l){if(!l||!(l.q>=1&&l.q<=20))return false;if(l.k==='item')return !!pfind(l.id);
 if(l.k!=='pizza'||!l.cfg||!l.cfg.top)return false;var c=l.cfg;if(c.preset&&!pizza(c.preset))return false;
 return ['size','crust','sauce','cheese'].every(function(g){return find(g,c[g])})&&Object.keys(c.top).every(function(t){return TOP.some(function(x){return x.id===t})&&SIDE.indexOf(c.top[t])>0})}
function loadCart(){try{CART=JSON.parse(localStorage.getItem('forno-cart')||'[]')}catch(e){CART=[]}if(!Array.isArray(CART))CART=[];CART=CART.filter(valid)}
function deliv(){return $('co').elements.mode.value==='delivery'}
function stepper(q,fn,name){var s=h('span','step'),m=h('button','','−'),p=h('button','','+');m.type=p.type='button';
 m.setAttribute('aria-label','Remove one '+name);p.setAttribute('aria-label','Add one '+name);m.onclick=function(){fn(-1)};p.onclick=function(){fn(1)};
 s.append(m,h('b','',String(q)),p);return s}
function change(i,d){var l=CART[i];l.q+=d;if(l.q>20)l.q=20;if(l.q<1)return drop(i);save();renderCart();renderProd()}
function drop(i){CART.splice(i,1);if(EDIT===i){EDIT=-1;if(PV==='build'){PV='pick';showPV()}}else if(EDIT>i)EDIT--;save();renderCart();renderProd()}
function setItem(id,d){var i=CART.findIndex(function(l){return l.k==='item'&&l.id===id});if(i<0)CART.push({k:'item',id:id,q:1});else return change(i,d);save();renderCart();renderProd()}
function addPizza(cfg){var key=JSON.stringify(cfg),i=CART.findIndex(function(l){return l.k==='pizza'&&JSON.stringify(l.cfg)===key});
 if(i>=0)CART[i].q=Math.min(20,CART[i].q+1);else CART.push({k:'pizza',q:1,cfg:cfg});save();renderCart()}
function say(t){var m=$('gmsg');m.textContent=t;setTimeout(function(){if(m.textContent===t)m.textContent=''},3000)}
function editLine(i){S=clone(CART[i].cfg);EDIT=i;PV='build';tab('Pizza');lidOpen();render();$('builder').scrollIntoView({behavior:'smooth',block:'start'})}

function renderCart(){var ul=$('lines'),sub=0,n=0;ul.innerHTML='';
 if(!CART.length)ul.appendChild(h('li','empty','Your order is empty. Pick a pizza, or choose something from the other tabs.'));
 CART.forEach(function(l,i){var li=h('li','line'),u,title,detail;
  if(l.k==='pizza'){var c=calc(l.cfg),pr=pizza(l.cfg.preset);u=c.unit;title=pr?pr.n:'Custom pizza';detail=c.parts.map(function(p){return p[0]}).join(' · ')}else{var p=pfind(l.id);u=p.p;title=p.n;detail=''}
  sub+=u*l.q;n+=l.q;li.append(h('span','lt',title),h('span','lp',peso(u*l.q)));if(detail)li.append(h('span','ls',detail));
  var a=h('span','la');a.append(stepper(l.q,function(d){change(i,d)},title));
  if(l.k==='pizza'){var e=h('button','link','Edit');e.type='button';e.onclick=function(){editLine(i)};a.append(e)}
  var r=h('button','link','Remove');r.type='button';r.onclick=function(){drop(i)};a.append(r);li.append(a);ul.appendChild(li)});
 var fee=deliv()&&CART.length?FEE:0;if(fee){var f=h('li','fee');f.append(h('span','','Delivery'),h('span','',peso(fee)));ul.appendChild(f)}
 $('total').textContent=peso(sub+fee);$('meta').textContent=n?n+' item'+(n>1?'s':''):'Nothing added yet';
 $('go').disabled=!CART.length;$('mcount').textContent=(n?n+' item'+(n>1?'s':'')+' · '+peso(sub+fee):'Your order is empty')}

/* pizza gallery */
function showPV(){$('gallery').hidden=PV!=='pick';$('builder').hidden=PV!=='build';if(PV==='build')render();else renderGallery()}
function startBuild(id){EDIT=-1;fresh(id);PV='build';showPV();lidOpen();$('builder').scrollIntoView({behavior:'smooth',block:'start'})}
function renderGallery(){var box=$('gbody');box.innerHTML='';
 var g0=h('div','grid'),t=h('div','prod byo');t.append(h('div','pn','Build your own'),h('div','pd','Start from scratch and choose the size, crust, sauce, cheese and every topping.'));
 var f=h('div','pf');f.append(h('span','pp','from '+peso(Math.min.apply(null,OPT.size.map(function(s){return s.p})))));
 var b=h('button','add','Start');b.type='button';b.onclick=function(){startBuild(null)};f.append(b);t.append(f);g0.append(t);box.append(g0);
 var cats=[];PIZ.forEach(function(p){if(cats.indexOf(p.cat)<0)cats.push(p.cat)});
 cats.forEach(function(c){box.append(h('h3','gh',c));var g=h('div','grid');
  PIZ.filter(function(p){return p.cat===c}).forEach(function(p){var t=h('div','prod');t.append(h('div','pn',p.n),h('div','pd',p.d));
   var f=h('div','pf');f.append(h('span','pp',peso(p.p)));var a=h('span','pb'),q=h('button','add alt','Customize'),ad=h('button','add','Add');
   q.type=ad.type='button';q.setAttribute('aria-label','Customize '+p.n);ad.setAttribute('aria-label','Add '+p.n+' to order');
   q.onclick=function(){startBuild(p.id)};ad.onclick=function(){fresh(p.id);addPizza(clone(S));say(p.n+' added to your order.')};
   a.append(q,ad);f.append(a);t.append(f);g.append(t)});box.append(g)})}

/* tabs and fixed-price menu */
function tab(name){TAB=name;$('pizzaView').hidden=name!=='Pizza';$('prodView').hidden=name==='Pizza';renderTabs();renderProd();if(name==='Pizza')showPV()}
function renderTabs(){var el=$('tabs');el.innerHTML='';['Pizza'].concat(CATS).forEach(function(c){var b=h('button','',c);b.type='button';b.setAttribute('aria-pressed',c===TAB);b.onclick=function(){tab(c)};el.appendChild(b)})}
function renderProd(){var box=$('prodView');box.innerHTML='';if(TAB==='Pizza')return;
 PROD.filter(function(p){return p.cat===TAB}).forEach(function(p){var i=CART.findIndex(function(l){return l.k==='item'&&l.id===p.id}),q=i<0?0:CART[i].q;
  var t=h('div','prod'+(q?' in':''));t.append(h('div','pn',p.n));if(p.d)t.append(h('div','pd',p.d));
  var f=h('div','pf');f.append(h('span','pp',peso(p.p)));
  if(!q){var b=h('button','add','Add');b.type='button';b.setAttribute('aria-label','Add '+p.n);b.onclick=function(){setItem(p.id,1)};f.append(b)}
  else f.append(stepper(q,function(d){setItem(p.id,d)},p.n));t.append(f);box.appendChild(t)})}

/* controls */
$('lid').onclick=lidOpen;
$('clear').onclick=function(){S.top={};render()};
$('backpick').onclick=function(){EDIT=-1;PV='pick';showPV()};
$('addp').onclick=function(){var cfg=clone(S),pr=pizza(S.preset),name=pr?pr.n:'Custom pizza',msg;
 if(EDIT>=0){CART[EDIT].cfg=cfg;EDIT=-1;save();renderCart();msg=name+' updated.'}else{addPizza(cfg);msg=name+' added to your order.'}
 PV='pick';showPV();say(msg);window.scrollTo({top:0,behavior:'smooth'})};
$('canceledit').onclick=function(){EDIT=-1;PV='pick';showPV()};

var form=$('co');
$('go').onclick=function(){$('go').hidden=true;form.hidden=false;form.elements.name.focus()};
$('back').onclick=function(){form.hidden=true;$('go').hidden=false};
form.addEventListener('change',function(){$('addr').hidden=!deliv();renderCart()});
form.onsubmit=function(e){e.preventDefault();var err=$('err'),btn=$('send');err.textContent='';
 var cart=CART.map(function(l){return l.k==='item'?{kind:'item',id:l.id,qty:l.q}:{kind:'pizza',qty:l.q,preset:l.cfg.preset,size:l.cfg.size,crust:l.cfg.crust,sauce:l.cfg.sauce,cheese:l.cfg.cheese,toppings:l.cfg.top}});
 var el=form.elements,body={cart:cart,name:el.name.value,phone:el.phone.value,mode:el.mode.value,address:el.address.value};
 btn.disabled=true;btn.textContent='Sending…';
 fetch('/api/orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
 .then(function(r){return r.json().then(function(j){return{ok:r.ok,j:j}})})
 .then(function(x){if(!x.ok)throw new Error(x.j.error||'Something went wrong.');CART=[];save();location.href=x.j.receipt_url})
 .catch(function(ex){err.textContent=ex.message||'Could not reach the shop. Check your connection and try again.';btn.disabled=false;btn.textContent='Confirm order'})};

fetch('/api/menu').then(function(r){return r.json()}).then(function(m){
 OPT={size:m.size||[],crust:m.crust||[],sauce:m.sauce||[],cheese:m.cheese||[]};TOP=m.topping||[];PROD=m.product||[];PIZ=m.pizza||[];FEE=m.delivery_fee;REFP=m.size_ref;
 CATS=[];PROD.forEach(function(p){if(CATS.indexOf(p.cat)<0)CATS.push(p.cat)});
 fresh(null);loadCart();renderTabs();showPV();renderCart()})
.catch(function(){$('lines').innerHTML='<li class="empty">The menu could not be loaded. Please refresh.</li>'});
