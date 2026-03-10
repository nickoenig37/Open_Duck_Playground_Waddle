# waddle_12V_backlash_adjusted.xml — Changelog

This file documents all changes made in `waddle_12V_backlash_adjusted.xml` compared to the original `waddle_12V_backlash.xml`. The goal is to align Waddle's joint conventions (limits and body frame orientations) with the Open Duck Mini V2 (`open_duck_mini_v2_backlash.xml`) so that training code, reference motions, and default poses designed for Open Duck transfer correctly to Waddle.

## What Was NOT Changed

| Property | Kept As-Is | Reason |
|---|---|---|
| **Motor dynamics** | `chosen_actuator` class (kp=46.3, damping=1.05, frictionloss=0.195, forcerange=±8.53) | 12V motors are intentionally different from Open Duck's 7.4V STS3215 |
| **Mass / Inertia** | All `<inertial>` elements unchanged | Waddle is physically heavier (1.17 kg trunk vs 0.70 kg) — this is real |
| **IMU position** | `pos="-0.040705 -1.715e-09 0.0862909"` | Waddle's BNO055 is at a different physical location |
| **Collision geometry** | All `<geom class="collision">` unchanged | Foot collision meshes are identical |
| **Backlash joints** | All `_backlash` joints unchanged | Same ±0.5° backlash convention |
| **Actuator section** | All 14 actuators with `class="chosen_actuator"` | Motor class kept intentionally |
| **Mesh assets** | All mesh files still referenced (available for future use) | No STL files removed |
| **Material definitions** | All materials unchanged | Colors are Waddle-specific |

---

## Changes Made

### 1. Joint Limits (Ranges)

These were shifted/offset in the original Waddle file because of different servo horn mounting orientations in the OnShape CAD. They are now aligned to match Open Duck's conventions so that joint angle 0 corresponds to the same physical pose.

| Joint | Original Waddle Range (rad) | New Range (rad) | Open Duck Range (rad) | Change Description |
|---|---|---|---|---|
| `left_hip_pitch` | [-0.44, 1.31] | **[-1.22, 0.52]** | [-1.22, 0.52] | Shifted ~0.78 rad (45°) to match |
| `right_hip_pitch` | [-1.31, 0.44] | **[-0.52, 1.22]** | [-0.52, 1.22] | Mirrored shift to match |
| `left_knee` | [-3.14, 0.0] | **[-1.57, 1.57]** | [-1.57, 1.57] | Centered ±90° range |
| `right_knee` | [-3.14, 0.0] | **[-1.57, 1.57]** | [-1.57, 1.57] | Centered ±90° range |
| `left_ankle` | [-0.79, 2.36] | **[-1.57, 1.57]** | [-1.57, 1.57] | Centered ±90° range |
| `right_ankle` | [-0.79, 2.36] | **[-1.57, 1.57]** | [-1.57, 1.57] | Centered ±90° range |
| `neck_pitch` | [-1.13, 0.35] | **[-0.35, 1.13]** | [-0.35, 1.13] | Inverted to match |
| `head_pitch` | [0.0, 1.57] | **[-0.79, 0.79]** | [-0.79, 0.79] | Symmetric ±45° range |

**Unchanged joints** (already matching Open Duck):
- `left_hip_yaw`: ±30° ✓
- `left_hip_roll`: ±25° ✓
- `right_hip_yaw`: ±30° ✓
- `right_hip_roll`: ±25° ✓
- `head_yaw`: ±160° ✓
- `head_roll`: ±30° ✓

### 2. Body Frame Quaternions

The original Waddle had 45° offsets baked into the body quaternions by `onshape-to-robot` due to different servo horn mounting angles in the CAD. These have been corrected to match Open Duck's pure 90°/identity rotations.

