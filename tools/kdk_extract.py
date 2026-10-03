#!/usr/bin/env python3
"""kdk_extract.py (--dmg DMG | --pkg PKG) OUT SOC...

Take kernel.release.<SOC> and its dSYM out of an Apple Kernel Debug Kit,
without macOS and without unpacking the rest of it.

* The disk image is opened with 7-Zip (7zz or 7z), which reads the UDIF image
  and the HFS+ volume inside it, to get at KernelDebugKit.pkg.
* The installer is a xar archive: its table of contents is zlib-compressed
  XML that says where each member sits in the heap behind it.  The component
  package's Payload is read from there directly.
* The Payload is pbzx -- a run of xz streams -- over an odc cpio archive.  It
  is decoded and walked as it streams, and only the files asked for are
  written: the kit's payload is several gigabytes, the files wanted here are
  under a hundred megabytes.

Files land in OUT with their path below System/Library/Kernels/, which is how
a kernel finds its dSYM.  Prints each file written with its size and SHA-256.
"""
import argparse, glob, hashlib, lzma, os, shutil, stat, struct, subprocess, sys, tempfile, zlib
import xml.etree.ElementTree as ET

KERNELS = "System/Library/Kernels/"


def find_pkg_in_dmg(dmg, work):
    tool = shutil.which("7zz") or shutil.which("7z")
    if not tool:
        sys.exit("kdk_extract: needs 7-Zip (7zz or 7z) to open a disk image")
    for _ in range(3):                     # dmg -> (partition image ->) volume
        subprocess.run([tool, "x", "-y", "-bso0", "-bsp0", "-o" + work, dmg], check=True)
        pkgs = glob.glob(os.path.join(work, "**", "*.pkg"), recursive=True)
        if pkgs:
            return sorted(pkgs, key=os.path.getsize)[-1]
        inner = [p for p in glob.glob(os.path.join(work, "**", "*"), recursive=True)
                 if os.path.isfile(p) and p.endswith((".hfs", ".img", ".apfs"))]
        if not inner:
            break
        dmg = max(inner, key=os.path.getsize)
    sys.exit("kdk_extract: no .pkg inside %s" % dmg)


class Bounded:
    """A file region, read sequentially."""
    def __init__(self, fh, start, length):
        self.fh, self.left = fh, length
        fh.seek(start)

    def read(self, n):
        n = min(n, self.left)
        data = self.fh.read(n)
        self.left -= len(data)
        return data


def xar_members(path):
    """{member path: (heap offset, length, encoding)} of a xar archive."""
    fh = open(path, "rb")
    magic, hsize, _ver, toc_c, _toc_u, _alg = struct.unpack(">IHHQQI", fh.read(28))
    if magic != 0x78617221:
        sys.exit("kdk_extract: %s is not a xar archive" % path)
    fh.seek(hsize)
    toc = ET.fromstring(zlib.decompress(fh.read(toc_c)))
    heap = hsize + toc_c
    out = {}

    def walk(node, prefix):
        for f in node.findall("file"):
            name = prefix + f.findtext("name")
            data = f.find("data")
            if data is not None:
                enc = data.find("encoding")
                out[name] = (heap + int(data.findtext("offset")), int(data.findtext("length")),
                             enc.get("style") if enc is not None else "application/octet-stream")
            walk(f, name + "/")

    walk(toc.find("toc"), "")
    return fh, out


def pbzx_chunks(src):
    if src.read(4) != b"pbzx":
        sys.exit("kdk_extract: Payload is not pbzx")
    src.read(8)                                      # chunk size
    while True:
        hdr = src.read(16)
        if len(hdr) < 16:
            return
        _flags, length = struct.unpack(">QQ", hdr)
        data = src.read(length)
        yield lzma.decompress(data) if data[:6] == b"\xfd7zXZ\x00" else data


class Stream:
    """Sequential reads over an iterator of byte chunks."""
    def __init__(self, chunks):
        self.it, self.buf, self.pos = iter(chunks), b"", 0

    def _fill(self):
        try:
            self.buf, self.pos = self.buf[self.pos:] + next(self.it), 0
            return True
        except StopIteration:
            return False

    def read(self, n):
        while len(self.buf) - self.pos < n and self._fill():
            pass
        out = self.buf[self.pos:self.pos + n]
        self.pos += len(out)
        return out

    def copy(self, n, sink):
        while n > 0:
            if self.pos >= len(self.buf) and not self._fill():
                raise EOFError("cpio data cut short")
            take = min(n, len(self.buf) - self.pos)
            if sink is not None:
                sink(self.buf[self.pos:self.pos + take])
            self.pos += take
            n -= take


def cpio_extract(stream, want, out):
    written = []
    while True:
        hdr = stream.read(76)
        if len(hdr) < 76:
            break
        if hdr[:6] != b"070707":
            sys.exit("kdk_extract: not an odc cpio header: %r" % hdr[:6])
        mode = int(hdr[18:24], 8)
        namesize = int(hdr[59:65], 8)
        filesize = int(hdr[65:76], 8)
        name = stream.read(namesize).rstrip(b"\0").decode("utf-8", "surrogateescape")
        if name == "TRAILER!!!":
            break
        rel = name[2:] if name.startswith("./") else name
        keep = want(rel)
        dest = os.path.join(out, rel[len(KERNELS):]) if keep else None
        if keep and stat.S_ISDIR(mode):
            os.makedirs(dest, exist_ok=True)
        if keep and stat.S_ISLNK(mode):
            target = bytearray()
            stream.copy(filesize, target.extend)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.symlink(bytes(target).decode(), dest)
            continue
        if keep and stat.S_ISREG(mode):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            h = hashlib.sha256()
            with open(dest, "wb") as fh:
                def sink(b):
                    fh.write(b)
                    h.update(b)
                stream.copy(filesize, sink)
            os.chmod(dest, stat.S_IMODE(mode))
            written.append((rel[len(KERNELS):], filesize, h.hexdigest()))
            continue
        stream.copy(filesize, None)
    return written


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--dmg")
    src.add_argument("--pkg")
    ap.add_argument("out")
    ap.add_argument("socs", nargs="+")
    a = ap.parse_args()

    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(a.out))) as work:
        pkg = a.pkg or find_pkg_in_dmg(a.dmg, work)
        fh, members = xar_members(pkg)
        payloads = [m for m in members if m.endswith("/Payload") or m == "Payload"]
        names = tuple(KERNELS + "kernel.release." + s for s in a.socs)

        def want(rel):
            return any(rel == n or rel.startswith(n + ".dSYM") for n in names)

        os.makedirs(a.out, exist_ok=True)
        written = []
        for p in payloads:
            off, length, enc = members[p]
            if enc != "application/octet-stream":
                sys.exit("kdk_extract: %s is stored as %s" % (p, enc))
            written += cpio_extract(Stream(pbzx_chunks(Bounded(fh, off, length))), want, a.out)
        if not written:
            sys.exit("kdk_extract: none of %s in %s" % (", ".join(names), pkg))
        for rel, size, digest in written:
            print("%s  %10d  %s" % (digest, size, rel))


if __name__ == "__main__":
    main()
