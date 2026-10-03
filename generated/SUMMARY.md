# hv guest-context layouts

From each Kernel Debug Kit's DWARF (`kernel.release.t8132`); offsets/sizes in bytes,
RO page at +0x4000.

| version | rw_dbgregs | rw_vgic_sysregs | rw_controls | rw_state_dirty | rw_extregs | ro_exit_esr | ro_state_valid | ro_ich_vtr | ro_svcr | ro_sme_ptr | builds |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.0.0 | 0x478/544 | 0x698/16 | 0x6a8/216 | 0x788/8 | 0x798/664 | 0x4010/8 | 0x4108/8 | 0x4120/8 | 0x4138/8 | 0x4148/8 | 25E246 |
| 3.0.3 | 0x488/544 | 0x6a8/24 | 0x920/216 | 0xa00/8 | 0xa10/664 | 0x4010/8 | 0x4108/8 | 0x4120/8 | 0x4138/8 | 0x4148/8 | 26A5368g |

| build | macOS | version | kernel | mirror's title |
|---|---|---|---|---|
| 25E246 | 26 | 3.0.0 | Darwin Kernel Version 25.4.0: Thu Mar 19 19:31:09 PDT 2026; root:xnu-12377.101.15~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.4 build 25E246 |
| 26A5368g | 27 | 3.0.3 | Darwin Kernel Version 27.0.0: Mon Jun 15 23:01:03 PDT 2026; root:xnu-13432.0.5.501.1~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.7 build 26A5368g |
