# Things I wanted to note down about my setup with this


- At the moment I'm using a venv for this, 
    - Setup with `uv venv`
    - sourced with `source .venv/bin/activate`

## To open the venv
`source .venv/bin/activate`

## What I run to test the onnx model:
`python -m playground.waddle.mujoco_infer --onnx_model_path ./WADDLE_ALRIGHT_ONNX_340.onnx`

## To train an onnx model:
`python -m playground.waddle.runner`


### Using the Reference Viewer
```bash
# Basic run with waddle-specific reference data
python -m playground.waddle.ref_motion_viewer \
  --reference_data playground/waddle/data/polynomial_coefficients_MARCH_4.pkl

# Custom velocity command (dx=0.1, dy=0.0, dtheta=0.0 = forward walk)
python -m playground.waddle.ref_motion_viewer \
  --reference_data playground/waddle/data/polynomial_coefficients_3p5cmraise_MARCH_5.pkl \
  --command 0.1 0.0 0.0