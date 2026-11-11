"""Paquete de la aplicación Prisma."""
import warnings

# pandas 2.2.x emite un falso aviso "ChainedAssignmentError" con Python 3.14 en asignaciones
# normales del tipo df["col"] = valor (no hay asignación encadenada en este código).
# Se silencia solo ese aviso; los resultados no cambian (verificado en tests/).
warnings.filterwarnings("ignore", message=r"ChainedAssignmentError", category=FutureWarning)
