# cluster_processor.py
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

import json
import numpy as np
import pandas as pd

from ovito.io import import_file, export_file
from ovito.modifiers import (
    ConstructSurfaceModifier,
    InvertSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ExpressionSelectionModifier,
)

# Tu loader tipado
from utils.config_loader import Config


class ClusterProcessor:
    def __init__(
        self,
        defect: Optional[str | Path] = None,
        cfg: Optional[Config] = None,
        config_path: Optional[str | Path] = None,
    ):
        """
        Constructor moderno usando ConfigV1.

        Parámetros
        ----------
        defect : str|Path|None
            Dump de defecto a procesar. Si es None, se toma el primero de cfg.paths.defect_inputs.
        cfg : ConfigV1|None
            Objeto de configuración ya cargado.
        config_path : str|Path|None
            Ruta a JSON de configuración (si no pasás 'cfg'). Se carga con ConfigV1.from_file(...).

        Reglas:
          - Si pasás 'cfg', se usa ese.
          - Si no pasás 'cfg' pero sí 'config_path', se carga desde el archivo.
          - Si no pasás nada, intenta "input_params.json" en el cwd.
        """
        # 1) cargar config
        if cfg is None:
            if config_path is None:
                config_path = Path.cwd() / "input_params.json"
            self.cfg = Config.from_file(config_path)
        else:
            self.cfg = cfg

        if defect is not None and str(defect).strip():
            self.defect_path = Path(defect).expanduser().resolve()
        else:
            if not self.cfg.paths.defect_inputs:
                raise ValueError("No hay defectos en cfg.paths.defect_inputs y no se pasó 'defect'.")
            self.defect_path = Path(self.cfg.paths.defect_inputs[0]).expanduser().resolve()

        if not self.defect_path.exists():
            raise FileNotFoundError(f"No existe el dump de defecto: {self.defect_path}")

        self.smoothing_level = int(self.cfg.preprocessing.smoothing_level_inference)

        #    b) radio de sonda (graph_construction.neighbor_radius)
        self.radius_probe = float(self.cfg.graph.neighbor_radius if self.cfg.graph.neighbor_radius > 0 else 1.0)

        #    c) cutoff para clustering (graph.cutoff con compat)
        cutoff = float(self.cfg.graph.cutoff)
        if getattr(self.cfg.clustering, "cutoff", None) is not None:
            # compat: si en el JSON estaba en clustering, ya lo migramos al graph en el loader,
            # pero por si acaso, mantenemos el valor mayor
            cutoff = max(cutoff, float(self.cfg.clustering.cutoff or 0.0))
        self.cutoff_radius = cutoff if cutoff > 0 else 3.0

        # 4) salidas
        self.outputs_root = Path(self.cfg.paths.outputs_root).expanduser().resolve()
        self.outputs_dump = self.outputs_root / "dump"
        self.outputs_json = self.outputs_root / "json"
        self.outputs_dump.mkdir(parents=True, exist_ok=True)
        self.outputs_json.mkdir(parents=True, exist_ok=True)

    def run(self) -> int:
        """
        1) Aplica ConstructSurfaceModifier al dump global y deja sólo vacíos (invierte selección + borra).
        2) Ejecuta ClusterAnalysisModifier para obtener conteo y clusters.
        3) Exporta 'key_areas.dump' (todas las partículas filtradas).
        4) Exporta 'key_area_{i}.dump' para cada cluster.

        Devuelve
        --------
        int : número de clusters detectados.
        """
        pipeline = import_file(str(self.defect_path))

        # 1) superficie + invertir + borrar
        r = self.radius_probe
        pipeline.modifiers.append(
            ConstructSurfaceModifier(
                radius=r,
                smoothing_level=self.smoothing_level,
                identify_regions=True,
                select_surface_particles=True,
            )
        )
        pipeline.modifiers.append(InvertSelectionModifier())      # invertimos selección
        pipeline.modifiers.append(DeleteSelectedModifier())       # borramos lo que NO nos interesa

        # 2) cluster analysis
        pipeline.modifiers.append(
            ClusterAnalysisModifier(
                cutoff=self.cutoff_radius,
                sort_by_size=True,
                unwrap_particles=True,
                compute_com=True,
            )
        )
        data = pipeline.compute()
        num_clusters = int(data.attributes["ClusterAnalysis.cluster_count"])

        # Guardar JSON simple con el conteo
        clusters_json_path = self.outputs_json / "clusters.json"
        with clusters_json_path.open("w", encoding="utf-8") as f:
            json.dump({"num_clusters": num_clusters}, f, indent=4)

        # 3) export global
        key_areas_dump_path = self.outputs_dump / "key_areas.dump"
        try:
            export_file(
                pipeline,
                str(key_areas_dump_path),
                "lammps/dump",
                columns=[
                    "Particle Identifier",
                    "Particle Type",
                    "Position.X",
                    "Position.Y",
                    "Position.Z",
                    "Cluster",
                ],
            )
            pipeline.modifiers.clear()
        except Exception as e:
            print(f"[WARN] No se pudo exportar {key_areas_dump_path.name}: {e}")

        # 4) export por cluster
        for i in range(1, num_clusters + 1):
            cluster_expr = f"Cluster=={i}"
            pipeline_2 = import_file(str(key_areas_dump_path))
            pipeline_2.modifiers.append(
                ClusterAnalysisModifier(
                    cutoff=self.cutoff_radius,
                    cluster_coloring=True,
                    unwrap_particles=True,
                    sort_by_size=True,
                )
            )
            pipeline_2.modifiers.append(ExpressionSelectionModifier(expression=cluster_expr))
            pipeline_2.modifiers.append(InvertSelectionModifier())
            pipeline_2.modifiers.append(DeleteSelectedModifier())

            out_i = self.outputs_dump / f"key_area_{i}.dump"
            try:
                export_file(
                    pipeline_2,
                    str(out_i),
                    "lammps/dump",
                    columns=[
                        "Particle Identifier",
                        "Particle Type",
                        "Position.X",
                        "Position.Y",
                        "Position.Z",
                        "Cluster",
                    ],
                )
                pipeline_2.modifiers.clear()
            except Exception as e:
                print(f"[WARN] No se pudo exportar {out_i.name}: {e}")

        print(f"Número de áreas clave encontradas: {num_clusters}")
        return num_clusters

    # (igual que antes)
    @staticmethod
    def extraer_encabezado(file_path: str | Path) -> list[str]:
        encabezado = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    encabezado.append(line)
                    if line.strip().startswith("ITEM: ATOMS"):
                        break
        except Exception:
            pass
        return encabezado
