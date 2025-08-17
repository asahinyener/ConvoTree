# LaTeX Environment Setup for ACL Paper

This document provides step-by-step instructions to set up the LaTeX environment and compile the "Knowledge Graphs for Dialogue State Tracking" paper.

## Prerequisites

Ensure you have `sudo` access and an internet connection for package installation.

## Installation Steps

### 1. Update Package Lists
```bash
sudo apt update
```

### 2. Install Essential LaTeX Packages
```bash
sudo apt install -y texlive-latex-base texlive-latex-extra texlive-bibtex-extra texlive-fonts-recommended
```

### 3. Install Additional Font Packages
```bash
sudo apt install -y texlive-fonts-extra
```

This step is required for the `inconsolata` font package used in the ACL template.

## Paper Compilation

### Navigate to LaTeX Directory
```bash
cd /teamspace/studios/this_studio/ConvoTree/Paper/latex
```

### Compile the Paper
```bash
pdflatex acl_latex.tex
```

**Note**: The first compilation may show citation warnings (marked with `???`) since the bibliography file is not yet processed. This is normal and the PDF will still be generated.

### Complete Bibliography Processing (Optional)
If you have bibliography entries, run:
```bash
bibtex acl_latex
pdflatex acl_latex.tex
pdflatex acl_latex.tex
```

The double compilation ensures all cross-references are resolved.

## Output

- **PDF File**: `acl_latex.pdf` (7 pages, ~196KB)
- **Log File**: `acl_latex.log` (compilation details)
- **Auxiliary Files**: Various `.aux`, `.out`, `.bbl` files

## Paper Configuration

The paper is currently configured with:
- Document class: `article` (11pt)
- ACL style: `final` mode (change to `review` for submission)
- Required packages: Times font, inconsolata, graphicx, etc.

## Troubleshooting

### Missing Font Errors
If you encounter "File 'inconsolata.sty' not found":
```bash
sudo apt install -y texlive-fonts-extra
```

### Missing Package Errors
For other missing packages, install the full TeXLive distribution:
```bash
sudo apt install -y texlive-full
```

### Permission Issues
Ensure you have write permissions in the latex directory for output files.

## File Structure

```
Paper/
├── latex/
│   ├── acl_latex.tex      # Main LaTeX file
│   ├── acl.sty           # ACL style file
│   ├── custom.bib        # Bibliography file
│   ├── acl_natbib.bst    # Bibliography style
│   └── acl_latex.pdf     # Compiled output
└── SETUP.md              # This file
```

## Quick Start Commands

```bash
# One-time setup
sudo apt update && sudo apt install -y texlive-latex-base texlive-latex-extra texlive-bibtex-extra texlive-fonts-recommended texlive-fonts-extra

# Compile paper
cd /teamspace/studios/this_studio/ConvoTree/Paper/latex
pdflatex acl_latex.tex
```

The PDF will be ready for review and analysis in your modify-evaluate-inspect-analyze workflow.