#!/bin/sh
# fetch.sh BUILD WORK -- the Kernel Debug Kit of BUILD from the mirror,
# checked against the SHA-256 the mirror publishes for it.
set -eu
build=$1 work=$2
mirror=${KDK_MIRROR:-dortania/KdkSupportPkg}
mkdir -p "$work"
gh release download "$build" -R "$mirror" -D "$work" --clobber \
    -p '*.dmg' -p SHA256SUM -p kernel_versions.json
dmg=$(ls "$work"/*.dmg)
want=$(tr -d ' \n' < "$work/SHA256SUM" | cut -c1-64)
got=$(sha256sum "$dmg" | cut -c1-64)
[ "$want" = "$got" ] || { echo "fetch.sh: $dmg: sha256 $got, mirror says $want" >&2; exit 1; }
gh release view "$build" -R "$mirror" --json name -q .name > "$work/release-name.txt"
mv "$dmg" "$work/kdk.dmg"
echo "$got  $(basename "$dmg")" > "$work/kdk.sha256"
