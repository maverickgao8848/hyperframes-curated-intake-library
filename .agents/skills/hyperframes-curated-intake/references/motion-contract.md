# Motion contract

An approved v3 scene is executable only when its numeric timing, visual state, semantic motion, and
required `uses` bindings are explicit. Build receipts reference Storyboard scene and use IDs rather
than copying creative prose. Selectors and target paths are implementation evidence, not Storyboard
fields.

One parent paused GSAP timeline owns each composition. Blocks mount as real sub-compositions;
Components mount their staged structure/runtime; SVG and Lottie use staged sources. All behavior is
deterministic under forward, backward, and direct seek.

Build evidence for every required use includes its implementation source, runtime target, timeline
binding, opening state, at least one diagnostic intermediate state, settled state, and final hold.
For fold, trace, split, decode, or morph, the intermediate state must visibly distinguish the named
behavior from an opacity/translate entrance. Scenes longer than three seconds must demonstrate the
declared internal semantic change or preserve the approved static reason. Transition evidence
samples outgoing, midpoint, and incoming states.
