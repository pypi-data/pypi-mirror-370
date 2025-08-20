from core import *
from pathlib import Path
import os
import pandas as pd
import warnings



def VacancyAnalysis():
    cfg = Config.from_file("input_params.json")
    cfg.ensure_output_dirs()
    cfg.save_resolved()  

    # Accesos limpios por etapa:
    print(cfg.reference.lattice, cfg.reference.a0, cfg.reference.cells, cfg.reference.element)
    print(cfg.paths.reference_root, cfg.paths.defect_inputs, cfg.paths.outputs_root)
    print(cfg.graph.neighbor_radius, cfg.graph.cutoff)
    print(cfg.clustering.tolerance, cfg.clustering.divisions, cfg.clustering.iterations)
    print(cfg.training.file_index, cfg.training.max_graph_size, cfg.training.max_graph_variations)
    print(cfg.pipeline.enable_training_assets)

    flat = cfg.as_flat()



    if cfg.pipeline.enable_training_assets:
        gen = CrystalStructureGenerator(cfg,cfg.paths.outputs_root)
        gen.generate()

    if cfg.pipeline.use_geometric_route:
        analyzer = DeformationAnalyzer(cfg.paths.defect_inputs, cfg.reference.lattice, cfg.reference.element, threshold=0.02)
        delta = analyzer.compute_metric()
        method = analyzer.select_method()
        print(f"Métrica δ = {delta:.4f}, método seleccionado: {method}")    
        if method == 'geometric' and cfg.pipeline.use_geometric_route:
            
            vac_analyzer = WSMethod(
                defect_dump_path=cfg.paths.defect_inputs,
                lattice_type=cfg,
                element=cfg.reference.element,
                tolerance=0.5#pendiente de agregar a input_params
            )
            vacancies = vac_analyzer.run()    
            print(f"Numero total de vacancias encontradas:{vacancies}")
    