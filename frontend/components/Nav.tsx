"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const tabs = [
  ["/", "Subnet"], ["/subnetting", "Subnetting"], ["/vlsm", "VLSM"],
  ["/supernet", "Supernet"], ["/convert", "Convert"], ["/history", "History"],
];

export default function Nav() {
  const path = usePathname();
  const [dark, setDark] = useState(false);

  function apply(t: string) {
    document.documentElement.dataset.theme = t;
    setDark(t === "dark");
    try { localStorage.setItem("theme", t); } catch {}
  }

  useEffect(() => {
    let t: string | null = null;
    try { t = localStorage.getItem("theme"); } catch {}
    apply(t ?? (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
  }, []);

  return (
    <nav>
      <span className="brand"><i className="mark">/24</i>IP Calculator</span>
      <div className="tabs">
        {tabs.map(([href, label]) => (
          <Link key={href} href={href} className={path === href ? "on" : ""}>{label}</Link>
        ))}
      </div>
      <button className="ghost theme" onClick={() => apply(dark ? "light" : "dark")}>
        {dark ? "Light mode" : "Dark mode"}
      </button>
    </nav>
  );
}
