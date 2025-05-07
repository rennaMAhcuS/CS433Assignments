# Assignment 4
_Due Date: 17th April_
## Verifying Neural Network Robustness Using SMT Solvers

### Objective:

Encode a trained neural network using an SMT solver and determine, for a given
instance, the maximum perturbation bound within which the model's output
remains unchanged.
 
### Task Description:

* Select a pre-trained neural network that performs image classification, and it
should only contain ReLU and ArgMax as non-linear components.
* Encode the neural network as a set of constraints suitable for analysis by an
SMT solver.
* For a given input image, using the SMT solver, find the maximum perturbation
such that the classification output remains the same.
* You need to submit the zip file containing the following:
    - SMT encoding of the model.
    - A brief report summarizing the results and methodology.