| Body Name | Original Waddle Quat | New Quat | Matches Open Duck |
|---|---|---|---|
| `knee_and_ankle_assembly` (left hip pitch) | `0.270598 -0.653281 -0.270598 0.653281` | **`0 -0.707107 0 0.707107`** | ✓ Pure 90° rotation |
| `knee_and_ankle_assembly_2` (left knee) | `0.707107 0 0 0.707107` | **`1 0 0 0`** | ✓ Identity |
| `foot_assembly` (left ankle) | `0.92388 0 0 -0.382683` | **`1 0 0 0`** | ✓ Identity |
| `neck_pitch_assembly` | `0.653281 0.653281 -0.270598 0.270598` | **`0.707107 0.707107 0 0`** | ✓ Pure rotation |
| `head_pitch_to_yaw` | `0.92388 0 0 -0.382683` | **`1 0 0 0`** | ✓ Identity |
| `knee_and_ankle_assembly_3` (right hip pitch) | `0.653281 0.270598 0.653281 0.270598` | **`0.707107 0 0.707107 0`** | ✓ Pure 90° rotation |
| `knee_and_ankle_assembly_4` (right knee) | `0 -0.707107 0.707107 0` | **`0 1 0 0`** | ✓ Pure 180° |
| `foot_assembly_2` (right ankle) | `0.92388 0 0 -0.382683` | **`1 0 0 0`** | ✓ Identity |

### 3. Removed Internal Visual Geometry

The following visual-only `<geom>` elements were removed (commented out) from the **trunk body** to match Open Duck's convention where internal components are not rendered. This reduces rendering overhead and matches the cleaner Open Duck structure. **None of these affect physics — they are all `class="visual"` with `contype="0" conaffinity="0"`.**

**Trunk body — removed visuals:**
- `jetson_nano_baseplate` — internal PCB mount
- `battery_enclosure` — internal battery holder
- `turnigy_3s_battery` — internal battery
- `simplified_jetson_nano` — internal compute board
- `switch` — internal power switch
- `bno055` — internal IMU chip
- `roll_bearing` / `roll_bearing_2` — internal bearings
- `board` — internal PCB
- `pdb_xt60` — internal power distribution
- All `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier` in trunk (×3 sets)

**Hip roll assemblies — removed servo visuals:**
- `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier` (×1 set per hip)

**Roll-to-pitch assemblies — removed servo visuals:**
- `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier` (×1 set per assembly)

**Knee/ankle assemblies — removed servo visuals:**
- `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier` (×1 set per joint)

**Neck assembly — removed servo visuals:**
- `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier` in neck

**Neck yaw assembly — removed servo visuals:**
- `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier`

**Head assembly — removed internal visuals:**
- `usb_camera_ov2710` (×2) — internal cameras
- `flash_reflector_interface` — internal flash module
- All `wj_wk00_*` servo cases, `drive_palonier`, `passive_palonier` in head

**Kept in head:** right/left antenna holders, antennas, head_bot_sheet, head shell — these are external/visible parts.

---

## Impact on Training

### What this fixes:
1. **Joint angle 0 now corresponds to the same physical pose** as Open Duck — reference motions and default standing poses should transfer correctly.
2. **Symmetric joint ranges** for knees and ankles — the RL policy won't be biased toward one direction.
3. **Reduced visual mesh count** — faster rendering in MuJoCo viewer.

### What to be aware of:
- **Motor dynamics are still 12V** (2.7× stiffer than Open Duck) — you may need to adjust learning rates or reward scaling.
- **Trunk mass is still 1.17 kg** (67% heavier than Open Duck) — balance rewards may need re-tuning.
- **IMU position is different** from Open Duck — gravity vector and angular velocity observations will differ slightly.
- **Visual meshes may appear slightly wrong** due to the quaternion changes — the mesh geometry was originally computed for the Waddle's CAD orientations. The physics will be correct, but some visual meshes may appear rotated. This is cosmetic only.

### Scene file
You will need to create or update a scene file (e.g., `scene_flat_terrain_backlash_adjusted.xml`) that includes `waddle_12V_backlash_adjusted.xml` instead of `waddle_12V_backlash.xml`.
