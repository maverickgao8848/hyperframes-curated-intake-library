import { createFidelityHost, destroyFidelity, htmlNode, svgNode, standardTimelines } from "../fidelity-runtime.js";

const CSS = `
.comp-tracing-beam{width:100%;min-height:420px;padding:28px 42px;border-radius:24px;overflow:hidden;background:#080a0d;color:#f4f7fb;font-family:var(--comp-font-sans,sans-serif)}
.comp-tracing-beam .tb-layout{position:relative;display:grid;grid-template-columns:64px 1fr;gap:28px;max-width:760px;margin:auto}
.comp-tracing-beam .tb-rail{position:relative}.comp-tracing-beam svg{position:absolute;inset:4px 0;width:64px;height:340px;overflow:visible}
.comp-tracing-beam .tb-base{fill:none;stroke:#25303d;stroke-width:3}.comp-tracing-beam .tb-live{fill:none;stroke:#69f0c0;stroke-width:4;stroke-linecap:round;filter:drop-shadow(0 0 8px #32da9f)}
.comp-tracing-beam .tb-dot{position:absolute;left:25px;width:14px;height:14px;border-radius:50%;border:2px solid #69f0c0;background:#09120f;box-shadow:0 0 0 6px rgba(105,240,192,.08)}
.comp-tracing-beam .tb-list{display:grid;gap:18px}.comp-tracing-beam .tb-item{min-height:72px;padding:16px 20px;border:1px solid #26303a;border-radius:14px;background:linear-gradient(110deg,#111820,#0c1015)}
.comp-tracing-beam .tb-index{font:600 10px/1 var(--comp-font-mono,monospace);letter-spacing:.18em;color:#69f0c0}.comp-tracing-beam .tb-label{margin-top:8px;font-size:20px;font-weight:650}
`;
export const meta={id:"tracing-beam",version:2,candidateId:"EDU-FLOW-01"};
export function mount(root,context={}){
  const {params={},fps=30}=context,{items=["SOURCE","TRANSFORM","VERIFY","DELIVER"],progress=1,orientation="vertical"}=params;
  const {element,gsap}=createFidelityHost(root,context,meta,"tb",CSS);
  const layout=htmlNode("div","tb-layout"),rail=htmlNode("div","tb-rail"),list=htmlNode("div","tb-list");layout.dataset.orientation=orientation;
  const svg=svgNode("svg",{viewBox:"0 0 64 340"}),base=svgNode("path",{d:"M32 8 C12 72 52 112 32 170 C12 228 52 270 32 332",class:"tb-base"}),live=svgNode("path",{d:base.getAttribute("d"),class:"tb-live",pathLength:"1"});
  svg.append(base,live);rail.append(svg);layout.append(rail,list);element.append(layout);
  const dots=[],cards=[];[...items].slice(0,4).forEach((label,i)=>{const dot=htmlNode("i","tb-dot");dot.style.top=`${i*91+2}px`;rail.append(dot);dots.push(dot);const card=htmlNode("article","tb-item");card.append(htmlNode("div","tb-index",`0${i+1} / TRACE`),htmlNode("div","tb-label",label));list.append(card);cards.push(card)});
  const state={progress:0};function render(){const p=Math.min(state.progress,Number(progress)||1);live.style.strokeDasharray=`${p} 1`;dots.forEach((d,i)=>d.style.opacity=String(p>=i/3 ? .95 : .2));cards.forEach((c,i)=>c.style.borderColor=p>=i/3?"rgba(105,240,192,.45)":"#26303a")}
  const segments=standardTimelines(gsap,element,[...cards,...dots],state,render);
  return{segments,seek(f){segments.enter.time(Math.max(0,f)/fps)},destroy(){destroyFidelity(element,segments)}};
}
