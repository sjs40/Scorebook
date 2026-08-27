import {
  ISSUE_RE,
  JSON_HEADERS,
  asInt,
  clientIp,
  kvKey,
  normalizeCounts,
  parseVoteBody,
  pickWinner,
  rateLimitKey,
  serializeCounts,
  totalVotes,
} from "../../_lib/potn.js";

const RATE_LIMIT_MAX = 12;
const RATE_LIMIT_TTL = 3600;

/** @param {string | string[] | undefined} raw */
function issueFromParam(raw) {
  if (typeof raw === "string") return raw;
  if (Array.isArray(raw) && typeof raw[0] === "string") return raw[0];
  return "";
}

/** @param {Record<string, unknown>} payload @param {number} status */
function json(payload, status = 200) {
  return new Response(JSON.stringify(payload), { status, headers: JSON_HEADERS });
}

/** @param {import("@cloudflare/workers-types").EventContext<unknown, string, unknown>} context */
export async function onRequest(context) {
  const issue = issueFromParam(context.params.issue);
  if (!issue || !ISSUE_RE.test(issue)) {
    return json({ error: "invalid_issue" }, 400);
  }

  const { request, env } = context;
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }

  const kv = env.POTN_VOTES;
  if (!kv) {
    return json({ error: "kv_unavailable" }, 503);
  }

  const key = kvKey(issue);

  if (request.method === "GET") {
    const raw = await kv.get(key);
    const counts = normalizeCounts(raw ? JSON.parse(raw) : {});
    const winner = pickWinner(counts);
    return json({
      issue,
      counts,
      total: totalVotes(counts),
      winner: winner ? { choice: winner.choice, count: winner.count } : null,
    });
  }

  if (request.method === "POST") {
    const ip = clientIp(request);
    const rlKey = rateLimitKey(issue, ip);
    const priorRl = asInt(await kv.get(rlKey), 0);
    if (priorRl >= RATE_LIMIT_MAX) {
      return json({ error: "rate_limited" }, 429);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid_json" }, 400);
    }

    const choice = parseVoteBody(body);
    if (!choice) {
      return json({ error: "invalid_choice" }, 400);
    }

    const raw = await kv.get(key);
    const counts = normalizeCounts(raw ? JSON.parse(raw) : {});
    counts[choice] = (counts[choice] || 0) + 1;

    await kv.put(key, serializeCounts(counts));
    await kv.put(rlKey, String(priorRl + 1), { expirationTtl: RATE_LIMIT_TTL });

    const winner = pickWinner(counts);
    return json({
      issue,
      counts,
      total: totalVotes(counts),
      winner: winner ? { choice: winner.choice, count: winner.count } : null,
      accepted: choice,
    });
  }

  return json({ error: "method_not_allowed" }, 405);
}
