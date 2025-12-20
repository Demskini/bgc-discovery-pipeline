# BGC Discovery Pipeline

Batch-oriented, containerized biosynthetic gene cluster (BGC) discovery pipeline using:

- RAST (genome annotation)
- antiSMASH (BGC detection)
- BiG-SCAPE (BGC cluster network)


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

