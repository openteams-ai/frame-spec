# Frames And The Surrounding Ecosystem

The Frame spec is open and tool-agnostic: nothing in this repository requires any specific product. Several projects led by [OpenTeams](https://openteams.com/) (the company stewarding this spec) are natural consumers or distributors of Frames, and the discussion docs mention them by name. This page gives the one-line definitions so those mentions are readable without prior context.

- **Cog** — a specialized, self-contained AI worker that performs discrete tasks, oriented by the Frames that apply to it. Cogs are described in the Intelligence Hub whitepaper; no Cog spec exists yet.
- **Op** — a workflow that coordinates Cogs and humans toward a larger outcome. Early drafts called these "Progs"; the concept was renamed to Ops.
- **Collab** — a desktop application for private, local-first AI from OpenTeams ([openteams.com/collab](https://openteams.com/collab/)). Collab applies Frames on the desktop and connects to a Collab server/hub that hosts and shares them. A public hub is available (currently by private invitation). The hub was previously known as "Nexus"; that name is retired.
- **Nebi** — an open-source, multi-user environment management tool led by OpenTeams ([nebi.nebari.dev](https://nebi.nebari.dev/)): "git for environments," built on Pixi, with versioned push/pull and publishing to OCI registries. Today Nebi manages computational environments; the plan is to expand it beyond environments, which could make it a natural packaging and distribution layer for Frames. Nebi does not currently define or ship Frame support — docs here that discuss Nebi describe possible future integration.
- **Intelligence Hub** — the broader architecture connecting the pieces above, described in the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper), which is maintained in its own public repository.

None of these projects define what a Frame is. The spec in this repository stands alone; these projects illustrate how Frames may be applied, hosted, and distributed.

## Reference Links

This page is the single place in the repository where these external URLs are recorded. Other documents link here rather than repeating them, so a URL only has to be updated in one file.

- Intelligence Hub whitepaper — <https://github.com/openteams-ai/inthub-whitepaper>
- Collab — <https://openteams.com/collab/>
- Nebi — <https://nebi.nebari.dev/>
- OpenTeams — <https://openteams.com/>
