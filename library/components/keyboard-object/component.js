import {
  createFidelityHost,
  destroyFidelity,
  htmlNode,
  standardTimelines,
} from "../fidelity-runtime.js";

const CSS = `
.comp-keyboard-object{position:relative;width:100%;min-height:360px;display:grid;place-items:center;overflow:hidden;border-radius:var(--comp-radius,22px);background:radial-gradient(circle at 50% 15%,#eef1f6,#aeb6c2 72%);color:#272a2f;font-family:var(--comp-font-sans,sans-serif);perspective:900px}
.comp-keyboard-object .kb-wrap{position:relative;width:min(88%,760px);padding:9px;border:1px solid rgba(0,0,0,.16);border-radius:17px;background:linear-gradient(#d9dee5,#aeb5bf);box-shadow:0 34px 65px rgba(30,40,55,.35),inset 0 1px rgba(255,255,255,.8);transform:rotateX(12deg)}
.comp-keyboard-object .kb-row{display:flex;gap:5px;margin-bottom:5px}
.comp-keyboard-object .kb-key{position:relative;flex:1;min-width:28px;height:40px;display:flex;align-items:center;justify-content:center;border:1px solid rgba(0,0,0,.15);border-radius:7px;background:linear-gradient(#fafafa,#dce0e5);box-shadow:0 3px 0 #8d949d,0 5px 8px rgba(0,0,0,.18),inset 0 1px #fff;font:600 11px/1 var(--comp-font-mono,monospace);transform-origin:center bottom}
.comp-keyboard-object .kb-key[data-wide="2"]{flex:1.7}.comp-keyboard-object .kb-key[data-wide="5"]{flex:5}
.comp-keyboard-object .kb-key[data-active="true"]{color:#fff;background:linear-gradient(#54d8ff,#337af5);box-shadow:0 1px 0 #2155b9,0 0 20px rgba(40,130,255,.55)}
.comp-keyboard-object .kb-caption{position:absolute;left:0;right:0;bottom:8px;text-align:center;font:700 9px/1 var(--comp-font-mono,monospace);letter-spacing:.18em;color:#505966}
`;

const DEFAULT_ROWS = [
  ["esc","1","2","3","4","5","6","7","8","9","0","-","=","delete"],
  ["tab","Q","W","E","R","T","Y","U","I","O","P","[","]","\\"],
  ["caps","A","S","D","F","G","H","J","K","L",";","'","return"],
  ["shift","Z","X","C","V","B","N","M",",",".","/","shift"],
  ["fn","ctrl","option","command","space","command","option","←","↑","↓","→"],
];

export const meta = { id: "keyboard-object", version: 2, candidateId: "EDU-OBJECT-02" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const { keys = DEFAULT_ROWS, activeKeys = ["command","K"], label = "COMMAND + K · OPEN SEARCH" } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "kb", CSS);
  const wrap = htmlNode("div", "kb-wrap");
  const keyElements = [];
  const rows = Array.isArray(keys?.[0]) ? keys : DEFAULT_ROWS;
  rows.forEach((rowValues) => {
    const row = htmlNode("div", "kb-row");
    rowValues.forEach((value) => {
      const text = String(value);
      const key = htmlNode("div", "kb-key", text === "space" ? "" : text);
      if (["delete","tab","caps","return","shift"].includes(text)) key.dataset.wide = "2";
      if (text === "space") key.dataset.wide = "5";
      key.dataset.key = text.toLowerCase();
      row.appendChild(key);
      keyElements.push(key);
    });
    wrap.appendChild(row);
  });
  wrap.appendChild(htmlNode("div", "kb-caption", label));
  element.appendChild(wrap);
  const targets = new Set((Array.isArray(activeKeys) ? activeKeys : [activeKeys]).map((value) => String(value).toLowerCase()));
  const state = { progress: 0 };
  function render() {
    keyElements.forEach((key, index) => {
      const active = targets.has(key.dataset.key) && state.progress > .42 + (index % 3) * .1;
      key.dataset.active = String(active);
      key.style.transform = active ? "translateY(3px) scale(.985)" : "translateY(0) scale(1)";
    });
    wrap.style.transform = `rotateX(${14-state.progress*7}deg) rotateZ(${(1-state.progress)*-1.4}deg)`;
  }
  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [wrap, ...keyElements], state, render);
  const segments = { enter, emphasis, dim, exit };
  return {
    segments,
    seek(localFrame) { enter.time(Math.max(0, localFrame) / fps); },
    destroy() { destroyFidelity(element, segments); },
  };
}
