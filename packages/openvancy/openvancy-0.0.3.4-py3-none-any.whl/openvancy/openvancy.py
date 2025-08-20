
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')
try:
    import ovito._extensions.pyscript 
except Exception:
    pass


from .core import *
from pathlib import Path
import os
import json


def _json_default(o):
    try:
        import numpy as np
        if isinstance(o, np.generic):
            return o.item()
    except Exception:
        pass
    from pathlib import Path
    if isinstance(o, Path):
        return str(o)

    return str(o)

def _safe_save_resolved(cfg, out=None):
    try:

        return cfg.save_resolved() if out is None else cfg.save_resolved(out)
    except TypeError:

        if out is None:
            out = Path(cfg.paths.outputs_root) / "resolved_config.json"
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)

        data = None
        if hasattr(cfg, "as_dict"):
            data = cfg.as_dict()
        else:
            try:
                from dataclasses import asdict, is_dataclass
                data = asdict(cfg) if is_dataclass(cfg) else cfg.__dict__
            except Exception:
                data = getattr(cfg, "__dict__", {})

        out.write_text(json.dumps(data, indent=2, default=_json_default), encoding="utf-8")
        return out


def VacancyAnalysis():
    cfg = Config.from_file("input_params.json")
    cfg.ensure_output_dirs()
    _safe_save_resolved(cfg)   


    print(cfg.reference.lattice, cfg.reference.a0, cfg.reference.cells, cfg.reference.element)
    print(cfg.paths.reference_root, cfg.paths.defect_inputs, cfg.paths.outputs_root)
    print(cfg.graph.neighbor_radius, cfg.graph.cutoff)
    print(cfg.clustering.tolerance, cfg.clustering.divisions, cfg.clustering.iterations)
    print(cfg.training.file_index, cfg.training.max_graph_size, cfg.training.max_graph_variations)
    print(cfg.pipeline.enable_training_assets)

    flat = cfg.as_flat()  
    proc = ClusterProcessor(cfg=cfg)         
    proc.run()
    
    if cfg.pipeline.use_external_reference:
        config_dict = {
            "paths": {
                "defect_inputs": [str(cfg.paths.defect_inputs[0])]
            },
            "reference": {
                "lattice": cfg.reference.lattice, 
                "a0": cfg.reference.a0,            
                "cells": cfg.reference.cells        
            }
        }

    # Después (pasando cfg e input explícito):
    if cfg.pipeline.enable_training_assets:
        gen = AtomicGraphGenerator(
            cfg=cfg,
            input_path=cfg.paths.defect_inputs[0],                # entra por el mismo dump que usás en todo el pipeline
            neighbor_radius=getattr(cfg.training, "neighbor_radius", None),  # opcional: overrides
            cutoff=cfg.graph.cutoff,
            smoothing_level=cfg.preprocessing.smoothing_level_training,
            iterations=cfg.training.max_graph_variations,
            max_graph_size=cfg.training.max_graph_size,
            export_dumps=getattr(cfg.training, "export_dumps", False),
            seed=getattr(cfg.training, "seed", None),
        )
        gen.run()

    

    for FILE in cfg.paths.defect_inputs:
        if cfg.pipeline.use_geometric_route:
            analyzer = DeformationAnalyzer(
                cfg.paths.defect_inputs[0],
                cfg.reference.lattice,  
                cfg.reference.element,
                threshold=0.02
            )
            delta = analyzer.compute_metric()
            method = analyzer.select_method()
            print(f"Métrica δ = {delta:.4f}, método seleccionado: {method}")

            if method == 'geometric' and cfg.pipeline.use_geometric_route:
            
                defect_dump = cfg.paths.defect_inputs[0] if hasattr(cfg.paths, "defect_inputs") else cfg.paths.defect_inputs
                vac_analyzer = WSMethod(
                    defect_dump_path=defect_dump,
                    lattice_type=cfg.reference.lattice,  
                    element=cfg.reference.element,
                    tolerance=0.5 
                )
                vacancies = vac_analyzer.run()
                print(f"Número total de vacancias encontradas: {vacancies}")
            else:
                                
                proc = ClusterProcessor(cfg=cfg)         
                proc.run()
                separator = KeyFilesSeparator(cfg.clustering.tolerance,os.path.join("outputs/json", "clusters.json"))
                separator.run()
        else:
            
                cfg = Config.from_file("input_params.json")
                proc = ClusterProcessor(cfg=cfg)          
                proc.run()

                separator = KeyFilesSeparator(cfg.clustering.tolerance,os.path.join("outputs/json", "clusters.json"))
                separator.run()






if __name__ == "__main__":
    VacancyAnalysis()
