import numpy as np
import pandas as pd
from eqc_models.graph.hypergraph import HypergraphModel

# List of lists example
list_of_lists = [['book','candle','cat'],['book','coffee cup'],['coffee cup','radio'],['radio']]

H = HypergraphModel(list_of_lists)
indices = H.indices
coefficients = H.coefficients
print(indices, coefficients)

# Dictionary example
scenes_dictionary = {
    0: ('FN', 'TH'),
    1: ('TH', 'JV'),
    2: ('BM', 'FN', 'JA'),
    3: ('JV', 'JU', 'CH', 'BM'),
    4: ('JU', 'CH', 'BR', 'CN', 'CC', 'JV', 'BM'),
    5: ('TH', 'GP'),
    6: ('GP', 'MP'),
    7: ('MA', 'GP'),
    8: ('FN', 'TH')
}

model = HypergraphModel(scenes_dictionary)
indices = model.indices
coefficients = model.coefficients
print(indices, coefficients)

# Nested Dictionary example
nested_dictionary =  {
    0: {'FN':{'time':'early', 'weight': 7}, 'TH':{'time':'late'}},
    1: {'TH':{'subject':'war'}, 'JV':{'observed_by':'someone'}},
    2: {'BM':{}, 'FN':{}, 'JA':{'role':'policeman'}},
    3: {'JV':{'was_carrying':'stick'}, 'JU':{}, 'CH':{}, 'BM':{'state':'intoxicated', 'color':'pinkish'}},
    4: {'JU':{'weight':15}, 'CH':{}, 'BR':{'state':'worried'}, 'CN':{}, 'CC':{}, 'JV':{}, 'BM':{}},
    5: {'TH':{}, 'GP':{}},
    6: {'GP':{}, 'MP':{}},
    7: {'MA':{}, 'GP':{'accompanied_by':'dog', 'weight':15, 'was_singing': 'Frère Jacques'}}
}

model = HypergraphModel(nested_dictionary)
indices = model.indices
coefficients = model.coefficients
print(indices, coefficients)

# Numpy array example
## Numpy arrays must have shape (N,2) where N = the number of desired incidences.
np_array = np.array([['A','a'],['A','b'],['A','c'],['B','a'],['B','d'],['C','c'],['C','d']])

model = HypergraphModel(np_array)
indices = model.indices
coefficients = model.coefficients
print(indices, coefficients)

# DataFrame example with Edge, Node, and Weight columns
df = pd.DataFrame({
    'edge': ['E1', 'E1', 'E1', 'E2', 'E2', 'E3', 'E3', 'E3', 'E4', 'E4'],
    'node': ['A', 'B', 'C', 'A', 'D', 'B', 'C', 'E', 'D', 'F'],
    'weight': [1.0, 0.5, 1.5, 2.0, 1.0, 0.75, 1.25, 1.0, 1.0, 1.2]
})

model = HypergraphModel(df)
indices = model.indices
coefficients = model.coefficients
print(indices, coefficients)