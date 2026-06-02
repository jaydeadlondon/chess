import struct
import wave
import io
import math
import base64
import os


def _generate_wav(freq, duration, volume=0.5, sample_rate=44100, fade=True):
    n_samples = int(sample_rate * duration)
    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        env = 1.0
        if fade:
            if i < 200:
                env = i / 200.0
            if i > n_samples - 400:
                env = (n_samples - i) / 400.0
        val = volume * env * math.sin(2 * math.pi * freq * t)
        samples.append(int(val * 32767))

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))

    return buf.getvalue()


def _generate_click():
    return _generate_wav(800, 0.06, volume=0.4)


def _generate_capture():
    buf = io.BytesIO()
    sr = 44100
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        samples = []
        for i in range(int(sr * 0.1)):
            t = i / sr
            env = 1.0 - (i / (sr * 0.1))
            val = (
                0.5
                * env
                * (
                    math.sin(2 * math.pi * 300 * t)
                    + 0.5 * math.sin(2 * math.pi * 150 * t)
                    + 0.3 * (2 * (t * 8000 % 1) - 1)
                )
            )
            samples.append(int(max(-1, min(1, val)) * 32767))
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buf.getvalue()


def _generate_check():
    buf = io.BytesIO()
    sr = 44100
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        samples = []
        for i in range(int(sr * 0.25)):
            t = i / sr
            env = 1.0 - (i / (sr * 0.25))
            val = (
                0.5
                * env
                * math.sin(2 * math.pi * 880 * t + 4 * math.sin(2 * math.pi * 4 * t))
            )
            samples.append(int(val * 32767))
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buf.getvalue()


def _generate_checkmate():
    buf = io.BytesIO()
    sr = 44100
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        samples = []
        notes = [523, 659, 784, 1047]
        note_len = int(sr * 0.15)
        for note_idx, freq in enumerate(notes):
            for i in range(note_len):
                t = i / sr
                total = len(notes) * note_len
                pos = note_idx * note_len + i
                env = 1.0
                if i < 100:
                    env = i / 100.0
                if i > note_len - 200:
                    env = (note_len - i) / 200.0
                val = 0.5 * env * math.sin(2 * math.pi * freq * t)
                samples.append(int(val * 32767))
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buf.getvalue()


def _generate_castle():
    buf = io.BytesIO()
    sr = 44100
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        samples = []
        for i in range(int(sr * 0.12)):
            t = i / sr
            env = 1.0 - (i / (sr * 0.12))
            freq = 600 + 200 * t / 0.12
            val = 0.4 * env * math.sin(2 * math.pi * freq * t)
            samples.append(int(val * 32767))
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buf.getvalue()


def _generate_new_game():
    buf = io.BytesIO()
    sr = 44100
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        samples = []
        notes = [440, 554, 659]
        note_len = int(sr * 0.12)
        for freq in notes:
            for i in range(note_len):
                t = i / sr
                env = 1.0
                if i < 50:
                    env = i / 50.0
                if i > note_len - 100:
                    env = (note_len - i) / 100.0
                val = 0.35 * env * math.sin(2 * math.pi * freq * t)
                samples.append(int(val * 32767))
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    return buf.getvalue()


def generate_all_sounds(output_dir="assets/sounds"):
    os.makedirs(output_dir, exist_ok=True)
    sounds = {
        "move.wav": _generate_click(),
        "capture.wav": _generate_capture(),
        "check.wav": _generate_check(),
        "checkmate.wav": _generate_checkmate(),
        "castle.wav": _generate_castle(),
        "new_game.wav": _generate_new_game(),
    }
    for name, data in sounds.items():
        path = os.path.join(output_dir, name)
        with open(path, "wb") as f:
            f.write(data)
    return sounds


if __name__ == "__main__":
    sounds = generate_all_sounds()
    for name, data in sounds.items():
        print(f"Generated {name}: {len(data)} bytes")
    print("Done!")
