# openvancy/training/training_graph.py
from __future__ import annotations

import copy
import csv
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from scipy.spatial import ConvexHull

from ovito.io import import_file, export_file
from ovito.modifiers import (
    ExpressionSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ConstructSurfaceModifier,
    InvertSelectionModifier,
)

from openvancy.utils.config_loader import Config


class AtomicGraphGenerator:
    """
    Genera subgrafos y exporta features a CSV.
    Ahora **NO** reabre input_params.json: recibe `cfg` desde openvancy.
    """

    def __init__(
        self,
        *,
        cfg: Config,
        input_path: Optional[str | Path] = None,
        neighbor_radius: Optional[float] = None,
        cutoff: Optional[float] = None,
        smoothing_level: Optional[int] = None,
        iterations: Optional[int] = None,
        max_graph_size: Optional[int] = None,
        export_dumps: Optional[bool] = None,
        seed: Optional[int] = None,
    ):
        # --- Config inyectada por openvancy ---
        self.cfg = cfg
        self.cfg.ensure_output_dirs()

        # Entrada
        if input_path is None:
            if not self.cfg.paths.defect_inputs:
                raise FileNotFoundError("paths.defect_inputs está vacío en la configuración.")
            input_path = self.cfg.paths.defect_inputs[0]
        self.input_path: Path = Path(input_path).expanduser().resolve()

        # Parámetros (defaults caen de cfg; se pueden overridear por kwargs)
        self.radius: float = float(
            neighbor_radius
            if neighbor_radius is not None
            else (getattr(self.cfg.training, "neighbor_radius", 0.0) or self.cfg.graph.neighbor_radius)
        )
        self.cutoff: float = float(cutoff if cutoff is not None else self.cfg.graph.cutoff)
        self.smoothing: int = int(
            smoothing_level if smoothing_level is not None else self.cfg.preprocessing.smoothing_level_training
        )
        self.iterations: int = int(iterations if iterations is not None else self.cfg.training.max_graph_variations)
        self.max_nodes: int = int(max_graph_size if max_graph_size is not None else self.cfg.training.max_graph_size)
        self.export_dumps: bool = bool(
            export_dumps if export_dumps is not None else getattr(self.cfg.training, "export_dumps", False)
        )
        self.seed = seed if seed is not None else getattr(self.cfg.training, "seed", None)
        self.rng = np.random.default_rng(self.seed)

        # Pipeline una sola vez
        self.pipeline = import_file(str(self.input_path), multiple_frames=False)

        # Salidas
        base = Path(self.cfg.paths.outputs_root)
        self.csv_path = base / "csv" / "training_graph.csv"
        self.dump_dir = base / "dump" / "training"
        self.dump_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        self.header = ["vacancys", "cluster_size", "surface_area", "filled_volume"]
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.header)

    def run(self):
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for variation_idx in range(self.iterations):
                for graph_size in range(1, self.max_nodes + 1):
                    ids, _ = self._generate_graph(graph_size)
                    if not ids:
                        continue
                    expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)

                    area, volume, count, dump_path = self._export_and_dump(expr, graph_size, variation_idx)
                    if count == 0 and area == 0.0 and volume == 0.0:
                        # nada que aportar; evita filas “en blanco”
                        continue

                    row = [len(ids), count, area, volume]
                    writer.writerow(row)

        print(f"✔️ CSV guardado en {self.csv_path}")

    def _generate_graph(self, length: int) -> Tuple[list, list]:
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        ids_arr = data.particles["Particle Identifier"].array

        N = len(pos)
        if N == 0:
            return [], []
        start = int(self.rng.integers(N))
        coords = [pos[start]]
        ids = [int(ids_arr[start])]
        current = coords[0]
        rem_set = set(range(N)) - {start}

        while len(coords) < length and rem_set:
            rem = np.fromiter(rem_set, dtype=int)
            dists = np.linalg.norm(pos[rem] - current, axis=1)
            order = np.argsort(dists)
            k = 2 if len(order) > 1 else 1
            cands = rem[order[:k]]
            choice = int(self.rng.choice(cands))
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            rem_set.remove(choice)

        return ids, coords

    def _export_and_dump(self, expr: str, i: int, a: int):
        """
        Mantiene SOLO los IDs seleccionados (fix del orden de select/delete),
        luego (opcional) aplica ConstructSurface y cuenta/convex-hull.
        Devuelve (area, volume, count, dump_path).
        """
        p = copy.deepcopy(self.pipeline)

        # ✅ Mantener solo seleccionados (antes borrabas lo seleccionado)
        p.modifiers.append(ExpressionSelectionModifier(expression=expr))
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())

        # Superficie (opcional; igual dejamos posiciones para el hull)
        if self.radius > 0:
            p.modifiers.append(
                ConstructSurfaceModifier(
                    radius=self.radius,
                    smoothing_level=self.smoothing,
                    select_surface_particles=False,  # no re-filtramos; medimos el conjunto resultante
                )
            )

        p.modifiers.append(ClusterAnalysisModifier(cutoff=self.cutoff, unwrap_particles=True))

        data = p.compute()
        pts = data.particles.positions.array
        count = int(len(pts))

        if count >= 4:
            hull = ConvexHull(pts)
            area = float(hull.area)
            volume = float(hull.volume)
        else:
            area, volume = 0.0, 0.0

        dump_path = None
        if self.export_dumps:
            dump_path = self.dump_dir / f"graph_{i}_{a}.dump"  # ✅ sin 'training/' duplicado
            export_file(
                p,
                str(dump_path),
                "lammps/dump",
                columns=["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"],
            )
        p.modifiers.clear()
        return area, volume, count, (str(dump_path) if dump_path else None)
