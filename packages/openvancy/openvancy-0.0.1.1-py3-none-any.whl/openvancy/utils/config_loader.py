# config_v1.py
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import json
import warnings

# ---------------------- Secciones ----------------------

@dataclass(frozen=True)
class Pipeline:
    use_geometric_route: bool = False
    enable_training_assets: bool = False
    use_external_reference: bool = True

@dataclass(frozen=True)
class Paths:
    reference_root: Optional[Path] = None
    defect_inputs: Tuple[Path, ...] = field(default_factory=tuple)
    outputs_root: Path = Path("outputs")

    def resolved(self) -> "Paths":
        def _res(p: Optional[Path]) -> Optional[Path]:
            return None if p is None else Path(p).expanduser().resolve()
        return Paths(
            reference_root=_res(self.reference_root),
            defect_inputs=tuple(_res(p) for p in self.defect_inputs),
            outputs_root=_res(self.outputs_root) or Path.cwd() / "outputs",
        )

@dataclass(frozen=True)
class Reference:
    lattice: str = "bcc"          # "bcc" | "fcc" | ...
    a0: float = 2.5
    cells: Tuple[int, int, int] = (6, 6, 6)  # (rx, ry, rz)
    element: str = "Fe"

@dataclass(frozen=True)
class Preprocessing:
    smoothing_level_inference: int = 0
    smoothing_level_training: int = 0

@dataclass(frozen=True)
class GraphConstruction:
    neighbor_radius: float = 2.0
    cutoff: float = 3.5           # nota: algunos JSON viejos lo ponían en clustering

@dataclass(frozen=True)
class Training:
    file_index: int = 0
    max_graph_size: int = 15
    max_graph_variations: int = 100
    neighbor_radius: float = 4.0   # radio para generar/entrenar features

@dataclass(frozen=True)
class Clustering:
    tolerance: float = 3.0
    divisions: int = 3
    iterations: int = 4
    # Alias de compatibilidad: cutoff aquí reubica a graph.cutoff
    cutoff: Optional[float] = None

@dataclass(frozen=True)
class Predictor:
    feature_columns: Tuple[str, ...] = field(default_factory=tuple)

# ---------------------- Raíz ----------------------

@dataclass(frozen=True)
class Config:
    config_version: str
    pipeline: Pipeline
    paths: Paths
    reference: Reference
    preprocessing: Preprocessing
    graph: GraphConstruction
    training: Training
    clustering: Clustering
    predictor: Predictor

    # ---------- Carga ----------
    @staticmethod
    def from_file(path: str | Path) -> "Config":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return Config.from_dict(data)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Config":
        # Defaults por sección
        pipeline = Pipeline(**d.get("pipeline", {}))

        # Paths → Path absolutos
        p_raw = d.get("paths", {})
        paths = Paths(
            reference_root=Path(p_raw["reference_root"]).expanduser() if p_raw.get("reference_root") else None,
            defect_inputs=tuple(Path(x).expanduser() for x in p_raw.get("defect_inputs", [])),
            outputs_root=Path(p_raw.get("outputs_root", "outputs")).expanduser(),
        ).resolved()

        reference = Reference(**d.get("reference", {}))
        preprocessing = Preprocessing(**d.get("preprocessing", {}))

        # graph_construction + (compat) clustering.cutoff
        g_raw = d.get("graph_construction", {}) or {}
        c_raw = d.get("clustering", {}) or {}
        cutoff = g_raw.get("cutoff", c_raw.get("cutoff", 3.5))
        if "cutoff" in c_raw and "cutoff" not in g_raw:
            warnings.warn("Mover 'clustering.cutoff' a 'graph_construction.cutoff' (usando compat).", RuntimeWarning)
        graph = GraphConstruction(
            neighbor_radius=float(g_raw.get("neighbor_radius", 2.0)),
            cutoff=float(cutoff),
        )

        training = Training(**d.get("training", {}))
        clustering = Clustering(**c_raw)
        predictor = Predictor(feature_columns=tuple(d.get("predictor", {}).get("feature_columns", [])))

        cfg = Config(
            config_version=str(d.get("config_version", "1.0")),
            pipeline=pipeline,
            paths=paths,
            reference=reference,
            preprocessing=preprocessing,
            graph=graph,
            training=training,
            clustering=clustering,
            predictor=predictor,
        )
        cfg._validate()
        return cfg

    # ---------- Utilidades ----------
    def ensure_output_dirs(self) -> None:
        base = self.paths.outputs_root
        for sub in ("csv", "dump", "json", "img"):
            (base / sub).mkdir(parents=True, exist_ok=True)

    def save_resolved(self, out: str | Path = None) -> Path:
        out = Path(out) if out else self.paths.outputs_root / "json" / "resolved_config.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        def _ser(obj):
            if isinstance(obj, Path): return obj.as_posix()
            if isinstance(obj, tuple): return [ _ser(x) for x in obj ]
            if isinstance(obj, list):  return [ _ser(x) for x in obj ]
            if hasattr(obj, "__dataclass_fields__"): return {k:_ser(v) for k,v in asdict(obj).items()}
            return obj
        out.write_text(json.dumps(_ser(self), indent=2), encoding="utf-8")
        return out

    def as_flat(self) -> Dict[str, Any]:
        """Diccionario 'plano' útil para logs/ML: keys tipo 'reference.a0'."""
        def walk(prefix, obj):
            if hasattr(obj, "__dataclass_fields__"):
                for k, v in asdict(obj).items():
                    yield from walk(f"{prefix}{k}.", v)
            elif isinstance(obj, (dict,)):
                for k, v in obj.items():
                    yield from walk(f"{prefix}{k}.", v)
            else:
                yield prefix[:-1], obj
        flat = dict(walk("", self))
        # Serializa Paths
        for k, v in list(flat.items()):
            if isinstance(v, Path):
                flat[k] = v.as_posix()
            if isinstance(v, tuple) and v and isinstance(v[0], Path):
                flat[k] = [p.as_posix() for p in v]
        return flat

    # ---------- Validación ----------
    def _validate(self) -> None:
        rx, ry, rz = self.reference.cells
        if any(n < 1 for n in (rx, ry, rz)):
            raise ValueError("reference.cells debe ser >= 1 en cada eje.")
        if self.graph.neighbor_radius <= 0:
            raise ValueError("graph_construction.neighbor_radius debe ser > 0.")
        if self.graph.cutoff <= 0:
            raise ValueError("graph_construction.cutoff debe ser > 0.")
        if self.training.neighbor_radius <= 0:
            warnings.warn("training.neighbor_radius <= 0; usando valor por defecto 4.0.", RuntimeWarning)
        # Paths mínimos
        if not self.paths.defect_inputs:
            warnings.warn("paths.defect_inputs está vacío.", RuntimeWarning)
