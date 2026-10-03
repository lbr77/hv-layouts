#!/usr/bin/env python3
"""plan.py -- which builds this run processes, as `builds=<json list>` for
$GITHUB_OUTPUT.

BUILDS (space or comma separated) names them outright.  Otherwise every build
the KDK mirror has released and layouts/ does not have yet, newest first, at
most LIMIT of them -- so a scheduled run picks up new betas by itself.
"""
import json, os, re, subprocess

MIRROR = os.environ.get("KDK_MIRROR", "dortania/KdkSupportPkg")
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
asked = [b for b in re.split(r"[\s,]+", os.environ.get("BUILDS", "")) if b]
if asked:
    builds = asked
else:
    rows = subprocess.run(
        ["gh", "api", "--paginate", "repos/%s/releases" % MIRROR,
         "--jq", ".[] | select(.assets | map(.name) | any(endswith(\".dmg\"))) | [.tag_name, .published_at] | @tsv"],
        check=True, capture_output=True, text=True).stdout.split("\n")
    have = set(os.listdir(os.path.join(root, "layouts")))
    rel = sorted((r.split("\t") for r in rows if r), key=lambda r: r[1], reverse=True)
    builds = [tag for tag, _ in rel if tag not in have][:int(os.environ.get("LIMIT") or 8)]
print("builds=" + json.dumps(builds))
