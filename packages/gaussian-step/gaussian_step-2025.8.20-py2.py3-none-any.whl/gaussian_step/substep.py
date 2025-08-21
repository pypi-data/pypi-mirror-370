# -*- coding: utf-8 -*-

"""Setup and run Gaussian"""

from collections import Counter
import configparser
import csv
from datetime import datetime, timezone
import gzip
import importlib
import json
import logging
from math import isnan
import os
from pathlib import Path
import pkg_resources
import platform
import pprint
import re
import shutil
import string
import textwrap
import time
import traceback

import cclib
from cpuinfo import get_cpu_info
import numpy as np
import pandas
from tabulate import tabulate

import gaussian_step
from molsystem import elements
import seamm
import seamm_exec
import seamm.data
from seamm_util import CompactJSONEncoder, Configuration, Q_
import seamm_util.printing as printing


try:
    from itertools import batched
except ImportError:
    from itertools import islice

    def batched(iterable, n):
        "Batch data into tuples of length n. The last batch may be shorter."
        # batched('ABCDEFG', 3) --> ABC DEF G
        if n < 1:
            raise ValueError("n must be at least one")
        it = iter(iterable)
        while batch := tuple(islice(it, n)):
            yield batch


logger = logging.getLogger("Gaussian")
job = printing.getPrinter()
printer = printing.getPrinter("gaussian")


def humanize(memory, suffix="B", kilo=1024):
    """
    Scale memory to its proper format e.g:

        1253656 => '1.20 MiB'
        1253656678 => '1.17 GiB'
    """
    if kilo == 1000:
        units = ["", "k", "M", "G", "T", "P"]
    elif kilo == 1024:
        units = ["", "Ki", "Mi", "Gi", "Ti", "Pi"]
    else:
        raise ValueError("kilo must be 1000 or 1024!")

    for unit in units:
        if memory < 10 * kilo:
            return f"{int(memory)}{unit}{suffix}"
        memory /= kilo


def dehumanize(memory, suffix="B"):
    """
    Unscale memory from its human readable form e.g:

        '1.20 MB' => 1200000
        '1.17 GB' => 1170000000
    """
    units = {
        "": 1,
        "k": 1000,
        "M": 1000**2,
        "G": 1000**3,
        "P": 1000**4,
        "Ki": 1024,
        "Mi": 1024**2,
        "Gi": 1024**3,
        "Pi": 1024**4,
    }

    tmp = memory.split()
    if len(tmp) == 1:
        return memory
    elif len(tmp) > 2:
        raise ValueError("Memory must be <number> <units>, e.g. 1.23 GB")

    amount, unit = tmp
    amount = float(amount)

    for prefix in units:
        if prefix + suffix == unit:
            return int(amount * units[prefix])

    raise ValueError(f"Don't recognize the units on '{memory}'")


_subscript = {
    "0": "\N{SUBSCRIPT ZERO}",
    "1": "\N{SUBSCRIPT ONE}",
    "2": "\N{SUBSCRIPT TWO}",
    "3": "\N{SUBSCRIPT THREE}",
    "4": "\N{SUBSCRIPT FOUR}",
    "5": "\N{SUBSCRIPT FIVE}",
    "6": "\N{SUBSCRIPT SIX}",
    "7": "\N{SUBSCRIPT SEVEN}",
    "8": "\N{SUBSCRIPT EIGHT}",
    "9": "\N{SUBSCRIPT NINE}",
}


def subscript(n):
    """Return the number using Unicode subscript characters."""
    return "".join([_subscript[c] for c in str(n)])


one_half = "\N{VULGAR FRACTION ONE HALF}"
degree_sign = "\N{DEGREE SIGN}"
standard_state = {
    "H": f"{one_half}H{subscript(2)}(g)",
    "He": "He(g)",
    "Li": "Li(s)",
    "Be": "Be(s)",
    "B": "B(s)",
    "C": "C(s,gr)",
    "N": f"{one_half}N{subscript(2)}(g)",
    "O": f"{one_half}O{subscript(2)}(g)",
    "F": f"{one_half}F{subscript(2)}(g)",
    "Ne": "Ne(g)",
    "Na": "Na(s)",
    "Mg": "Mg(s)",
    "Al": "Al(s)",
    "Si": "Si(s)",
    "P": "P(s)",
    "S": "S(s)",
    "Cl": f"{one_half}Cl{subscript(2)}(g)",
    "Ar": "Ar(g)",
    "K": "K(s)",
    "Ca": "Ca(s)",
    "Sc": "Sc(s)",
    "Ti": "Ti(s)",
    "V": "V(s)",
    "Cr": "Cr(s)",
    "Mn": "Mn(s)",
    "Fe": "Fe(s)",
    "Co": "Co(s)",
    "Ni": "Ni(s)",
    "Cu": "Cu(s)",
    "Zn": "Zn(s)",
    "Ga": "Ga(s)",
    "Ge": "Ge(s)",
    "As": "As(s)",
    "Se": "Se(s)",
    "Br": f"{one_half}Br{subscript(2)}(l)",
    "Kr": "(g)",
}


