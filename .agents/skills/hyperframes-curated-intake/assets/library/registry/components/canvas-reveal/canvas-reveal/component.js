import {
  createFidelityHost,
  destroyFidelity,
  htmlNode,
  standardTimelines,
} from "../fidelity-runtime.js";

const CSS = `
.comp-canvas-reveal{position:relative;width:100%;min-height:360px;overflow:hidden;border-radius:var(--comp-radius,22px);background:#030506;color:#fff}
.comp-canvas-reveal .cr-canvas{display:block;width:100%;height:360px}
.comp-canvas-reveal .cr-vignette{position:absolute;inset:0;background:linear-gradient(to bottom,transparent 45%,rgba(2,3,5,.82));pointer-events:none}
.comp-canvas-reveal .cr-copy{position:absolute;left:34px;bottom:30px;z-index:2;font-family:var(--comp-font-sans,sans-serif);font-size:clamp(24px,4vw,52px);font-weight:750;letter-spacing:-.045em}
.comp-canvas-reveal .cr-meta{display:block;margin-bottom:8px;font:600 10px/1 var(--comp-font-mono,monospace);letter-spacing:.22em;color:rgba(255,255,255,.5)}
`;

const VERTEX = `
attribute vec2 a_position;
void main(){ gl_Position=vec4(a_position,0.0,1.0); }
`;

const FRAGMENT = `
precision highp float;
uniform vec2 u_resolution;
uniform float u_progress;
uniform float u_seed;
uniform vec3 u_color_a;
uniform vec3 u_color_b;
uniform float u_dot_size;
float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7))+u_seed)*43758.5453123); }
void main(){
  vec2 p=gl_FragCoord.xy;
  vec2 uv=p/u_resolution;
  float cell=max(4.0,u_dot_size*4.0);
  vec2 grid=floor(p/cell);
  vec2 local=fract(p/cell)-0.5;
  float dotMask=1.0-smoothstep(u_dot_size/cell,u_dot_size/cell+0.075,length(local));
  vec2 center=vec2(0.5,0.48);
  float radius=length((uv-center)*vec2(u_resolution.x/u_resolution.y,1.0));
  float noise=hash(grid);
  float front=u_progress*1.05;
  float reveal=1.0-smoothstep(front-0.16,front+0.08,radius+noise*0.13);
  float wave=exp(-42.0*abs(radius-front))*step(0.02,u_progress);
  float alpha=dotMask*clamp(reveal*(0.25+noise*0.8)+wave,0.0,1.0);
  vec3 color=mix(u_color_a,u_color_b,clamp(uv.x+noise*0.22,0.0,1.0));
  color+=wave*0.35;
  gl_FragColor=vec4(color,alpha);
}
`;

function shader(gl, type, source) {
  const value = gl.createShader(type);
  gl.shaderSource(value, source);
  gl.compileShader(value);
  if (!gl.getShaderParameter(value, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(value));
  return value;
}

function colorArray(value, fallback) {
  const source = Array.isArray(value) ? value : fallback;
  return source.map((channel) => Math.max(0, Math.min(255, Number(channel) || 0)) / 255);
}

export const meta = { id: "canvas-reveal", version: 2, candidateId: "EDU-REVEAL-02" };

export function mount(root, context = {}) {
  const { params = {}, fps = 30 } = context;
  const {
    label = "Signal resolved",
    colors = [[0, 229, 255], [139, 92, 246]],
    opacities = [0.3, 0.5, 0.8, 1],
    dotSize = 2,
    seed = 17,
  } = params;
  const { element, gsap } = createFidelityHost(root, context, meta, "cr", CSS);
  const canvas = htmlNode("canvas", "cr-canvas");
  canvas.width = 920;
  canvas.height = 360;
  const copy = htmlNode("div", "cr-copy", label);
  copy.prepend(htmlNode("span", "cr-meta", `GPU DOT MATRIX · ${opacities.length} OPACITY LEVELS`));
  element.append(canvas, htmlNode("div", "cr-vignette"), copy);
  const gl = canvas.getContext("webgl", { alpha: true, antialias: false, preserveDrawingBuffer: true });
  if (!gl) throw new Error("[canvas-reveal] WebGL 不可用");
  const program = gl.createProgram();
  gl.attachShader(program, shader(gl, gl.VERTEX_SHADER, VERTEX));
  gl.attachShader(program, shader(gl, gl.FRAGMENT_SHADER, FRAGMENT));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]), gl.STATIC_DRAW);
  const position = gl.getAttribLocation(program, "a_position");
  gl.enableVertexAttribArray(position);
  gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
  const uniforms = Object.fromEntries(["u_resolution","u_progress","u_seed","u_color_a","u_color_b","u_dot_size"].map((name) => [name, gl.getUniformLocation(program, name)]));
  const state = { progress: 0 };
  const first = colorArray(colors[0], [0,229,255]);
  const second = colorArray(colors[1] ?? colors[0], [139,92,246]);

  function render() {
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0.01, 0.02, 0.025, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform2f(uniforms.u_resolution, canvas.width, canvas.height);
    gl.uniform1f(uniforms.u_progress, state.progress);
    gl.uniform1f(uniforms.u_seed, Number(seed) || 17);
    gl.uniform3fv(uniforms.u_color_a, first);
    gl.uniform3fv(uniforms.u_color_b, second);
    gl.uniform1f(uniforms.u_dot_size, Math.max(1, Math.min(5, Number(dotSize) || 2)));
    gl.drawArrays(gl.TRIANGLES, 0, 6);
  }

  const { enter, emphasis, dim, exit } = standardTimelines(gsap, element, [canvas, copy], state, render);
  const segments = { enter, emphasis, dim, exit };
  return {
    segments,
    seek(localFrame) {
      enter.time(Math.max(0, localFrame) / fps);
    },
    destroy() {
      gl.deleteBuffer(buffer);
      gl.deleteProgram(program);
      destroyFidelity(element, segments);
    },
  };
}
