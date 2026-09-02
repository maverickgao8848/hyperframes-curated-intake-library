import{createFidelityHost,destroyFidelity,htmlNode,svgNode,standardTimelines}from"../fidelity-runtime.js";
const CSS=`
.comp-animated-beam{width:100%;min-height:390px;display:grid;place-items:center;border-radius:24px;background:#07090e;color:#edf4ff;font-family:var(--comp-font-sans,sans-serif);overflow:hidden}
.comp-animated-beam .ab-stage{position:relative;width:820px;height:330px}.comp-animated-beam svg{position:absolute;inset:0;width:100%;height:100%}.comp-animated-beam .ab-track{fill:none;stroke:#273244;stroke-width:2}.comp-animated-beam .ab-beam{fill:none;stroke:url(#ab-gradient);stroke-width:4;stroke-linecap:round;filter:drop-shadow(0 0 8px #62d9ff)}
.comp-animated-beam .ab-source,.comp-animated-beam .ab-target{position:absolute;display:grid;place-items:center;border:1px solid #34445b;background:#101722;box-shadow:0 18px 45px #0008;font-weight:700}.comp-animated-beam .ab-source{left:18px;width:110px;height:58px;border-radius:14px}.comp-animated-beam .ab-target{right:20px;top:104px;width:180px;height:120px;border-radius:28px;border-color:#64d9ff;font-size:22px}
`;
export const meta={id:"animated-beam",version:2,candidateId:"EDU-FLOW-03"};
export function mount(root,context={}){
 const{params={},fps=30}=context,{sources=["TEXT","DATA","MEDIA"],target="MODEL",pulse=.75}=params,{element,gsap}=createFidelityHost(root,context,meta,"ab",CSS),stage=htmlNode("div","ab-stage"),svg=svgNode("svg",{viewBox:"0 0 820 330"});
 const gradientId=`ab-gradient-${context.instanceId}`,defs=svgNode("defs"),grad=svgNode("linearGradient",{id:gradientId,x1:"0",x2:"1"});grad.append(svgNode("stop",{offset:"0","stop-color":"#a274ff"}),svgNode("stop",{offset:".55","stop-color":"#54e6ff"}),svgNode("stop",{offset:"1","stop-color":"#75ffbd"}));defs.append(grad);svg.append(defs);
 const paths=[];[70,165,260].forEach((y,i)=>{const d=`M128 ${y} C330 ${y}, 420 165, 620 165`;svg.append(svgNode("path",{d,class:"ab-track"}));const p=svgNode("path",{d,class:"ab-beam",pathLength:"1"});p.style.stroke=`url(#${gradientId})`;svg.append(p);paths.push(p);const node=htmlNode("div","ab-source",sources[i]??`INPUT ${i+1}`);node.style.top=`${y-29}px`;stage.append(node)});
 const targetNode=htmlNode("div","ab-target",target);stage.prepend(svg);stage.append(targetNode);element.append(stage);const state={progress:0};
 function render(){const p=state.progress;paths.forEach((path,i)=>{const head=Math.max(0,Math.min(1,p*1.5-i*.13));path.style.strokeDasharray=`${Math.max(.001,Number(pulse)*.16)} 1`;path.style.strokeDashoffset=String(1-head)});targetNode.style.boxShadow=`0 0 ${20+p*45}px rgba(84,230,255,${.08+p*.22})`}
 const segments=standardTimelines(gsap,element,[...stage.querySelectorAll(".ab-source"),targetNode],state,render);return{segments,seek(f){segments.enter.time(Math.max(0,f)/fps)},destroy(){destroyFidelity(element,segments)}};
}
