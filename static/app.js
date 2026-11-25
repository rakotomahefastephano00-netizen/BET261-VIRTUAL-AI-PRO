const $=id=>document.getElementById(id);
async function loadStatus(){try{const s=await fetch('/api/status').then(r=>r.json());$('apiStatus').textContent=s.message;$('apiBadge').textContent=s.api_connector==='configured'?'Configuré':'Non configuré';}catch(e){$('apiStatus').textContent='Serveur indisponible';}}
async function loadData(){
 const [matches,stats]=await Promise.all([fetch('/api/matches').then(r=>r.json()),fetch('/api/stats').then(r=>r.json())]);
 $('total').textContent=stats.total;$('finished').textContent=stats.finished;
 $('matchRows').innerHTML=matches.length?matches.map(m=>`<tr><td><b>${esc(m.home)} – ${esc(m.away)}</b><br><small>${esc(m.league)} ${esc(m.round_name||'')}</small></td><td>${m.odd1??'–'} / ${m.oddx??'–'} / ${m.odd2??'–'}</td><td>${m.home_goals===null?'–':m.home_goals+'–'+m.away_goals}</td><td>${esc(m.source)}</td></tr>`).join(''):'<tr><td colspan="4">Aucun match enregistré.</td></tr>';
 $('frequencies').innerHTML=stats.frequent_scores.length?stats.frequent_scores.map(x=>`<div><b>${x.score}</b> : ${x.count} fois</div>`).join(''):'Aucun résultat terminé.';
}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
$('matchForm').addEventListener('submit',async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target));const r=await fetch('/api/matches',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const j=await r.json();if(!r.ok){alert(j.error||'Erreur');return;}e.target.reset();e.target.league.value='English League';await loadData();alert('Match enregistré.');});
$('refreshBtn').onclick=loadData;
$('ocrBtn').onclick=async()=>{const file=$('imageInput').files[0];if(!file){alert('Choisissez d’abord une capture.');return;}$('ocrBtn').disabled=true;$('ocrBtn').textContent='Lecture en cours…';try{const result=await Tesseract.recognize(file,'eng');$('ocrText').value=result.data.text;}catch(e){alert('Lecture OCR impossible : '+e.message);}finally{$('ocrBtn').disabled=false;$('ocrBtn').textContent='Lire la capture';}};
$('predictForm').addEventListener('submit',async e=>{e.preventDefault();const data=Object.fromEntries(new FormData(e.target));const r=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const j=await r.json();$('prediction').textContent=j.available?`Échantillon : ${j.sample_size} résultats\\nScores historiques les plus fréquents :\\n${j.historical_scores.map(x=>`${x.score} : ${x.count} fois (${x.share_percent} %)`).join('\\n')}\\n\\n${j.note}`:j.message;});
loadStatus();loadData();
