/** @typedef {Record<string, number>} PotnCounts */

export const ISSUE_RE = /^\d{4}-\d{2}-\d{2}$/;
export const CHOICE_RE = /^[a-z0-9_-]{1,32}$/;

/** @param {string} issue */
export function kvKey(issue) {
  return "potn:votes:" + issue;
}

/** @param {string} issue @param {string} ip */
export function rateLimitKey(issue, ip) {
  return "potn:rl:" + issue + ":" + ip;
}

/** @param {unknown} raw */
export function normalizeCounts(raw) {
  /** @type {PotnCounts} */
  const counts = {};
  if (!raw || typeof raw !== "object") return counts;
  for (const [key, value] of Object.entries(/** @type {Record<string, unknown>} */ (raw))) {
    if (!CHOICE_RE.test(key)) continue;
    const n = Number(value);
    if (!Number.isFinite(n) || n < 0) continue;
    counts[key] = Math.floor(n);
  }
  return counts;
}

/** @param {PotnCounts} counts */
export function serializeCounts(counts) {
  return JSON.stringify(counts);
}

/** @param {PotnCounts} counts */
export function totalVotes(counts) {
  return Object.values(counts).reduce((sum, n) => sum + n, 0);
}

/**
 * @param {PotnCounts} counts
 * @param {string[]} [order]
 */
export function pickWinner(counts, order) {
  const keys = Object.keys(counts);
  if (!keys.length) return null;

  const ranked = keys.slice().sort((a, b) => {
    const diff = (counts[b] || 0) - (counts[a] || 0);
    if (diff !== 0) return diff;
    if (order) {
      return order.indexOf(a) - order.indexOf(b);
    }
    return a.localeCompare(b);
  });

  const top = counts[ranked[0]] || 0;
  if (top === 0) return null;

  return {
    choice: ranked[0],
    count: top,
    counts,
    total: totalVotes(counts),
  };
}

/** @param {Request} request */
export function clientIp(request) {
  return (
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ||
    "unknown"
  );
}

/** @param {unknown} body */
export function parseVoteBody(body) {
  if (!body || typeof body !== "object") return null;
  const choice = /** @type {{ choice?: unknown }} */ (body).choice;
  if (typeof choice !== "string" || !CHOICE_RE.test(choice)) return null;
  return choice;
}

/** @param {unknown} value @param {number} fallback */
export function asInt(value, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  return Math.floor(n);
}

export const JSON_HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "no-store",
};
