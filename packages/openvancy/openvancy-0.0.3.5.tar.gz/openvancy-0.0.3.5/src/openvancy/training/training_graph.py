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
    Incluye carteles (logs) para depurar por qué no se extraen características.
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
        verbose: bool = True,  # <- NUEVO: controla carteles
    ):
        self.verbose = bool(verbose)
        self._csv_rows_appended = 0

        def _log(msg: str):
            if self.verbose:
                print(f"[TRAIN] {msg}")

        self._log = _log

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

        # Carteles de parámetros
        self._log(f"Ruta de entrada: {self.input_path}")
        self._log(
            "Parámetros efectivos -> "
            f"neighbor_radius={self.radius}, cutoff={self.cutoff}, smoothing={self.smoothing}, "
            f"iterations={self.iterations}, max_graph_size={self.max_nodes}, export_dumps={self.export_dumps}, seed={self.seed}"
        )

        # Pipeline una sola vez
        if not self.input_path.exists():
            self._log("ERROR: El archivo de entrada no existe.")
            raise FileNotFoundError(self.input_path)
        self.pipeline = import_file(str(self.input_path), multiple_frames=False)

        # Probar un compute inicial
        try:
            data0 = self.pipeline.compute()
            N0 = int(len(data0.particles.positions.array))
            props = list(data0.particles.keys())
            self._log(f"Átomos en el dump: {N0}")
            self._log(f"Propiedades disponibles: {props}")
            if "Particle Identifier" not in props:
                self._log("ADVERTENCIA: Falta 'Particle Identifier' en las propiedades. "
                          "La selección por ID podría fallar.")
        except Exception as e:
            self._log(f"ERROR al leer el dump: {e}")
            raise

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
            self._log(f"Creado CSV con encabezado en: {self.csv_path}")
        else:
            self._log(f"Anexando filas a CSV existente: {self.csv_path}")

    def run(self):
        self._log("== INICIO del loop de variaciones/tamaños de grafo ==")
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for variation_idx in range(self.iterations):
                self._log(f"-- Variación #{variation_idx+1}/{self.iterations}")
                for graph_size in range(1, self.max_nodes + 1):
                    ids, _ = self._generate_graph(graph_size)
                    if not ids:
                        self._log(f"[VAR {variation_idx}] Tamaño {graph_size}: sin IDs seleccionados → salto.")
                        continue

                    # Mostrar hasta 8 IDs como ejemplo
                    sample_ids = ids[:8]
                    self._log(f"[VAR {variation_idx}] Tamaño {graph_size}: IDs seleccionados (muestra): {sample_ids} "
                              f"(total={len(ids)})")

                    expr = " || ".join(f"ParticleIdentifier=={pid}" for pid in ids)
                    self._log(f"[VAR {variation_idx}] Expresión de selección: {expr[:200]}{'...' if len(expr)>200 else ''}")

                    area, volume, count, dump_path = self._export_and_dump(expr, graph_size, variation_idx)
                    self._log(f"[VAR {variation_idx}] Resultado: count={count}, area={area:.4f}, volume={volume:.4f}, "
                              f"dump={'sí' if dump_path else 'no'}")

                    if count == 0 and area == 0.0 and volume == 0.0:
                        self._log(f"[VAR {variation_idx}] Tamaño {graph_size}: sin features (posibles causas: "
                                  f"IDs no válidos, selección vacía, o <4 puntos para hull).")
                        continue

                    row = [len(ids), count, area, volume]
                    writer.writerow(row)
                    self._csv_rows_appended += 1

        self._log(f"✔️ CSV guardado en {self.csv_path} (filas añadidas: {self._csv_rows_appended})")

    def _generate_graph(self, length: int) -> Tuple[list, list]:
        """Selecciona un 'camino' pseudo-aleatorio de longitud 'length' por vecinos más cercanos."""
        data = self.pipeline.compute()
        pos = data.particles.positions.array
        try:
            ids_arr = data.particles["Particle Identifier"].array
        except Exception:
            self._log("ERROR: No se pudo acceder a 'Particle Identifier'. "
                      "¿Existe esa propiedad en el dump?")
            return [], []

        N = len(pos)
        if N == 0:
            self._log("ADVERTENCIA: El dump no tiene partículas (N=0).")
            return [], []
        if length <= 0:
            self._log("ADVERTENCIA: length <= 0, no se generará grafo.")
            return [], []

        start = int(self.rng.integers(N))
        coords = [pos[start]]
        ids = [int(ids_arr[start])]
        current = coords[0]
        rem_set = set(range(N)) - {start}

        while len(coords) < length and rem_set:
            rem = np.fromiter(rem_set, dtype=int)
            # distancias a candidatos
            dists = np.linalg.norm(pos[rem] - current, axis=1)
            order = np.argsort(dists)
            if len(order) == 0:
                break
            # elegimos uno de los dos más cercanos para no ser deterministas
            k = 2 if len(order) > 1 else 1
            cands = rem[order[:k]]
            choice = int(self.rng.choice(cands))
            coords.append(pos[choice])
            ids.append(int(ids_arr[choice]))
            current = pos[choice]
            rem_set.remove(choice)

        if len(ids) < length:
            self._log(f"AVISO: Se pidieron {length} nodos, pero sólo se armaron {len(ids)} "
                      f"(posible N insuficiente o estructura muy dispersa).")

        return ids, coords

    def _export_and_dump(self, expr: str, i: int, a: int):
        """
        Mantiene SOLO los IDs seleccionados (fix del orden de select/delete),
        luego (opcional) aplica ConstructSurface y cuenta/convex-hull.
        Devuelve (area, volume, count, dump_path).
        """
        p = copy.deepcopy(self.pipeline)

        # Antes de filtrar
        data_pre = p.compute()
        n_pre = int(len(data_pre.particles.positions.array))
        self._log(f"[VAR {a}][{i}] Partículas antes de selección: {n_pre}")

        # ✅ Mantener solo seleccionados
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
        else:
            self._log(f"[VAR {a}][{i}] neighbor_radius<=0 → no se aplica ConstructSurfaceModifier.")

        p.modifiers.append(ClusterAnalysisModifier(cutoff=self.cutoff, unwrap_particles=True))

        try:
            data = p.compute()
        except Exception as e:
            self._log(f"[VAR {a}] ERROR al computar pipeline filtrado: {e}")
            return 0.0, 0.0, 0, None

        pts = data.particles.positions.array
        count = int(len(pts))
        self._log(f"[VAR {a}][{i}] Partículas luego de selección: {count}")

        # Si la selección quedó vacía, explicamos un posible motivo
        if count == 0:
            self._log(f"[VAR {a}][{i}] Selección vacía. Causas típicas: "
                      f"IDs inexistentes en el dump, 'ParticleIdentifier' desfasado, "
                      f"dump sin 'Particle Identifier', o expresión mal formada.")
            return 0.0, 0.0, 0, None

        # Calcular hull si hay suficientes puntos
        if count >= 4:
            try:
                hull = ConvexHull(pts)
                area = float(hull.area)
                volume = float(hull.volume)
            except Exception as e:
                self._log(f"[VAR {a}] [{i}] ERROR en ConvexHull (count={count}): {e}")
                area, volume = 0.0, 0.0
        else:
            area, volume = 0.0, 0.0
            self._log(f"[VAR {a}] [{i}] count<4 → no se puede calcular área/volumen (ConvexHull).")

        dump_path = None
        if self.export_dumps:
            try:
                dump_path = self.dump_dir / f"graph_{i}_{a}.dump"
                export_file(
                    p,
                    str(dump_path),
                    "lammps/dump",
                    columns=["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"],
                )
                self._log(f"[VAR {a}] [{i}] Dump exportado: {dump_path}")
            except Exception as e:
                self._log(f"[VAR {a}] [{i}] ADVERTENCIA: fallo export_file de dump ({e})")
        p.modifiers.clear()
        return area, volume, count, (str(dump_path) if dump_path else None)
