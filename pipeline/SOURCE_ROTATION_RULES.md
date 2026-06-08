# Today on Earth Source Rotation Rules

## Flexible Provider Rotation

Daily source selection should be random and flexible across two approved pools:

- SkylineWebcams direct-HLS: large pool, hundreds of possible cameras.
- User-curated YouTube list: `C:\Users\Administrator\Desktop\today-on-earth\镜头源.txt`. These are manually selected and maintained by the user, so they count as quality-approved candidates, not low-priority leftovers.

Do not use fixed provider quotas. Do not force 2-3 YouTube sources, and do not force the episode to start from Skyline. Let the available candidate set, freshness rules, geography, and final visual check decide.

Default 7-region selection posture:

- Build a candidate list from unused Skyline sources and unused curated YouTube sources.
- Shuffle/randomize candidates first so the show does not feel manually patterned.
- Select 7 by filtering for non-repeat, country/city-cluster spread, broad geo-zone spread, and visual fit.
- Provider mix is a result, not an input. A normal episode may have many Skyline sources, several YouTube sources, or occasionally mostly YouTube if the curated list and diversity checks support it.

Reason:

- Skyline direct HLS gives scale and automation stability.
- The curated YouTube file gives hand-picked high-quality views and will keep growing as the user adds sources.
- Random flexible selection avoids burning through the small YouTube list while still allowing good YouTube views to appear naturally.

## Selection Priority

- Treat Skyline and curated YouTube as eligible candidates after they pass source checks.
- Do not choose all sources from the provider that happened to work best in the previous test run unless random selection and diversity checks naturally lead there.
- Keep daily non-repeat by `source_id`, city cluster, and country cluster. Treat provider balance as a quality judgment, not a hard ratio.
- Normal 7-region episodes should aim for at least 6 countries and at least 4 broad geo-zones when possible.

## Quality Check

- Skyline: verify direct HLS frame is clean and does not contain giant burned-in overlays.
- YouTube/OpenCLI: verify precheck frames and final timeline show real video, no browser UI, and distinct views for every source.
- Always inspect the final timeline/contact sheet before delivery.
