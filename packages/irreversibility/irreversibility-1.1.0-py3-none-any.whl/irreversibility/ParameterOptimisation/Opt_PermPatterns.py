
"""
Optimisation of the parameters for the Permutation patterns test

From:
    Zanin, M., Rodríguez-González, A., Menasalvas Ruiz, E., & Papo, D. (2018).
    Assessing time series reversibility through permutation patterns. Entropy, 20(9), 665.
"""

import numpy as np
from itertools import product
from multiprocessing import Pool
from functools import partial

from irreversibility.Metrics.PermPatterns import GetPValue


def Optimisation( tsSet, paramSet = None, criterion = np.median, numProcesses = -1, **kwargs ):

    """
    Optimise the parameters for the Permutation patterns test.

    Parameters
    ----------
    tsSet : list of numpy.array
        Time series to be used in the optimisation.
    paramSet : list
        List of parameters' values to be evaluated. For each parameter (in the case of this test, one), the list must contain a list of possible values, e.g. [ [3, 4] ]. If None, a standard set is used. Optional, default: None.
    criterion : function
        Function to be applied to the set of p-values to obtain the best option. Optional, default: numpy.median.
    numProcesses : int
        Number of parallel tasks used in the evaluation. If -1, only one task is used. Optional, default: False.
    kwargs : 
        Other options to be passed to the function to obtain the p-values.

    Returns
    -------
    dictionary
        Set of best parameters.
    float
        Lowest obtained p-value.

    Raises
    ------
    ValueError
        If the parameters are not correct.
    """

    if paramSet is None:
        p1Set = [ 3, 4, 5 ]
    else:
        p1Set = paramSet[ 0 ]

    bestPValue = 1.0
    bestParameters = []

    for pSet in p1Set:

        pV = np.zeros( ( len( tsSet ) ) )

        if numProcesses == -1:

            for k in range( len( tsSet ) ):
                pV[ k ] = GetPValue( tsSet[ k ], pSize = pSet, **kwargs )[ 0 ]

        else:

            with Pool( processes = numProcesses ) as pool:

                async_result = []
                for k in range( len( tsSet ) ):
                    func = partial( GetPValue, TS = tsSet[ k ], pSize = pSet, **kwargs )
                    async_result.append( pool.apply_async( func ) )
                
                [result.wait() for result in async_result]
                for k in range( len( tsSet ) ):
                    pV[ k ] = async_result[ k ].get()[0]

        synthPV = criterion( pV )
        if synthPV < bestPValue:
            bestPValue = synthPV
            bestParameters = { 'pSize': pSet }

    return bestParameters, bestPValue


