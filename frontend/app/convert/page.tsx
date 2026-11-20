"use client";
import { FormEvent, useState } from "react";
import { KV, Status, useCall } from "@/components/ui";

export default function ConvertPage() {
  const [value, setValue] = useState("192.168.1.1");
  const { data, error, loading, run } = useCall();
  const submit = (e: FormEvent) => { e.preventDefault(); run("convert", { value }); };

  return (
    <>
      <h1>Convert</h1>
      <p className="hint">
        Dotted, binary (<code>11000000.10101000.00000001.00000001</code>), hex (<code>0xC0A80101</code>),
        decimal, or IPv6. Every form is converted to all the others.
      </p>
      <form className="row" onSubmit={submit}>
        <input aria-label="Value to convert" value={value} onChange={(e) => setValue(e.target.value)} />
        <button>Convert</button>
      </form>
      <Status error={error} loading={loading} />
      {data && <KV data={data} />}
    </>
  );
}
