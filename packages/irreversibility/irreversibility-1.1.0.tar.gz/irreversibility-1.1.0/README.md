# Irreversibility Tests Library

The assessment of time irreversibility is the assessment of the lack of invariance of the statistical properties of a system under the operation of time reversal. As a simple example, suppose a movie of an ice cube melting in a glass, and one with the ice cube forming from liquid water: an observer can easily decide which one is the original and which the time-reversed one; in this case, the creation (or destruction) of entropy is what makes the process irreversible. On the other hand, the movement of a pendulum and its time-reversed version are undistinguishable, and hence the dynamics is reversible.

Irreversible dynamics have been found in many real-world systems, with alterations being connected to, for instance, pathologies in the human brain, heart and gait, or to inefficiencies in financial markets. Assessing irreversibility in time series is not an easy task, due to its many aetiologies and to the different ways it manifests in data.

This is a library that will (hopefully) make your life easier when it comes to the analysis of the irreveribility of real-world time series. It comprises a large number of tests (not all existing ones, but we are quite close to that); and utilities to simply the whole process.

If you are interested in the concept of irreversibility, you may start from our papers:

M. Zanin, D. Papo
Tests for assessing irreversibility in time series: review and comparison.
Entropy 2021, 23(11), 1474. https://www.mdpi.com/1099-4300/23/11/1474

Zanin, M., & Papo, D. (2025).
Algorithmic Approaches for Assessing Multiscale Irreversibility in Time Series: Review and Comparison.
Entropy, 27(2), 126. https://www.mdpi.com/1099-4300/27/2/126




## Setup

This package can be installed from PyPI using pip:

```bash
pip install irreversibility
```

This will automatically install all the necessary dependencies as specified in the
`pyproject.toml` file.



## Getting started

Check the files Example_*.py for examples on how to use each test, and also [here](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home#examples).

Information about all methods, parameters, and other relevant issues can be found both in the previous papers, and in the wiki: [Go to the wiki](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home). You can also check our take on the question: [why there are so many tests?](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Why-so-many-tests%3F)

Note that all implementations have been developed in-house, and as such may contain errors or inefficient code; we welcome readers to send us comments, suggestions and corrections, using the "Issues" feature.


## Full documentation

* [Irreversibility metrics](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Irreversibility-metrics): list of all irreversibility tests, and description of how to use them. You may also wondering [why there are so many tests](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Why-so-many-tests%3F).
* [Parameter optimisation](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Parameter-optimisation): functions to optimise the parameters of each test.
* [Time series generation](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Time-series-generation): utility functions to create synthetic time series, to be used to test the metrics.
* [Time series manipulation](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Time-series-manipulation): utility functions to manipulate the irreversibility of time series.

Additional topics:
* [How p-values are obtained from measures.](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Obtaining-pValues)
* [Why do we need so many tests?](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Why-so-many-tests%3F)
* [Techniques used to reduce the computational cost.](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Computational-optimisation)
* [Analysis of the computational cost](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Computational-cost) of each test. Note that some of them are quite long to execute.



## Change log

See the [Version History](https://gitlab.com/MZanin/irreversibilitytestslibrary/-/wikis/home/Version-History) section of the Wiki for details.



## Acknowledgements

This project has received funding from the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation programme (grant agreement No 851255).

This work was partially supported by the María de Maeztu project CEX2021-001164-M funded by the MICIU/AEI/10.13039/501100011033 and FEDER, EU.

This work was partially supported by grant CNS2023-144775 funded by MICIU/AEI/10.13039/501100011033 by "European Union NextGenerationEU/PRTR".


