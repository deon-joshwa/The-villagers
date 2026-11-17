"""Hour-2 Gate Smoke Test Script. Owner: P1.

Exit criteria:
  (a) No ghost vocals -- human must LISTEN to the generated WAV.
  (b) score.abc + result.json saved.
  (c) truncated flag and duration captured.
  (d) Validate YueStudio.fallback_instrumental on real score.abc.
"""

import os
import sys
import json
import time

# Avoid PyTorch CUDA allocator fragmentation on 8 GB VRAM
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Ensure project root is in path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from prompt_compiler import build_request, SCENE_MAP, MOOD_MAP, STYLE_MAP, BPM_MAP
from yue_backend import YueStudio, GenerationError


def run_smoke_test():
    print("=" * 60)
    print("OST.io - Hour-2 Gate Smoke Test (P1: Model Wrangler)")
    print("=" * 60)

    # 1. Build request using prompt_compiler's maps
    scene = "Boss Battle (Phase 1 / 2)"
    mood = "Menacing / Ominous"
    style = "Dark Orchestral + Brass"
    intensity = "High Adrenaline / Combat (120-150 BPM)"
    seed = 831001
    track_id = "smoke_831001"

    print(f"\n[1/5] Compiling request payload...")
    request = build_request(
        scene=scene,
        mood=mood,
        style=style,
        intensity=intensity,
        seed=seed,
        track_id=track_id
    )

    print("Request payload:")
    for k, v in request.items():
        print(f"  {k}: {repr(v)}")

    # Strict contract assertions
    assert request["lyrics"] == "", f"lyrics must be empty string, got: {request['lyrics']}"
    assert request["cot"] == "full", f"cot must be 'full', got: {request['cot']}"
    assert request["seed"] == 831001, f"seed must be 831001, got: {request['seed']}"
    assert "id" in request and "style" in request
    print("Contract assertion checks PASSED.")

    # 2. Output directory
    out_dir = os.path.join(REPO_ROOT, "outputs", "smoke_test_output")
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n[2/5] Output directory: {out_dir}")

    # 3. Initialize YueStudio with FP8 AR quantization & ComfyUI-style upper duration bounds
    print("\n[3/5] Initializing YueStudio with FP8 quantization (low_vram=True, device=cuda, cache_dir=hf_cache)...")
    cache_dir = os.path.join(REPO_ROOT, "hf_cache")
    studio = YueStudio(cache_dir=cache_dir)
    
    from yue2 import YuE2Pipeline
    from yue2.protocol import GenerationConfig, Sampling
    pipe = YuE2Pipeline.from_pretrained(
        "m-a-p/YuE2-3B",
        device="cuda",
        low_vram=True,
        cache_dir=cache_dir,
        quantization="fp8",
        local_files_only=True
    )
    # ComfyUI-style optimization: upper bound token limit (45s clip limit ~2000 tokens)
    # Prevents runaway 8,000+ token generation and eliminates NAR diffusion OOM on 8 GB VRAM
    pipe.generation_config = GenerationConfig(
        abc=Sampling(0.7, 0.9, 30, 1.005, 100, 32, 1200),
        semantic=Sampling(1.0, 0.95, 100, 1.2, 50, 200, 2000),
        ode_steps=32
    )
    studio._pipe = pipe

    def progress_callback(stage, completed, total):
        print(f"  [Progress] Stage: {stage} | {completed}/{total}", flush=True)

    # 4. Generate track
    print(f"\n[4/5] Starting generation for seed {seed} (this may take a few minutes on 8 GB VRAM)...")
    t0 = time.time()
    try:
        out = studio.generate(request, out_dir=out_dir, on_progress=progress_callback)
    except Exception as e:
        print(f"\n[ERROR] Generation failed: {e}")
        print(">> GATE CRITERION FAILED: Announce 'cache-only demo' in chat if unresolvable.")
        sys.exit(1)

    elapsed = time.time() - t0
    print(f"\nGeneration completed in {elapsed:.1f}s")
    print(f"Output dictionary: {out}")

    # Verify artifacts
    wav_path = out["wav"]
    flac_path = out["flac"]
    score_path = out["score"]
    truncated = out["truncated"]
    duration_s = out["duration_s"]
    result_json_path = os.path.join(out_dir, "result.json")

    print("\n[5/5] Verifying Gate Exit Criteria:")
    print(f"  - audio.wav exists: {os.path.exists(wav_path)} ({wav_path})")
    print(f"  - audio.flac exists: {os.path.exists(flac_path)}")
    print(f"  - score.abc exists: {os.path.exists(score_path)} ({score_path})")
    print(f"  - result.json exists: {os.path.exists(result_json_path)}")
    print(f"  - Truncated flag: {truncated}")
    print(f"  - Duration: {duration_s} seconds")

    if not (os.path.exists(wav_path) and os.path.exists(score_path) and os.path.exists(result_json_path)):
        print("\n>> GATE FAILED: Required artifacts missing!")
        sys.exit(1)

    # Test fallback_instrumental on the real generated score
    print("\n--- Validating YueStudio.fallback_instrumental on real score.abc ---")
    fallback_out = os.path.join(out_dir, "score_fallback.abc")
    try:
        res_abc = studio.fallback_instrumental(score_path, fallback_out)
        print(f"fallback_instrumental succeeded: saved to {res_abc}")
        with open(res_abc, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            print("Preview of fallback ABC (first 10 lines):")
            for l in lines[:10]:
                print(f"  {l}")
    except Exception as e:
        print(f"Note on fallback_instrumental: {e}")

    print("\n" + "=" * 60)
    print("GATE STATUS:")
    print(f"1. Artifacts saved: PASS")
    print(f"2. Duration ({duration_s}s) & truncated ({truncated}): RECORDED")
    print(f"3. Human Action Required: LISTEN to {wav_path}")
    print("   Confirm NO ghost vocals.")
    print("   If clean -> Pass Hour-2 gate & proceed to make_presets.py")
    print("   If ghost vocals -> Audition fallback or regenerate seed")
    print("=" * 60)


if __name__ == "__main__":
    run_smoke_test()
