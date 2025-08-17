# Knowledge Graph-Enhanced Dialogue State Tracking Paper

This directory contains the academic paper **"A Taxonomy of Knowledge Graph-Enhanced Dialogue State Tracking and ConvoTree: A Neural Consolidation Engine"**.

## Contents

### Main Paper
- `latex/acl_latex.tex` - Main LaTeX source file
- `latex/acl_latex.pdf` - Compiled PDF (11 pages)
- `latex/custom.bib` - Bibliography with 52+ references
- `latex/acl.sty` - ACL conference style file
- `latex/acl_natbib.bst` - Bibliography style

### Documentation
- `SETUP.md` - LaTeX environment setup instructions
- `GREP_POINTS.md` - Searchable reference guide for paper navigation

## Paper Structure

1. **Introduction** - Problem statement and contribution overview
2. **Related Work** - Concise survey of DST and Knowledge Graph foundations  
3. **Methods** - Systematic taxonomy with 4 dimensions:
   - Graph Construction Strategy (Static/Dynamic/Hierarchical)
   - Integration with Language Models (Transformers/Generation/Learned)
   - Scope and Domain Coverage (Single/Multi/Cross-lingual)
   - Computational Efficiency (Lightweight/Scalable)
4. **Discussion** - Evaluation metrics and comparative analysis
5. **Limitations** - Challenges and future work
6. **ConvoTree** - Practical implementation demonstration
7. **Appendix A** - Detailed ConvoTree implementation

## Key Contributions

- **Systematic Taxonomy**: First comprehensive organization of KG-enhanced DST approaches
- **Design Pattern Analysis**: Identification of convergence toward hybrid architectures
- **Practical Validation**: ConvoTree implementation achieving 15-25x compression ratios
- **Research Directions**: Clear guidance for future graph-enhanced dialogue systems

## Compilation

```bash
cd latex/
pdflatex acl_latex.tex
bibtex acl_latex
pdflatex acl_latex.tex
pdflatex acl_latex.tex
```

## Citation Format

All citations use standard `\citep{}` format for consistency with ACL guidelines.

## Paper Stats

- **Length**: 11 pages (targeting 7.5 pages content)
- **References**: 52 citations spanning 2008-2025
- **Taxonomy**: 4 dimensions, 12 subcategories
- **Implementation**: Open-source ConvoTree system

## Quality Assurance

- ✅ LaTeX compilation verified
- ✅ Bibliography properly rendered  
- ✅ Citations standardized
- ✅ ACL formatting compliant
- ✅ Content thoroughly reviewed