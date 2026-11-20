"use client";
import { FormEvent, useState } from "react";
import { Rows, Status, useCall } from "@/components/ui";

function Bar({ data }: { data: any }) {
  return (
    <div className="alloc" aria-label="Address space allocation">
      {data.allocations.map((a: any, i: number) => (
        <div key={i} className={`seg c${i % 5}`} style={{ flexGrow: a.total_addresses }} title={`${a.name}: ${a.cidr}`}>
          <b>{a.name}</b><code>{a.cidr}</code>
        </div>
      ))}
      {data.addresses_free > 0 && (
        <div className="seg free" style={{ flexGrow: data.addresses_free }}><b>free</b><code>{data.addresses_free}</code></div>
      )}
    </div>
  );
}

export default function VlsmPage() {
  const [network, setNetwork] = useState("192.168.1.0/24");
  const [text, setText] = useState("LAN-A, 100\nLAN-B, 50\nLAN-C, 10");
  const { data, error, loading, run } = useCall();
  const submit = (e: FormEvent) => {
    e.preventDefault();
    const requirements = text.split("\n").map((l) => l.trim()).filter(Boolean).map((l, i) => {
      const parts = l.split(/[,\s]+/);
      const hosts = parseInt(parts[parts.length - 1], 10);
      return { name: parts.length > 1 ? parts.slice(0, -1).join(" ") : `Subnet ${i + 1}`, hosts };
    });
    run("vlsm", { network, requirements });
  };

  return (
    <>
      <h1>VLSM</h1>
      <p className="hint">One requirement per line as <code>name, hosts</code>. Largest subnets are placed first.</p>
      <form onSubmit={submit}>
        <div className="row">
          <input aria-label="Parent network" value={network} onChange={(e) => setNetwork(e.target.value)} />
        </div>
        <textarea aria-label="Requirements" value={text} onChange={(e) => setText(e.target.value)} />
        <div className="row"><button>Allocate</button></div>
      </form>
      <Status error={error} loading={loading} />
      {data && <>
        <p className="hint">{data.addresses_used} addresses used, {data.addresses_free} free in {data.parent}</p>
        <Bar data={data} />
        <Rows rows={data.allocations} />
      </>}
    </>
  );
}
