"use client";
import { FormEvent, useState } from "react";
import { KV, Status, useCall } from "@/components/ui";

export default function SupernetPage() {
  const [text, setText] = useState("192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24");
  const { data, error, loading, run } = useCall();
  const submit = (e: FormEvent) => {
    e.preventDefault();
    run("supernet", { networks: text.split("\n").map((l) => l.trim()).filter(Boolean) });
  };

  return (
    <>
      <h1>Supernetting</h1>
      <p className="hint">One network per line. Finds the smallest single route that covers all of them.</p>
      <form onSubmit={submit}>
        <textarea aria-label="Networks" value={text} onChange={(e) => setText(e.target.value)} />
        <div className="row"><button>Summarize</button></div>
      </form>
      <Status error={error} loading={loading} />
      {data && <>
        <KV data={{ summary_route: data.summary.cidr, exact_match: data.exact,
          wasted_addresses: data.wasted_addresses, aggregated_networks: data.aggregated }} />
        <KV data={data.summary} />
      </>}
    </>
  );
}
