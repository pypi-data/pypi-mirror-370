
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')
try:
    import ovito._extensions.pyscript 
except Exception:
    pass


from .core import (
    Config, CrystalStructureGenerator, DeformationAnalyzer,
    WSMethod, ClusterProcessor
)
from pathlib import Path
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

    
    if cfg.pipeline.enable_training_assets:
        gen = CrystalStructureGenerator(cfg, cfg.paths.outputs_root)
        gen.generate()

    for FILE in cfg.paths.defect_inputs:
        if cfg.pipeline.use_geometric_route:
            analyzer = DeformationAnalyzer(
                cfg.paths.defect_inputs,  
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
                
                processor = ClusterProcessor(cfg=cfg)
                n_clusters = processor.run()
                print(f"Clusters detectados (ML): {n_clusters}")

        else:
            
            processor = ClusterProcessor(cfg=cfg)
            n_clusters = processor.run()
            print(f"Clusters detectados (ML): {n_clusters}")

if __name__ == "__main__":
    VacancyAnalysis()
