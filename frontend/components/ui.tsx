"use client";
import { ReactNode, useState } from "react";

type Obj = Record<string, any>;

async function call(method: string, path: string, body?: unknown) {
  const r = await fetch(`/api/${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof j.detail === "string" ? j.detail : "Check the values and try again.");
  return j;
}
export const get = (path: string) => call("GET", path);
export const del = (path: string) => call("DELETE", path);

export function useCall() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function run(path: string, body: unknown) {
    setLoading(true); setError("");
    try { setData(await call("POST", path, body)); }
    catch (e: any) { setData(null); setError(e.message); }
    finally { setLoading(false); }
  }
  return { data, error, loading, run };
}

// Works on plain http:// (a VPS without TLS) where navigator.clipboard is unavailable.
async function copyText(t: string): Promise<boolean> {
  try { await navigator.clipboard.writeText(t); return true; } catch {}
  try {
    const a = document.createElement("textarea");
    a.value = t; document.body.appendChild(a); a.select();
    const ok = document.execCommand("copy"); a.remove(); return ok;
  } catch { return false; }
}

function useCopied(text: string) {
  const [done, setDone] = useState(false);
  async function copy() {
    if (await copyText(text)) { setDone(true); setTimeout(() => setDone(false), 1200); }
  }
  return { done, copy };
}

export function Copy({ text }: { text: string }) {
  const { done, copy } = useCopied(text);
  return (
    <button type="button" className="copy" aria-label={`Copy ${text}`} onClick={copy}>
      {done ? "Copied" : "Copy"}
    </button>
  );
}

export function Stat({ label, value }: { label: string; value: string | number }) {
  const { done, copy } = useCopied(String(value));
  return (
    <button type="button" className="stat" onClick={copy} aria-label={`Copy ${label}: ${value}`}>
      <span className="k">{done ? "Copied" : label}</span>
      <code>{String(value)}</code>
    </button>
  );
}

const ACRONYMS = new Set(["ip", "cidr", "vlsm", "ipv4", "ipv6", "dns", "vlan", "mac"]);
const label = (k: string) =>
  k.split("_")
    .map((w) => (ACRONYMS.has(w.toLowerCase()) ? w.toUpperCase() : w.charAt(0).toUpperCase() + w.slice(1)))
    .join(" ");

export function KV({ data }: { data: Obj }) {
  return (
    <div className="scroll"><table><tbody>
      {Object.entries(data).map(([k, v]) => (
        <tr key={k}><th>{label(k)}</th><td><code>{String(v)}</code><Copy text={String(v)} /></td></tr>
      ))}
    </tbody></table></div>
  );
}

export function Rows({ rows }: { rows: Obj[] }) {
  if (!rows.length) return <p className="hint">Nothing here yet.</p>;
  const cols = Object.keys(rows[0]);
  return (
    <div className="scroll boxed"><table>
      <thead><tr>{cols.map((c) => <th key={c}>{label(c)}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => (
        <tr key={i}>{cols.map((c) => <td key={c}><code>{String(r[c])}</code></td>)}</tr>
      ))}</tbody>
    </table></div>
  );
}

/** 32-bit view of an IPv4 address: network bits vs host bits, with the boundary marked. */
export function BitStrip({ address, binary, prefix }: { address: string; binary: string; prefix: number }) {
  const bits = binary.replace(/\./g, "");
  const dec = address.split(".");
  return (
    <>
      <div className="bits" role="img" aria-label={`${prefix} network bits and ${32 - prefix} host bits`}>
        {[0, 1, 2, 3].map((o) => (
          <div className="octet" key={o}>
            <div className="cells">
              {bits.slice(o * 8, o * 8 + 8).split("").map((b, i) => {
                const idx = o * 8 + i;
                return <span key={i} className={(idx < prefix ? "n" : "h") + (idx === prefix ? " edge" : "")}>{b}</span>;
              })}
            </div>
            <small>{dec[o]}</small>
          </div>
        ))}
      </div>
      <div className="legend">
        <span><i style={{ background: "var(--net)" }} />{prefix} network bits</span>
        <span><i style={{ background: "var(--host)" }} />{32 - prefix} host bits</span>
      </div>
    </>
  );
}

export function Status({ error, loading }: { error: string; loading: boolean }): ReactNode {
  return <>{error && <p className="err" role="alert">{error}</p>}{loading && <p className="hint">Calculating…</p>}</>;
}
