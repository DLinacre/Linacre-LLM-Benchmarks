/**
 * Hardware Compatibility Calculator Engine
 * Independently testable, transparent assumptions, zero fabricated precision.
 */

export const QUANTISATION_BPP = Object.freeze({
  Q2_K: { label: 'Q2_K (~2.6 bpw)', bitsPerParam: 2.65 },
  Q3_K_M: { label: 'Q3_K_M (~3.4 bpw)', bitsPerParam: 3.45 },
  Q4_K_M: { label: 'Q4_K_M (~4.8 bpw, recommended)', bitsPerParam: 4.85 },
  Q5_K_M: { label: 'Q5_K_M (~5.7 bpw)', bitsPerParam: 5.7 },
  Q6_K: { label: 'Q6_K (~6.6 bpw)', bitsPerParam: 6.6 },
  Q8_0: { label: 'Q8_0 (~8.5 bpw)', bitsPerParam: 8.5 },
  FP16: { label: 'FP16 / BF16 (16 bpw)', bitsPerParam: 16.0 }
});

export const MODEL_FORMATS = Object.freeze(['GGUF', 'FP16', 'BF16', 'EXL2']);

export function estimateHardwareCompatibility(input) {
  const paramsB = Number(input.parametersBillions);
  const vramGb = Number(input.gpuVramGb);
  const ramGb = Number(input.systemRamGb);
  const diskGb = Number(input.diskSpaceGb);
  const contextTokens = Number(input.contextWindow);
  const quantKey = input.quantisation || 'Q4_K_M';
  const format = input.modelFormat || 'GGUF';

  if (!Number.isFinite(paramsB) || paramsB <= 0) {
    return {
      valid: false,
      error: 'Model parameter count (in billions) is required to estimate memory.',
      classification: 'No Data Available'
    };
  }
  if (!Number.isFinite(vramGb) || vramGb < 0 || !Number.isFinite(ramGb) || ramGb <= 0) {
    return {
      valid: false,
      error: 'Valid GPU VRAM (>= 0 GB) and System RAM (> 0 GB) are required.',
      classification: 'No Data Available'
    };
  }

  const quant = QUANTISATION_BPP[quantKey] || QUANTISATION_BPP.Q4_K_M;
  const effectiveBpp = (format === 'FP16' || format === 'BF16') ? 16.0 : quant.bitsPerParam;

  // 1. Model weight memory (GB): params (1e9) * bits / 8 / 1024^3
  const weightMemoryGb = Number(((paramsB * 1e9 * (effectiveBpp / 8)) / (1024 ** 3)).toFixed(2));

  // 2. KV cache memory estimate (GB):
  // Scales with context window and approximate hidden dimension / layer count (heuristic for GQA transformers)
  const safeContext = Number.isFinite(contextTokens) && contextTokens > 0 ? contextTokens : 4096;
  const kvBytesPerTokenPerBillion = 24_000; // ~24 KB/token per 1B params under typical GQA FP16 KV cache
  const kvCacheGb = Number(((safeContext * paramsB * kvBytesPerTokenPerBillion) / (1024 ** 3)).toFixed(2));

  // 3. Runtime & framework overhead (CUDA/Metal/llama.cpp compute buffers)
  const runtimeOverheadGb = Number((0.6 + Math.min(2.5, paramsB * 0.03)).toFixed(2));

  // 4. Total memory required
  const totalRequiredGb = Number((weightMemoryGb + kvCacheGb + runtimeOverheadGb).toFixed(2));

  // 5. GPU vs CPU/RAM offloading
  const usableVramGb = Math.max(0, Number((vramGb * 0.92).toFixed(2)));
  const usableRamGb = Math.max(0, Number((ramGb * 0.80).toFixed(2)));

  let gpuOffloadPercent = 0;
  let cpuSpilloverGb = 0;

  if (usableVramGb >= totalRequiredGb) {
    gpuOffloadPercent = 100;
    cpuSpilloverGb = 0;
  } else if (usableVramGb > 0) {
    gpuOffloadPercent = Math.max(0, Math.min(99, Math.round((usableVramGb / totalRequiredGb) * 100)));
    cpuSpilloverGb = Number(Math.max(0, totalRequiredGb - usableVramGb).toFixed(2));
  } else {
    gpuOffloadPercent = 0;
    cpuSpilloverGb = totalRequiredGb;
  }

  const totalCombinedPoolGb = Number((usableVramGb + usableRamGb).toFixed(2));
  const vramHeadroomGb = Number((usableVramGb - totalRequiredGb).toFixed(2));
  const combinedHeadroomGb = Number((totalCombinedPoolGb - totalRequiredGb).toFixed(2));

  // 6. Disk space check (weights + 15% buffer)
  const requiredDiskGb = Number((weightMemoryGb * 1.15).toFixed(2));
  const diskSufficient = !Number.isFinite(diskGb) || diskGb <= 0 ? null : diskGb >= requiredDiskGb;

  // 7. Classification
  let classification = 'Unlikely to fit';
  let summary = 'Total required memory exceeds available GPU VRAM and usable System RAM.';

  if (diskSufficient === false) {
    classification = 'Unlikely to fit';
    summary = `Insufficient disk space: needs ~${requiredDiskGb} GB, available ${diskGb} GB.`;
  } else if (vramHeadroomGb >= 1.5) {
    classification = 'Excellent fit';
    summary = 'Fits entirely in GPU VRAM with comfortable headroom for fast inference.';
  } else if (vramHeadroomGb >= 0) {
    classification = 'Good fit';
    summary = 'Fits in GPU VRAM with tight headroom; consider lowering context window if OOM occurs.';
  } else if (combinedHeadroomGb >= 2.0 && gpuOffloadPercent >= 40) {
    classification = 'Limited fit';
    summary = `Requires hybrid GPU/CPU offloading (~${gpuOffloadPercent}% GPU, ~${cpuSpilloverGb} GB in System RAM). Expect reduced token speed.`;
  } else if (combinedHeadroomGb >= 2.0) {
    classification = 'Limited fit';
    summary = `Primarily CPU/RAM inference (~${cpuSpilloverGb} GB in System RAM). Functional but significantly slower than GPU.`;
  }

  return {
    valid: true,
    inputs: {
      gpuModel: input.gpuModel || 'Not Specified',
      gpuVramGb: vramGb,
      systemRamGb: ramGb,
      cpu: input.cpu || 'Not Specified',
      os: input.os || 'Not Specified',
      diskSpaceGb: Number.isFinite(diskGb) ? diskGb : null,
      parametersBillions: paramsB,
      contextWindow: safeContext,
      modelFormat: format,
      quantisation: quantKey
    },
    estimates: {
      weightMemoryGb,
      kvCacheGb,
      runtimeOverheadGb,
      totalRequiredGb,
      requiredDiskGb,
      gpuOffloadPercent,
      cpuSpilloverGb,
      vramHeadroomGb,
      combinedHeadroomGb,
      diskSufficient
    },
    classification,
    summary,
    assumptions: [
      'Estimates assume standard dense transformer GQA architecture; MoE or unusual KV head counts may differ.',
      'Usable VRAM is budgeted at 92% and usable System RAM at 80% to leave room for the OS and display.',
      'KV cache assumes FP16 precision; quantized KV cache (Q8_0/Q4_0) can reduce context memory further.',
      'Actual runtime memory depends on backend (llama.cpp, Ollama, vLLM, ExLlamaV2) and batch size.'
    ]
  };
}
