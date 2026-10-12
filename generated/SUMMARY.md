# hv guest-context layouts

From each Kernel Debug Kit's DWARF (`kernel.release.<soc>`, the newest SoC in the kit);
offsets/sizes in bytes, RO page at +0x4000.  One row per distinct layout, by the
versions its kernels report; layouts with no version constant (before macOS 26.4) first.

| layout | versions | rw_dbgregs | rw_vgic_sysregs | rw_controls | rw_state_dirty | rw_extregs | ro_exit_esr | ro_state_valid | ro_ich_vtr | ro_svcr | ro_sme_ptr | builds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8b5b294984e8 | ? | 0x478/544 | - | 0x698/224 | 0x780/8 | 0x790/664 | 0x400c/4 | 0x4108/8 | 0x4120/4 | - | - | 23J220 .. 23J631 (3) |
| 0a33aad489fd | ? | 0x478/544 | - | 0x698/224 | 0x780/8 | 0x790/664 | 0x400c/4 | 0x4108/8 | 0x4120/4 | 0x4130/8 | 0x4140/8 | 24G419 .. 24H32 (5) |
| 6f0cdc4b3fca | ? | 0x478/544 | 0x698/16 | 0x6a8/216 | 0x788/8 | 0x798/664 | 0x400c/4 | 0x4100/8 | 0x4118/4 | 0x4128/8 | 0x4138/8 | 25C5037j .. 25D5087f (7) |
| 8471e34eb817 | 3.0.0 | 0x478/544 | 0x698/16 | 0x6a8/216 | 0x788/8 | 0x798/664 | 0x4010/8 | 0x4108/8 | 0x4120/8 | 0x4138/8 | 0x4148/8 | 25E246 .. 25G83 (20) |
| dc1202a8be1a | 3.0.2 3.0.3 | 0x488/544 | 0x6a8/24 | 0x920/216 | 0xa00/8 | 0xa10/664 | 0x4010/8 | 0x4108/8 | 0x4120/8 | 0x4138/8 | 0x4148/8 | 26A5353q .. 26A5378n (3) |
| 45699c01ffac | 3.0.4 | 0x488/544 | 0x6a8/24 | 0x920/224 | 0xa08/8 | 0xa18/664 | 0x4010/8 | 0x4110/8 | 0x4128/8 | 0x4140/8 | 0x4150/8 | 26A428 .. 26B5101f (9) |

