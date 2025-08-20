import numpy as np
from pathlib import Path
from typing import Tuple, Union, Optional, List

# Uso opcional de V1Config; si no existe, operamos con dict.
try:
    from openvancy.utils.config_loader import Config as V1Config
except Exception:
    V1Config = None


class CrystalStructureGenerator:
    """
    Crea una red BCC/FCC perfecta y escribe un dump LAMMPS:
      - Copia literalmente el TIMESTEP del dump de entrada (2 líneas).
      - Copia literalmente el bloque 'ITEM: BOX BOUNDS ...' y sus 3 líneas siguientes,
        sea ortogonal o triclinic, con los mismos flags/tilts del archivo original.
      - Recalcula 'ITEM: NUMBER OF ATOMS' según la red generada.
      - Escribe 'ITEM: ATOMS id type x y z'.

    Config esperada (dict o V1Config):
      dict:
        {
          "paths": {"defect_inputs": ["ruta/al/defecto.dump"]},
          "reference": {"lattice": "bcc"|"fcc", "a0": float, "cells": [rx,ry,rz]}
        }
      V1Config:
        paths.defect_inputs[0], reference.lattice, reference.a0, reference.cells
    """

    def __init__(self, config: Union[dict, "V1Config"], out_dir: Path, auto_fit_to_box: bool = False):
       
        if (V1Config is not None) and isinstance(config, V1Config):
            self.path_defect = Path(config.paths.defect_inputs[0]).expanduser().resolve()
            self.lattice_type = str(config.reference.lattice).lower().strip()
            self.a0 = float(config.reference.a0)
            rx, ry, rz = config.reference.cells
            self.reps = (int(rx), int(ry), int(rz))
        elif isinstance(config, dict):
            
            if "paths" in config and "defect_inputs" in config["paths"]:
                self.path_defect = Path(config["paths"]["defect_inputs"][0]).expanduser().resolve()
            elif "CONFIG" in config and config["CONFIG"]:
                self.path_defect = Path(config["CONFIG"][0]["paths"]["defect_inputs"][0]).expanduser().resolve()
            else:
                raise ValueError("No encuentro paths.defect_inputs en la configuración.")

            
            ref = None
            if "reference" in config:
                ref = config["reference"]
            elif "CONFIG" in config and config["CONFIG"]:
                ref = config["CONFIG"][0]["reference"]
            else:
                raise ValueError("No encuentro reference en la configuración.")

            self.lattice_type = str(ref["lattice"]).lower().strip()
            self.a0 = float(ref["a0"])
            rx, ry, rz = ref["cells"]
            self.reps = (int(rx), int(ry), int(rz))
        else:
            raise TypeError("config debe ser dict o V1Config.")

        if not self.path_defect.exists():
            raise FileNotFoundError(f"No se encontró el dump de defecto: {self.path_defect}")

        self.out_dir = Path(out_dir).expanduser().resolve()
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.auto_fit_to_box = bool(auto_fit_to_box)

        
        self._read_header_and_box()

    

    def _read_header_and_box(self) -> None:
        """
        Captura literalmente:
          - TIMESTEP line + value (2 líneas)
          - BOX BOUNDS line tal cual + sus 3 líneas (4 líneas)
        Además parsea xlo..zhi y posibles tilts (si existen).
        """
        text = self.path_defect.read_text(encoding="utf-8", errors="ignore").splitlines()

        
        t_idx = next((i for i, l in enumerate(text) if l.startswith("ITEM: TIMESTEP")), None)
        if t_idx is None or t_idx + 1 >= len(text):
            raise ValueError("No se encontró bloque 'ITEM: TIMESTEP' (2 líneas).")
        self.header_timestep_lines: List[str] = [text[t_idx], text[t_idx + 1]]

       
        b_idx = next((i for i, l in enumerate(text) if l.startswith("ITEM: BOX BOUNDS")), None)
        if b_idx is None or b_idx + 3 >= len(text):
            raise ValueError("No se encontró bloque 'ITEM: BOX BOUNDS' con 3 líneas siguientes.")
        self.header_boxbounds_line: str = text[b_idx]               
        self.header_boxbounds_vals: List[str] = text[b_idx + 1 : b_idx + 4]  
        
        def _floats_first_two(s: str):
            parts = s.split()
            if len(parts) < 2:
                raise ValueError(f"Línea inválida de BOX BOUNDS: {s!r}")
            return float(parts[0]), float(parts[1])

        xlo, xhi = _floats_first_two(self.header_boxbounds_vals[0])
        ylo, yhi = _floats_first_two(self.header_boxbounds_vals[1])
        zlo, zhi = _floats_first_two(self.header_boxbounds_vals[2])
        self.box_limits = (xlo, xhi, ylo, yhi, zlo, zhi)
        self.box_center = np.array([(xlo + xhi) / 2.0, (ylo + yhi) / 2.0, (zlo + zhi) / 2.0], dtype=float)
        self.box_lengths = np.array([xhi - xlo, yhi - ylo, zhi - zlo], dtype=float)

    def _build_unit_lattice(self) -> np.ndarray:
        if self.lattice_type == "fcc":
            return np.array([[0, 0, 0],
                             [0.5, 0.5, 0],
                             [0.5, 0, 0.5],
                             [0, 0.5, 0.5]], dtype=float) * self.a0
        elif self.lattice_type == "bcc":
            return np.array([[0, 0, 0],
                             [0.5, 0.5, 0.5]], dtype=float) * self.a0
        else:
            raise ValueError(f"Tipo de red no soportado: {self.lattice_type!r} (usa 'bcc' o 'fcc').")

    def _build_replica(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera la réplica:
          - Si auto_fit_to_box=True: ajusta reps a ~ box_lengths/a0 (redondeo).
          - Si no: usa reps del input_params.
          - Hace mod a la celda réplica => coords en [0,dims).
        """
        rx, ry, rz = self.reps
        if self.auto_fit_to_box:
            rx = max(1, int(round(self.box_lengths[0] / self.a0)))
            ry = max(1, int(round(self.box_lengths[1] / self.a0)))
            rz = max(1, int(round(self.box_lengths[2] / self.a0)))

        base = self._build_unit_lattice()
        dims = np.array([rx, ry, rz], dtype=float) * self.a0

        coords = []
        for i in range(rx):
            for j in range(ry):
                for k in range(rz):
                    disp = np.array([i, j, k], dtype=float) * self.a0
                    for p in base:
                        coords.append(p + disp)
        coords = np.array(coords, dtype=float)


        coords = np.mod(coords, dims)
       
        coords = np.unique(np.round(coords, 8), axis=0)
        return coords, dims

    @staticmethod
    def _wrap_to_box(coords: np.ndarray, xlo, xhi, ylo, yhi, zlo, zhi) -> np.ndarray:
        origin = np.array([xlo, ylo, zlo], dtype=float)
        lengths = np.array([xhi - xlo, yhi - ylo, zhi - zlo], dtype=float)
        lengths[lengths == 0.0] = 1.0
        return origin + np.mod(coords - origin, lengths)

    def _write_dump(self, coords: np.ndarray, out_file: Path) -> None:
        """
        Escribe:
          [TIMESTEP (copiado literal)]
          ITEM: NUMBER OF ATOMS
          <N>
          [BOX BOUNDS (línea y 3 renglones copiados literal)]
          ITEM: ATOMS id type x y z
          ...
        """
        with Path(out_file).open("w", encoding="utf-8") as f:
            
            for line in self.header_timestep_lines:
                f.write(line + "\n")

            f.write("ITEM: NUMBER OF ATOMS\n")
            f.write(f"{len(coords)}\n")

            f.write(self.header_boxbounds_line + "\n")
            for line in self.header_boxbounds_vals:
                f.write(line + "\n")

            f.write("ITEM: ATOMS id type x y z\n")
            for idx, (x, y, z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.8f} {y:.8f} {z:.8f}\n")


    def generate(self) -> Path:
        """
        1) Replica perfecta BCC/FCC.
        2) Centra en el centro de la caja del dump de entrada.
        3) Wrap a la caja original (del encabezado copiado).
        4) Escribe el archivo con encabezado copiado literalmente.
        """
        (xlo, xhi, ylo, yhi, zlo, zhi) = self.box_limits

        coords, dims = self._build_replica()

        coords_centered = coords - dims / 2.0
        coords_aligned = coords_centered + self.box_center

        coords_wrapped = self._wrap_to_box(coords_aligned, xlo, xhi, ylo, yhi, zlo, zhi)

        out_file = self.out_dir / "relax_structure.dump"
        self._write_dump(coords_wrapped, out_file)
        return out_file
