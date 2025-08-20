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

# >>> Cambiado: ahora importamos la Config local
from openvancy.utils.config_loader import Config


class AtomicGraphGenerator:
    """
    Genera subgrafos atómicos aleatorios, construye superficie (vacíos),
    y exporta features tabulares a CSV para entrenamiento.

    Carga de parámetros vía config_loader.Config (config_v1):
      - cfg.paths.defect_inputs[0] : archivo de entrada .dump/.xyz/...
      - cfg.training.neighbor_radius (fallback a cfg.graph.neighbor_radius)
      - cfg.graph.cutoff
      - cfg.preprocessing.smoothing_level_training
      - cfg.training.max_graph_variations
      - cfg.training.max_graph_size
      - (opt) cfg.training.export_dumps (bool, si existe)
      - (opt) cfg.training.seed (si existe)
    """

    def __init__(self, config_path: Optional[str | Path] = None):
        
        config_path = Path(config_path) if config_path else Path.cwd() / "input_params.json"
        self.cfg: Config = Config.from_file(config_path)
        self.cfg.ensure_output_dirs()

        if not self.cfg.paths.defect_inputs:
            raise FileNotFoundError("paths.defect_inputs está vacío en la configuración.")
        self.input_path: Path = Path(self.cfg.paths.defect_inputs[0]).expanduser().resolve()

        # Parámetros
        self.radius: float = float(getattr(self.cfg.training, "neighbor_radius", 0.0) or self.cfg.graph.neighbor_radius)
        self.cutoff: float = float(self.cfg.graph.cutoff)
        self.smoothing: int = int(self.cfg.preprocessing.smoothing_level_training)
        self.iterations: int = int(self.cfg.training.max_graph_variations)
        self.max_nodes: int = int(self.cfg.training.max_graph_size)
        self.export_dumps: bool = bool(getattr(self.cfg.training, "export_dumps", False))
        self.seed = getattr(self.cfg.training, "seed", None)
        self.rng = np.random.default_rng(self.seed)  # reproducibilidad

        # OVITO pipeline (un único input)
        self.pipeline = import_file(str(self.input_path), multiple_frames=False)

        # Salidas
        base = self.cfg.paths.outputs_root
        self.csv_path = base / "csv" / "training_graph.csv"
        self.dump_dir = base / "dump"
        self.dump_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

        # CSV header
        self.header = [
            "vacancys",
            "cluster_size",
            "surface_area",
            "filled_volume",
        ]
        if not self.csv_path.exists() or self.csv_path.stat().st_size == 0:
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.header)

    def run(self):
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            for variation_idx in range(self.iterations):
                for graph_size in range(1, self.max_nodes + 1):
                    ids, _ = self._generate_graph(graph_size)
                    expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)

                    area, volume, count, dump_path = self._export_and_dump(
                        expr, graph_size, variation_idx
                    )

                    row = [
                        len(ids),   # número de nodos del subgrafo
                        count,      # partículas tras superficie + cluster
                        area,
                        volume,
                    ]
                    writer.writerow(row)

        print(f"✔️ CSV guardado en {self.csv_path}")

    def _generate_graph(self, length: int) -> Tuple[list, list]:
        """Camino aleatorio simple por vecinos cercanos (heurístico)."""
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        ids_arr = data.particles["Particle Identifier"].array

        N = len(pos)
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
        """Devuelve (area, volume, count, dump_path). dump_path puede ser None si no se exporta."""
        p = copy.deepcopy(self.pipeline)
        p.modifiers.append(ExpressionSelectionModifier(expression=expr))
        p.modifiers.append(DeleteSelectedModifier())
        p.modifiers.append(
            ConstructSurfaceModifier(
                radius=self.radius,
                smoothing_level=self.smoothing,
                select_surface_particles=True,
            )
        )
        p.modifiers.append(InvertSelectionModifier())
        p.modifiers.append(DeleteSelectedModifier())
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
            dump_path = self.dump_dir / f"graph_{i}_{a}.dump"
            export_file(
                p,
                str(dump_path),
                "lammps/dump",
                columns=[
                    "Particle Identifier",
                    "Particle Type",
                    "Position.X",
                    "Position.Y",
                    "Position.Z",
                ],
            )
        p.modifiers.clear()
        return area, volume, count, (str(dump_path) if dump_path else None)

