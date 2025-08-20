from pathlib import Path
from typing import List
import csv

import typer
from ordered_set import OrderedSet
from pynmrstar import Entry

from nef_pipelines.lib.nef_lib import (
    NEF_MOLECULAR_SYSTEM,
    read_entry_from_file_or_stdin_or_exit_error,
)
from nef_pipelines.lib.sequence_lib import sequence_from_entry, sequence_to_nef_frame
from nef_pipelines.lib.structures import SequenceResidue, Linking
from nef_pipelines.lib.util import (
    exit_error,
    parse_comma_separated_options,
)
from nef_pipelines.tools.sequences import sequences_app

app = typer.Typer()

NO_CHAIN_START_HELP = """don't include the start chain link type on a chain for the first residue [linkage will be
                         middle] for the named chains. Either use a comma joined list of chains [e.g. A,B] or call this
                         option multiple times to set chain starts for multiple chains"""
NO_CHAIN_END_HELP = """don't include the end chain link type on a chain for the last residue [linkage will be
                       middle] for the named chains. Either use a comma joined list of chains [e.g. A,B] or call this
                       option multiple times to set chain ends for multiple chains"""


def parse_ucbshift_csv(file_path: Path) -> List[SequenceResidue]:
    """Parse UCBShift CSV file and extract sequence information."""
    residues = []
    
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                try:
                    resnum = int(row['RESNUM'])
                    resname = row['RESNAME'].strip()
                    
                    # Create SequenceResidue with default chain code 'A'
                    residue = SequenceResidue(
                        chain_code='A',
                        sequence_code=resnum,
                        residue_name=resname,
                        linking=None  # Will be set later based on position
                    )
                    residues.append(residue)
                    
                except (ValueError, KeyError) as e:
                    exit_error(f"Error parsing row {reader.line_num}: {e}")
                    
    except FileNotFoundError:
        exit_error(f"UCBShift file not found: {file_path}")
    except Exception as e:
        exit_error(f"Error reading UCBShift file {file_path}: {e}")
    
    return residues


@sequences_app.command()
def ucbshift(
    no_chain_starts: List[str] = typer.Option(
        [], "--no-chain-start", help=NO_CHAIN_START_HELP
    ),
    no_chain_ends: List[str] = typer.Option(
        [], "--no-chain-end", help=NO_CHAIN_END_HELP
    ),
    chain_code: str = typer.Option(
        "A", "--chain-code", help="chain code to assign to the sequence (default: A)"
    ),
    entry_name: str = typer.Option(
        "ucbshift", help="a name for the entry if required"
    ),
    input_path: Path = typer.Option(
        None,
        metavar="|PIPE|",
        help="file to read NEF data from default is stdin '-'",
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="if set don't output the nef stream"
    ),
    file_path: Path = typer.Argument(
        None, help="UCBShift CSV file to read", metavar="<UCBSHIFT-CSV-FILE>"
    ),
):
    """- import sequence from UCBShift CSV format
    
    UCBShift format is a CSV file with columns RESNUM, RESNAME and various chemical shift data.
    This command extracts the sequence information from the RESNUM and RESNAME columns.
    """

    if not file_path:
        exit_error("no UCBShift CSV file provided")

    if input_path:
        entry = read_entry_from_file_or_stdin_or_exit_error(input_path)
    else:
        entry = Entry.from_scratch(entry_id=entry_name)

    sequence_residues = OrderedSet(sequence_from_entry(entry))

    no_chain_starts = parse_comma_separated_options(no_chain_starts)
    no_chain_ends = parse_comma_separated_options(no_chain_ends)

    # Parse UCBShift CSV file
    ucbshift_residues = parse_ucbshift_csv(file_path)

    if len(ucbshift_residues) == 0:
        exit_error(f"no residues read from {file_path}")

    # Update chain codes if specified
    if chain_code != 'A':
        ucbshift_residues = [
            SequenceResidue(
                chain_code=chain_code,
                sequence_code=res.sequence_code,
                residue_name=res.residue_name,
                linking=res.linking
            )
            for res in ucbshift_residues
        ]

    sequence_residues.update(ucbshift_residues)

    sequence_frame = sequence_to_nef_frame(
        sequence_residues, no_chain_starts, no_chain_ends
    )

    if NEF_MOLECULAR_SYSTEM in entry:
        entry.remove_saveframe(NEF_MOLECULAR_SYSTEM)
    entry.add_saveframe(sequence_frame)

    if not quiet:
        print(entry)