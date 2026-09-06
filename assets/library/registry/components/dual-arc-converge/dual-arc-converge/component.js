import { createFidelityHost,destroyFidelity,htmlNode,svgNode,standardTimelines } from "../fidelity-runtime.js";
const CSS=`
.comp-dual-arc-converge{width:100%;min-height:390px;display:grid;place-items:center;border-radius:24px;overflow:hidden;background:radial-gradient(circle at 50% 55%,#163026,#070b09 52%);color:#f5fff9;font-family:var(--comp-font-sans,sans-serif)}
.comp-dual-arc-converge .dac-stage{position:relative;width:820px;height:330px}.comp-dual-arc-converge svg{position:absolute;inset:0;width:100%;height:100%}
.comp-dual-arc-converge .dac-arc{fill:none;stroke-width:3;stroke-linecap:round}.comp-dual-arc-converge .dac-left{stroke:#61e6ff}.comp-dual-arc-converge .dac-right{stroke:#a17bff}.comp-dual-arc-converge .dac-ghost{stroke:#27312d;stroke-width:1.5;fill:none}
.comp-dual-arc-converge .dac-node{position:absolute;top:120px;width:168px;padding:18px;border:1px solid #334139;border-radius:18px;background:rgba(13,20,17,.88);text-align:center;font-weight:700;letter-spacing:.08em}.comp-dual-arc-converge .dac-node:first-of-type{left:20px}.comp-dual-arc-converge .dac-node:nth-of-type(2){right:20px}
.comp-dual-arc-converge .dac-result{position:absolute;left:50%;top:112px;translate:-50% 0;width:210px;padding:26px 18px;border:1px solid #66f0b6;border-radius:50%;background:#10251c;text-align:center;box-shadow:0 0 55px rgba(80,239,175,.2);font-size:22px;font-weight:750}
`;
export const meta={id:"dual-arc-converge",version:2,candidateId:"EDU-FLOW-02"};
export function mount(root,context={}){
 const{params={},fps=30}=context,{leftLabel="SIGNAL A",rightLabel="SIGNAL B",summary="SHARED RESULT",progress=1}=params,{element,gsap}=createFidelityHost(root,context,meta,"dac",CSS);
 const stage=htmlNode("div","dac-stage"),svg=svgNode("svg",{viewBox:"0 0 820 330"}),paths=[];
 [["M110 165 C230 20 330 28 410 165","dac-left"],["M710 165 C590 20 490 28 410 165","dac-right"],["M110 165 C230 310 330 300 410 165","dac-left"],["M710 165 C590 310 490 300 410 165","dac-right"]].forEach(([d,c])=>{svg.append(svgNode("path",{d,class:"dac-ghost"}));const p=svgNode("path",{d,class:`dac-arc ${c}`,pathLength:"1"});svg.append(p);paths.push(p)});
 const left=htmlNode("div","dac-node",leftLabel),right=htmlNode("div","dac-node",rightLabel),result=htmlNode("div","dac-result",summary);stage.append(svg,left,right,result);element.append(stage);
 const state={progress:0};function render(){const p=Math.min(state.progress,Number(progress)||1);paths.forEach((path,i)=>{path.style.strokeDasharray=`${p} 1`;path.style.strokeDashoffset=String(i%2?p-1:1-p)});result.style.transform=`scale(${.82+p*.18})`;result.style.opacity=String(.25+p*.75)}
 const segments=standardTimelines(gsap,element,[left,right,result],state,render);return{segments,seek(f){segments.enter.time(Math.max(0,f)/fps)},destroy(){destroyFidelity(element,segments)}};
}
