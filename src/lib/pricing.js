/**
 * AI Pricing Intelligence — Token Cost Calculator
 */

export function formatUsd(amount, decimals = 4) {
  if (amount === null || amount === undefined || !Number.isFinite(Number(amount))) {
    return 'No Data Available';
  }
  const num = Number(amount);
  if (num === 0) return '$0.00';
  if (num < 0.01) return `$${num.toFixed(decimals)}`;
  return `$${num.toFixed(2)}`;
}

export function calculateTokenCost({
  inputPricePer1M,
  outputPricePer1M,
  cachedInputPricePer1M = null,
  inputTokens = 0,
  outputTokens = 0,
  cachedInputTokens = 0,
  requests = 1
}) {
  const safeReqs = Math.max(1, Number(requests) || 1);
  const inTok = Math.max(0, Number(inputTokens) || 0) * safeReqs;
  const outTok = Math.max(0, Number(outputTokens) || 0) * safeReqs;
  const cacheTok = Math.max(0, Number(cachedInputTokens) || 0) * safeReqs;

  const hasInputPrice = inputPricePer1M !== null && inputPricePer1M !== undefined && Number.isFinite(Number(inputPricePer1M));
  const hasOutputPrice = outputPricePer1M !== null && outputPricePer1M !== undefined && Number.isFinite(Number(outputPricePer1M));

  if (!hasInputPrice && !hasOutputPrice) {
    return {
      valid: false,
      error: 'No verified pricing available for this model.'
    };
  }

  const inputCost = hasInputPrice ? (inTok / 1_000_000) * Number(inputPricePer1M) : 0;
  const outputCost = hasOutputPrice ? (outTok / 1_000_000) * Number(outputPricePer1M) : 0;
  const effectiveCachedRate =
    cachedInputPricePer1M !== null && cachedInputPricePer1M !== undefined && Number.isFinite(Number(cachedInputPricePer1M))
      ? Number(cachedInputPricePer1M)
      : (hasInputPrice ? Number(inputPricePer1M) : 0);
  const cachedCost = (cacheTok / 1_000_000) * effectiveCachedRate;
  const totalCost = inputCost + outputCost + cachedCost;

  return {
    valid: true,
    totalInputTokens: inTok,
    totalOutputTokens: outTok,
    totalCachedTokens: cacheTok,
    inputCost: Number(inputCost.toFixed(6)),
    outputCost: Number(outputCost.toFixed(6)),
    cachedCost: Number(cachedCost.toFixed(6)),
    totalCost: Number(totalCost.toFixed(6))
  };
}
