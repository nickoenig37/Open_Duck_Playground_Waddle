"""
Compile the waddle_v2 URDF into a complete MJCF robot file for training.

This script:
  1. Loads the URDF and compiles it via MuJoCo
  2. Saves the compiled MJCF
  3. Adds training-specific elements: freejoint, sites, sensors, actuators,
     named collision geoms, joint properties, solver options
  4. Writes the final robot XML that can be <include>d from a scene file

Run this whenever the URDF changes:
    python -m playground.waddle_urdf.compile_urdf
"""

import os
import tempfile
import xml.etree.ElementTree as ET

import mujoco

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
URDF_PATH = os.path.join(SCRIPT_DIR, "xmls", "waddle_v2.urdf")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "xmls", "waddle_v2_compiled.xml")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")


def _load_assets():
    assets = {}
    for f in os.listdir(ASSETS_DIR):
        if f.endswith(".stl"):
            with open(os.path.join(ASSETS_DIR, f), "rb") as fh:
                assets[f] = fh.read()
    return assets


def _compile_urdf_to_mjcf(urdf_path, assets):
    """Compile URDF via MuJoCo and return the MJCF XML string."""
    with open(urdf_path) as f:
        urdf_text = f.read()
    model = mujoco.MjModel.from_xml_string(urdf_text, assets=assets)
    tmp = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
    try:
        mujoco.mj_saveLastXML(tmp.name, model)
        with open(tmp.name) as f:
            return f.read()
    finally:
        os.unlink(tmp.name)


def _make_elem(tag, attribs):
    """Create an XML element with attributes."""
    return ET.Element(tag, attrib=attribs)


def _add_training_elements(tree):
    """Add all MuJoCo-specific elements needed for training."""
    root = tree.getroot()

    # ── 1. Solver options ─────────────────────────────────────────────────
    option = ET.SubElement(root, "option", attrib={
        "iterations": "1", "ls_iterations": "5",
    })
    ET.SubElement(option, "flag", attrib={"eulerdamp": "disable"})

    # ── 2. Update compiler ────────────────────────────────────────────────
    compiler = root.find("compiler")
    if compiler is not None:
        compiler.set("angle", "radian")
        compiler.set("meshdir", "../assets")
        compiler.set("autolimits", "true")

    # ── 3. Joint property defaults (sts3215_12v motor class) ──────────────
    default_elem = ET.SubElement(root, "default")
    d12v = ET.SubElement(default_elem, "default", attrib={"class": "sts3215_12v"})
    ET.SubElement(d12v, "joint", attrib={
        "damping": "1.05", "frictionloss": "0.195", "armature": "0.032",
    })
    ET.SubElement(d12v, "position", attrib={
        "kp": "46.3", "kv": "0.0", "forcerange": "-8.53 8.53",
    })

    # ── 4. Re-create trunk_assembly body ──────────────────────────────────
    # fusestatic="true" fused trunk_assembly (fixed-joint root link) into
    # worldbody.  We need to wrap everything back into a proper body so
    # we can attach a freejoint to it.
    worldbody = root.find("worldbody")
    trunk = worldbody.find("body[@name='trunk_assembly']")
    if trunk is None:
        # Create a trunk_assembly body and move ALL worldbody children into it
        trunk = ET.Element("body", attrib={"name": "trunk_assembly"})
        children = list(worldbody)
        for child in children:
            worldbody.remove(child)
            trunk.append(child)
        worldbody.append(trunk)

    # Add freejoint as first child of trunk_assembly
    fj = ET.Element("freejoint", attrib={"name": "floating_base"})
    trunk.insert(0, fj)

    # Compute composite inertial for trunk from URDF data
    # (trunk_assembly + all fused dummy links)
    trunk.insert(1, _make_elem("inertial", {
        "pos": "-0.019 0 0.0648909",
        "mass": "0.5",
        "diaginertia": "0.001 0.001 0.001",
    }))

    # Add IMU site (position from URDF's imu dummy link frame)
    ET.SubElement(trunk, "site", attrib={
        "name": "imu",
        "pos": "-0.040705 -1.715e-09 0.0862909",
        "group": "3",
    })

    # Add trunk site
    ET.SubElement(trunk, "site", attrib={
        "name": "trunk",
        "pos": "-0.024 0 0.0881909",
        "group": "3",
    })

    # ── 5. Add foot sites and name collision geoms ────────────────────────
    _add_foot_elements(trunk, "foot_assembly", "left_foot",
                       foot_site_pos="0.0005 -0.036225 0.01955",
                       foot_site_quat="0.707107 -0.707107 0 0")
    _add_foot_elements(trunk, "foot_assembly_2", "right_foot",
                       foot_site_pos="0.0005 -0.036225 0.01955",
                       foot_site_quat="0.707107 -0.707107 0 0")

    # ── 6. Add head site ─────────────────────────────────────────────────
    head_assembly = trunk.find(".//body[@name='head_assembly']")
    if head_assembly is not None:
        ET.SubElement(head_assembly, "site", attrib={
            "name": "head",
            "pos": "0.04245 0 0.03595",
            "quat": "0.707107 0 0.707107 0",
            "group": "3",
        })

    # ── 7. Fix antenna joints → remove them (make bodies static) ─────────
    for antenna_name in ["left_antenna", "right_antenna"]:
        for body in trunk.iter("body"):
            joint = body.find(f"joint[@name='{antenna_name}']")
            if joint is not None:
                body.remove(joint)
                break

    # ── 8. Apply motor class to all actuated joints ──────────────────────
    actuator_joints = [
        "left_hip_yaw", "left_hip_roll", "left_hip_pitch", "left_knee", "left_ankle",
        "neck_pitch", "head_pitch", "head_yaw", "head_roll",
        "right_hip_yaw", "right_hip_roll", "right_hip_pitch", "right_knee", "right_ankle",
    ]
    for jname in actuator_joints:
        for j in trunk.iter("joint"):
            if j.get("name") == jname:
                j.set("class", "sts3215_12v")
                # Remove the generic actuatorfrcrange from URDF compilation
                if "actuatorfrcrange" in j.attrib:
                    del j.attrib["actuatorfrcrange"]
                break

    # ── 9. Sensors ────────────────────────────────────────────────────────
    sensor = ET.SubElement(root, "sensor")
    sensor_defs = [
        ("gyro", {"site": "imu", "name": "gyro"}),
        ("velocimeter", {"site": "imu", "name": "local_linvel"}),
        ("accelerometer", {"site": "imu", "name": "accelerometer"}),
        ("framezaxis", {"objtype": "site", "objname": "imu", "name": "upvector"}),
        ("framexaxis", {"objtype": "site", "objname": "imu", "name": "forwardvector"}),
        ("framelinvel", {"objtype": "site", "objname": "imu", "name": "global_linvel"}),
        ("frameangvel", {"objtype": "site", "objname": "imu", "name": "global_angvel"}),
        ("framepos", {"objtype": "site", "objname": "imu", "name": "position"}),
        ("framequat", {"objtype": "site", "objname": "imu", "name": "orientation"}),
        ("framelinvel", {"objtype": "site", "objname": "right_foot", "name": "right_foot_global_linvel"}),
        ("framelinvel", {"objtype": "site", "objname": "left_foot", "name": "left_foot_global_linvel"}),
        ("framexaxis", {"objtype": "site", "objname": "left_foot", "name": "left_foot_upvector"}),
        ("framexaxis", {"objtype": "site", "objname": "right_foot", "name": "right_foot_upvector"}),
        ("framepos", {"objtype": "site", "objname": "left_foot", "name": "left_foot_pos"}),
        ("framepos", {"objtype": "site", "objname": "right_foot", "name": "right_foot_pos"}),
    ]
    for tag, attribs in sensor_defs:
        ET.SubElement(sensor, tag, attrib=attribs)

    # ── 10. Actuators ────────────────────────────────────────────────────
    actuator = ET.SubElement(root, "actuator")
    for jname in actuator_joints:
        ET.SubElement(actuator, "position", attrib={
            "class": "sts3215_12v",
            "name": jname,
            "joint": jname,
            "inheritrange": "1",
        })

    return tree


