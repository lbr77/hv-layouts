# hv-layouts

The layout of the per-vCPU guest context that macOS's hypervisor shares with
user space -- `arm_guest_rw_context_t` and `arm_guest_ro_context_t` in xnu's
`osfmk/arm64/hv/guest_thread_state.h` -- for every macOS build that has a
Kernel Debug Kit, read from the kernel's own DWARF.

OpenHypervisor addresses that context directly, so it needs these offsets,
and they move: macOS 26.4 (version 3.0.0) and the macOS 27 betas (3.0.3) put
the control block at 0x6a8 and 0x920 respectively. The open-source xnu leaves
out the Apple-private members; the KDK's dSYM has all of them.

## What a run does

For each build (`.github/workflows/layouts.yml`, on Linux runners):

1. `tools/fetch.sh` downloads the KDK from the
   [dortania/KdkSupportPkg](https://github.com/dortania/KdkSupportPkg)
   release mirror and checks it against the SHA-256 the mirror publishes. The
   packages are Apple's (on a Mac, `pkgutil --check-signature` reports
   "signed Apple Software"); this repository stores none of them, only what is
   derived from them.
2. `tools/kdk_extract.py` takes `kernel.release.t8132` and its dSYM out of
   the kit: 7-Zip opens the disk image, and the installer (xar), its pbzx
   payload and the cpio inside are read in Python, streaming, so only the
   files wanted reach the disk.
3. `tools/dump.sh` runs `tools/hvlayout.py` in LLDB, which prints every
   member of the hv types with its offset and size, and `tools/hvver.py`,
   which finds the kernel's `ARM_HV_STATE_VER` constant (the one 8-byte word
   in `__TEXT,__const` whose high half is `" hyp"`).
4. `tools/collect.py` groups the builds by version -- Apple bumps it
   whenever the layout changes -- and writes `generated/`.

The layout does not depend on the SoC: within one build, the t8103, t6000,
t6041, t8122 and t8132 kernels dump identically, so `t8132` stands for all.

## Outputs

* `layouts/<build>/` -- `layout.txt` (the full dump), `version.txt`,
  `meta.json` (macOS version, kernel version string, KDK SHA-256).
* `generated/layouts.json` -- per version: the builds, the fields a VMM uses
  (`tools/fields.py`, matched by name across versions), and every member of
  the register blocks by name.
* `generated/ohv_hv_layouts.h` -- the same fields as a C table, keyed by
  `ARM_HV_STATE_VER`.
* `generated/SUMMARY.md` -- one row per version.
* `generated/CONFLICTS.md` -- versions whose builds disagree (none expected).

## Running it

Actions -> hv layouts -> Run workflow, with `builds` naming KDK builds
(e.g. `26A5368g 25E246`), or empty to take what the mirror has that
`layouts/` does not, newest first. It also runs weekly to pick up new betas.

The tools run on a Mac too (`LLDB=$(xcrun -f lldb)`, and `--pkg` to
`kdk_extract.py` for a mounted kit).
