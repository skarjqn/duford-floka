import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const root=path.resolve(import.meta.dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'capture-manifest.json'),'utf8'));
const seen=new Set(),errors=[];
for(const entry of Object.values(manifest.pages)){
  const text=fs.readFileSync(path.join(root,'site',entry.path),'utf8');
  for(const m of text.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/gi)){
    if(/\bsrc\s*=/.test(m[1]) || /type=["'](?:application\/(?:ld\+)?json|text\/template|speculationrules|importmap)/.test(m[1]) || !m[2].trim() || seen.has(m[2]))continue;
    seen.add(m[2]);
    try{new vm.Script(m[2],{filename:entry.path});}catch(e){errors.push({page:entry.path,error:e.message});}
  }
}
fs.writeFileSync(path.join(root,'inline-script-report.json'),JSON.stringify({unique_scripts:seen.size,errors},null,2));
console.log(JSON.stringify({unique_scripts:seen.size,errors},null,2));
process.exitCode=errors.length?1:0;
