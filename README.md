# BGC Discovery Pipeline

Batch-oriented, containerized biosynthetic gene cluster (BGC) discovery pipeline using:

- RAST (genome annotation)
- antiSMASH (BGC detection)
- BiG-SCAPE (BGC cluster network)
- Statistical Summary of Findings


## Motivation

Our lab conducts comparative genomics analyses involving multiple researchers,
many of whom do not have formal training in computational methods. This project
aims to provide a reproducible, batch-oriented pipeline that enables wet-lab
researchers to perform biosynthetic gene cluster discovery and comparison
without requiring direct interaction with the command line.

## Design Principles

- **Batch isolation**  
  Each analysis batch is fully self-contained, with independent input,
  antiSMASH output, and BiG-SCAPE results to prevent cross-project
  contamination.

- **Reproducibility through containerization**  
  All computational steps are designed to run via Docker, ensuring consistent
  behavior across Windows, Linux, and macOS systems.

- **Accessibility for non-technical users**  
  The pipeline is being developed with click-based execution in mind, allowing
  wet-lab researchers to run analyses without needing command-line experience.

- **Scalability for comparative genomics**  
  The batch-based structure supports multi-genome and multi-project
  comparative analyses in a clear, organized manner.

## Platform Architecture

This pipeline is designed to run across Windows, Linux, and macOS.

Core tools used in this workflow, specifically antiSMASH and
BiG-SCAPE are distributed as Docker images built for
linux/amd64 (x86_64) architecture and do not currently provide native
arm64 builds.

To ensure cross-platform compatibility, all Docker containers are explicitly
executed using:

--platform linux/amd64

On Apple Silicon systems, this forces Docker to run the containers via x86_64
emulation. While this may incur a small performance cost on macOS, it guarantees
consistent and reproducible behavior across development machines and Linux-based
HPC environments.

## Streamlit User Interface and Input Handling

The pipeline includes an optional Streamlit-based graphical user interface (GUI)
designed to further lower the barrier to entry for non-computational users.
Through this interface, users can create, manage, and execute analysis batches
entirely through a web browser without interacting directly with the command
line.

## Batch Creation and File Upload

Users create new analysis batches by providing a batch name and uploading one
or more genome files. The interface enforces basic validation rules at upload
time to prevent common input errors, including:

-Restricting uploads to supported genome file types
--(.fna, .fasta, .gbk, and .txt)

-Preventing invalid or unsafe batch names

-Preventing accidental overwriting of existing batches

Each batch is automatically organized into a standardized directory structure
(input/, antismash/, bigscape/) to ensure consistency across analyses.

## FASTA Validation and Automatic Format Normalization

To accommodate common laboratory data-sharing practices, the interface allows
genome sequences to be uploaded as plain-text (.txt) files, provided they are
formatted as valid FASTA files. Uploaded text files are checked for FASTA
formatting prior to batch creation.

When valid FASTA-formatted .txt files are detected, they are automatically
normalized to a standard FASTA file extension before downstream analysis. This
ensures compatibility with antiSMASH, which determines input validity based on
file extension rather than file contents.

This design choice allows users to upload files in familiar formats while
maintaining strict compatibility with downstream bioinformatics tools.

## Guided Execution and Progress Feedback

Pipeline execution is initiated through a single action in the interface.
During execution, the interface provides live, step-by-step status updates,
including:

-Per-genome antiSMASH execution status

-BiG-SCAPE clustering progress and cutoff-specific execution

-Informative messages when clustering is skipped due to insufficient
comparable BGC content

This feedback allows users to monitor long-running analyses without requiring
direct access to terminal output, which is especially important for computational
steps that may run for a while.

## BiG-SCAPE Output Handling and Statistical Summary

BiG-SCAPE can sometimes fail when generating its HTML report due to known
template issues, even when the clustering and network analysis itself runs
correctly. In these cases, BiG-SCAPE may exit with a non-zero status despite
producing valid clustering results.

Because of this, the pipeline does not rely on BiG-SCAPE’s HTML output.
Instead, it works directly with BiG-SCAPE’s core output files to generate
a custom statistical summary of BGC similarity.