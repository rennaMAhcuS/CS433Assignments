# `verifier.py`

## Maybe Changes

### Variable Indexing:

Adjusted var function to use (node - 1) \* k + color, ensuring correct 1-based indexing for nodes and colors.

### 1D Distance Clauses:

Corrected loop for generating distance clauses to consider nodes both before and after the current node i within distance c.

Added checks to avoid duplicate clauses by only considering pairs where j > i.

### 2D Color Range:

Fixed the loop for colors in distance clauses to iterate from 1 to d (inclusive), ensuring nodes within distance d can't share colors ≤ d.

### Center Node Correction:

Set the center clause to use node 1 (coordinates (0,0)) instead of non-existent node 0.

### DRAT Proof Generation:

Updated the kissat command to include the --drat option for proper proof file generation.

### Node Counting:

Corrected the total nodes calculation in 2D to use 2 _ r _ (r + 1) + 1 to ensure all nodes within L1 radius r are included.
