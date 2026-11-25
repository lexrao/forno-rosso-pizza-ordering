var btn=document.getElementById('copy');
if(btn)btn.onclick=function(){var t=btn.dataset.text,m=document.getElementById('copied');
 function ok(){m.textContent='Copied. Paste it into a message to the shop.'}
 function fallback(){var a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');ok()}catch(e){m.textContent='Could not copy. Select the order text and copy it by hand.'}a.remove()}
 if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(ok,fallback);else fallback()};
