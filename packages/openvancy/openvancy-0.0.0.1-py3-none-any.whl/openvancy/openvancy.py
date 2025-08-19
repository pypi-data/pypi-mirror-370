from core import *



cfg = Config.from_file("input_params.json")
cfg.ensure_output_dirs()
cfg.save_resolved()  

# Accesos limpios por etapa:
print(cfg.reference.lattice, cfg.reference.a0, cfg.reference.cells, cfg.reference.element)
print(cfg.paths.reference_root, cfg.paths.defect_inputs, cfg.paths.outputs_root)
print(cfg.graph.neighbor_radius, cfg.graph.cutoff)
print(cfg.clustering.tolerance, cfg.clustering.divisions, cfg.clustering.iterations)
print(cfg.training.file_index, cfg.training.max_graph_size, cfg.training.max_graph_variations)

# Diccionario plano (útil para ML/logs):
flat = cfg.as_flat()

