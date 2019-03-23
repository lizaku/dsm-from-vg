# dsm-from-vg
This is the repo accompanying the paper "Distributional semantics in the real world: building word vector representations from a truth-theoretic model" (Kuzmenko & Herbelot, 2019), presented at IWCS.

## Abstract 

Distributional semantics models are known to produce excellent representations of lexical meaning, which correlate well with a range of behavioural data. They are also fundamentally different from truth-theoretic models of semantics, where meaning is defined as a correspondence relation to the world. There are two main aspects to this difference: a) they are built over corpus data which may or may not reflect *what is in the world*; b) they are built from word co-occurrences, that is, from lexical types rather than entities and sets. In this paper, we inspect the properties of a distributional model built over an approximation of *the real world*. We take the annotation of the Visual Genome, a large database of images marked with objects, attributes and relations, convert the data into a representation akin to first-order logic and build several distributional models using various combinations of features. We evaluate our world-based models over both relatedness and similarity datasets, and compare their performance to standard corpora-based models, allowing us to quantitatively assess the contribution of *what is* vs. *what is said* in vector-based representations of conceptual knowledge.

## Running the code

The repo contains the following files:
* `parse.py` - this script parses the entities, relations and attributes from the [Visual Genome dataset](http://visualgenome.org/api/v0/api_home.html) and produces an XML file further used for building the space.
* `build_vg_space.py` - this script works with the file created by `parse.py` and builds the space by counting co-occurreces for the entities, optionally taking into account relations, attributes and situations. 
* `evaluate.py` - this script evaluates the created spaces against MEN and SimLex-999 datasets and outputs the spearman correlations between human-based similarity scores and similarity scores extracted from the models.
* `utils.py` - this script contains auxiliary functions and is not run directly.
