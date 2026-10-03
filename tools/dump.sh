#!/bin/sh
# dump.sh BUILD KERNELS OUT [SOC] -- the hv layout and version of one build.
#
# KERNELS is what kdk_extract.py wrote: kernel.release.<SOC> and its dSYM.
# Writes OUT/BUILD/layout.txt (every hv guest-context type, from the DWARF)
# and OUT/BUILD/version.txt (the ARM_HV_STATE_VER constant in the kernel).
# LLDB is ${LLDB:-lldb-18, or lldb}; any LLDB with Python reads a Mach-O
# kernel and its dSYM on Linux as well as on macOS.
set -eu
build=$1 kernels=$2 out=$3 soc=${4:-t8132}
here=$(cd "$(dirname "$0")" && pwd)
lldb=${LLDB:-$(command -v lldb-18 || command -v lldb)}
kernel=$kernels/kernel.release.$soc
dwarf=$kernel.dSYM/Contents/Resources/DWARF/kernel.release.$soc
mkdir -p "$out/$build"
# The layout comes from the dSYM's DWARF on its own: that is all it needs, and
# Ubuntu's LLDB 18 dies with SIGBUS parsing the kernel binary itself.  The
# kernel is still read for its version constant, below.
status=0
"$lldb" --batch --no-lldbinit \
    -o "target create $dwarf" \
    -o "command script import $here/hvlayout.py" \
    -o "hvlayout $out/$build/layout.txt" > "$out/$build/lldb.log" 2>&1 || status=$?
[ "$status" -eq 0 ] || echo "dump.sh: $lldb exited with $status" >&2
grep -qs "^## arm_guest_rw_context_t size 0x4000" "$out/$build/layout.txt" || {
    cat "$out/$build/lldb.log" >&2
    echo "dump.sh: no arm_guest_rw_context_t in the DWARF of $kernel" >&2
    exit 1
}
python3 "$here/hvver.py" "$kernel" > "$out/$build/version.txt"
[ "$(wc -l < "$out/$build/version.txt")" -eq 1 ] || {
    cat "$out/$build/version.txt" >&2
    echo "dump.sh: expected exactly one ARM_HV_STATE_VER constant in $kernel" >&2
    exit 1
}
cat "$out/$build/version.txt"
