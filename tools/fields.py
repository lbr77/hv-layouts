"""The guest-context fields OpenHypervisor reads and writes, by a stable name.

Each is matched in a layout dump (hvlayout.py) by the first of its paths the
dump has: Apple moves fields into sub-structures between versions
(state_dirty -> misc.state_dirty), and the offset is what matters.  RO-page
fields are given as offsets into the whole two-page context, i.e. + 0x4000.
"""
import re

RW, RO = "arm_guest_rw_context_t", "arm_guest_ro_context_t"
RO_BASE = 0x4000

FIELDS = [
    ("rw_x0", RW, ["regs.x"]), ("rw_fp", RW, ["regs.fp"]), ("rw_lr", RW, ["regs.lr"]),
    ("rw_sp", RW, ["regs.sp"]), ("rw_pc", RW, ["regs.pc"]), ("rw_cpsr", RW, ["regs.cpsr"]),
    ("rw_neon_q0", RW, ["neon.q"]), ("rw_fpsr", RW, ["neon.fpsr"]), ("rw_fpcr", RW, ["neon.fpcr"]),
    ("rw_shared_sysregs", RW, ["shared_sysregs"]),
    ("rw_banked_sysregs", RW, ["banked_sysregs"]),
    ("rw_dbgregs", RW, ["dbgregs"]),
    ("rw_vgic_sysregs", RW, ["vgic_sysregs"]),
    ("rw_ich_ap0r0", RW, ["vgic_sysregs.ich_ap0r0_el2"]),
    ("rw_ich_ap1r0", RW, ["vgic_sysregs.ich_ap1r0_el2"]),
    ("rw_controls", RW, ["controls"]),
    ("rw_vtimer_offset", RW, ["controls.virtual_timer_offset"]),
    ("rw_timer", RW, ["controls.timer"]),
    ("rw_frozen", RW, ["frozen"]),
    ("rw_state_dirty", RW, ["state_dirty", "misc.state_dirty"]),
    ("rw_guest_ticks", RW, ["guest_tick_count", "misc.guest_tick_count"]),
    ("rw_extregs", RW, ["extregs"]),
    ("rw_vncr", RW, ["vncr"]),
    ("rw_avncr", RW, ["avncr"]),
    ("ro_ver", RO, ["ver"]),
    ("ro_exit_reason", RO, ["exit.vmexit_reason"]),
    ("ro_exit_esr", RO, ["exit.vmexit_esr"]),
    ("ro_exit_instr", RO, ["exit.vmexit_instr"]),
    ("ro_exit_far", RO, ["exit.vmexit_far"]),
    ("ro_exit_hpfar", RO, ["exit.vmexit_hpfar"]),
    ("ro_controls", RO, ["controls"]),
    ("ro_state_valid", RO, ["state_valid", "state.valid"]),
    ("ro_state_dirty", RO, ["state_dirty", "state.dirty"]),
    ("ro_state_used", RO, ["state_used", "state.used"]),
    ("ro_ich_vtr", RO, ["ich_vtr_el2", "ich.ich_vtr_el2"]),
    ("ro_ich_misr", RO, ["ich_misr_el2", "ich.ich_misr_el2"]),
    ("ro_ich_elrsr", RO, ["ich_elrsr_el2", "ich.ich_elrsr_el2"]),
    ("ro_svcr", RO, ["svcr", "sme_state.svcr"]),
    ("ro_svl_b", RO, ["svl_b", "sme_state.svl_b"]),
    ("ro_sme_ptr", RO, ["sme", "misc.sme"]),
    ("ro_amx_ptr", RO, ["amx", "misc.amx"]),
]

# Blocks whose members a VMM addresses by register name.
BLOCKS = ["arm_guest_shared_sysregs_t", "arm_guest_banked_sysregs_t", "arm_guest_dbgregs_t",
          "arm_vgic_sysregs_t", "arm_guest_controls_t", "arm_guest_extregs_t",
          "arm_vncr_context_t", "apple_vncr_context_t"]


def load(path):
    """{type: {path: (offset, size)}} from a layout dump."""
    types, cur = {}, None
    for line in open(path):
        if line.startswith("## "):
            cur = line.split()[1]
            types[cur] = {} if "MISSING" not in line else None
            continue
        m = re.match(r"(0x[0-9a-f]+)\s+(\d+)\s+(\S+)", line)
        if m and cur and types[cur] is not None:
            types[cur].setdefault(m.group(3), (int(m.group(1), 16), int(m.group(2))))
    return types


def fields(types):
    """{name: (offset, size) or None} for FIELDS."""
    out = {}
    for name, t, paths in FIELDS:
        got = None
        for p in paths:
            if p in (types.get(t) or {}):
                off, size = types[t][p]
                got = (off + (RO_BASE if t == RO else 0), size)
                break
        out[name] = got
    return out


def members(types, block):
    """{member: (offset within the block, size)} of a block's direct members."""
    return {p: v for p, v in (types.get(block) or {}).items() if "." not in p and "[" not in p}
