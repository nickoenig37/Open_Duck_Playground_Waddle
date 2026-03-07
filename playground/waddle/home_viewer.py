import mujoco
import mujoco.viewer

model = mujoco.MjModel.from_xml_path('./xmls/scene_flat_terrain_backlash.xml')
data = mujoco.MjData(model)

# Load the "home" keyframe
key_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "home")
mujoco.mj_resetDataKeyframe(model, data, key_id)
mujoco.mj_forward(model, data)

mujoco.viewer.launch(model, data)