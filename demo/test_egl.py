import mujoco
model = mujoco.MjModel.from_xml_string("<mujoco><worldbody><body name='box' pos='0 0 0'><geom type='box' size='0.1 0.1 0.1'/></body></worldbody></mujoco>")
data = mujoco.MjData(model)
mujoco.mj_step(model, data)
print("MuJoCo model loaded successfully!")
