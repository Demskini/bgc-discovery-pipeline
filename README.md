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

Some core tools used in this workflow — specifically antiSMASH and
BiG-SCAPE — are distributed as Docker images built for
linux/amd64 (x86_64) architecture and do not currently provide native
arm64 builds.

To ensure cross-platform compatibility, all Docker containers are explicitly
executed using:

--platform linux/amd64

On Apple Silicon systems, this forces Docker to run the containers via x86_64
emulation. While this may incur a small performance cost on macOS, it guarantees
consistent and reproducible behavior across development machines and Linux-based
HPC environments.

## BiG-SCAPE Output Handling and Statistical Summary

BiG-SCAPE can sometimes fail when generating its HTML report due to known
template issues, even when the clustering and network analysis itself runs
correctly. In these cases, BiG-SCAPE may exit with a non-zero status despite
producing valid clustering results.

Because of this, the pipeline does not rely on BiG-SCAPE’s HTML output.
Instead, it works directly with BiG-SCAPE’s core output files to generate
a custom statistical summary of BGC similarity and clustering patterns.