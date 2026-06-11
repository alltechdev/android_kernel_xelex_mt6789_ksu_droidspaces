#!/usr/bin/env python3
"""
Repack a GKI v4 boot.img for the Zinwa Q25 (MT6789).
Reads the original header and ramdisk from tools/ in this repo,
replaces the kernel with a freshly built Image.gz.

Environment overrides:
  KERNEL_IMAGE  path to Image.gz  (default: out/arch/arm64/boot/Image.gz)
  OUT_BOOT      output path       (default: out/boot.img)
"""
import os, struct, math, sys

PAGE      = 4096
PART_SIZE = 67108864   # BOARD_BOOTIMAGE_PARTITION_SIZE

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, 'tools')

kernel_path = os.environ.get('KERNEL_IMAGE', os.path.join(REPO, 'out/arch/arm64/boot/Image.gz'))
out_path    = os.environ.get('OUT_BOOT',     os.path.join(REPO, 'out/boot.img'))
hdr_path    = os.path.join(TOOLS, 'boot_header.bin')
rdisk_path  = os.path.join(TOOLS, 'ramdisk.cpio.gz')

def page_pad(data):
    rem = len(data) % PAGE
    return data + b'\x00' * (PAGE - rem) if rem else data

kernel  = open(kernel_path, 'rb').read()
ramdisk = open(rdisk_path,  'rb').read()
hdr     = bytearray(open(hdr_path, 'rb').read())

struct.pack_into('<I', hdr, 8,  len(kernel))
struct.pack_into('<I', hdr, 12, len(ramdisk))

out = page_pad(bytes(hdr)) + page_pad(kernel) + page_pad(ramdisk)

if len(out) > PART_SIZE:
    sys.exit(f"ERROR: image {len(out)} bytes exceeds partition {PART_SIZE}")

out += b'\x00' * (PART_SIZE - len(out))

os.makedirs(os.path.dirname(out_path), exist_ok=True)
open(out_path, 'wb').write(out)
print(f"boot.img  → {out_path}")
print(f"  kernel  {len(kernel)/1024/1024:.2f} MB")
print(f"  ramdisk {len(ramdisk)/1024/1024:.2f} MB")
print(f"  total   {len(out)/1024/1024:.0f} MB")
