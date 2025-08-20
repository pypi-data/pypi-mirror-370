"""Functionailty to calculate the complexit of coordinate model"""

import argparse
import logging
import os
import sys

from mmcif.api.DataCategory import DataCategory
from mmcif.api.PdbxContainers import DataContainer
from mmcif.io.IoAdapterCore import IoAdapterCore as IoAdapter

logger = logging.getLogger(__name__)


class PdbxModelCompletity:
    def __init__(self, threshold=1e6):
        self.__data = {}
        self.__threshold = threshold

    def calculate(self, fpath):
        """Calculates complexity of coordinate file in fpath.  Returns True on success.  Returns False if file does not exist"""

        if not os.path.exists(fpath):
            logger.error("Filename %s does not exist", fpath)
            return False

        io = IoAdapter()
        cL = io.readFile(fpath, selectList=["entity", "pdbx_struct_assembly"])

        if not cL or len(cL) < 1:
            logger.error("Error processing complexity %s", fpath)
            return False

        b0 = cL[0]

        # Determine oligo count - use first row of pdbx_struct_assembly if present
        oligo_count = 1
        if b0.exists("pdbx_struct_assembly"):
            cObj = b0.getObj("pdbx_struct_assembly")

            if "oligomeric_count" in cObj.getAttributeList():
                val = cObj.getValueOrDefault("oligomeric_count", rowIndex=0, defaultValue="1")
                try:
                    valI = int(val)
                    oligo_count = valI
                except ValueError:
                    pass

        # Calculate complexity
        entry_complexity = 0
        non_poly_complexity = 0
        polymer_complexity = 0

        if b0.exists("entity"):
            cObj = b0.getObj("entity")

            # Ensure real data
            for attr in ["type", "pdbx_number_of_molecules", "formula_weight"]:
                if attr not in cObj.getAttributeList():
                    logger.error("Entity category missing attribute %s", attr)
                    return False

            for row in range(cObj.getRowCount()):
                etype = cObj.getValueOrDefault("type", row, "unknown")
                num_mol = cObj.getValueOrDefault("pdbx_number_of_molecules", row, "1")
                fw = cObj.getValueOrDefault("formula_weight", row, "unknown")

                try:
                    num_mol_int = int(num_mol)
                    fw_val = float(fw)
                except ValueError:
                    logger.error("Error converting values %s %s", num_mol, fw)

                if etype == "polymer":
                    entity_complexity = num_mol_int * fw_val * oligo_count
                    entry_complexity += entity_complexity
                    polymer_complexity += entity_complexity
                else:
                    # water, ligands, branched chain carbo, etc
                    entity_complexity = num_mol_int * fw_val
                    entry_complexity += entity_complexity
                    non_poly_complexity += entity_complexity

            is_complex = True if entry_complexity > self.__threshold else False  # noqa: SIM210

            self.__data = {
                "is_complex": is_complex,
                "entry_complexity": entry_complexity,
                "polymer_complexity": polymer_complexity,
                "non_poly_complexity": non_poly_complexity,
            }

        return True

    def write_output(self, fpath):
        """Writes out the"""

        c0 = DataContainer("complexity")

        is_complex = str(self.__data.get("is_complex", False))
        entry_complexity = str(self.__data.get("entry_complexity", 0))
        polymer_complexity = str(self.__data.get("polymer_complexity", 0))
        non_poly_complexity = str(self.__data.get("non_poly_complexity", 0))
        threshold = f"{self.__threshold:.2e}"

        attrlist = [
            "is_complex",
            "entry_complexity",
            "polymer_complexity",
            "non_poly_complexity",
            "complex_threshold",
        ]
        data = [
            [
                is_complex,
                entry_complexity,
                polymer_complexity,
                non_poly_complexity,
                threshold,
            ]
        ]

        cat = DataCategory("pdbx_complexity", attrlist, data)
        c0.append(cat)

        clist = [c0]

        io = IoAdapter()
        io.writeFile(fpath, clist)


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        prog="PdbxModelComplexity.py",
        description="Calculates the complexity of a model file and outputs a CIF file with information",
    )
    parser.add_argument("--model", required=True, help="model file to calculate complexity")
    parser.add_argument("--output", required=True, help="output file to record complexity")
    parser.add_argument(
        "--threshold",
        type=float,
        default=1e8,
        help="threshold value to use as cutoff (1.0E+6 default)",
    )
    args = parser.parse_args()

    threshold = args.threshold
    modelpath = args.model
    output = args.output

    pmc = PdbxModelCompletity(threshold=threshold)
    ok = pmc.calculate(modelpath)
    if ok:
        pmc.write_output(output)
    else:
        print("Could not parse input file %s" % modelpath)  # noqa: T201
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
