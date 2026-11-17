# Common School Archive: local and cloud setup

This handoff is a static Leaflet application and a separate 1887 district-map pilot. It does not need credentials, a database, Node.js, a tile provider, a build service, or a paid account. It does not modify the existing archive site.

## Start from a clean checkout

Use main or the exact commit linked with this report. This repository already contains large archive assets; a sparse partial clone avoids downloading the full collection.

```sh
git clone --filter=blob:none --sparse --branch main https://github.com/zmuhls/cs-archive.git
cd cs-archive
git sparse-checkout set research/common-school-handoff
git rev-parse HEAD
```

If you already have the repository, fetch origin main, then use a separate worktree or clean clone rather than changing a checkout with local edits.

## Run and verify

From the repository root:

```sh
cd research/common-school-handoff
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/atlas/` for the archive atlas and `http://127.0.0.1:8000/monroe-1887-pilot/` for the Clarkson pilot. On an agent's cloud computer, use its authenticated port-preview or forward port 8000 through its existing tooling rather than exposing an unauthenticated listener. If the preview requires binding to all interfaces, do so only in the environment's private preview network. On a local machine, the two `index.html` files can also be opened directly. Internet access is needed for linked archival sources, not for the initial local map.

1. Check that the atlas opens with the source credit and county selector. Pick a county, narrow the dates, and check the record list as well as the map.
2. Open a marker and check whether the label describes a schoolhouse vicinity or a meeting venue. Unpinned entries are not missing software features: the source may not support a location.
3. Open the separate Clarkson pilot. Compare the map crop and digitized outline; check the date and the reported uncertainty. It is one 1887 depiction, not a legally authoritative or statewide district layer.
4. Check a narrow viewport and navigate the controls by keyboard. Confirm that serving without access to third-party tiles or APIs still renders both maps.
5. Read the report and the two packages' README/license files before changing data or deploying. County boundaries and school district boundaries are distinct. Do not mix new source files into the public package without verifying rights and provenance.

## Instructions to paste into a local or cloud agent

> Clone or fetch the Common School handoff on main in `zmuhls/cs-archive` using a sparse checkout for `research/common-school-handoff`. Record the exact commit. Read `REPORT.md`, this runbook and both package READMEs. Start a private static Python preview (port 8000) and verify the atlas county/date filter, keyboard navigation, a source disclosure, an approximate point, and the independent Clarkson pilot. Check that both work without external map tiles. Report your exact commit, preview address, controls tested and failures. Keep original scans untouched; do not publish, deploy, commit, authenticate to any third-party service, or spend money without a separate request. Do not invent locations or convert candidate geography into exact sites. If the historical add-on isn't present, ask the project owner for the matching licensed package rather than copying unrelated data or calling the modern boundaries historical.
