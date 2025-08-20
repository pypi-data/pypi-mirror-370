import os
import numpy as np
from pathlib import Path
from typing import Tuple

class CrystalStructureGenerator:
    """
    Genera una estructura BCC o FCC replicada alineada al centro de la caja
    del archivo de defecto (self.path_defect). Escribe un dump LAMMPS.
    """
    def __init__(self, config: dict, out_dir: Path):
        self.config = config
        self.out_dir = Path(out_dir).expanduser().resolve()
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # Obtener ruta al dump de defecto, soportando estructura plana o anidada
        defect_cfg = None
        if 'defect' in config:
            defect_cfg = config['defect']
        elif 'CONFIG' in config and isinstance(config['CONFIG'], list) and config['CONFIG']:
            first = config['CONFIG'][0]
            if 'defect' in first:
                defect_cfg = first['defect']
        if defect_cfg is None:
            raise ValueError("No se encontró la clave 'defect' en la configuración")

        # defect_cfg puede ser lista o string
        if isinstance(defect_cfg, list):
            if not defect_cfg:
                raise ValueError("La configuración 'defect' está vacía")
            path_str = defect_cfg[0]
        else:
            path_str = defect_cfg
        if not isinstance(path_str, (str, Path)):
            raise TypeError(f"Tipo inválido para ruta defect: {type(path_str)}")
        self.path_defect = Path(path_str).expanduser().resolve()

        # Parámetros de la red a generar: ['bcc'|'fcc', a0, rx, ry, rz]
        self.structure_type = str(config['generate_relax'][0]).lower().strip()
        self.lattice = float(config['generate_relax'][1])
        rx, ry, rz = map(int, config['generate_relax'][2:5])
        self.reps = (rx, ry, rz)

        # Leer box bounds y centro del archivo de defecto
        self._read_defect_box()

    def _read_defect_box(self):
        """
        Lee los límites de caja en self.path_defect y calcula el centro.
        Guarda:
          - self.box_limits = (xlo,xhi,ylo,yhi,zlo,zhi)
          - self.box_center = np.array([cx, cy, cz])
        """
        if not self.path_defect.exists():
            raise FileNotFoundError(f"No se encontró: {self.path_defect}")
        lines = self.path_defect.read_text(encoding="utf-8", errors="ignore").splitlines()
        idx = next((i for i, l in enumerate(lines)
                    if l.strip().startswith('ITEM: BOX BOUNDS')), None)
        if idx is None or idx + 3 > len(lines):
            raise ValueError("No se encontró BOX BOUNDS de 3 líneas en el dump")
        bounds = []
        for line in lines[idx+1:idx+4]:
            lo, hi = map(float, line.split()[:2])
            bounds.extend([lo, hi])
        self.box_limits = tuple(bounds)
        xlo, xhi, ylo, yhi, zlo, zhi = self.box_limits
        self.box_center = np.array([(xlo + xhi)/2,
                                    (ylo + yhi)/2,
                                    (zlo + zhi)/2], dtype=float)

    def generate(self) -> Path:
        """
        Construye la réplica con reps, alinea al centro de la caja de defecto,
        escribe relax_structure.dump y devuelve su Path.
        """
        coords, dims = self._build_replica(self.reps)

        # Igual que el primer archivo: centrar y trasladar al centro de la caja
        coords_centered = coords - dims/2.0
        coords_aligned = coords_centered + self.box_center

        half = dims/2.0
        box = (
            self.box_center[0]-half[0], self.box_center[0]+half[0],
            self.box_center[1]-half[1], self.box_center[1]+half[1],
            self.box_center[2]-half[2], self.box_center[2]+half[2],
        )

        out_file = self.out_dir / 'relax_structure.dump'
        self._write_dump(coords_aligned, box, out_file)
        return out_file

    def _build_replica(self, reps: Tuple[int, int, int]) -> Tuple[np.ndarray, np.ndarray]:
        if self.structure_type == 'fcc':
            base = np.array([[0,0,0],
                             [0.5,0.5,0],
                             [0.5,0,0.5],
                             [0,0.5,0.5]], dtype=float) * self.lattice
        elif self.structure_type == 'bcc':
            base = np.array([[0,0,0],
                             [0.5,0.5,0.5]], dtype=float) * self.lattice
        else:
            raise ValueError(f"Tipo no soportado: {self.structure_type!r}")

        rx, ry, rz = reps
        dims = np.array([rx, ry, rz], dtype=float) * self.lattice

        coords = []
        for i in range(rx):
            for j in range(ry):
                for k in range(rz):
                    disp = np.array([i, j, k], dtype=float) * self.lattice
                    for p in base:
                        coords.append(p + disp)

        coords = np.array(coords, dtype=float)

        # CLAVE: mantener puntos en [0, dims) para que al centrar queden en (-L/2, L/2]
        coords = np.mod(coords, dims)

        # (Opcional) limpiar duplicados numéricos mínimos
        coords = np.unique(np.round(coords, 6), axis=0)

        return coords, dims

    def _write_dump(self, coords: np.ndarray, box: Tuple[float, float, float, float, float, float], out_file: Path):
        xlo, xhi, ylo, yhi, zlo, zhi = box
        with out_file.open('w', encoding='utf-8') as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n")
            f.write(f"{xlo} {xhi}\n")
            f.write(f"{ylo} {yhi}\n")
            f.write(f"{zlo} {zhi}\n")
            f.write("ITEM: ATOMS id type x y z\n")
            for idx, (x, y, z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.6f} {y:.6f} {z:.6f}\n")
