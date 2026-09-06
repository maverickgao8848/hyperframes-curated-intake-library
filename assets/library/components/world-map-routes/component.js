import{createFidelityHost,destroyFidelity,htmlNode,svgNode,standardTimelines}from"../fidelity-runtime.js";
const CSS=`
.comp-world-map-routes{width:100%;min-height:410px;display:grid;place-items:center;border-radius:24px;overflow:hidden;background:#070a0f;color:#eff7ff;font-family:var(--comp-font-sans,sans-serif)}
.comp-world-map-routes .wm-stage{position:relative;width:880px;height:390px}.comp-world-map-routes svg{width:100%;height:100%}.comp-world-map-routes .wm-land{fill:#111a24;stroke:#273849;stroke-width:1}.comp-world-map-routes .wm-grid{stroke:#172330;stroke-width:1;fill:none}.comp-world-map-routes .wm-route{fill:none;stroke:#63e6ff;stroke-width:2.5;stroke-linecap:round;filter:drop-shadow(0 0 5px #50d6ff)}.comp-world-map-routes .wm-point{fill:#fff;stroke:#63e6ff;stroke-width:4}
.comp-world-map-routes .wm-head{position:absolute;left:24px;top:22px;font:600 11px/1 var(--comp-font-mono,monospace);letter-spacing:.18em}.comp-world-map-routes .wm-focus{position:absolute;right:24px;top:22px;padding:8px 12px;border:1px solid #2c5269;border-radius:999px;font:600 10px/1 var(--comp-font-mono,monospace);color:#76e8ff}
`;
export const meta={id:"world-map-routes",version:2,candidateId:"EDU-GEO-01"};
export function mount(root,context={}){
 const{params={},fps=30}=context,{routes=["SFO → LON","LON → SHA"],focusRegion="GLOBAL",progress=1}=params,{element,gsap}=createFidelityHost(root,context,meta,"wm",CSS),stage=htmlNode("div","wm-stage"),svg=svgNode("svg",{viewBox:"0 0 880 390"});
 for(let x=80;x<880;x+=80)svg.append(svgNode("path",{d:`M${x} 45V355`,class:"wm-grid"}));for(let y=85;y<360;y+=55)svg.append(svgNode("path",{d:`M30 ${y}H850`,class:"wm-grid"}));
 ["M86 124L140 90 211 104 250 143 222 184 168 177 141 222 104 203Z","M353 92L416 74 474 104 462 145 506 166 482 217 440 207 413 290 367 241 379 184 340 153Z","M493 102L568 76 682 101 751 148 731 200 664 187 621 231 565 204 531 156Z","M702 260L755 248 797 279 774 324 720 318Z"].forEach(d=>svg.append(svgNode("path",{d,class:"wm-land"})));
 const coords=[[130,165],[397,130],[650,171],[752,292]],routeEls=[];routes.forEach((_,i)=>{const A=coords[i%coords.length],B=coords[(i+1)%coords.length],d=`M${A[0]} ${A[1]} Q${(A[0]+B[0])/2} ${Math.min(A[1],B[1])-70} ${B[0]} ${B[1]}`;const p=svgNode("path",{d,class:"wm-route",pathLength:"1"});svg.append(p);routeEls.push(p)});coords.forEach(([cx,cy])=>svg.append(svgNode("circle",{cx,cy,r:"4",class:"wm-point"})));
 stage.append(svg,htmlNode("div","wm-head",routes.join("  /  ")),htmlNode("div","wm-focus",focusRegion));element.append(stage);const state={progress:0};function render(){const p=Math.min(state.progress,Number(progress)||1);routeEls.forEach((r,i)=>{const q=Math.max(0,p-i*.14);r.style.strokeDasharray=`${q} 1`})}
 const segments=standardTimelines(gsap,element,[svg,...stage.querySelectorAll("div")],state,render);return{segments,seek(f){segments.enter.time(Math.max(0,f)/fps)},destroy(){destroyFidelity(element,segments)}};
}
