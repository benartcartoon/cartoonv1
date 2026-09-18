# AnimateDiff Colab
One-cell AUTOMATIC1111 + AnimateDiff launcher for Google Colab.

Drive root: `MyDrive/AnimateDiff-Colab`
- models: checkpoints and motion modules
- characters: reference character images
- input: source images/videos
- output: generated outputs
- config: saved settings

Open `colab/ONE_CELL.py` in a Colab GPU runtime and run it as one cell. The launcher prints a Gradio public URL.

The motion module is cached automatically in Drive. Put `disneyPixarCartoon_v10.safetensors` in the Drive models folder to reuse the same local checkpoint without downloading it every session.
