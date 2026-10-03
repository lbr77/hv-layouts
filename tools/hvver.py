#!/usr/bin/env python3
"""hvver.py KERNEL -- the ARM_HV_STATE_VER constants a kernel binary carries
(8-byte words whose high half is the " hyp" magic), with the Mach-O section
each one is in.  Data, not code: the constant is a literal the hv code loads."""
import struct, sys
data = open(sys.argv[1], "rb").read()
magic, ncmds = struct.unpack_from("<II", data, 0)[0], struct.unpack_from("<I", data, 16)[0]
assert magic == 0xfeedfacf, hex(magic)
sects, off = [], 32
for _ in range(ncmds):
    cmd, size = struct.unpack_from("<II", data, off)
    if cmd == 0x19:                                   # LC_SEGMENT_64
        nsects = struct.unpack_from("<I", data, off + 64)[0]
        s = off + 72
        for _ in range(nsects):
            sect = data[s:s + 16].rstrip(b"\0").decode()
            seg = data[s + 16:s + 32].rstrip(b"\0").decode()
            addr, sz, foff = struct.unpack_from("<QQI", data, s + 32)
            sects.append((foff, sz, seg + "," + sect, addr))
            s += 80
    off += size
pos = 0
while True:
    i = data.find(struct.pack("<I", 0x20687970), pos)
    if i < 0:
        break
    pos = i + 1
    if (i - 4) % 8:
        continue
    val = struct.unpack_from("<Q", data, i - 4)[0]
    where = next(("%s+0x%x (vm 0x%x)" % (n, i - 4 - fo, a + i - 4 - fo)
                  for fo, sz, n, a in sects if fo <= i - 4 < fo + sz), "?")
    print("0x%016x  %d.%d.%d  file 0x%x  %s" % (val, (val >> 24) & 0xff, (val >> 16) & 0xff,
          val & 0xffff, i - 4, where))
