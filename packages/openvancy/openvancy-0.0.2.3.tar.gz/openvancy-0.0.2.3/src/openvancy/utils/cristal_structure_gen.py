import os
import numpy as np
from pathlib import Path
from typing import Tuple, Union

try:
    # Si está disponible, lo usamos. Si no, igual funciona con dict.
    from openvancy.utils.config_loader import Config as V1Config
except Exception:
    V1Config = None


class CrystalStructureGenerator:
    """
    Genera una estructura BCC o FCC replicada y alineada al centro de la caja
    del archivo de defecto. Escribe un dump LAMMPS con 'pp pp pp'.
    - Acepta config: dict (como tu ejemplo) o V1Config.
    - Imitación fiel de la clase que te funcionaba:
        * coords = mod(coords, dims) en la celda [0, dims)
        * luego centra: coords - dims/2 y traslada al centro de la caja del defecto
        * BOX BOUNDS sin eps, 'pp pp pp'
    """

    def __init__(self, config: Union[dict, "V1Config"], out_dir: Path):
        self.config = config
        self.out_dir = Path(out_dir).expanduser().resolve()
        self.out_dir.mkdir(parents=True, exist_ok=True)

        # === Extrae parámetros de forma robusta, ya sea dict o V1Config ===
        if V1Config is not None and isinstance(config, V1Config):
            # --- V1Config ---
            # defect
            if not config.paths.defect_inputs:
                raise ValueError("paths.defect_inputs está vacío en la configuración (V1Config).")
            self.path_defect = Path(config.paths.defect_inputs[0]).expanduser().resolve()

            # generate_relax equivalente:
            self.structure_type = str(config.reference.lattice).lower().strip()  # 'bcc'/'fcc'
            self.lattice = float(config.reference.a0)
            rx, ry, rz = config.reference.cells
            self.reps = (int(rx), int(ry), int(rz))
        else:
            # --- dict ---
            cfg = config
            # defect: puede venir plano ('defect') o dentro de CONFIG[0]['defect']
            defect_cfg = None
            if 'defect' in cfg:
                defect_cfg = cfg['defect']
            elif 'CONFIG' in cfg and isinstance(cfg['CONFIG'], list) and cfg['CONFIG']:
                first = cfg['CONFIG'][0]
                if 'defect' in first:
                    defect_cfg = first['defect']
            if defect_cfg is None:
                raise ValueError("No se encontró la clave 'defect' en la configuración (dict).")

            if isinstance(defect_cfg, list):
                if not defect_cfg:
                    raise ValueError("La configuración 'defect' está vacía (dict).")
                path_str = defect_cfg[0]
            else:
                path_str = defect_cfg
            if not isinstance(path_str, (str, Path)):
                raise TypeError(f"Tipo inválido para ruta defect: {type(path_str)}")
            self.path_defect = Path(path_str).expanduser().resolve()

            # generate_relax: [tipo, a0, rx, ry, rz]
            if 'generate_relax' in cfg:
                gr = cfg['generate_relax']
            elif 'CONFIG' in cfg and isinstance(cfg['CONFIG'], list) and cfg['CONFIG']:
                gr = cfg['CONFIG'][0].get('generate_relax')
            else:
                gr = None
            if not gr or len(gr) < 5:
                raise ValueError("Se esperaba 'generate_relax' = [tipo, a0, rx, ry, rz] en config (dict).")

            self.structure_type = str(gr[0]).lower().strip()
            self.lattice = float(gr[1])
            rx, ry, rz = map(int, gr[2:5])
            self.reps = (rx, ry, rz)

        # Leer box bounds y centro del archivo de defecto
        self._read_defect_box()

    # ---------------- Internos ----------------

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
        idx = next((i for i, l in enumerate(lines) if l.strip().startswith('ITEM: BOX BOUNDS')), None)
        if idx is None or idx + 3 > len(lines):
            raise ValueError("No se encontró 'ITEM: BOX BOUNDS' de 3 líneas en el dump de defecto.")
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
        Construye la celda base (bcc/fcc) con parámetro de red self.lattice y la replica rx×ry×rz.
        Devuelve:
          - coords: (N, 3) posiciones en [0, dims) tras aplicar mod
          - dims: (3,) dimensiones totales de la réplica (en Å)
        """
        if self.structure_type == 'fcc':
            base = np.array([
                [0, 0, 0],
                [0.5, 0.5, 0],
                [0.5, 0, 0.5],
                [0, 0.5, 0.5]
            ]) * self.lattice
        elif self.structure_type == 'bcc':
            base = np.array([
                [0, 0, 0],
                [0.5, 0.5, 0.5]
            ]) * self.lattice
        else:
            raise ValueError(f"Tipo no soportado: {self.structure_type!r}. Usa 'bcc' o 'fcc'.")

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
        # === CLAVE: wrap a la celda réplica antes de centrar, como tu clase ===
        coords = np.mod(coords, dims)

        # Dejar única la nube para evitar duplicados numéricos
        coords = np.unique(np.round(coords, 6), axis=0)
        return coords, dims

    def _write_dump(self, coords: np.ndarray, box: Tuple[float, float, float, float, float, float], out_file: Path):
        xlo, xhi, ylo, yhi, zlo, zhi = box
        with Path(out_file).open('w', encoding='utf-8') as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
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
        Construye la réplica con self.reps, la alinea al centro de la caja del defecto
        y la escribe como 'relax_structure.dump' en self.out_dir (periódica en 3D).
        """
        coords, dims = self._build_replica(self.reps)

        # Igual que tu clase: centrar y alinear al centro de la caja del defecto
        coords_centered = coords - dims / 2.0
        coords_aligned = coords_centered + self.box_center

        half = dims / 2.0
        box = (
            self.box_center[0] - half[0], self.box_center[0] + half[0],
            self.box_center[1] - half[1], self.box_center[1] + half[1],
            self.box_center[2] - half[2], self.box_center[2] + half[2],
        )

        out_file = self.out_dir / 'relax_structure.dump'
        self._write_dump(coords_aligned, box, out_file)
        return out_file
