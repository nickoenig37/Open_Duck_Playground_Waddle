# Things I wanted to note down about my setup with this


- At the moment I'm using a venv for this, 
    - Setup with `uv venv`
    - sourced with `source .venv/bin/activate`

## To open the venv
`source .venv/bin/activate`

## What I run to test the onnx model:
`python playground/open_duck_mini_v2/mujoco_infer.py --onnx_model_path ./BEST_WALK_ONNX.onnx`

## To train an onnx model:
`python playground/open_duck_mini_v2/runner.py`