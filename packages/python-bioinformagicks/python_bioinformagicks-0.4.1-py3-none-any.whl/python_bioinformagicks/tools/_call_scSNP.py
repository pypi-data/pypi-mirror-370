import pysam
import pandas as pd

def call_scSNP(
    cell_barcodes: list[str],
    bam_file: pysam.AlignmentFile | str,
    contig: str,
    position: int,
    alt: str,
    threshold: int = 9,
    cb_tag: str = "CB",
    return_stats: bool = False,
): 
    '''
    With a list of valid cell barcodes as reference,
    scan a BAM file for reads aligning to a given 
    genomic position and perform variant calling
    at that position for each cell.
    
    This function is crude and useful only for single 
    point mutation calling, i.e. "I know there is a 
    mutation this position; tell me which cells have it."
    Consider using more comprehensive tools such as
    `cellsnp-lite`.
    
    Parameters
    ----------
    cell_barcodes: list of str
        A list of valid cell barcodes
    
    bam_file: pysam.AlignmentFile or str
        An instantiated pysam.AlignmentFile object
        representing an open, indexed BAM file.
        If str, function will open using:
        `f = pysam.AlignmentFile(bam_file, "rb")`
        
    contig: str 
        The contig containing the genomic position
        of interest.
    
    position: int > 0
        The 1-indexed position on the contig 
        of the genomic position of interest.
    
    alt: str 
        The alternate nucleotide. Number of reads with
        this alt nucleotide will be compared to total 
        number of reads to perform variant calling. 
        One of `["A", "G", "T", "C"]`.
    
    threshold: int (default: 9)
        The minimum number of reads covering the 
        region of needed to perform variant calling.
        If `#reads < threshold`, call NA. 
        If `#reads(ALT) < (threshold/3)`, call WT.
        Else, call alt allele.
    
    cb_tag: str (default: "CB")
        The tag in the BAM file that stores the
        (corrected) cell barcodes. Usually one of
        ["CB", "CR"].

    return_stats: bool (default: False)
        If True, return dictionary of variant calling 
        statistics, including per-cell allele frequencies.
    
    Returns
    -------
    variant_calls: list of str
        List corresponding 1-to-1 with list of cell
        barcodes. 
    
    stats: dict (when `return_stats is True`)
        Dictionary of variant calling statistics
    
    References
    ----------

    * https://doi.org/10.1093/bioinformatics/btab358

    * https://github.com/single-cell-genetics/cellsnp-lite

    '''    
    
    # Open the BAM file if necessary
    if (type(bam_file) is str):
        try:
            bam_file = pysam.AlignmentFile(bam_file, "rb")
        except Exception as e:
            print("Unable to open bam file:")
            print(e)
            return None
    
    # validate alt
    if (alt not in ["A", "G", "T", "C"]):
        print("alt must be one of [A,G,T,C]")
        return None

    # Get reads in region
    position  = position - 1 # Pysam 0-indexes, correct it here
    start_pos = position - 1
    end_pos   = position + 1
    reads_in_region = bam_file.fetch(
        contig, 
        start=start_pos,
        end=end_pos
    )
    
    # Generate dictionary of reads
    read_dict = {}
    for barcode in cell_barcodes:
        read_dict[barcode] = []

    for read in reads_in_region:
        barcode = read.get_tag(cb_tag)
        if (barcode in read_dict.keys()):
            seq = read.get_forward_sequence()
            # only insert the single nucleotide of interest
            # into the dictionary, instead of the whole read
            reference_positions = read.get_reference_positions()
            for j, pos in enumerate(reference_positions):
                if (pos == (position)):
                    read_dict[barcode].append(seq[j])
                    break
    
    # Pileup the reads
    pileup_dict = {}
    for k,v in read_dict.items():
        pileup_dict[k] = {
            "C": 0,
            "T": 0,
            "G": 0,
            "A": 0,
            "N": 0,
        }
        if (v):
            for base in v:
                if (base in pileup_dict[k].keys()):
                    pileup_dict[k][base] += 1
    df = pd.DataFrame.from_dict(pileup_dict).T
        
    variant_calls = df.apply(
        lambda x: _do_call_thresholding(x, alt, threshold),
        axis=1
    ).tolist()

    if (return_stats):
        return variant_calls, pileup_dict
    else:
        return variant_calls

def _do_call_thresholding(x, alt, threshold):
    if (x.sum() < threshold):
        return "NA"
    elif (x[alt] < (threshold/3.0)):
        return "WT"
    else:
        return alt
