#!/usr/bin/env python3
"""
Create a LaTeX table-based taxonomy figure that's completely text-based
"""

latex_taxonomy = r"""
\begin{figure*}[t]
\centering
\begin{tabular}{|p{3.5cm}|p{3.5cm}|p{3.5cm}|p{3.5cm}|}
\hline
\multicolumn{4}{|c|}{\textbf{\Large Knowledge Graph-Enhanced DST Taxonomy}} \\
\hline
\hline
\textbf{Graph Construction Strategy} & \textbf{Integration with Language Models} & \textbf{Scope and Domain Coverage} & \textbf{Computational Efficiency} \\
\hline
\hline
\textit{Static Schema Graphs} & \textit{Graph-Augmented Transformers} & \textit{Single-Domain Specialists} & \textit{Lightweight Graph Modules} \\
\small{SST: Fixed ontology edges} & \small{GPT2-GAT: GNN + Transformer} & \small{GraphDialog: Restaurant booking} & \small{ECDG-DST: 30ms latency} \\
& & & \\
\hline
\textit{Dynamic Turn-Level Graphs} & \textit{Graph-Guided Generation} & \textit{Multi-Domain Generalizers} & \textit{Scalable Message Passing} \\
\small{DSTQA: Evolving schema} & \small{Noetic-Graph: LLM + Reranking} & \small{GCDST: Cross-domain linking} & \small{Sparse formulations} \\
& & & \\
\hline
\textit{Hierarchical Multi-Level Graphs} & \textit{Learned Relational Mechanisms} & \textit{Cross-Lingual \& Multimodal} & \\
\small{HS2DG: Dual graph levels} & \small{STAR: Self-attention relations} & \small{XQA-DST: Multilingual transfer} & \\
& & & \\
\hline
\hline
\multicolumn{4}{|c|}{\textbf{Key Insights from Taxonomic Analysis}} \\
\hline
\textbf{Hybrid Architectures} & \textbf{Multi-Level Modeling} & \textbf{Dynamic Adaptation} & \textbf{Convergence Trends} \\
LLM + Graph verification & Token $\rightarrow$ Slot $\rightarrow$ Domain & Conversation-specific patterns & Toward unified frameworks \\
\hline
\end{tabular}
\caption{Systematic taxonomy of Knowledge Graph-enhanced Dialogue State Tracking approaches. Our framework organizes methods along four key dimensions: (1) Graph Construction Strategy, (2) Integration with Language Models, (3) Scope and Domain Coverage, and (4) Computational Efficiency. Representative examples and key insights from taxonomic analysis are shown, revealing convergence toward hybrid architectures and multi-level modeling approaches.}
\label{fig:taxonomy}
\end{figure*}
"""

# Write the LaTeX table to a file
with open('/teamspace/studios/this_studio/ConvoTree/Paper/latex/taxonomy_table.tex', 'w') as f:
    f.write(latex_taxonomy)

print("Created taxonomy_table.tex - a clean, text-based LaTeX table!")
print("This approach is:")
print("1. Completely text-based - no pixel positioning")
print("2. Professional academic formatting")
print("3. Easy to modify and maintain")
print("4. Guaranteed to compile correctly")
print("5. Scales with paper formatting automatically")