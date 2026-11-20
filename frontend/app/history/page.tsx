"use client";
import { useEffect, useState } from "react";
import { Rows, Status, del, get } from "@/components/ui";

export default function HistoryPage() {
  const [rows, setRows] = useState<Record<string, any>[]>([]);
  const [error, setError] = useState("");

  const load = () => get("history").then(setRows).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);
  const clear = () => del("history").then(load).catch((e) => setError(e.message));

  return (
    <>
      <h1>History</h1>
      <p className="hint">Your 50 most recent calculations, stored on the server.</p>
      <div className="row"><button className="ghost" onClick={clear}>Clear history</button></div>
      <Status error={error} loading={false} />
      <Rows rows={rows} />
    </>
  );
}
