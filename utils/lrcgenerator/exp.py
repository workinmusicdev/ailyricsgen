from faster_whisper import WhisperModel
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
model_size = "large-v3"
print("h")

# Run on GPU with FP16
#model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")
print("2h")
segments, info = model.transcribe("./539b31d8-6c87-49b1-a1b4-9a3a33a9eca0.mp3", beam_size=5)
print("3h")
print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))