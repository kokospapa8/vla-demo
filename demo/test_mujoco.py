import mujoco
model = mujoco.MjModel.from_xml_string("""
<mujoco>
  <worldbody>
    <body name='ball' pos='0 0 0.3'>
      <geom size='0.2' type='sphere'/>
    </body>
  </worldbody>
</mujoco>
""")
print("MuJoCo model loaded successfully!")