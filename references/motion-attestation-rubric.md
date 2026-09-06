# Motion attestation rubric v1

This rubric is the semantic authority used by the normal Curated Intake or Visual Director agent.
Its only production identifier is the exact, case-sensitive string `motion-attestation/v1`.
It does not add a user approval step. The CLI validates only the external attestation's structure,
supported agent provenance, exact Storyboard hash, exact full `motionQuote`, scene coverage, and
duplicate/conflicting records; it performs no keyword, prefix, length, denylist, substring, or NLP
semantic judgment.

For each scene longer than three seconds, attest `internal-change` only when the motion describes
specific unequal before and after semantic states and a concrete direction between them. Attest
`static-reason` only when it identifies the held object and a specific production reason for holding
it. Generic change claims, templates, same-state paraphrases, missing direction, and generic static
claims fail the rubric. Record the conclusion and rationale outside Storyboard v3, quote `motion`
verbatim, and identify the rubric version plus model or run provenance.

The executable review fixture is
`references/fixtures/curated-intake-motion-attestation-v1.json` inside this skill.
