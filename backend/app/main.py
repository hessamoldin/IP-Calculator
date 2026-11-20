from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import calc, db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init()
    yield


app = FastAPI(title="IP Calculator API", version="0.1.0", lifespan=lifespan)


class SubnetIn(BaseModel):
    input: str = Field(examples=["172.16.2.12/24", "172.16.0.0 255.128.0.0"])


class SplitIn(BaseModel):
    network: str = Field(examples=["192.168.0.0/24"])
    new_prefix: int | None = Field(default=None, examples=[26])
    count: int | None = Field(default=None, examples=[4])


class Requirement(BaseModel):
    name: str
    hosts: int


class VlsmIn(BaseModel):
    network: str = Field(examples=["192.168.1.0/24"])
    requirements: list[Requirement]


class SupernetIn(BaseModel):
    networks: list[str] = Field(examples=[["192.168.0.0/24", "192.168.1.0/24"]])


class ConvertIn(BaseModel):
    value: str = Field(examples=["192.168.1.1", "0xC0A80101", "3232235777"])


def run(kind: str, label: str, fn, *args):
    try:
        result = fn(*args)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    db.add(kind, label)
    return result


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/subnet")
def subnet(body: SubnetIn):
    return run("subnet", body.input, calc.subnet_info, body.input)


@app.post("/api/split")
def split(body: SplitIn):
    label = f"{body.network} -> /{body.new_prefix}" if body.new_prefix else f"{body.network} x{body.count}"
    return run("split", label, calc.split, body.network, body.new_prefix, body.count)


@app.post("/api/vlsm")
def vlsm(body: VlsmIn):
    reqs = [r.model_dump() for r in body.requirements]
    label = f"{body.network} [{', '.join(str(r['hosts']) for r in reqs)}]"
    return run("vlsm", label, calc.vlsm, body.network, reqs)


@app.post("/api/supernet")
def supernet(body: SupernetIn):
    return run("supernet", ", ".join(body.networks), calc.supernet, body.networks)


@app.post("/api/convert")
def convert(body: ConvertIn):
    return run("convert", body.value, calc.convert, body.value)


@app.get("/api/history")
def history(limit: int = 50):
    return db.recent(min(max(limit, 1), 200))


@app.delete("/api/history")
def clear_history():
    db.clear()
    return {"status": "cleared"}
