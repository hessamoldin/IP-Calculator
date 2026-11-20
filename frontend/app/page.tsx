"use client";
import { FormEvent, useEffect, useState } from "react";
import { BitStrip, KV, Stat, Status, useCall } from "@/components/ui";

const examples = ["172.16.2.12/24", "10.0.0.0 255.255.0.0", "192.168.1.77/27", "2001:db8::1/64"];

export default function SubnetPage() {
  const [value, setValue] = useState(examples[0]);
  const { data, error, loading, run } = useCall();
  const go = (v: string) => { setValue(v); run("subnet", { input: v }); };
  const submit = (e: FormEvent) => { e.preventDefault(); run("subnet", { input: value }); };
  useEffect(() => { run("subnet", { input: examples[0] }); }, []);

  return (
    <>
      <h1>Subnet calculator</h1>
      <p className="hint">
        Enter <code>172.16.2.12/24</code> or <code>172.16.0.0 255.128.0.0</code>. IPv6 works too. Click any value to copy it.
      </p>
      <form className="row" onSubmit={submit}>
        <input aria-label="IP address with prefix or mask" value={value} onChange={(e) => setValue(e.target.value)} />
        <button>Calculate</button>
      </form>
      <div className="chips">
        {examples.map((x) => <button key={x} type="button" onClick={() => go(x)}>{x}</button>)}
      </div>
      <Status error={error} loading={loading} />
      {data && (
        <>
          <div className="stats">
            <Stat label="Network" value={`${data.network}/${data.prefix}`} />
            {data.version === 4 ? (
              <>
                <Stat label="Broadcast" value={data.broadcast} />
                <Stat label="Usable hosts" value={data.usable_hosts} />
                <Stat label="Subnet mask" value={data.netmask} />
              </>
            ) : (
              <>
                <Stat label="First address" value={data.first_address} />
                <Stat label="Last address" value={data.last_address} />
                <Stat label="Total addresses" value={data.total_addresses} />
              </>
            )}
          </div>
          {data.version === 4 && (
            <section className="card">
              <h2>Where the subnet boundary falls in {data.address}</h2>
              <BitStrip address={data.address} binary={data.ip_binary} prefix={data.prefix} />
            </section>
          )}
          <section className="card">
            <h2>All details</h2>
            <KV data={data} />
          </section>
        </>
      )}
    </>
  );
}
