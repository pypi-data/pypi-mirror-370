# openvancy/defect_analisys.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ovito.io import import_file, export_file
from ovito.modifiers import (
    ConstructSurfaceModifier,
    InvertSelectionModifier,
    DeleteSelectedModifier,
    ClusterAnalysisModifier,
    ExpressionSelectionModifier,
)

from openvancy.utils.config_loader import Config


class ClusterProcessor:
    """
    Procesa un dump de defecto:
      1) superficie + invertir + borrar (quedan vacíos),
      2) clustering,
      3) exporta key_areas.dump y key_area_{i}.dump en outputs/dump/pipeline/.
    """

    def __init__(
        self,
        defect: Optional[str | Path] = None,
        cfg: Optional[Config] = None,
        config_path: Optional[str | Path] = None,
    ) -> None:

        if cfg is None:
            config_path = Path(config_path) if config_path else Path.cwd() / "input_params.json"
            self.cfg = Config.from_file(config_path)
        else:
            self.cfg = cfg

        if hasattr(self.cfg, "ensure_output_dirs"):
            self.cfg.ensure_output_dirs()

        if defect is not None and str(defect).strip():
            self.defect_path = Path(defect).expanduser().resolve()
        else:
            if not self.cfg.paths.defect_inputs:
                raise ValueError("No hay defectos en cfg.paths.defect_inputs y no se pasó 'defect'.")
            self.defect_path = Path(self.cfg.paths.defect_inputs[0]).expanduser().resolve()
        if not self.defect_path.exists():
            raise FileNotFoundError(f"No existe el dump de defecto: {self.defect_path}")

        self.smoothing_level = int(getattr(self.cfg.preprocessing, "smoothing_level_inference", 0))
        self.radius_probe = float(getattr(self.cfg.graph, "neighbor_radius", 1.0)) or 1.0
        cutoff_graph = float(getattr(self.cfg.graph, "cutoff", 0.0))
        cutoff_compat = float(getattr(self.cfg.clustering, "cutoff", 0.0) or 0.0)
        self.cutoff_radius = max(cutoff_graph, cutoff_compat, 3.0)

        self.outputs_root = Path(self.cfg.paths.outputs_root).expanduser().resolve()
        self.outputs_dump = self.outputs_root / "dump"
        self.outputs_dump_pipeline = self.outputs_dump / "pipeline"  
        self.outputs_json = self.outputs_root / "json"
        self.outputs_dump.mkdir(parents=True, exist_ok=True)
        self.outputs_dump_pipeline.mkdir(parents=True, exist_ok=True) 
        self.outputs_json.mkdir(parents=True, exist_ok=True)

    def run(self) -> int:
        """Ejecuta el pipeline y exporta resultados. Devuelve el número de clusters detectados."""
        pipeline = import_file(str(self.defect_path))

        pipeline.modifiers.append(
            ConstructSurfaceModifier(
                radius=self.radius_probe,
                smoothing_level=self.smoothing_level,
                identify_regions=True,
                select_surface_particles=True,
            )
        )
        pipeline.modifiers.append(InvertSelectionModifier())
        pipeline.modifiers.append(DeleteSelectedModifier())

        pipeline.modifiers.append(
            ClusterAnalysisModifier(
                cutoff=self.cutoff_radius,
                sort_by_size=True,
                unwrap_particles=True,
                compute_com=True,
            )
        )
        data = pipeline.compute()
        num_clusters = int(data.attributes.get("ClusterAnalysis.cluster_count", 0))

        with (self.outputs_json / "clusters.json").open("w", encoding="utf-8") as f:
            json.dump({"num_clusters": num_clusters}, f, indent=4)

        key_areas_dump_path = self.outputs_dump_pipeline / "key_areas.dump"
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

        if not key_areas_dump_path.exists():
            print("[WARN] No existe key_areas.dump, se omite la exportación por cluster.")
            print(f"Número de áreas clave encontradas: {num_clusters}")
            return num_clusters

        for i in range(1, num_clusters + 1):
            pipeline_2 = import_file(str(key_areas_dump_path))
            pipeline_2.modifiers.append(
                ClusterAnalysisModifier(
                    cutoff=self.cutoff_radius,
                    cluster_coloring=True,
                    unwrap_particles=True,
                    sort_by_size=True,
                )
            )
            pipeline_2.modifiers.append(ExpressionSelectionModifier(expression=f"Cluster=={i}"))
            pipeline_2.modifiers.append(InvertSelectionModifier())
            pipeline_2.modifiers.append(DeleteSelectedModifier())

            out_i = self.outputs_dump_pipeline / f"key_area_{i}.dump"
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
