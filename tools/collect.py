#!/usr/bin/env python3
"""collect.py [INCOMING] -- fold new per-build results into layouts/ and
regenerate generated/.

INCOMING holds <build>/{layout.txt,version.txt,meta.json} directories, as the
extract jobs upload them.

Builds are grouped by the layout itself -- a fingerprint of every hv type the
dump has -- not by version number: before macOS 26.4 the kernel does not keep
ARM_HV_STATE_VER as data, so many builds have no number to group by.  Each
layout lists the versions its builds do report.  Apple bumps the version
whenever the layout changes, so one version on two layouts is reported in
generated/CONFLICTS.md rather than averaged over.
"""
import hashlib, json, os, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fields import BLOCKS, FIELDS, RO, RW, fields, load, members

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYOUTS, GEN = os.path.join(ROOT, "layouts"), os.path.join(ROOT, "generated")


def fingerprint(types):
    keep = {t: sorted((p, list(v)) for p, v in (types.get(t) or {}).items()) for t in [RW, RO] + BLOCKS}
    return hashlib.sha256(json.dumps(keep, sort_keys=True).encode()).hexdigest()[:12]


def read_version(d):
    """(word, "a.b.c") or (None, None); a build may report more than one."""
    p = os.path.join(d, "version.txt")
    found = []
    for line in open(p) if os.path.exists(p) else []:
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("0x"):
            found.append((parts[0], parts[1]))
    return found


