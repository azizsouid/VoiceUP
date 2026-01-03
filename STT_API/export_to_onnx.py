# export_to_onnx.py
import torch
from faster_whisper import WhisperModel

# WARNING: this is a template. Faster-Whisper's wrapper may not expose a single
# torch.nn.Module that accepts raw audio. You likely need to export a trimmed
# encoder/decoder part and implement preprocessing (audio -> mel) on-device.

MODEL = "tiny"
OUTPATH = "tiny_whisper.onnx"

print("Loading model (this may download weights)...")
wm = WhisperModel(MODEL, device="cpu")  # ensure CPU for export

# Try to access underlying PyTorch module (may not be a direct API)
try:
    torch_model = wm.model  # may or may not exist depending on faster-whisper internals
except Exception:
    raise RuntimeError(
        "faster-whisper wrapper doesn't expose .model for direct ONNX export. Adapt export manually.")

# Dummy input: you must match the real expected input shape (example only)
dummy_input = torch.randn(1, 80, 3000)  # (batch, n_mels, time)
torch.onnx.export(
    torch_model,
    dummy_input,
    OUTPATH,
    opset_version=16,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch", 2: "time"},
                  "output": {0: "batch", 1: "time"}}
)
print("Exported to", OUTPATH)
