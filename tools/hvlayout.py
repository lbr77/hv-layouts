"""LLDB command `hvlayout OUT [TYPE...]`: dump the hv guest-context types of the
loaded kernel, from its DWARF, as `offset size path type` rows -- absolute
offsets, nested anonymous members flattened, arrays of structs shown once with
their element layout.  Load with: command script import hvlayout.py"""
import lldb

TYPES = [
    "arm_guest_context_t", "arm_guest_rw_context_t", "arm_guest_ro_context_t",
    "arm_guest_shared_sysregs_t", "arm_guest_banked_sysregs_t", "arm_guest_dbgregs_t",
    "arm_vgic_sysregs_t", "arm_guest_controls_t", "arm_guest_frozen_t",
    "arm_guest_vmexit_t", "arm_guest_extregs_t", "arm_vncr_context_t",
    "apple_vncr_context_t", "arm_guest_sme_context_t",
]
AGG = (lldb.eTypeClassStruct, lldb.eTypeClassUnion, lldb.eTypeClassClass)

def walk(t, base, path, rows, depth=0):
    t = t.GetCanonicalType()
    for i in range(t.GetNumberOfFields()):
        f = t.GetFieldAtIndex(i)
        ft = f.GetType()
        ct = ft.GetCanonicalType()
        name = f.GetName() or ""
        p = (path + "." + name) if (path and name) else (name or path)
        off = base + f.GetOffsetInBytes()
        bits = ""
        if f.IsBitfield():
            bits = " :%d@%d" % (f.GetBitfieldSizeInBits(), f.GetOffsetInBits() % 8)
        rows.append((off, ft.GetByteSize(), p or "(anon)", (ft.GetName() or "?") + bits, depth))
        if ct.GetTypeClass() in AGG and depth < 6:
            walk(ct, off, p, rows, depth + 1)
        elif ct.GetTypeClass() == lldb.eTypeClassArray:
            el = ct.GetArrayElementType().GetCanonicalType()
            if el.GetTypeClass() in AGG and depth < 6:
                walk(el, off, p + "[0]", rows, depth + 1)

def hvlayout(debugger, command, result, internal_dict):
    args = command.split()
    out = args[0]
    names = args[1:] or TYPES
    target = debugger.GetSelectedTarget()
    with open(out, "w") as fh:
        for tn in names:
            t = target.FindFirstType(tn)
            if not t.IsValid():
                fh.write("## %s MISSING\n" % tn)
                continue
            fh.write("## %s size 0x%x\n" % (tn, t.GetByteSize()))
            rows = []
            walk(t, 0, "", rows)
            for off, size, p, tname, depth in rows:
                fh.write("0x%05x %6d  %s%s  %s\n" % (off, size, "  " * depth, p, tname))
    result.AppendMessage("wrote " + out)

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("command script add -f hvlayout.hvlayout hvlayout")
