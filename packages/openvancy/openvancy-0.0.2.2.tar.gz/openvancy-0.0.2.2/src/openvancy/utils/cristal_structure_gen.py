import numpy as np
from pathlib import Path
from typing import Tuple, Union, Optional

from openvancy.utils.config_loader import Config as V1Config


class CrystalStructureGenerator:
    """
    Genera una estructura BCC o FCC replicada y alineada al centro de la caja
    del archivo de defecto (self.path_defect). Escribe un dump LAMMPS.

    - Lee: cfg.paths.defect_inputs[0]
    - Usa: cfg.reference.lattice ('bcc'/'fcc'), cfg.reference.a0 (lattice const),
           cfg.reference.cells (rx, ry, rz)
    - Salida: {out_dir}/relax_structure.dump
    """

    def __init__(self, config: Union[V1Config, dict], out_dir: Path):

        if isinstance(config, V1Config):
            self.cfg: V1Config = config
        elif isinstance(config, dict):
            self.cfg = V1Config.from_dict(config)
        else:
            raise TypeError(f"Config debe ser V1Config o dict, no {type(config)}")

        self.out_dir = Path(out_dir).expanduser().resolve() / "dump"
        self.out_dir.mkdir(parents=True, exist_ok=True)

        if not self.cfg.paths.defect_inputs:
            raise ValueError("paths.defect_inputs está vacío en la configuración.")
        self.path_defect: Path = Path(self.cfg.paths.defect_inputs[0]).expanduser().resolve()
        if not self.path_defect.exists():
            raise FileNotFoundError(f"No se encontró el archivo de defecto: {self.path_defect}")

        self.structure_type: str = str(self.cfg.reference.lattice).lower().strip()
        self.a0: float = float(self.cfg.reference.a0)
        rx, ry, rz = self.cfg.reference.cells
        self.reps: Tuple[int, int, int] = (int(rx), int(ry), int(rz))

        # límites y centro de la caja del dump de defecto
        self._read_defect_box()

    def _read_defect_box(self) -> None:
        """
        Lee los límites de caja en self.path_defect y calcula el centro.
          - self.box_limits = (xlo,xhi,ylo,yhi,zlo,zhi)
          - self.box_center = np.array([cx, cy, cz])
        """
        lines = self.path_defect.read_text(encoding="utf-8", errors="ignore").splitlines()
        idx = next((i for i, l in enumerate(lines) if l.strip().startswith('ITEM: BOX BOUNDS')), None)
        if idx is None or idx + 3 > len(lines):
            raise ValueError("No se encontró bloque 'ITEM: BOX BOUNDS' de 3 líneas en el dump de defecto.")

        bounds = []
        for line in lines[idx+1:idx+4]:
            parts = line.split()
            if len(parts) < 2:
                raise ValueError(f"Línea inválida en BOX BOUNDS: {line!r}")
            lo, hi = map(float, parts[:2])
            bounds.extend([lo, hi])

        self.box_limits = tuple(bounds)
        xlo, xhi, ylo, yhi, zlo, zhi = self.box_limits
        self.box_center = np.array([(xlo + xhi) / 2.0,
                                    (ylo + yhi) / 2.0,
                                    (zlo + zhi) / 2.0], dtype=float)

    def _build_replica(self, reps: Tuple[int, int, int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Construye la celda base (bcc/fcc) con parámetro de red a0 y la replica rx×ry×rz.
        Devuelve:
          - coords: (N, 3) posiciones absolutas
          - dims: (3,) dimensiones totales de la réplica (en Å)
        """
        if self.structure_type == 'fcc':
            base = np.array([
                [0, 0, 0],
                [0.5, 0.5, 0],
                [0.5, 0, 0.5],
                [0, 0.5, 0.5]
            ]) * self.a0
        elif self.structure_type == 'bcc':
            base = np.array([
                [0, 0, 0],
                [0.5, 0.5, 0.5]
            ]) * self.a0
        else:
            raise ValueError(f"Tipo de red no soportado: {self.structure_type!r} (usa 'bcc' o 'fcc').")

        rx, ry, rz = reps
        dims = np.array([rx, ry, rz], dtype=float) * self.a0

        coords = []
        for i in range(rx):
            for j in range(ry):
                for k in range(rz):
                    disp = np.array([i, j, k], dtype=float) * self.a0
                    for p in base:
                        coords.append(p + disp)

        coords = np.array(coords, dtype=float)
        # remover duplicados por efecto numérico
        coords = np.unique(np.round(coords, 6), axis=0)
        return coords, dims

    @staticmethod
    def _wrap_to_box(coords: np.ndarray, box: Tuple[float, float, float, float, float, float]) -> np.ndarray:
        """
        Envuelve (mapea por módulo) todas las coordenadas dentro de [lo, hi) en cada eje.
        """
        xlo, xhi, ylo, yhi, zlo, zhi = box
        origin = np.array([xlo, ylo, zlo], dtype=float)
        lengths = np.array([xhi - xlo, yhi - ylo, zhi - zlo], dtype=float)
        # Evita divisiones por cero en longitudes nulas
        lengths[lengths == 0.0] = 1.0
        return origin + np.mod(coords - origin, lengths)

    def _write_dump(self, coords: np.ndarray, box: Tuple[float, float, float, float, float, float], out_file: Path) -> None:
        """
        Escribe un LAMMPS dump simple con posiciones (caja periódica).
        """
        xlo, xhi, ylo, yhi, zlo, zhi = box
        with Path(out_file).open("w", encoding="utf-8") as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
            # Periodicidad total
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{xlo} {xhi}\n")
            f.write(f"{ylo} {yhi}\n")
            f.write(f"{zlo} {zhi}\n")
            f.write("ITEM: ATOMS id type x y z\n")
            for idx, (x, y, z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.6f} {y:.6f} {z:.6f}\n")

    # ---------------- API pública ----------------

    def generate(self) -> Path:
        """
        Construye la réplica con reps, la alinea al centro de la caja del defecto
        y la escribe como 'relax_structure.dump' en self.out_dir, con PBC + wrap.
        """
        coords, dims = self._build_replica(self.reps)

        # centra réplica y la alinea al centro de la caja del defecto
        coords_centered = coords - dims / 2.0
        coords_aligned = coords_centered + self.box_center

        # define la caja periódica alrededor del centro (semicerrada [lo, hi))
        eps = 1e-5
        half = dims / 2.0
        box = (
            self.box_center[0] - half[0], self.box_center[0] + half[0] - eps,
            self.box_center[1] - half[1], self.box_center[1] + half[1] - eps,
            self.box_center[2] - half[2], self.box_center[2] + half[2] - eps,
        )

        # WRAP a la caja periódica
        coords_wrapped = self._wrap_to_box(coords_aligned, box)

        out_file = self.out_dir / "relax_structure.dump"
        self._write_dump(coords_wrapped, box, out_file)
        return out_file