| build | macOS | version | layout | kernel | mirror's title |
|---|---|---|---|---|---|
| 23J220 | 14 | ? | 8b5b294984e8 | Darwin Kernel Version 23.6.0: Wed Nov  5 21:49:14 PST 2025; root:xnu-10063.141.1.708.2~1/RELEASE_ARM64_T8122 | Kernel Debug Kit 14.8.3 build 23J220 |
| 23J319 | 14 | ? | 8b5b294984e8 | Darwin Kernel Version 23.6.0: Mon Jan 19 22:04:04 PST 2026; root:xnu-10063.141.1.710.3~1/RELEASE_ARM64_T8122 | Kernel Debug Kit 14.8.4 build 23J319 |
| 23J631 | 14 | ? | 8b5b294984e8 | Darwin Kernel Version 23.6.0: Tue Jul 21 21:57:40 PDT 2026; root:xnu-10063.141.1.713.39~1/RELEASE_ARM64_T8122 | Kernel Debug Kit 14.8.9 build 23J631 |
| 24G419 | 15 | ? | 0a33aad489fd | Darwin Kernel Version 24.6.0: Wed Nov  5 21:34:00 PST 2025; root:xnu-11417.140.69.705.2~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 15.7.3 build 24G419 |
| 24G517 | 15 | ? | 0a33aad489fd | Darwin Kernel Version 24.6.0: Mon Jan 19 22:01:41 PST 2026; root:xnu-11417.140.69.708.3~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 15.7.4 build 24G517 |
| 24G830 | 15 | ? | 0a33aad489fd | Darwin Kernel Version 24.6.0: Tue Jul 21 20:51:25 PDT 2026; root:xnu-11417.140.69.711.44~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 15.7.9 build 24G830 |
| 24H23 | 15 | ? | 0a33aad489fd | Darwin Kernel Version 24.6.0: Sun Aug 23 20:37:17 PDT 2026; root:xnu-11417.140.69.712.69~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 15.8 build 24H23 |
| 24H32 | 15 | ? | 0a33aad489fd | Darwin Kernel Version 24.6.0: Sun Aug 23 20:37:17 PDT 2026; root:xnu-11417.140.69.712.69~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 15.8.1 build 24H32 |
| 25C5037j | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.2.0: Tue Nov  4 20:46:18 PST 2025; root:xnu-12377.60.50.501.1~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.2 build 25C5037j |
| 25C5048a | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.2.0: Thu Nov 13 23:28:51 PST 2025; root:xnu-12377.61.11~7/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.2 build 25C5048a |
| 25C56 | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.2.0: Tue Nov 18 21:08:48 PST 2025; root:xnu-12377.61.12~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.2 build 25C56 |
| 25D125 | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.3.0: Wed Jan 28 20:49:24 PST 2026; root:xnu-12377.81.4~5/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.3 build 25D125 |
| 25D2128 | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.3.0: Wed Jan 28 20:54:55 PST 2026; root:xnu-12377.91.3~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.3.1 build 25D2128 |
| 25D2140 | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.3.0: Wed Jan 28 20:54:55 PST 2026; root:xnu-12377.91.3~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.3.2 build 25D2140 |
| 25D5087f | 26 | ? | 6f0cdc4b3fca | Darwin Kernel Version 25.3.0: Fri Dec  5 23:13:21 PST 2025; root:xnu-12377.80.260.0.1~42/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.3 build 25D5087f |
| 25E246 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.4.0: Thu Mar 19 19:31:09 PDT 2026; root:xnu-12377.101.15~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.4 build 25E246 |
| 25E253 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.4.0: Thu Mar 19 19:31:09 PDT 2026; root:xnu-12377.101.15~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.4.1 build 25E253 |
| 25E5233c | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.4.0: Thu Mar  5 22:43:32 PST 2026; root:xnu-12377.101.14~19/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.4 build 25E5233c |
| 25F5042g | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.5.0: Fri Mar 20 18:54:08 PDT 2026; root:xnu-12377.120.72.0.4~13/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.5.1 build 25F5042g |
| 25F5058e | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.5.0: Tue Apr 14 21:52:36 PDT 2026; root:xnu-12377.120.99.0.7~25/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.5 Build 25F5058e |
| 25F5068a | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.5.0: Thu Apr 23 21:23:23 PDT 2026; root:xnu-12377.121.5~4/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.5.4 build 25F5068a |
| 25F71 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.5.0: Mon Apr 27 20:41:26 PDT 2026; root:xnu-12377.121.6~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.5 build 25F71 |
| 25F80 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.5.0: Mon Apr 27 20:41:26 PDT 2026; root:xnu-12377.121.6~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.5.1 build 25F80 |
| 25F84 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.5.0: Tue Jun  9 22:26:22 PDT 2026; root:xnu-12377.121.10~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.5.2 build 25F84 |
| 25G229 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Tue Aug 18 17:51:33 PDT 2026; root:xnu-12377.161.15.700.19~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.7 build 25G229 |
| 25G241 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Tue Aug 18 17:51:33 PDT 2026; root:xnu-12377.161.15.700.19~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.7.1 build 25G241 |
| 25G5043d | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Tue Jun  9 23:05:09 PDT 2026; root:xnu-12377.160.70.501.6~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6 build 25G5043d |
| 25G5052e | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Thu Jun 18 00:38:51 PDT 2026; root:xnu-12377.160.73.0.5~11/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6 build 25G5052e |
| 25G5057c | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Sun Jun 28 20:27:27 PDT 2026; root:xnu-12377.160.87.0.2~12/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6 Build 25G5057c |
| 25G5065a | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Fri Jul 10 00:22:44 PDT 2026; root:xnu-12377.161.12~4/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6 build 25G5065a |
| 25G70 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Sat Jul 11 15:26:29 PDT 2026; root:xnu-12377.161.13~4/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6 build 25G70 |
| 25G72 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Sat Jul 11 15:26:29 PDT 2026; root:xnu-12377.161.13~4/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6 build 25G72 |
| 25G76 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Sat Jul 11 15:26:29 PDT 2026; root:xnu-12377.161.13~4/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6.1 build 25G76 |
| 25G82 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Fri Jul 31 19:11:03 PDT 2026; root:xnu-12377.161.14~5/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6.2 build 25G82 |
| 25G83 | 26 | 3.0.0 | 8471e34eb817 | Darwin Kernel Version 25.6.0: Fri Jul 31 19:11:03 PDT 2026; root:xnu-12377.161.14~5/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.6.2 build 25G83 |
| 26A428 | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.0.0: Tue Aug 11 21:02:57 PDT 2026; root:xnu-13432.1.9~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.0 build 26A428 |
| 26A434 | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.0.0: Tue Aug 11 21:02:57 PDT 2026; root:xnu-13432.1.9~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.0.1 build 26A434 |
| 26A5353q | 27 | 3.0.2 | dc1202a8be1a | Darwin Kernel Version 27.0.0: Wed May 27 02:11:37 PDT 2026; root:xnu-13361.0.0.501.1~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.0 build 26A5353q |
| 26A5368g | 27 | 3.0.3 | dc1202a8be1a | Darwin Kernel Version 27.0.0: Mon Jun 15 23:01:03 PDT 2026; root:xnu-13432.0.5.501.1~2/RELEASE_ARM64_T8132 | Kernel Debug Kit 26.7 build 26A5368g |
| 26A5378n | 27 | 3.0.3 | dc1202a8be1a | Darwin Kernel Version 27.0.0: Mon Jun 29 21:23:20 PDT 2026; root:xnu-13432.0.50.501.3~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.0 build 26A5378n |
| 26A5388g | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.0.0: Tue Jul 14 21:40:50 PDT 2026; root:xnu-13432.0.94.501.4~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 27 build 26A5388g |
| 26A5406e | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.0.0: Wed Aug  5 22:05:23 PDT 2026; root:xnu-13432.1.6.501.1~1/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.0 build 26A5406e |
| 26A5416b | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.0.0: Tue Aug 11 22:02:53 PDT 2026; root:xnu-13432.1.9~3/RELEASE_ARM64_T8132 | Kernel Debug Kit 27 build 26A5416b |
| 26A5425a | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.0.0: Tue Aug 11 22:02:53 PDT 2026; root:xnu-13432.1.9~3/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.0 build 26A5425a |
| 26B5086k | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.2.0: Fri Sep  4 23:26:57 PDT 2026; root:xnu-13432.40.144.0.1~53/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.2 build 26B5086k |
| 26B5091g | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.2.0: Sun Sep 13 19:47:19 PDT 2026; root:xnu-13432.40.162~92/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.2 build 26B5091g |
| 26B5101f | 27 | 3.0.4 | 45699c01ffac | Darwin Kernel Version 27.2.0: Tue Sep 29 21:47:26 PDT 2026; root:xnu-13432.40.177.0.3~56/RELEASE_ARM64_T8132 | Kernel Debug Kit 27.2 build 26B5101f |
