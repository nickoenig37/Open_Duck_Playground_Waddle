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