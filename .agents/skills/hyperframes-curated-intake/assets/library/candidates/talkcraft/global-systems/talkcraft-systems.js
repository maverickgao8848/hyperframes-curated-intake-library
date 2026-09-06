/* Native HyperFrames/GSAP ports of TalkCraft's P0 cross-shot systems.
   These are migration candidates, not published Registry items. */
(function (global) {
  "use strict";
  const assertGsap = () => { if (!global.gsap) throw new Error("GSAP must be available before TalkCraftSystems"); return global.gsap; };
  const target = (value) => typeof value === "string" ? document.querySelector(value) : value;
  const at = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;

  function cameraRig(timeline, selector, keys) {
    const gsap = assertGsap(), node = target(selector);
    if (!node || !Array.isArray(keys) || keys.length < 2) return timeline;
    for (let i = 1; i < keys.length; i += 1) {
      const previous = keys[i - 1], key = keys[i];
      timeline.to(node, {
        x: at(key.x), y: at(key.y), scale: at(key.scale, 1), rotation: at(key.rotation),
        duration: Math.max(0, at(key.time) - at(previous.time)), ease: key.ease || "sine.inOut",
      }, at(previous.time));
    }
    return timeline;
  }

  function parallax(timeline, layers, start, duration, distance) {
    const gsap = assertGsap();
    Array.from(layers || []).forEach((node, index) => {
      const depth = at(node.dataset.depth, index + 1);
      timeline.to(node, {x: at(distance, 24) * depth, y: -at(distance, 24) * depth * .35, duration: at(duration, 4), ease: "none"}, at(start));
    });
    return timeline;
  }

  function live(timeline, selector, start, duration, amplitude) {
    const node = target(selector), amp = at(amplitude, 5), span = at(duration, 4);
    if (!node) return timeline;
    timeline.to(node, {y: -amp, rotation: .25, duration: span / 2, ease: "sine.inOut"}, at(start));
    timeline.to(node, {y: 0, rotation: -.18, duration: span / 2, ease: "sine.inOut"}, at(start) + span / 2);
    return timeline;
  }

  function defocus(timeline, selector, start, duration, blur, opacity) {
    const node = target(selector); if (!node) return timeline;
    timeline.to(node, {filter: `blur(${at(blur, 10)}px)`, opacity: at(opacity, .42), duration: at(duration, .35), ease: "power2.out"}, at(start));
    return timeline;
  }

  function environment(timeline, selector, start, duration) {
    const node = target(selector); if (!node) return timeline;
    timeline.to(node, {backgroundPosition: "62% 44%", opacity: .9, duration: at(duration, 8), ease: "none"}, at(start));
    return timeline;
  }

  function mask(timeline, selector, start, duration, direction) {
    const node = target(selector); if (!node) return timeline;
    const from = direction === "left" ? "inset(0 0 0 100%)" : "inset(0 100% 0 0)";
    const to = "inset(0 0% 0 0%)";
    global.gsap.set(node, {clipPath: from});
    timeline.to(node, {clipPath: to, duration: at(duration, .7), ease: "power3.inOut"}, at(start));
    return timeline;
  }

  global.TalkCraftSystems = Object.freeze({cameraRig, parallax, live, defocus, environment, mask});
})(window);

