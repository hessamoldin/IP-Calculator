"use client";
import { FormEvent, useState } from "react";
import { Rows, Status, useCall } from "@/components/ui";

export default function SubnettingPage() {
  const [network, setNetwork] = useState("192.168.0.0/24");
  const [mode, setMode] = useState<"count" | "prefix">("count");
  const [n, setN] = useState("4");
  const { data, error, loading, run } = useCall();
  const submit = (e: FormEvent) => {
    e.preventDefault();
    run("split", mode === "count" ? { network, count: +n } : { network, new_prefix: +n });
  };

  return (
    <>
      <h1>Subnetting</h1>
      <p className="hint">Split a network into equal subnets, by number of subnets or by new prefix length.</p>
      <form className="row" onSubmit={submit}>
        <input aria-label="Network" value={network} onChange={(e) => setNetwork(e.target.value)} />
        <select aria-label="Split by" value={mode} onChange={(e) => setMode(e.target.value as "count" | "prefix")}>
          <option value="count">Number of subnets</option>
          <option value="prefix">New prefix (/n)</option>
        </select>
        <input className="num" type="number" aria-label="Value" value={n} onChange={(e) => setN(e.target.value)} />
        <button>Split</button>
      </form>
      <Status error={error} loading={loading} />
      {data && <><p className="hint">{data.count} subnets of {data.parent}, each /{data.new_prefix}</p><Rows rows={data.subnets} /></>}
    </>
  );
}
