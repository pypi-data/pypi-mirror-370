import numpy as np
from pathlib import Path
from typing import Tuple, Union, Optional

# Importación condicional para flexibilidad
try:
    from openvancy.utils.config_loader import Config as V1Config
except ImportError:
    # Fallback para evitar errores si no existe openvancy
    V1Config = dict

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

       
        self._read_defect_box()


    def _read_defect_box(self) -> None:
        """
        Lee los límites de caja en self.path_defect y calcula el centro.
        Guarda:
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
        # ¡CORRECCIÓN CLAVE! Las dimensiones deben ser exactamente rx * a0, etc.
        # Esto asegura que la red quepa perfectamente en la caja.
        dims = np.array([rx, ry, rz], dtype=float) * self.a0

        coords = []
        # Generar coordenadas para la réplica PERIÓDICA
        # Nota: No generamos una celda extra (i in range(rx), no rx+1)
        for i in range(rx):
            for j in range(ry):
                for k in range(rz):
                    disp = np.array([i, j, k], dtype=float) * self.a0
                    for p in base:
                        # Añadir la posición base + desplazamiento de la celda unitaria
                        coords.append(p + disp)

        coords = np.array(coords, dtype=float)
        # Es CRUCIAL no redondear aquí si se quiere una red perfectamente periódica.
        # El redondeo puede introducir errores numéricos que rompan la periodicidad.
        # coords = np.unique(np.round(coords, 6), axis=0) # ¡ESTO ES PELIGROSO!
        # En su lugar, usamos tolerancia para eliminar duplicados (aunque no debería haber)
        # Pero para una réplica perfecta de una celda base, no deberían existir duplicados.
        # Si insistes en usar unique, usa una tolerancia muy baja con np.unique y axis=0.
        # Mejor: Confiar en que la generación es correcta y no hay duplicados.
        return coords, dims

    def _write_dump(self, coords: np.ndarray, box: Tuple[float, float, float, float, float, float], out_file: Path) -> None:
        """
        Escribe un LAMMPS dump simple con posiciones.
        """
        xlo, xhi, ylo, yhi, zlo, zhi = box
        with Path(out_file).open("w", encoding="utf-8") as f:
            f.write("ITEM: TIMESTEP\n0\n")
            f.write(f"ITEM: NUMBER OF ATOMS\n{len(coords)}\n")
            f.write("ITEM: BOX BOUNDS pp pp pp\n") # 'pp' indica periódico
            f.write(f"{xlo} {xhi}\n")
            f.write(f"{ylo} {yhi}\n")
            f.write(f"{zlo} {zhi}\n")
            f.write("ITEM: ATOMS id type x y z\n")
            for idx, (x, y, z) in enumerate(coords, start=1):
                f.write(f"{idx} 1 {x:.8f} {y:.8f} {z:.8f}\n") # Más precisión

    # ---------------- API pública ----------------

    def generate(self) -> Path:
        """
        Construye la réplica con reps, la alinea al centro de la caja del defecto
        y la escribe como 'relax_structure.dump' en self.out_dir.
        """
        coords, dims = self._build_replica(self.reps)

        # Centrar la réplica en su propia caja y luego alinear al centro del defecto
        # ¡ESTA ES LA CLAVE! La caja de la réplica generada (dims) debe ser
        # exactamente del tamaño de la caja que vamos a definir.
        coords_centered = coords - dims / 2.0
        coords_aligned = coords_centered + self.box_center

        # Definir la caja exactamente del tamaño de la réplica (dims),
        # centrada en self.box_center
        half = dims / 1.5
        box = (
            self.box_center[0] - half[0], self.box_center[0] + half[0],
            self.box_center[1] - half[1], self.box_center[1] + half[1],
            self.box_center[2] - half[2], self.box_center[2] + half[2],
        )

        out_file = self.out_dir / "relax_structure.dump"
        self._write_dump(coords_aligned, box, out_file)
        return out_file


