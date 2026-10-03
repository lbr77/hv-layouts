#!/usr/bin/env python3
"""meta.py BUILD WORK OUT SOC -- OUT/BUILD/meta.json: where this build's
layout came from."""
import json, os, re, sys
build, work, out, soc = sys.argv[1:5]
name = open(os.path.join(work, "release-name.txt")).read().strip()
versions = json.load(open(os.path.join(work, "kernel_versions.json")))
# The macOS major version from the build number's first two digits: 20x-24x
# are macOS 11-15, and from 25x (macOS 26) the two numbers are one apart.
# The mirror's release titles are not always right about it, so they are
# kept as they are and not trusted.
prefix = int(re.match(r"\d+", build).group())
json.dump({
    "build": build,
    "macos": prefix - 9 if prefix <= 24 else prefix + 1,
    "release": name,
    "kernel": versions.get("kernel.release." + soc, ""),
    "soc": soc,
    "kdk_sha256": open(os.path.join(work, "kdk.sha256")).read().split()[0],
    "mirror": os.environ.get("KDK_MIRROR", "dortania/KdkSupportPkg"),
}, open(os.path.join(out, build, "meta.json"), "w"), indent=1, sort_keys=True)
