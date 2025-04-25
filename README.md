docker build -t robosuite-cpu .
docker run -it --rm -v $(pwd):/workspace robosuite-cpu bash

> 
python3 demo/demo_composite_policy.py --robot GR1 --headless
python3 demo_composite_policy_integrated --robot GR1 --headless --timesteps=150_000