class Substep(seamm.Node):
    def __init__(
        self,
        flowchart=None,
        title="no title",
        extension=None,
        logger=logger,
        module=__name__,
    ):
        """Initialize the node"""

        logger.debug("Creating Energy {}".format(self))

        super().__init__(
            flowchart=flowchart, title=title, extension=extension, logger=logger
        )

        self._chkpt = None
        self._input_only = False
        self._timing_data = []
        self._timing_path = Path("~/.seamm.d/timing/gaussian.csv").expanduser()

        # Set up the timing information
        self._timing_header = [
            "node",  # 0
            "cpu",  # 1
            "cpu_version",  # 2
            "cpu_count",  # 3
            "cpu_speed",  # 4
            "date",  # 5
            "SMILES",  # 6
            "H_SMILES",  # 7
            "formula",  # 8
            "net_charge",  # 9
            "spin_multiplicity",  # 10
            "model",  # 11
            "keywords",  # 12
            "symmetry",  # 13
            "symmetry_used",  # 14
            "nbf",  # 15
            "nproc",  # 16
            "time",  # 17
        ]
        try:
            self._timing_path.parent.mkdir(parents=True, exist_ok=True)

            self._timing_data = 18 * [""]
            self._timing_data[0] = platform.node()
            tmp = get_cpu_info()
            if "arch" in tmp:
                self._timing_data[1] = tmp["arch"]
            if "cpuinfo_version_string" in tmp:
                self._timing_data[2] = tmp["cpuinfo_version_string"]
            if "count" in tmp:
                self._timing_data[3] = str(tmp["count"])
            if "hz_advertized_friendly" in tmp:
                self._timing_data[4] = tmp["hz_advertized_friendly"]

            if not self._timing_path.exists():
                with self._timing_path.open("w", newline="") as fd:
                    writer = csv.writer(fd)
                    writer.writerow(self._timing_header)
        except Exception:
            self._timing_data = None

    @property
    def version(self):
        """The semantic version of this module."""
        return gaussian_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return gaussian_step.__git_revision__

    @property
    def global_options(self):
        return self.parent.global_options

    @property
    def gversion(self):
        return self.parent.gversion

    @property
    def chkpt(self):
        """The path to the current checkpoint file."""
        return self._chkpt

    @chkpt.setter
    def chkpt(self, value):
        self._chkpt = value

    @property
    def input_only(self):
        """Whether to write the input only, not run MOPAC."""
        return self._input_only

    @input_only.setter
    def input_only(self, value):
        self._input_only = value

    @property
    def is_runable(self):
        """Indicate whether this not runs or just adds input."""
        return True

    @property
    def options(self):
        return self.parent.options

    def calculate_enthalpy_of_formation(self, data):
        """Calculate the enthalpy of formation from the results of a calculation.

        This uses tabulated values of the enthalpy of formation of the atoms for
        the elements and tabulated energies calculated for atoms with the current
        method.

        Parameters
        ----------
        data : dict
            The results of the calculation.
        """

        # Read the tabulated values from either user or data directory
        personal_file = Path("~/.seamm.d/data/atom_energies.csv").expanduser()
        if personal_file.exists():
            personal_table = pandas.read_csv(personal_file, index_col=False)
        else:
            personal_table = None

        path = Path(pkg_resources.resource_filename(__name__, "data/"))
        csv_file = path / "atom_energies.csv"
        table = pandas.read_csv(csv_file, index_col=False)

        self.logger.debug(f"self.model = {self.model}")

        # Check if have the data
        atom_energies = None
        correction_energy = None
        if self.model.startswith("U") or self.model.startswith("R"):
            column = self.model[1:]
        else:
            column = self.model

        self.logger.debug(f"Looking for '{column}'")

        column2 = column + " correction"
        if personal_table is not None and column in personal_table.columns:
            atom_energies = personal_table[column].to_list()
            if column2 in personal_table.columns:
                correction_energy = personal_table[column2].to_list()
        elif column in table.columns:
            atom_energies = table[column].to_list()
            if column2 in table.columns:
                correction_energy = table[column2].to_list()

        if atom_energies is None:
            self.logger.debug("     and didn't find it!")

        DfH0gas = None
        references = None
        term_symbols = None
        if personal_table is not None and "ΔfH°gas" in personal_table.columns:
            DfH0gas = personal_table["ΔfH°gas"].to_list()
            if "Reference" in personal_table.columns:
                references = personal_table["Reference"].to_list()
            if "Term Symbol" in personal_table.columns:
                term_symbols = personal_table["Term Symbols"].to_list()
        elif "ΔfH°gas" in table.columns:
            DfH0gas = table["ΔfH°gas"].to_list()
            if "Reference" in table.columns:
                references = table["Reference"].to_list()
            if "Term Symbol" in table.columns:
                term_symbols = table["Term Symbol"].to_list()
        if references is not None:
            len(references)

        if atom_energies is None:
            return f"There are no tabulated atom energies for {column}"

        # Get the atomic numbers and counts
        _, configuration = self.get_system_configuration(None)
        counts = Counter(configuration.atoms.atomic_numbers)

        # Get the Hill formula as a list
        symbols = sorted(elements.to_symbols(counts.keys()))
        composition = []
        if "C" in symbols:
            composition.append((6, "C", counts[6]))
            symbols.remove("C")
            if "H" in symbols:
                composition.append((1, "H", counts[1]))
                symbols.remove("H")

        for symbol in symbols:
            atno = elements.symbol_to_atno[symbol]
            composition.append((atno, symbol, counts[atno]))

        # And the reactions. First, for atomization energy
        middot = "\N{MIDDLE DOT}"
        lDelta = "\N{GREEK CAPITAL LETTER DELTA}"
        formula = ""
        tmp = []
        for atno, symbol, count in composition:
            if count == 1:
                formula += symbol
                tmp.append(f"{symbol}(g)")
            else:
                formula += f"{symbol}{subscript(count)}"
                tmp.append(f"{count}{middot}{symbol}(g)")
        gas_atoms = " + ".join(tmp)
        tmp = []
        for atno, symbol, count in composition:
            if count == 1:
                tmp.append(standard_state[symbol])
            else:
                tmp.append(f"{count}{middot}{standard_state[symbol]}")
        standard_elements = " + ".join(tmp)

        # The atomization energy is the electronic energy minus the energy of the atoms
        try:
            name = "SMILES: " + configuration.canonical_smiles
            if name is None:
                name = "Formula: " + formula
        except Exception:
            name = "Formula: " + formula
        try:
            name = configuration.PC_iupac_name(fallback=name)
        except Exception:
            pass

        if name is None:
            name = "Formula: " + formula

        text = f"Thermochemistry of {name} with {column}\n\n"
        text += "Atomization Energy\n"
        text += "------------------\n"
        text += textwrap.fill(
            f"The atomization energy,  {lDelta}atE{degree_sign}, is the energy to break"
            " all the bonds in the system, separating the atoms from each other."
        )
        text += f"\n\n    {formula} --> {gas_atoms}\n\n"
        text += textwrap.fill(
            "The following table shows in detail the calculation. The first line is "
            "the system and its calculated energy. The next lines are the energies "
            "of each type of atom in the system. These have been tabulated by running "
            "calculations on each atom, and are included in the SEAMM release. "
            "The last two lines give the formation energy from atoms in atomic units "
            "and as kJ/mol.",
        )
        text += "\n\n"
        table = {
            "System": [],
            "Term": [],
            "Value": [],
            "Units": [],
        }

        E = data["energy"]

        Eatoms = 0.0
        for atno, symbol, count in composition:
            Eatom = atom_energies[atno - 1]
            if isnan(Eatom):
                # Don't have the data for this element
                return f"Do not have tabulated atom energies for {symbol} in {column}"
            Eatoms += count * Eatom
            tmp = Q_(Eatom, "kJ/mol").m_as("E_h")
            table["System"].append(f"{symbol}(g)")
            table["Term"].append(f"{count} * {tmp:.6f}")
            table["Value"].append(f"{count * tmp:.6f}")
            table["Units"].append("")

        table["Units"][0] = "E_h"

        table["System"].append("^")
        table["Term"].append("-")
        table["Value"].append("-")
        table["Units"].append("")

        table["System"].append(formula)
        table["Term"].append(f"{-E:.6f}")
        table["Value"].append(f"{-E:.6f}")
        table["Units"].append("E_h")

        data["E atomization"] = Eatoms - Q_(E, "E_h").m_as("kJ/mol")

        table["System"].append("")
        table["Term"].append("")
        table["Value"].append("=")
        table["Units"].append("")

        result = f'{Q_(data["E atomization"], "kJ/mol").m_as("E_h"):.6f}'
        table["System"].append(f"{lDelta}atE")
        table["Term"].append("")
        table["Value"].append(result)
        table["Units"].append("E_h")

        table["System"].append("")
        table["Term"].append("")
        table["Value"].append(f'{data["E atomization"]:.2f}')
        table["Units"].append("kJ/mol")

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            colalign=("center", "center", "decimal", "center"),
            disable_numparse=True,
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        text_lines.append(f"Atomization Energy for {formula}".center(length))
        text_lines.append(tmp)
        text += textwrap.indent("\n".join(text_lines), 4 * " ")

        if "H" not in data:
            text += "\n\n"
            text += "Cannot calculate enthalpy of formation without the enthalpy"
            return text
        if DfH0gas is None:
            text += "\n\n"
            text += "Cannot calculate enthalpy of formation without the tabulated\n"
            text += "atomization enthalpies of the elements."
            return text

        # Atomization enthalpy of the elements, experimental
        table = {
            "System": [],
            "Term": [],
            "Value": [],
            "Units": [],
            "Reference": [],
        }

        E = data["energy"]

        DfH_at = 0.0
        refno = 1
        for atno, symbol, count in composition:
            DfH_atom = DfH0gas[atno - 1]
            DfH_at += count * DfH_atom
            tmp = Q_(DfH_atom, "kJ/mol").m_as("E_h")
            table["System"].append(f"{symbol}(g)")
            if count == 1:
                table["Term"].append(f"{tmp:.6f}")
            else:
                table["Term"].append(f"{count} * {tmp:.6f}")
            table["Value"].append(f"{count * tmp:.6f}")
            table["Units"].append("")
            refno += 1
            table["Reference"].append(refno)

        table["Units"][0] = "E_h"

        table["System"].append("^")
        table["Term"].append("-")
        table["Value"].append("-")
        table["Units"].append("")
        table["Reference"].append("")

        table["System"].append(standard_elements)
        table["Term"].append("")
        table["Value"].append("0.0")
        table["Units"].append("E_h")
        table["Reference"].append("")

        table["System"].append("")
        table["Term"].append("")
        table["Value"].append("=")
        table["Units"].append("")
        table["Reference"].append("")

        result = f'{Q_(DfH_at, "kJ/mol").m_as("E_h"):.6f}'
        table["System"].append(f"{lDelta}atH{degree_sign}")
        table["Term"].append("")
        table["Value"].append(result)
        table["Units"].append("E_h")
        table["Reference"].append("")

        table["System"].append("")
        table["Term"].append("")
        table["Value"].append(f"{DfH_at:.2f}")
        table["Units"].append("kJ/mol")
        table["Reference"].append("")

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            colalign=("center", "center", "decimal", "center", "center"),
            disable_numparse=True,
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        text_lines.append(
            "Atomization enthalpy of the elements (experimental)".center(length)
        )
        text_lines.append(tmp)

        text += "\n\n"
        text += "Enthalpy of Formation\n"
        text += "---------------------\n"
        text += textwrap.fill(
            f"The enthalpy of formation, {lDelta}fHº, is the enthalpy of creating the "
            "molecule from the elements in their standard state:"
        )
        text += f"\n\n   {standard_elements} --> {formula} (1)\n\n"
        text += textwrap.fill(
            "The standard state of the element, denoted by the superscript º,"
            " is its form at 298.15 K and 1 atm pressure, e.g. graphite for carbon, "
            "H2 gas for hydrogen, etc."
        )
        text += "\n\n"
        text += textwrap.fill(
            "Since it is not easy to calculate the enthalpy of e.g. graphite we will "
            "use two sequential reactions that are equivalent. First, we will create "
            "gas phase atoms from the elements:"
        )
        text += f"\n\n    {standard_elements} --> {gas_atoms} (2)\n\n"
        text += textwrap.fill(
            "This will use the experimental values of the enthalpy of formation of the "
            "atoms in the gas phase to calculate the enthalpy of this reaction. "
            "Then we react the atoms to get the desired system:"
        )
        text += f"\n\n    {gas_atoms} --> {formula} (3)\n\n"
        text += textwrap.fill(
            "Note that this is reverse of the atomization reaction, so "
            f"{lDelta}H = -{lDelta}atH."
        )
        text += "\n\n"
        text += textwrap.fill(
            "First we calculate the enthalpy of the atomization of the elements in "
            "their standard state, using tabulated experimental values:"
        )
        text += "\n\n"
        text += textwrap.indent("\n".join(text_lines), 4 * " ")

        # And the calculated atomization enthalpy
        table = {
            "System": [],
            "Term": [],
            "Value": [],
            "Units": [],
        }

        Hatoms = 0.0
        dH = Q_(6.197, "kJ/mol").m_as("E_h")
        for atno, symbol, count in composition:
            Eatom = atom_energies[atno - 1]
            # 6.197 is the H298-H0 for an atom
            Hatoms += count * (Eatom + 6.197)
            if correction_energy is not None and not isnan(correction_energy[atno - 1]):
                Hatoms += count * correction_energy[atno - 1]

            tmp = Q_(Eatom, "kJ/mol").m_as("E_h")
            table["System"].append(f"{symbol}(g)")
            if count == 1:
                table["Term"].append(f"{-tmp:.6f} + {dH:.6f}")
            else:
                table["Term"].append(f"{count} * ({-tmp:.6f} + {dH:.6f})")
            table["Value"].append(f"{-count * (tmp + dH):.6f}")
            table["Units"].append("")

        table["System"].append("^")
        table["Term"].append("-")
        table["Value"].append("-")
        table["Units"].append("")

        H = data["H"]

        table["System"].append(formula)
        table["Term"].append(f"{H:.6f}")
        table["Value"].append("")
        table["Units"].append("E_h")

        data["H atomization"] = Hatoms - Q_(H, "E_h").m_as("kJ/mol")
        data["DfH0"] = DfH_at - data["H atomization"]
        table["System"].append("")
        table["Term"].append("")
        table["Value"].append("=")
        table["Units"].append("")

        result = f'{Q_(data["H atomization"], "kJ/mol").m_as("E_h"):.6f}'
        table["System"].append(f"{lDelta}atH{degree_sign}")
        table["Term"].append("")
        table["Value"].append(result)
        table["Units"].append("E_h")

        table["System"].append("")
        table["Term"].append("")
        table["Value"].append(f'{data["H atomization"]:.2f}')
        table["Units"].append("kJ/mol")

        tmp = tabulate(
            table,
            headers="keys",
            tablefmt="rounded_outline",
            colalign=("center", "center", "decimal", "center"),
            disable_numparse=True,
        )
        length = len(tmp.splitlines()[0])
        text_lines = []
        text_lines.append("Atomization Enthalpy (calculated)".center(length))
        text_lines.append(tmp)
        text += "\n\n"

        text += textwrap.fill(
            "Next we calculate the atomization enthalpy of the system. We have the "
            "calculated enthalpy of the system, but need the enthalpy of gas phase "
            f"atoms at the standard state (25{degree_sign}C, 1 atm). The tabulated "
            "energies for the atoms, used above, are identical to H0 for an atom. "
            "We will add H298 - H0 to each atom, which [1] is 5/2RT = 0.002360 E_h"
        )
        text += "\n\n"
        text += textwrap.indent("\n".join(text_lines), 4 * " ")
        text += "\n\n"
        text += textwrap.fill(
            "The enthalpy change for reaction (3) is the negative of this atomization"
            " enthalpy. Putting the two reactions together with the negative for Rxn 3:"
        )
        text += "\n\n"
        text += f"{lDelta}fH{degree_sign} = {lDelta}H(rxn 2) - {lDelta}H(rxn 3)\n"
        text += f"     = {DfH_at:.2f} - {data['H atomization']:.2f}\n"
        text += f"     = {DfH_at - data['H atomization']:.2f} kJ/mol\n"

        text += "\n\n"
        text += "References\n"
        text += "----------\n"
        text += "1. https://en.wikipedia.org/wiki/Monatomic_gas\n"
        refno = 1
        for atno, symbol, count in composition:
            refno += 1
            text += f"{refno}. {lDelta}fH{degree_sign} = {DfH0gas[atno - 1]} kJ/mol"
            if term_symbols is not None:
                text += f" for {term_symbols[atno - 1]} {symbol}"
            else:
                text += f" for {symbol}"
            if references is not None:
                text += f" from {references[atno-1]}\n"

        return text

    def cleanup(self):
        """Perform any requested cleanup at the end of the calculation."""
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )
        handling = P["file handling"]
        if handling == "keep all":
            pass
        elif handling == "remove checkpoint files":
            if self.chkpt.is_relative_to(self.wd):
                self.chkpt.unlink(missing_ok=True)
                self.chkpt = None
        elif handling == "remove all":
            directory = Path(self.directory)
            shutil.rmtree(directory)
            if self.chkpt.is_relative_to(self.wd):
                self.chkpt = None

    def get_functional(self, P=None):
        """Work out the DFT functional"""
        if P is None:
            P = self.parameters.current_values_to_dict(
                context=seamm.flowchart_variables._data
            )
        if P["level"] == "recommended":
            functional = P["functional"]
        else:
            functional = P["advanced_functional"]
        if not self.is_expr(functional):
            found = functional in gaussian_step.dft_functionals
            if not found:
                # Might be first part of name, or Gaussian-encoded name
                for _key, _data in gaussian_step.dft_functionals.items():
                    if functional == _key.split(":")[0].strip():
                        functional = _key
                        found = True
                        break
            if not found:
                # Might be the internal Gaussian name
                for _key, _data in gaussian_step.dft_functionals.items():
                    if functional == _data["name"]:
                        functional = _key
                        found = True
                        break
            if not found:
                raise ValueError(f"Don't recognize functional '{functional}'")

        return functional

    def get_method(self, P=None):
        """The method ... HF, DFT, ... used."""
        # Figure out the method.
        if P is None:
            P = self.parameters.current_values_to_dict(
                context=seamm.flowchart_variables._data
            )
        if P["level"] == "recommended":
            method_string = P["method"]
        else:
            method_string = P["advanced_method"]

        # If we don't recognize the string presume (hope?) it is a Gaussian method
        if method_string in gaussian_step.methods:
            method_data = gaussian_step.methods[method_string]
            method = method_data["method"]
        else:
            # See if it matches the keyword part
            for _key, _mdata in gaussian_step.methods.items():
                if method_string == _mdata["method"]:
                    method_string = _key
                    method_data = _mdata
                    method = method_data["method"]
                    break
            else:
                method_data = {}
                method = method_string

        return method, method_data, method_string

    def make_plots(self, data):
        """Create the density and orbital plots if requested.

        Parameters
        ----------
        data : dict()
             Dictionary of results from the calculation (results.tag file)
        """
        text = "\n\n"

        directory = Path(self.directory)
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Get the configuration and basic information
        system, configuration = self.get_system_configuration(None)

        periodicity = configuration.periodicity
        if periodicity != 0:
            raise NotImplementedError("Periodic cube files not implemented yet!")

        # Have the needed data?
        if "homos" not in data:
            return ""

        spin_polarized = len(data["homos"]) == 2

        # Prepare to run
        executor = self.parent.flowchart.executor

        # Read configuration file for Gaussian
        seamm_options = self.global_options
        ini_dir = Path(seamm_options["root"]).expanduser()
        full_config = configparser.ConfigParser()
        full_config.read(ini_dir / "gaussian.ini")
        executor_type = executor.name
        if executor_type not in full_config:
            raise RuntimeError(
                f"No section for '{executor_type}' in MOPAC ini file "
                f"({ini_dir / 'mopac.ini'})"
            )
        config = dict(full_config.items(executor_type))

        # Set up the environment
        if config["root-directory"] != "":
            env = {"g09root": config["root-directory"]}
        else:
            env = {}

        if config["setup-environment"] != "":
            cmd = [". {setup-environment} && cubegen"]
        else:
            cmd = ["cubegen"]

        npts = "-2"

        keys = []
        if P["total density"]:
            keys.append("total density")
        if spin_polarized and P["total spin density"]:
            keys.append("spin density")

        n_errors = 0
        for key in keys:
            if key == "total density":
                args = f"1 Density=SCF gaussian.fchk Total_Density.cube {npts} h"
            elif key == "spin density":
                args = f"1 Spin=SCF gaussian.fchk Spin_Density.cube {npts} h"

            # And run CUBEGEN
            result = executor.run(
                cmd=[*cmd, args],
                config=config,
                directory=self.directory,
                files={},
                return_files=["*"],
                in_situ=True,
                shell=True,
                env=env,
            )
            if not result:
                self.logger.error("There was an error running CubeGen")
                n_errors += 1
                printer.important(f"There was an error calling CUBEGEN, {cmd} {args}")

        # Any requested orbitals
        if P["orbitals"]:
            n_orbitals = data["NMO"]
            # and work out the orbitals
            txt = P["selected orbitals"]
            for spin, homo in enumerate(data["homos"]):
                if txt == "all":
                    orbitals = [*range(n_orbitals)]
                else:
                    orbitals = []
                    for chunk in txt.split(","):
                        chunk = chunk.strip()
                        if ":" in chunk or ".." in chunk:
                            if ":" in chunk:
                                first, last = chunk.split(":")
                            elif ".." in chunk:
                                first, last = chunk.split("..")
                            first = first.strip().upper()
                            last = last.strip().upper()

                            if first == "HOMO":
                                first = homo
                            elif first == "LUMO":
                                first = homo + 1
                            else:
                                first = int(
                                    first.removeprefix("HOMO").removeprefix("LUMO")
                                )
                                if first < 0:
                                    first = homo + first
                                else:
                                    first = homo + 1 + first

                            if last == "HOMO":
                                last = homo
                            elif last == "LUMO":
                                last = homo + 1
                            else:
                                last = int(
                                    last.removeprefix("HOMO").removeprefix("LUMO")
                                )
                                if last < 0:
                                    last = homo + last
                                else:
                                    last = homo + 1 + last

                            orbitals.extend(range(first, last + 1))
                        else:
                            first = chunk.strip().upper()

                            if first == "HOMO":
                                first = homo
                            elif first == "LUMO":
                                first = homo + 1
                            else:
                                first = int(
                                    first.removeprefix("HOMO").removeprefix("LUMO")
                                )
                                if first < 0:
                                    first = homo + first
                                else:
                                    first = homo + 1 + first
                            orbitals.append(first)

                # Remove orbitals out of limits
                tmp = orbitals
                orbitals = []
                for x in tmp:
                    if x >= 0 and x < n_orbitals:
                        orbitals.append(x)

                if spin_polarized:
                    l1 = ("A", "B")[spin]
                    l2 = ("α-", "β-")[spin]
                else:
                    l1 = ""
                    l2 = ""
                for mo in orbitals:
                    if mo == homo:
                        filename = f"{l2}HOMO.cube"
                    elif mo < homo:
                        filename = f"{l2}HOMO-{homo - mo}.cube"
                    elif mo == homo + 1:
                        filename = f"{l2}LUMO.cube"
                    else:
                        filename = f"{l2}LUMO+{mo - homo - 1}.cube"
                    args = f"1 {l1}MO={mo + 1} gaussian.fchk {filename} {npts} h"

                    # And run CUBEGEN
                    result = executor.run(
                        cmd=[*cmd, args],
                        config=config,
                        directory=self.directory,
                        files={},
                        return_files=["*"],
                        in_situ=True,
                        shell=True,
                        env=env,
                    )
                    if not result:
                        self.logger.error("There was an error running CubeGen")
                        n_errors += 1
                        printer.important(
                            f"There was an error calling CUBEGEN, {cmd} {args}"
                        )

        # Finally rename and gzip the cube files
        n_processed = 0
        paths = directory.glob("*.cube")
        for path in paths:
            out = path.with_suffix(".cube.gz")
            with path.open("rb") as f_in:
                with gzip.open(out, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            n_processed += 1
            path.unlink()
        if n_errors > 0:
            text += (
                f"Created {n_processed} density and orbital cube files, but there were "
                f"{n_errors} errors trying to create cube files."
            )
        else:
            text += f"Created {n_processed} density and orbital cube files."

        return text

    def parse_fchk(self, path, data={}):
        """Process the data of a formatted Chk file given as lines of data.

        Parameters
        ----------
        path : pathlib.Path
            The path to the checkpoint file
        """
        if not path.exists():
            return data

        lines = path.read_text().splitlines()

        if len(lines) < 2:
            return data

        it = iter(lines)
        # Ignore first potentially truncated title line
        next(it)

        # Type line (A10,A30,A30)
        line = next(it)
        data["calculation"] = line[0:10].strip()
        data["method"] = line[10:40].strip()

        # The rest of the file consists of a line defining the data.
        # If the data is a scalar, it is on the control line, otherwise it follows
        translation = self.metadata["translation"]
        while True:
            try:
                line = next(it)
            except StopIteration:
                break
            try:
                key = line[0:40].strip()
                if key in translation:
                    key = translation[key]
                code = line[43]
                is_array = line[47:49] == "N="
                if is_array:
                    count = int(line[49:61].strip())
                    value = []
                    if code == "I":
                        i = 0
                        while i < count:
                            line = next(it)
                            for pos in range(0, 6 * 12, 12):
                                value.append(int(line[pos : pos + 12].strip()))
                                i += 1
                                if i == count:
                                    break
                    elif code == "R":
                        i = 0
                        while i < count:
                            line = next(it)
                            for pos in range(0, 5 * 16, 16):
                                text = line[pos : pos + 16].strip()
                                # Fortran drops E in format for large exponents...
                                text = re.sub(r"([0-9])-", r"\1E-", text)
                                value.append(float(text))
                                i += 1
                                if i == count:
                                    break
                    elif code == "C":
                        value = ""
                        i = 0
                        while i < count:
                            line = next(it)
                            for pos in range(0, 5 * 12, 12):
                                value += line[pos : pos + 12]
                                i += 1
                                if i == count:
                                    break
                                value = value.rstrip()
                    elif code == "H":
                        value = ""
                        i = 0
                        while i < count:
                            line = next(it)
                            for pos in range(0, 9 * 8, 8):
                                value += line[pos : pos + 8]
                                i += 1
                                if i == count:
                                    break
                                value = value.rstrip()
                    elif code == "L":
                        i = 0
                        while i < count:
                            line = next(it)
                            for pos in range(72):
                                value.append(line[pos] == "T")
                                i += 1
                                if i == count:
                                    break
                else:
                    if code == "I":
                        value = int(line[49:].strip())
                    elif code == "R":
                        value = float(line[49:].strip())
                    elif code == "C":
                        value = line[49:].strip()
                    elif code == "L":
                        value = line[49] == "T"
                data[key] = value
            except Exception:
                pass
        return data

    def parse_output(self, path, data={}):
        """Process the output.

        Parameters
        ----------
        path : pathlib.Path
            The Gaussian log file.
        """
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        lines = path.read_text().splitlines()

        # Did it end properly?
        data["success"] = "Normal termination" in lines[-1]

        # Find the date and version of Gaussian
        # Gaussian 09:  EM64M-G09RevE.01 30-Nov-2015
        it = iter(lines)
        for line in it:
            if "Cite this work" in line:
                for line in it:
                    if "**********************" in line:
                        line = next(it)
                        if "Gaussian" in line:
                            try:
                                _, version, revision, date = line.split()
                                _, month, year = date.split("-")
                                revision = revision.split("Rev")[1]
                                data["G revision"] = revision
                                data["G version"] = f"G{version.strip(':')}"
                                data["G month"] = month
                                data["G year"] = year
                            except Exception as e:
                                self.logger.warning(
                                    f"Could not find the Gaussian citation: {e}"
                                )
                            break
            elif "AO basis set in the form of general basis input" in line:
                _, configuration = self.get_system_configuration(None)
                symbols = configuration.atoms.symbols
                atnos = configuration.atoms.atomic_numbers
                tmp = []
                first = True
                found = set()
                keep = True
                section = {}
                for line in it:
                    if "nuclear repulsion energy" in line:
                        break
                    if line.strip() == "":
                        tmp = [section[k] for k in sorted(section.keys())]
                        pprint.pp(tmp)
                        data["basis set"] = "\n".join(tmp) + "\n"
                        break
                    if first:
                        first = False
                        # n is one-based atom number
                        n, _ = line.strip().split()
                        n = int(n)
                        atno = atnos[n - 1]
                        symbol = symbols[n - 1]
                        keep = symbol not in found
                        if keep:
                            found.add(symbol)
                            tmp.append(f"-{symbol}")
                    elif keep:
                        tmp.append(line)
                    if "****" in line:
                        if keep:
                            section[atno] = "\n".join(tmp)
                        tmp = []
                        first = True

        # Electronic state. Hope that the last one is the one we want!
        it = iter(reversed(lines))
        for line in it:
            if "The electronic state is" in line:
                data["state"] = line.split()[-1].replace("-", "").strip(".")
                break

        # And the optimization steps, if any.
        #
        # Need to be careful about end of the first (and presumably only?) optimization.
        # The FORCE calculation prints out the same information about convergence, but
        # may indicate no convergence. This can confuse this code unless we look for the
        # end of the optimization step and quit then
        it = iter(lines)
        n_steps = 0
        max_force = []
        rms_force = []
        max_displacement = []
        rms_displacement = []
        converged = None
        for line in it:
            if line == "         Item               Value     Threshold  Converged?":
                n_steps += 1
                converged = True

                tmp1, tmp2, value, threshold, criterion = next(it).split()
                if tmp1 == "Maximum" and tmp2 == "Force":
                    max_force.append(float(value))
                    data["maximum atom force threshold"] = float(threshold)
                    if criterion != "YES":
                        converged = False

                tmp1, tmp2, value, threshold, criterion = next(it).split()
                if tmp1 == "RMS" and tmp2 == "Force":
                    rms_force.append(float(value))
                    data["RMS atom force threshold"] = float(threshold)
                    if criterion != "YES":
                        converged = False

                tmp1, tmp2, value, threshold, criterion = next(it).split()
                if tmp1 == "Maximum" and tmp2 == "Displacement":
                    max_displacement.append(float(value))
                    data["maximum atom displacement threshold"] = float(threshold)
                    if criterion != "YES":
                        converged = False

                tmp1, tmp2, value, threshold, criterion = next(it).split()
                if tmp1 == "RMS" and tmp2 == "Displacement":
                    rms_displacement.append(float(value))
                    data["RMS atom displacement threshold"] = float(threshold)
                    if criterion != "YES":
                        converged = False
            elif line == " Optimization completed.":
                line = next(it)
                if line == "    -- Stationary point found.":
                    converged = True
                else:
                    self.logger.warning(f"Optimization completed: {line}")
                break
            elif line == "    -- Stationary point found.":
                converged = True
                break

        data["N steps optimization"] = n_steps

        if converged is not None:
            data["optimization is converged"] = converged
            data["maximum atom force"] = max_force[-1]
            data["RMS atom force"] = rms_force[-1]
            data["maximum atom displacement"] = max_displacement[-1]
            data["RMS atom displacement"] = rms_displacement[-1]
        data["maximum atom force trajectory"] = max_force
        data["RMS atom force trajectory"] = rms_force
        data["maximum atom displacement trajectory"] = max_displacement
        data["RMS atom displacement trajectory"] = rms_displacement

        method, method_data, method_string = self.get_method(P)

        # Look for thermochemistry output. Composite methods may override some values
        text = []
        found = False
        for line in reversed(lines):
            if "Sum of electronic and thermal Free Energies=" in line:
                found = True
                text.append(line)
            elif found:
                text.append(line)
                if "- Thermochemistry -" in line:
                    break

        if found:
            it = iter(reversed(text))
            for line in it:
                if "Rotational symmetry number" in line:
                    tmp = line.split()[3].rstrip(".")
                    data["symmetry number"] = int(tmp)
                elif "Thermal correction to Energy=" in line:
                    tmp = line.split("=")[1].strip()
                    data["E thermal"] = float(tmp)
                elif "Thermal correction to Enthalpy=" in line:
                    tmp = line.split("=")[1].strip()
                    data["H thermal"] = float(tmp)
                elif "Thermal correction to Gibbs Free Energy=" in line:
                    tmp = line.split("=")[1].strip()
                    data["G thermal"] = float(tmp)
                elif "Sum of electronic and zero-point Energies=" in line:
                    tmp = line.split("=")[1].strip()
                    data["H 0"] = float(tmp)
                elif "Sum of electronic and thermal Energies=" in line:
                    tmp = line.split("=")[1].strip()
                    data["E T"] = float(tmp)
                elif "Sum of electronic and thermal Enthalpies=" in line:
                    tmp = line.split("=")[1].strip()
                    data["U"] = float(tmp)
                elif "Sum of electronic and thermal Free Energies=" in line:
                    tmp = line.split("=")[1].strip()
                    data["G"] = float(tmp)

        # CBS calculations

        # Complete Basis Set (CBS) Extrapolation:
        # M. R. Nyden and G. A. Petersson, JCP 75, 1843 (1981)
        # G. A. Petersson and M. A. Al-Laham, JCP 94, 6081 (1991)
        # G. A. Petersson, T. Tensfeldt, and J. A. Montgomery, JCP 94, 6091 (1991)
        # J. A. Montgomery, J. W. Ochterski, and G. A. Petersson, JCP 101, 5900 (1994)
        #
        # Temperature=               298.150000 Pressure=                       1.000000
        # E(ZPE)=                      0.050496 E(Thermal)=                     0.053508
        # E(SCF)=                    -78.059017 DE(MP2)=                       -0.281841
        # DE(CBS)=                    -0.071189 DE(MP34)=                      -0.024136
        # DE(Int)=                     0.021229 DE(Empirical)=                 -0.075463
        # CBS-4 (0 K)=               -78.439921 CBS-4 Energy=                 -78.436908
        # CBS-4 Enthalpy=            -78.435964 CBS-4 Free Energy=            -78.460753

        self.logger.debug(f"Checking for CBS extrapolation for {method}")
        if method[0:4] == "CBS-":
            # Need last section
            if method == "CBS-4M":
                match = "CBS-4 Enthalpy="
                tmp_method = "CBS-4"
            else:
                match = f"{method} Enthalpy="
                tmp_method = method
            self.logger.debug(f"Looking for '{match}'")
            text = []
            found = False
            for line in reversed(lines):
                if found:
                    text.append(line)
                    if "Complete Basis Set" in line:
                        break
                elif match in line:
                    found = True
                    text.append(line)

            self.logger.debug(f"Found CBS extrapolation: {found}")
            if found:
                translation = self.metadata["translation"]
                text = text[::-1]
                it = iter(text)
                next(it)
                citations = []
                for line in it:
                    tmp = line.strip()
                    if tmp == "":
                        break
                    citations.append(tmp)
                data["citations"] = citations

                for line in it:
                    line = line.strip()
                    if len(line) > 40:
                        part = [line[0:37], line[38:]]
                    else:
                        part = [line]
                    for p in part:
                        if "=" not in p:
                            continue
                        key, value = p.split("=", 1)
                        key = key.strip()
                        value = float(value.strip())
                        if key.startswith(tmp_method):
                            key = key.split(" ", 1)[1]
                        key = "Composite/" + key
                        if key in translation:
                            key = translation[key]
                        data[key] = value
                data["energy"] = data["H 0"] - data["ZPE"]
                data["U"] = data["energy"] + data["E thermal"]
                data["model"] = method
                data["Composite/summary"] = "\n".join(text)

        # Gn calculations. No header!!!!!

        # Temperature=              298.150000 Pressure=                      1.000000
        # E(ZPE)=                     0.050251 E(Thermal)=                    0.053306
        # E(CCSD(T))=               -78.321715 E(Empiric)=                   -0.041682
        # DE(Plus)=                  -0.005930 DE(2DF)=                      -0.076980
        # E(Delta-G3XP)=             -0.117567 DE(HF)=                       -0.008255
        # G4(0 K)=                  -78.521880 G4 Energy=                   -78.518825
        # G4 Enthalpy=              -78.517880 G4 Free Energy=              -78.542752

        if method in (
            "G1",
            "G2",
            "G3",
            "G4",
            "G2MP2",
            "G3B3",
            "G3MP2",
            "G3MP2B3",
            "G4MP2",
        ):
            # Need last section
            if method == "G2":
                match = "G2MP2 Enthalpy="
            elif method == "G3B3":
                match = "G3 Enthalpy="
                method = "G3"
            elif method == "G3MP2B3":
                match = "G3MP2 Enthalpy="
                method = "G3MP2"
            else:
                match = f"{method} Enthalpy="
            text = []
            found = False
            for line in reversed(lines):
                if found:
                    if line.strip() == "":
                        break
                    text.append(line)
                elif match in line:
                    found = True
                    text.append(line)

            if found:
                translation = self.metadata["translation"]
                text = text[::-1]
                for line in text:
                    line = line.strip()
                    if len(line) > 36:
                        part = [line[0:36], line[37:]]
                    else:
                        part = [line]
                    for p in part:
                        if "=" not in p:
                            continue
                        key, value = p.split("=", 1)
                        key = key.strip()
                        value = float(value.strip())
                        if key.startswith(method):
                            key = key[len(method) :].strip()
                        elif key == "E(Empiric)":
                            key = "DE(Empirical)"
                        key = "Composite/" + key
                        if key in translation:
                            key = translation[key]
                        data[key] = value

                data["energy"] = data["H 0"] - data["ZPE"]
                data["U"] = data["energy"] + data["E thermal"]
                data["model"] = method
                tmp = " " * 20 + f"{method[0:2]} composite method extrapolation\n\n"
                data["Composite/summary"] = tmp + "\n".join(text)

        # The Wiberg bond orders ... which look like this:

        # Wiberg bond index matrix in the NAO basis:
        #
        #     Atom    1       2       3       4       5       6       7       8       9
        #     ---- ------  ------  ------  ------  ------  ------  ------  ------  -----
        #   1.  C  0.0000  1.8962  0.0134  0.1327  0.9261  0.9249  0.0071  0.0005  0.00x
        #   2.  C  1.8962  0.0000  1.1131  0.0127  0.0044  0.0049  0.9112  0.0029  0.01x
        #  ...
        #  10.  H  0.0002  0.0022  0.0049  0.9269  0.0000  0.0002  0.0015  0.0171  0.00x
        #
        #     Atom   10
        #     ---- ------
        #   1.  C  0.0002
        #   2.  C  0.0022
        #  ...

        it = iter(lines)
        for line in it:
            n_atoms = None
            if line.startswith(" Wiberg bond index matrix in the NAO basis:"):
                bond_orders = []
                next(it)
                # Read each chunk of output
                while True:
                    # Skip the two header lines
                    next(it)
                    next(it)
                    count = 0
                    # And add the data to the bond_order matrix
                    for line in it:
                        line = line.strip()
                        if line == "":
                            if n_atoms is None:
                                n_atoms = count
                            break
                        count += 1
                        vals = [float(val) for val in line.split()[2:]]
                        if len(bond_orders) < count:
                            bond_orders.append(vals)
                        else:
                            bond_orders[count - 1].extend(vals)
                    if len(bond_orders[0]) >= n_atoms:
                        break

                data["Wiberg bond order matrix"] = bond_orders

        # Wavefunction stability analysis

        # Sections introduced by line like this:
        #
        #  Stability analysis using <AA,BB:AA,BB> singles matrix:
        #
        # Possible next lines:
        #
        # The wavefunction has an RHF -> UHF instability.
        # The wavefunction is stable under the perturbations considered.
        # The wavefunction has an internal instability.
        #
        # Each section looks like this:
        # ***********************************************************************
        # Stability analysis using <AA,BB:AA,BB> singles matrix:
        # ***********************************************************************

        # Eigenvectors of the stability matrix:

        # Eigenvector   1:  1.046-A    Eigenvalue= 0.1445303  <S**2>=0.024
        #      9A -> 10A        0.70700
        #      9B -> 10B        0.70695
        # SavETr:  write IOETrn=   770 NScale= 10 NData=  16 NLR=1 NState=    1 LETr ...
        # The wavefunction is stable under the perturbations considered.
        # The wavefunction is already stable.

        it = iter(lines)
        for line in it:
            if line.startswith(" Stability analysis using"):
                # Capture the eigenvector analysis
                next(it)
                next(it)
                text = []
                for line in it:
                    if line.startswith(" SavETr"):
                        if "wavefunction stability text" not in data:
                            data["wavefunction stability text"] = []
                            data["wavefunction stability"] = []
                        data["wavefunction stability text"].append("\n".join(text))
                        text = []
                        break
                    else:
                        text.append(line[1:])  # Lines start with a blank
            elif line.startswith(" The wavefunction has an RHF -> UHF instability."):
                data["wavefunction stability"].append("RHF -> UHF")
                data["wavefunction is stable"] = False
            elif line.startswith(
                " The wavefunction is stable under the perturbations considered."
            ):
                data["wavefunction stability"].append("stable")
                data["wavefunction is stable"] = True
            elif line.startswith(" The wavefunction has an internal instability."):
                data["wavefunction stability"].append("internal")
                data["wavefunction is stable"] = False

        return data

    def parse_punch(self, path, n_atoms, data):
        """Digest the Gaussian punch file.

        Parameters
        ----------
        path : pathlib.Path
            The path to the Punch file.
        n_atoms : int
            The number of atoms in the configuration
        data : dict
            The current data for the calculation.

        Returns
        -------
        dict
        """
        lines = path.read_text().splitlines()
        n_lines = len(lines)

        # Coordinates come first
        if n_lines < n_atoms:
            printer.important("Warning: Punch file does not have coordinates.")
        else:
            XYZs = []
            start = 0
            stop = n_atoms
            for line in lines[start:stop]:
                atno, x, y, z = line.replace("D", "E").split()
                XYZs.append(float(x))
                XYZs.append(float(y))
                XYZs.append(float(z))
            # What is in data[] is the standard orientation not the input orientation
            # so replace with this, which is in the input orientation
            data["Current cartesian coordinates"] = XYZs

        # Gradients are a 3*N list ... make into N lists of 3
        data["gradients"] = [xyz for xyz in batched(data["gradients"], 3)]

        # Gradients next if they are here
        start = stop
        stop = start + n_atoms
        if n_lines > start and n_lines < stop:
            printer.important("Warning: Punch file does not have complete gradients.")
        if n_lines >= 2 * n_atoms:
            XYZs = []
            for line in lines[start:stop]:
                x, y, z = line.replace("D", "E").split()
                XYZs.append([float(x), float(y), float(z)])

            if len(XYZs) != n_atoms:
                raise RuntimeError("Error in the number of gradients in the Punch file")

            if "gradients" in data:
                # Check that the same values to 4 figures
                same = True
                for xyz0, xyz1 in zip(data["gradients"], XYZs):
                    for x0, x1 in zip(xyz0, xyz1):
                        if abs(x0 - x1) > 0.001:
                            same = False
                if not same:
                    text = "Warning: gradients from the Punch file differ in\n"
                    text += "\t" + self.header + "\n"
                    for xyz0, xyz1 in zip(data["gradients"], XYZs):
                        old = ""
                        new = ""
                        for x0 in xyz0:
                            old += f"{x0:9.4f} "
                        for x1 in xyz1:
                            new += f"{x1:9.4f} "
                        text += f"\n\t{old} <-- {new}"
                    text += "\n\n"
                    printer.important(text)
                data["gradients"] = XYZs

        # Force constants. Triangular matrix, 3 per line.
        ntri = (3 * n_atoms) * (3 * n_atoms + 1) // 2
        n = ntri // 3 if ntri % 3 == 0 else ntri // 3 + 1
        start = stop
        stop = start + n
        if n_lines > start and n_lines < stop:
            printer.important(
                "Warning: Punch file does not have complete force constants."
            )
        if n_lines >= stop:
            count = 0
            d2E = []
            factor = Q_(1.0, "E_h/a_0^2").m_as("kcal/mol/Å^2")
            for line in lines[start:stop]:
                for tmp in line.replace("D", "E").split():
                    d2E.append(float(tmp) * factor)
                    count += 1
                    if count == ntri:
                        break
            if count == ntri:
                data["force constants"] = d2E

        return data

    def process_data(self, data):
        """Massage the cclib data to a more easily used form."""
        self.logger.debug(pprint.pformat(data))
        # Convert numpy arrays to Python lists
        new = {}
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                new[key] = value.tolist()
            elif isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], np.ndarray):
                    new[key] = [i.tolist() for i in value]
                else:
                    new[key] = value
            elif isinstance(value, dict):
                for k, v in value.items():
                    newkey = f"{key}/{k}"
                    if isinstance(v, np.ndarray):
                        new[newkey] = v.tolist()
                    else:
                        new[newkey] = v
            else:
                new[key] = value

        for key in ("metadata/cpu_time", "metadata/wall_time"):
            if key in new:
                time = new[key][0]
                for tmp in new[key][1:]:
                    time += tmp
                new[key] = str(time).lstrip("0:")
                if "." in new[key]:
                    new[key] = new[key].rstrip("0")

        # Pull out the HOMO and LUMO energies as scalars
        if "homos" in new and "moenergies" in new:
            homos = new["homos"]
            if len(homos) == 2:
                for i, letter in enumerate(["alpha", "beta"]):
                    Es = new["moenergies"][i]
                    homo = homos[i]
                    new[f"{letter} HOMO orbital number"] = homo + 1
                    new[f"E {letter} homo"] = Es[homo]
                    if homo > 0:
                        new[f"E {letter} nhomo"] = Es[homo - 1]
                    if homo + 1 < len(Es):
                        new[f"E {letter} lumo"] = Es[homo + 1]
                        new[f"E {letter} gap"] = Es[homo + 1] - Es[homo]
                    if homo + 2 < len(Es):
                        new[f"E {letter} slumo"] = Es[homo + 2]
                    if "mosyms" in new and len(new["mosyms"]) > i:
                        syms = new["mosyms"][i]
                        new[f"{letter} HOMO symmetry"] = syms[homo]
                        if homo > 0:
                            new[f"{letter} NHOMO symmetry"] = syms[homo - 1]
                        if homo + 1 < len(syms):
                            new[f"{letter} LUMO symmetry"] = syms[homo + 1]
                        if homo + 2 < len(syms):
                            new[f"{letter} SLUMO symmetry"] = syms[homo + 2]
            else:
                Es = new["moenergies"][0]
                homo = homos[0]
                new["alpha HOMO orbital number"] = homo + 1
                new["beta HOMO orbital number"] = homo + 1
                new["E alpha homo"] = Es[homo]
                new["E beta homo"] = Es[homo]
                if homo > 0:
                    new["E alpha nhomo"] = Es[homo - 1]
                    new["E beta nhomo"] = Es[homo - 1]
                if homo + 1 < len(Es):
                    new["E alpha lumo"] = Es[homo + 1]
                    new["E beta lumo"] = Es[homo + 1]
                    new["E alpha gap"] = Es[homo + 1] - Es[homo]
                    new["E beta gap"] = Es[homo + 1] - Es[homo]
                if homo + 2 < len(Es):
                    new["E alpha slumo"] = Es[homo + 2]
                    new["E beta slumo"] = Es[homo + 2]
                if "mosyms" in new:
                    syms = new["mosyms"][0]
                    new["alpha HOMO symmetry"] = syms[homo]
                    new["beta HOMO symmetry"] = syms[homo]
                    if homo > 0:
                        new["alpha NHOMO symmetry"] = syms[homo - 1]
                        new["beta NHOMO symmetry"] = syms[homo - 1]
                    if homo + 1 < len(syms):
                        new["alpha LUMO symmetry"] = syms[homo + 1]
                        new["beta LUMO symmetry"] = syms[homo + 1]
                    if homo + 2 < len(syms):
                        new["alpha SLUMO symmetry"] = syms[homo + 2]
                        new["beta SLUMO symmetry"] = syms[homo + 2]

        # moments
        if "moments" in new:
            moments = new["moments"]
            new["multipole reference point"] = moments[0]
            new["dipole moment"] = moments[1]
            new["dipole moment magnitude"] = np.linalg.norm(moments[1])
            if len(moments) > 2:
                new["quadrupole moment"] = moments[2]
            if len(moments) > 3:
                new["octapole moment"] = moments[3]
            if len(moments) > 4:
                new["hexadecapole moment"] = moments[4]
            del new["moments"]

        for key in ("symmetry group", "symmetry group used"):
            if key in new:
                new[key] = new[key].capitalize()

        return new

    def run_gaussian(
        self,
        keywords,
        extra_sections={},
        spin_multiplicity=None,
        charge=None,
        old_chkpt=None,
        chkpt=None,
    ):
        """Run Gaussian.

        Parameters
        ----------
        keywords : set(str)
            The keywords for Gaussian
        extra_sections : {str: str}
            Any extra sections needed in the input
        spin_multiplicity: int
            Specify the spin multiplicity (default: None -- given by configuration)
        charge : int
            Specify the charge (default: None -- given by configuration)
        old_chkpt : str or pathlib.Path
            A previous checkpoint file to use. Default is None
        chkpt : str or pathlib.Path
            The checkpoint file for this run. Default is {step_no}_1

        Returns
        -------
        seamm.Node
            The next node object in the flowchart.
        """
        # Create the directory
        directory = self.wd
        directory.mkdir(parents=True, exist_ok=True)

        # Check for successful run, don't rerun
        success_file = directory / "success.dat"
        if not success_file.exists():
            # Get the system & configuration
            system, configuration = self.get_system_configuration(None)

            # Access the options
            options = self.options
            seamm_options = self.global_options

            # Get the computational environment and set limits
            ce = seamm_exec.computational_environment()

            # How many threads to use
            n_cores = ce["NTASKS"]
            self.logger.debug("The number of cores available is {}".format(n_cores))

            if seamm_options["parallelism"] not in ("openmp", "any"):
                n_threads = 1
            else:
                if options["ncores"] == "available":
                    n_threads = n_cores
                else:
                    n_threads = int(options["ncores"])
                if n_threads > n_cores:
                    n_threads = n_cores
                if n_threads < 1:
                    n_threads = 1
                if seamm_options["ncores"] != "available":
                    n_threads = min(n_threads, int(seamm_options["ncores"]))
            ce["NTASKS"] = n_threads
            self.logger.debug(f"Gaussian will use {n_threads} threads.")

            # How much memory to use
            if seamm_options["memory"] == "all":
                mem_limit = ce["MEM_PER_NODE"]
            elif seamm_options["memory"] == "available":
                # For the default, 'available', use in proportion to number of
                # cores used
                mem_limit = ce["MEM_PER_CPU"] * n_threads
            else:
                mem_limit = dehumanize(seamm_options["memory"])

            if options["memory"] == "all":
                memory = ce["MEM_PER_NODE"]
            elif options["memory"] == "available":
                # For the default, 'available', use in proportion to number of
                # cores used
                memory = ce["MEM_PER_CPU"] * n_threads
            else:
                memory = dehumanize(options["memory"])

            memory = min(memory, mem_limit)
            ce["MEM_PER_NODE"] = memory

            # Apply a minimum of 800 MB
            min_memory = dehumanize("800 MB")
            if min_memory > memory:
                memory = min_memory

            # Gaussian allows no decimal points.
            memory = humanize(memory, kilo=1000)

            lines = []
            if old_chkpt is None:
                step_no = int(self._id[-1])
                if step_no > 1:
                    last_chkpt = directory.parent / f"{step_no - 1}.chk"
                    if last_chkpt.exists():
                        old_chkpt = last_chkpt
            if chkpt is None:
                step_no = int(self._id[-1])
                new_chkpt = directory.parent / f"{step_no}.chk"
            else:
                new_chkpt = self.file_path(chkpt)
            self.chkpt = new_chkpt

            if old_chkpt is not None:
                lines.append(f"%OldChk={old_chkpt}")
            lines.append("%Chk=gaussian.chk")
            lines.append(f"%Mem={memory}")
            lines.append(f"%NProcShared={n_threads}")

            if spin_multiplicity is not None or charge is not None:
                if spin_multiplicity is None:
                    spin_multiplicity = configuration.spin_multiplicity
                if charge is None:
                    charge = configuration.charge
                if "Geom=AllCheck" in keywords:
                    keywords.remove("Geom=AllCheck")
                    keywords.add("Geom=Check")
            else:
                spin_multiplicity = configuration.spin_multiplicity
                charge = configuration.charge

            lines.append("# " + " ".join(keywords))
            lines.append("# Punch=(Coord,Derivatives)")

            if "Geom=AllCheck" not in keywords:
                lines.append(" ")
                lines.append(f"{self.title} of {system.name}/{configuration.name}")
                lines.append(" ")
                lines.append(f"{charge}    {spin_multiplicity}")

            # Atoms with coordinates
            if "Geom=AllCheck" not in keywords and "Geom=Check" not in keywords:
                symbols = configuration.atoms.symbols
                XYZs = configuration.atoms.coordinates
                for symbol, xyz in zip(symbols, XYZs):
                    x, y, z = xyz
                    lines.append(f"{symbol:2}   {x:10.6f} {y:10.6f} {z:10.6f}")
            lines.append(" ")

            for section in (
                "Initial force constants",
                "NBO input",
            ):
                if section in extra_sections:
                    lines.append(extra_sections[section])

            files = {"input.dat": "\n".join(lines)}
            self.logger.debug("input.dat:\n" + files["input.dat"])

            printer.important(
                self.indent + f"    Gaussian will use {n_threads} OpenMP threads and "
                f"up to {memory} of memory.\n"
            )
            if self.input_only:
                # Just write the input files and stop
                for filename in files:
                    path = directory / filename
                    path.write_text(files[filename])
                data = {}
            else:
                executor = self.parent.flowchart.executor

                # Read configuration file for Gaussian if it exists
                executor_type = executor.name
                full_config = configparser.ConfigParser()
                ini_dir = Path(seamm_options["root"]).expanduser()
                path = ini_dir / "gaussian.ini"

                # If the config file doesn't exist, get the default
                if not path.exists():
                    resources = importlib.resources.files("gaussian_step") / "data"
                    ini_text = (resources / "gaussian.ini").read_text()
                    txt_config = Configuration(path)
                    txt_config.from_string(ini_text)
                    txt_config.save()

                full_config.read(ini_dir / "gaussian.ini")

                # Getting desperate! Look for an executable in the path
                if (
                    executor_type not in full_config
                    or "root-directory" not in full_config[executor_type]
                    or "setup-environment" not in full_config[executor_type]
                ):
                    # See if we can find the Gaussian environment variables
                    if "g16root" in os.environ:
                        g_ver = "g16"
                        root_directory = os.environ["g16root"]
                        if "GAUSS_BSDDIR" in os.environ:
                            setup_directory = Path(os.environ["GAUSS_BSDDIR"])
                        else:
                            setup_directory = Path(root_directory) / g_ver / "bsd"
                    elif "g09root" in os.environ:
                        g_ver = "g09"
                        root_directory = os.environ["g09root"]
                        if "GAUSS_BSDDIR" in os.environ:
                            setup_directory = Path(os.environ["GAUSS_BSDDIR"])
                        else:
                            setup_directory = Path(root_directory) / g_ver / "bsd"
                    else:
                        root_directory = None
                        exe_path = shutil.which("g16")
                        if exe_path is None:
                            exe_path = shutil.which("g09")
                        if exe_path is None:
                            raise RuntimeError(
                                f"No section for '{executor_type}' in Gaussian ini file"
                                f" ({ini_dir / 'gaussian.ini'}), nor in the defaults, "
                                "nor in the path!"
                            )
                        g_ver = exe_path.name
                        root_directory = str(exe_path.parent.parent)
                        setup_directory = Path(root_directory) / g_ver / "bsd"
                    setup_environment = str(setup_directory / f"{g_ver}.profile")

                    txt_config = Configuration(path)

                    if not txt_config.section_exists(executor_type):
                        txt_config.add_section(executor_type)

                    txt_config.set_value(executor_type, "installation", "local")
                    txt_config.set_value(executor_type, "code", g_ver)
                    txt_config.set_value(
                        executor_type, "root-directory", root_directory
                    )
                    txt_config.set_value(
                        executor_type, "setup-environment", setup_environment
                    )
                    txt_config.save()
                    full_config.read(ini_dir / "gaussian.ini")

                config = dict(full_config.items(executor_type))
                # Use the matching version of the seamm-gaussian image by default.
                config["version"] = self.version

                g_ver = config["code"]

                # Setup the calculation environment definition
                if config["root-directory"] != "":
                    env = {f"{g_ver}root": config["root-directory"]}
                else:
                    env = {}

                if config["setup-environment"] != "":
                    cmd = f". {config['setup-environment']} ; {g_ver}"
                else:
                    cmd = g_ver

                if "scratch-dir" in config and config["scratch-dir"] != "":
                    path = Path(config["scratch-dir"])
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except Exception:
                        pass
                    else:
                        env["GAUSS_SCRDIR"] = config["scratch-dir"]

                cmd += " < input.dat > output.txt && formchk gaussian"

                return_files = [
                    "output.txt",
                    "gaussian.chk",
                    "gaussian.fchk",
                    "fort.7",
                ]

                self.logger.debug(f"{cmd=}")
                self.logger.debug(f"{env=}")

                if self._timing_data is not None:
                    self._timing_data[12] = " ".join(keywords)
                    self._timing_data[5] = datetime.now(timezone.utc).isoformat()
                t0 = time.time_ns()

                result = executor.run(
                    cmd=[cmd],
                    config=config,
                    directory=self.directory,
                    files=files,
                    return_files=return_files,
                    in_situ=True,
                    shell=True,
                    env=env,
                )

                t = (time.time_ns() - t0) / 1.0e9
                if self._timing_data is not None:
                    self._timing_data[17] = f"{t:.3f}"
                    self._timing_data[16] = str(n_threads)

                # Check for errors
                chkpoint_ok = True
                if "stderr" in result and result["stderr"] != "":
                    if "formchk" in result["stderr"]:
                        # Something happened with formchk, but it is not fatal
                        # However, don't reuse the checkpoint file
                        chkpoint_ok = False
                    printer.normal("\n\nThere was an error running Gaussian:")
                    for line in result["stderr"].split("\n"):
                        printer.normal("\t" + line)
                if not result:
                    self.logger.error("There was an error running Gaussian")
                    return None

                if chkpoint_ok:
                    (directory / "gaussian.chk").rename(self.chkpt)
                else:
                    (directory / "gaussian.chk").unlink(missing_ok=True)

        if not self.input_only:
            # Reget or parse the data
            data_file = directory / "data.json"
            if data_file.exists():
                with data_file.open("rt") as fd:
                    data = json.load(fd)
                self.model = data["model"][9:]
            else:
                # And output
                path = directory / "output.txt"
                if path.exists():
                    try:
                        data = vars(cclib.io.ccread(path))
                        data = self.process_data(data)
                    except Exception as e:
                        with open(directory / "cclib_error.out", "a") as fd:
                            traceback.print_exc(file=fd)
                        self.logger.warning(
                            f"\ncclib raised an exception {e}\nPlease report!\n"
                            f"More detail is in {str(directory / 'cclib_error.out')}."
                        )
                        data = {}
                else:
                    data = {}

                # Switch to standard names
                translation = self.metadata["translation"]
                keys = [*data.keys()]
                for key in keys:
                    if key in translation:
                        to = translation[key]
                        if to in data and data[to] != data[key]:
                            self.logger.warning(
                                f"Overwriting {to} with {key}\n"
                                f"\t{data[key]} --> {data[to]}"
                            )
                        data[to] = data[key]
                        del data[key]

                # Adding timing information from SEAMM
                data["SEAMM elapsed time"] = round(t, 1)
                data["SEAMM np"] = n_threads

                self.logger.debug("after cclib")
                self.logger.debug(f"{pprint.pformat(data)}")
                self.logger.debug(80 * "*")

                success = "success" if "success" in data else False

                if not success:
                    print("\n\nCould not find 'success' in data:\n")
                    pprint.pprint(data)
                    raise RuntimeError("Gaussian did not complete successfully")

                # Get the data from the formatted checkpoint file
                if not (directory / "gaussian.fchk").exists():
                    raise RuntimeError(
                        "Gaussian did not complete successfully. There is no fchk file"
                    )
                data = self.parse_fchk(directory / "gaussian.fchk", data)

                # Debug output
                if self.logger.isEnabledFor(logging.DEBUG):
                    keys = "\n".join(data.keys())
                    self.logger.debug("After parse_fchk")
                    self.logger.debug(f"Data keys:\n{keys}")
                    self.logger.debug(f"Data:\n{pprint.pformat(data)}")

                # And parse a bit more out of the output
                if path.exists():
                    data = self.parse_output(path, data)

                # Check whether Gaussian ran ok.
                success = "success" if "success" in data else False
                if not success:
                    raise RuntimeError("Gaussian did not complete successfully")

                # Add the requested spin state and charge
                data["requested spin multiplicity"] = spin_multiplicity
                data["requested spin state"] = self.spin_state(spin_multiplicity)
                data["charge"] = charge

                # The ideal value of S^2
                S = (spin_multiplicity - 1) / 2
                S2 = S * (S + 1)
                data["ideal S**2"] = S2
                if data["method"].startswith("R"):
                    data["S**2"] = S2

                # And the Punch file, if it exists
                punch = Path(directory / "fort.7")
                if punch.exists():
                    data = self.parse_punch(punch, configuration.n_atoms, data)

                # The model chemistry
                if "model" in data:
                    self.model = data["model"]
                elif "method" in data:
                    if data["method"].endswith("DFT"):
                        model = data["method"] + "/" + data["density functional"]
                    else:
                        model = data["method"]
                    # Remove the initial R or U since it makes reusing structures and
                    # properties difficult
                    if model[0] in ("U", "R"):
                        model = model[1:]

                    # Check if the method uses a basis set
                    methods = gaussian_step.methods
                    tmp = data["method"][1:]
                    tmp = [m for m, d in methods.items() if d["method"] == tmp]
                    if (
                        len(tmp) == 1
                        and "nobasis" in methods[tmp[0]]
                        and methods[tmp[0]]["nobasis"]
                    ):
                        self.model = model
                    elif "basis set name" in data:
                        self.model = model + "/" + data["basis set name"]
                    else:
                        self.model = model
                else:
                    self.model = "unknown"
                self.logger.debug(f"model = {self.model}")
                data["model"] = "Gaussian/" + self.model

                # Capitalize symmetry names
                for key in ("symmetry group", "symmetry group used"):
                    if key in data:
                        data[key] = data[key].capitalize()

                # Check for QCI and change the energy names
                if "QCISD" in data["model"]:
                    if "E cc" in data:
                        data["E qcisd"] = data["E cc"]
                        del data["E cc"]
                    if "E ccsd_t" in data:
                        data["E qcisd_t"] = data["E ccsd_t"]
                        del data["E ccsd_t"]

                # printer.normal(f"\n\n\n\n\nData:\n{pprint.pformat(data)}\n\n\n\n\n")

                # Debug output
                if self.logger.isEnabledFor(logging.DEBUG):
                    keys = "\n".join(data.keys())
                    self.logger.debug(f"Data keys:\n{keys}")
                    self.logger.debug(f"Data:\n{pprint.pformat(data)}")

                # Save the parsed data as JSON
                with data_file.open("w") as fd:
                    json.dump(
                        data, fd, indent=4, sort_keys=True, cls=CompactJSONEncoder
                    )

            # If ran successfully, put out the success file
            if data["success"]:
                success_file.write_text("success")

                if self._timing_data is not None:
                    self._timing_data[11] = data["model"]
                    if "metadata/symmetry_detected" in data:
                        self._timing_data[13] = str(data["metadata/symmetry_detected"])
                    else:
                        self._timing_data[13] = ""
                    if "metadata/symmetry_used" in data:
                        self._timing_data[14] = str(data["metadata/symmetry_used"])
                    else:
                        self._timing_data[14] = ""
                    if "Number of basis functions" in data:
                        self._timing_data[15] = str(data["Number of basis functions"])
                    else:
                        self._timing_data[15] = ""
                    try:
                        with self._timing_path.open("a", newline="") as fd:
                            writer = csv.writer(fd)
                            writer.writerow(self._timing_data)
                    except Exception:
                        pass

        # Add other citations here or in the appropriate place in the code.
        # Add the bibtex to data/references.bib, and add a self.reference.cite
        # similar to the above to actually add the citation to the references.
        if "G version" in data:
            try:
                template = string.Template(self._bibliography[data["G version"]])
                citation = template.substitute(
                    month=data["G month"],
                    version=data["G revision"],
                    year=data["G year"],
                )
                self.references.cite(
                    raw=citation,
                    alias="Gaussian",
                    module="gaussian_step",
                    level=1,
                    note="The principle Gaussian citation.",
                )
            except Exception:
                pass

        return data