def _add_foot_elements(root_body, foot_body_name, site_name, foot_site_pos, foot_site_quat):
    """Find the foot body, add a named site and name the collision geom."""
    foot_body = root_body.find(f".//body[@name='{foot_body_name}']")
    if foot_body is None:
        print(f"WARNING: Could not find body '{foot_body_name}'")
        return

    # Add foot site
    ET.SubElement(foot_body, "site", attrib={
        "name": site_name,
        "pos": foot_site_pos,
        "quat": foot_site_quat,
        "group": "3",
    })

    # Name the collision geom (the one without explicit contype="0")
    # Visual geoms have contype="0" conaffinity="0", collision geoms omit these
    geom_name = f"{site_name}_bottom_tpu"
    for geom in foot_body.findall("geom"):
        contype = geom.get("contype")  # None when attribute absent
        conaffinity = geom.get("conaffinity")
        if contype is None and conaffinity is None:
            geom.set("name", geom_name)
            break


def _indent(elem, level=0):
    """Pretty-print XML with indentation."""
    indent = "\n" + "  " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent
    if level == 0:
        elem.tail = "\n"


def main():
    print(f"Loading URDF: {URDF_PATH}")
    assets = _load_assets()
    mjcf_text = _compile_urdf_to_mjcf(URDF_PATH, assets)

    print("Parsing compiled MJCF...")
    tree = ET.ElementTree(ET.fromstring(mjcf_text))

    print("Adding training elements...")
    tree = _add_training_elements(tree)

    _indent(tree.getroot())

    print(f"Writing: {OUTPUT_PATH}")
    tree.write(OUTPUT_PATH, encoding="unicode", xml_declaration=True)

    # Verify the result loads correctly
    print("Verifying compiled model...")
    with open(OUTPUT_PATH) as f:
        xml = f.read()
    model = mujoco.MjModel.from_xml_string(xml, assets=assets)
    print(f"  joints: {model.njnt} (expect 15: 1 free + 14 actuated)")
    print(f"  actuators: {model.nu} (expect 14)")
    print(f"  sites: {model.nsite}")
    print(f"  sensors: {model.nsensor}")

    # Print joint info
    for i in range(model.njnt):
        jtype = "free" if int(model.jnt_type[i]) == 0 else "hinge"
        print(f"  joint {i}: {model.jnt(i).name} ({jtype})")

    # Print site info
    for i in range(model.nsite):
        print(f"  site {i}: {model.site(i).name}")

    # Check collision geoms
    for i in range(model.ngeom):
        name = model.geom(i).name
        if name and "foot" in name.lower():
            print(f"  collision geom {i}: {name}")

    print("\nDone! You can now use scene_flat_terrain.xml for training.")


if __name__ == "__main__":
    main()