def main():
    if len(sys.argv) > 1 and not os.path.isdir(sys.argv[1]):
        print("collect.py: nothing arrived in %s" % sys.argv[1])
    elif len(sys.argv) > 1:
        for b in sorted(os.listdir(sys.argv[1])):
            src = os.path.join(sys.argv[1], b)
            if os.path.isfile(os.path.join(src, "layout.txt")):
                dst = os.path.join(LAYOUTS, b)
                shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns("lldb.log"))

    builds = {}
    for b in sorted(os.listdir(LAYOUTS)):
        d = os.path.join(LAYOUTS, b)
        if not os.path.isfile(os.path.join(d, "layout.txt")):
            continue
        meta_p = os.path.join(d, "meta.json")
        types = load(os.path.join(d, "layout.txt"))
        builds[b] = {"versions": read_version(d), "types": types, "fp": fingerprint(types),
                     "meta": json.load(open(meta_p)) if os.path.exists(meta_p) else {}}

    order, layouts = [], {}
    for b in sorted(builds):
        fp = builds[b]["fp"]
        if fp not in layouts:
            order.append(fp)
            layouts[fp] = {"builds": [], "versions": {}, "types": builds[b]["types"]}
        layouts[fp]["builds"].append(b)
        for word, ver in builds[b]["versions"]:
            layouts[fp]["versions"][ver] = word

    # Release builds sort before their own betas by build number (26A428 <
    # 26A5353q), so order by the lowest version a layout is known by, and the
    # unversioned ones (all older) first, by their first build.
    def vkey(fp):
        vs = sorted(tuple(int(x) for x in v.split(".")) for v in layouts[fp]["versions"])
        return (1, vs[0], "") if vs else (0, (), layouts[fp]["builds"][0])
    order.sort(key=vkey)

    conflicts = []
    by_version = {}
    for fp in order:
        for ver in layouts[fp]["versions"]:
            by_version.setdefault(ver, []).append(fp)
    for ver, fps in sorted(by_version.items()):
        if len(fps) > 1:
            conflicts.append("version %s appears on %d layouts: %s" % (
                ver, len(fps), "; ".join("%s (%s)" % (fp, " ".join(layouts[fp]["builds"])) for fp in fps)))
    for b, info in sorted(builds.items()):
        if len(info["versions"]) > 1:
            conflicts.append("%s carries %d version constants: %s" % (
                b, len(info["versions"]), " ".join(v for _, v in info["versions"])))

    out = {"layouts": [], "builds": {}}
    for fp in order:
        L = layouts[fp]
        f = fields(L["types"])
        out["layouts"].append({
            "id": fp,
            "versions": sorted(L["versions"]),
            "words": [L["versions"][v] for v in sorted(L["versions"])],
            "builds": L["builds"],
            "fields": {k: list(v) if v else None for k, v in f.items()},
            # [name, offset in the block, size], in offset order
            "blocks": {blk: [[m, v[0], v[1]] for m, v in sorted(members(L["types"], blk).items(),
                                                                  key=lambda kv: kv[1][0])]
                       for blk in BLOCKS},
        })
    for b, info in sorted(builds.items()):
        out["builds"][b] = dict(info["meta"], layout=info["fp"],
                                version=info["versions"][0][1] if info["versions"] else None)

    os.makedirs(GEN, exist_ok=True)
    with open(os.path.join(GEN, "layouts.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    write_header(out)
    write_summary(out)
    with open(os.path.join(GEN, "CONFLICTS.md"), "w") as fh:
        fh.write("# Versions that do not name one layout\n\n")
        fh.write("".join("* %s\n" % c for c in conflicts) or "None.\n")
    print("%d builds, %d layouts, %d with a version, %d conflicts" % (
        len(builds), len(order), sum(1 for fp in order if layouts[fp]["versions"]), len(conflicts)))


def write_header(out):
    names = [f[0] for f in FIELDS]
    lines = [
        "/* Generated by tools/collect.py from Kernel Debug Kit DWARF -- do not edit. */",
        "#pragma once",
        "#include <stdint.h>",
        "",
        "/* Offsets into the two-page hv guest context (RO page at +0x4000), and",
        " * sizes, of the fields a VMM touches.  0 size: not in this layout.",
        " * Entries below are positional, field name in the comment, so the header",
        " * is plain C and C++11 alike. */",
        "typedef struct { uint16_t off; uint16_t size; } ohv_hv_field_t;",
        "",
        "/*",
        " * One entry per layout.  ver is the ARM_HV_STATE_VER its kernels report,",
        " * or 0 where the kernels keep no such constant (before macOS 26.4): match",
        " * those by build (kern.osversion) against `builds`, a space-separated list.",
        " * A layout reported under several versions appears once per version.",
        " */",
        "typedef struct {",
        "    uint64_t ver;",
        "    const char *id;",
        "    const char *builds;",
    ] + ["    ohv_hv_field_t %s;" % n for n in names] + [
        "} ohv_hv_layout_t;",
        "",
        "static const ohv_hv_layout_t ohv_hv_layouts[] = {",
    ]
    for L in out["layouts"]:
        for word, ver in (list(zip(L["words"], L["versions"])) or [("0", "no version constant")]):
            lines.append("    { /* %s */" % ver)
            lines.append("        %s, /* ver */" % word)
            lines.append('        "%s", /* id */' % L["id"])
            lines.append('        "%s", /* builds */' % " ".join(L["builds"]))
            for n in names:
                f = L["fields"][n] or (0, 0)
                lines.append("        { 0x%x, %d }, /* %s */" % (f[0], f[1], n))
            lines.append("    },")
    lines += ["};", ""]
    open(os.path.join(GEN, "ohv_hv_layouts.h"), "w").write("\n".join(lines))


def write_summary(out):
    cols = ["rw_dbgregs", "rw_vgic_sysregs", "rw_controls", "rw_state_dirty", "rw_extregs",
            "ro_exit_esr", "ro_state_valid", "ro_ich_vtr", "ro_svcr", "ro_sme_ptr"]
    lines = ["# hv guest-context layouts", "",
             "From each Kernel Debug Kit's DWARF (`kernel.release.<soc>`, the newest SoC in the kit);",
             "offsets/sizes in bytes, RO page at +0x4000.  One row per distinct layout, by the",
             "versions its kernels report; layouts with no version constant (before macOS 26.4) first.", "",
             "| layout | versions | " + " | ".join(cols) + " | builds |",
             "|---" * (len(cols) + 3) + "|"]
    for L in out["layouts"]:
        cells = ["0x%x/%d" % tuple(L["fields"][c]) if L["fields"][c] else "-" for c in cols]
        bs = L["builds"]
        span = bs[0] if len(bs) == 1 else "%s .. %s (%d)" % (bs[0], bs[-1], len(bs))
        lines.append("| %s | %s | %s | %s |" % (L["id"], " ".join(L["versions"]) or "?",
                                                " | ".join(cells), span))
    lines += ["", "| build | macOS | version | layout | kernel | mirror's title |",
              "|---|---|---|---|---|---|"]
    for b, m in out["builds"].items():
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            b, m.get("macos", ""), m.get("version") or "?", m["layout"],
            m.get("kernel", ""), m.get("release", "")))
    open(os.path.join(GEN, "SUMMARY.md"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
