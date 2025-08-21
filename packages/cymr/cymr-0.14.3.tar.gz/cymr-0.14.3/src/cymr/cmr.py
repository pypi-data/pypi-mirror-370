"""Models of free recall."""

from __future__ import annotations
import json
import numpy as np
import h5py
from typing import Union, Any, Iterable, Optional, Tuple
from numpy.typing import ArrayLike
from cymr.fit import Recall
from cymr import fit
from cymr import network
from cymr.parameters import Parameters


Region = Union[Tuple[str, str], Tuple[Tuple[str, str], Tuple[str, str]]]


def save_patterns(h5_file, items, **kwargs):
    """
    Write patterns and similarity matrices to hdf5.

    Parameters
    ----------
    h5_file : str
        Path to hdf5 file to save patterns in.

    items : list of str
        Item strings corresponding to the patterns.

    Additional keyword arguments set named feature vectors. Feature
    vector arrays must have shape [items x units].
    """
    with h5py.File(h5_file, 'w') as f:
        # items
        dt = h5py.special_dtype(vlen=str)
        items = np.asarray(items)
        dset = f.create_dataset('items', items.shape, dtype=dt)
        for i, item in enumerate(items):
            dset[i] = item

        # features
        features = list(kwargs.keys())
        dset = f.create_dataset('features', (len(features),), dtype=dt)
        for i, feature in enumerate(features):
            dset[i] = feature

        # patterns
        for name, vectors in kwargs.items():
            # save vectors
            f.create_dataset('vector/' + name, data=vectors)

            # set pattern similarity to dot product
            sim = np.dot(vectors, vectors.T)
            f.create_dataset('similarity/' + name, data=sim)


def load_patterns(h5_file, features=None):
    """
    Load weights from an hdf5 file.

    Parameters
    ----------
    h5_file : str
        Path to file saved with `save_patterns`.

    features : list of str, optional
        Names of features to load. Default is to load all features.

    Returns
    -------
    patterns : dict of (str: dict of (str: numpy.array))
        Loaded patterns. The "vector" field contains vector patterns.
        The "similarity" field contains pairwise similarity matrices.
        Each type of pattern contains a field for each loaded feature.
    """
    with h5py.File(h5_file, 'r') as f:
        patterns = {
            'items': np.array([item for item in f['items'].asstr()]),
            'vector': {},
            'similarity': {},
        }

        if features is None:
            features = f['features'].asstr()

        for name in features:
            patterns['vector'][name] = f['vector/' + name][()]
            patterns['similarity'][name] = f['similarity/' + name][()]
    return patterns


def encode_region(region: Region) -> str:
    """Encode a region as a string."""
    if len(region) == 0:
        raise ValueError('Cannot encode an empty region.')
    elif isinstance(region[0], str):
        region_str = '-'.join(region)
    else:
        region_str = '_'.join('-'.join(segment) for segment in region)
    return region_str


def decode_region(
    region_str: str
) -> Union[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    """Decode a region string."""
    if '_' in region_str:
        region = tuple([tuple(s.split('-')) for s in region_str.split('_')])
    else:
        region = tuple(region_str.split('-'))
    return region


def read_config(json_file):
    """Read model configuration from a JSON file."""
    with open(json_file, 'r') as f:
        par_dict = json.load(f)

    par = CMRParameters()
    if 'options' in par_dict:
        par.set_options(par_dict['options'])
    par.set_free(par_dict['free'])
    par.set_fixed(par_dict['fixed'])
    par.set_dependent(par_dict['dependent'])
    for trial_type, p in par_dict['dynamic'].items():
        for name, val in p.items():
            if 'scope' in par_dict['dynamic'] and name in par_dict['dynamic']['scope']:
                scope = par_dict['dynamic']['scope'][name]
            else:
                scope = 'item'
            par.set_dynamic(trial_type, scope, {name: val})
    par.set_sublayers(par_dict['sublayers'])
    for connect, p in par_dict['weights'].items():
        weight_dict = {decode_region(region): expr for region, expr in p.items()}
        par.set_weights(connect, weight_dict)
    for layer, sublayer_param in par_dict['sublayer_param'].items():
        for sublayer, param in sublayer_param.items():
            par.set_sublayer_param(layer, sublayer, param)
    return par


class CMRParameters(Parameters):
    """
    Configuration of CMR model parameters.

    Attributes
    ----------
    fixed : dict of (str: float)
        Values of fixed parameters.

    free : dict of (str: tuple)
        Bounds of each free parameter.

    dependent : dict of (str: str)
        Expressions to define dependent parameters based the other
        parameters.

    dynamic : dict of (str: dict of (str: str))
        First dict specifies trial_type for dynamic parameters,
        second dict keys are parameter names, and values are
        expressions specifying how to update the parameter.

    sublayers : dict of (list of str)
        Names of sublayers for each layer in the network.

    weights : dict of (tuple of (tuple of str)): str
        Weights template to set network connections. Weights are
        indicated by region within the network. Each region is
        specified with a tuple giving names of sublayers and segments:
        ((f_sublayer, f_segment), (c_sublayer, c_segment)). The value
        for each region should be an expression to be evaluated with
        patterns and/or parameters.

    sublayer_param : dict of (str: dict of (str: dict of str))
        Parameters that vary by sublayer. These parameters are
        specified in terms of their layer and sublayer. Each value
        should contain an expression to be evaluated with parameters.
    """

    def __init__(self) -> None:
        super().__init__()
        self.options: dict[str, Any] = {
            'distraction': False, 'scope': 'list', 'filter_recalls': False
        }
        self.fixed: dict[str, float] = {}
        self.free: dict[str, Iterable[float]] = {}
        self.dependent: dict[str, str] = {}
        self.dynamic: dict[str, dict[str, str]] = {}
        self.sublayers: dict[str, list[str]] = {}
        self.weights: dict[str, dict[Region, str]] = {}
        self.sublayer_param: dict[str, dict[str, dict[str, str]]] = {}
        self._fields.extend(['options', 'sublayers', 'weights', 'sublayer_param'])

    def to_json(self, json_file: str) -> None:
        """
        Write parameter definitions to a JSON file.

        Parameters
        ----------
        json_file : str
            Path to file to save json data.
        """
        data: dict[str, Any] = {
            'options': self.options,
            'fixed': self.fixed,
            'free': self.free,
            'dependent': self.dependent,
            'dynamic': self.dynamic,
            'sublayers': self.sublayers,
            'weights': {},
            'sublayer_param': self.sublayer_param,
        }
        for layer, regions in self.weights.items():
            data['weights'][layer] = {}
            for region, expr in regions.items():
                region_str = encode_region(region)
                data['weights'][layer][region_str] = expr
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=4)

    def set_sublayers(self, *args: dict[str, list[str]], **kwargs: list[str]) -> None:
        """
        Set layers and sublayers of a network.

        Examples
        --------
        >>> from cymr.cmr import CMRParameters
        >>> param_def = CMRParameters()
        >>> param_def.set_sublayers(f=['task'], c=['task'])
        """
        self.sublayers.update(*args, **kwargs)

    def set_weights(
        self, connect: str, regions: dict[Region, str]
    ) -> None:
        """
        Set weights on model patterns.

        Parameters
        ----------
        connect : str
            Network connection to set weights for.

        regions : dict of (tuple of (tuple of str)): str
            Weights for each region to set.

        Examples
        --------
        >>> from cymr.cmr import CMRParameters
        >>> param_def = CMRParameters()
        >>> region = (('f_sub', 'f_reg'), ('c_sub', 'c_reg'))
        >>> param_def.set_weights('fc', {region: 'b * pattern'})
        """
        if connect in self.weights:
            self.weights[connect].update(regions)
        else:
            self.weights[connect] = regions

    def eval_weights(
        self,
        patterns: dict[str, dict[str, Any]],
        param: Optional[dict[str, float]] = None,
        item_index: Optional[Any] = None
    ) -> dict[str, dict[Region, ArrayLike]]:
        """
        Evaluate weights based on parameters and patterns.

        Parameters
        ----------
        patterns : dict of str: (dict of str: numpy.ndarray)
            Patterns to use when evaluating weights.

        param : dict, optional
            Parameters to use when evaluating weights.

        item_index : numpy.ndarray, optional
            Item indices to include in the patterns.

        Returns
        -------
        weights : dict of str: (dict of str: numpy.ndarray)
            Weight matrices for each region in each connection matrix.
        """
        weights: dict[str, dict[Region, ArrayLike]] = {}
        for connect, regions in self.weights.items():
            # get necessary patterns
            weights[connect] = {}
            if connect in ['fc', 'cf']:
                layer_type = 'vector'
            elif connect == 'ff':
                layer_type = 'similarity'
            else:
                raise ValueError(f'Invalid connection: {connect}.')
            data = patterns[layer_type].copy()

            # filter by item index
            if item_index is not None:
                for feature, mat in data.items():
                    if layer_type == 'vector':
                        data[feature] = mat[item_index, :]
                    else:
                        data[feature] = mat[np.ix_(item_index, item_index)]

            # evaluate expressions to get weights
            if param is not None:
                data.update(param)
            for region, expr in regions.items():
                weights[connect][region] = eval(expr, np.__dict__, data)
        return weights

    def set_sublayer_param(
        self, layer: str, sublayer: str, *args: dict[str, str], **kwargs: str
    ) -> None:
        """
        Set sublayer parameters.

        Parameters
        ----------
        layer : str
            Layer containing the sublayer to set.

        sublayer : str
            Sublayer to set parameters for.

        Examples
        --------
        >>> from cymr.cmr import CMRParameters
        >>> param_def = CMRParameters()
        >>> param_def.set_sublayer_param('c', 'sub1', a='2 * d'})
        >>> param_def.set_sublayer_param('c', 'sub1', {'b': 'exp(f)'})
        """
        if layer in self.sublayer_param:
            if sublayer in self.sublayer_param[layer]:
                self.sublayer_param[layer][sublayer].update(*args, **kwargs)
            else:
                self.sublayer_param[layer][sublayer] = dict(*args, **kwargs)
        else:
            self.sublayer_param[layer] = {sublayer: dict(*args, **kwargs)}

    def eval_sublayer_param(
        self, 
        layer: str, 
        param: dict[str, Any], 
        n_trial: int = None,
        sublayer_params: list[str] = None, 
    ) -> dict[str, Union[float, ArrayLike]]:
        """
        Evaluate sublayer parameters.

        Parameters
        ----------
        layer : str
            Layer to evaluate.

        param : dict
            Parameters to use when evaluating sublayer parameters.

        n_trial : int, optional
            Number of trials. If indicated, parameters will be tiled
            over all trials.

        sublayer_params : list of str, optional
            Parameters to evaluate. If not specified, all sublayer
            parameters will be evaluated.

        Returns
        -------
        eval_param : dict
            Input parameters with sublayer-specific parameters set.
        """
        eval_param = param.copy()

        # get parameter values for each sublayer
        param_lists: dict[str, list[ArrayLike]] = {}
        for sublayer in self.sublayers[layer]:
            if sublayer_params is None:
                names = self.sublayer_param[layer][sublayer].keys()
            else:
                names = sublayer_params

            for par in names:
                if par not in self.sublayer_param[layer][sublayer]:
                    continue
                expr = self.sublayer_param[layer][sublayer][par]
                if par not in param_lists:
                    param_lists[par] = []
                if isinstance(expr, str):
                    value = eval(expr, np.__dict__, param)
                else:
                    value = expr
                param_lists[par].append(value)

        # prepare parameter arrays
        for par, values in param_lists.items():
            if any([isinstance(v, np.ndarray) for v in values]):
                size = (max([v.size for v in values if isinstance(v, np.ndarray)]),)
                eval_param[par] = np.asarray(
                    [network.expand_param(v, size) for v in values]
                ).T
            elif n_trial is not None:
                eval_param[par] = np.tile(np.asarray(values), (n_trial, 1))
            else:
                eval_param[par] = np.array(values)
        return eval_param
    
    def expand_param(self, param, names, n_item=1, n_sub=1):
        """Expand parameters to a specified size."""
        expanded = param.copy()
        size = (n_item, n_sub)
        for name in names:
            if name not in param:
                continue
            expanded[name] = network.expand_param(param[name], size)
        return expanded


def primacy(n_item, L, P1, P2):
    """
    Primacy gradient in learning rate.

    Parameters
    ----------
    n_item : int
        Number of items in study list.

    L : float, numpy.ndarray
        Base learning rate. Asymptote of gradient for later positions.
        May vary by trial (row) and/or sublayer (column).

    P1 : float
        Additional learning for first item.

    P2 : float
        Decay rate for primacy gradient.

    Returns
    -------
    rate : numpy.array
        Learning rate for each serial position (and sublayer).
    """
    position = np.arange(n_item)[:, np.newaxis]
    rate = L + (P1 * np.exp(-P2 * position))
    return rate


def p_stop_op(n_item, X1, X2, pmin=0.000001):
    """
    Probability of stopping based on output position.

    Parameters
    ----------
    n_item : int
        Number of items available for recall.

    X1 : float
        Probability of not recalling any items.

    X2 : float
        Shape parameter of exponential function increasing stop
        probability by output position.

    pmin : float, optional
        Minimum probability of stopping recall at any position.

    Returns
    -------
    p_stop : numpy.array
        Probability of stopping for each output position.
    """
    p_stop = X1 * np.exp(X2 * np.arange(n_item + 1))
    p_stop[p_stop < pmin] = pmin
    p_stop[p_stop > (1 - pmin)] = 1 - pmin

    # after recalling all items, P(stop)=1 by definition
    p_stop[-1] = 1
    return p_stop


def config_loc_cmr(n_item):
    """
    Configure a localist CMR network.

    Parameters
    ----------
    n_item : int
        Number of item patterns to include in the network

    Returns
    -------
    param_def : cymr.parameters.Parameters
        Parameters object with configuration for the network.

    patterns : dict
        Patterns to place in the network.
    """
    items = np.arange(n_item)
    patterns = {'items': items, 'vector': {'loc': np.eye(n_item)}}
    param_def = CMRParameters()
    param_def.set_sublayers(f=['task'], c=['task'])
    param_def.set_weights(
        'fc', {(('task', 'item'), ('task', 'item')): 'Afc + Dfc * loc'}
    )
    param_def.set_weights(
        'cf', {(('task', 'item'), ('task', 'item')): 'Acf + Dcf * loc'}
    )
    return param_def, patterns


def init_network(param_def, patterns, param, item_index, index_segments=None):
    """
    Initialize a network with pattern weights.

    Parameters
    ----------
    param_def : cymr.cmr.CMRParameters
        Parameters definition defining network sublayers and weights.

    patterns : dict
        Patterns to place in the network.

    param : dict of (str: float)
        Parameter values; used to initialize network weights.

    item_index : numpy.array
        Indices of item patterns to include in the network.

    index_segments : list of str
        Context units of these segments will be indexed by item_index,
        sorting them in that order and excluding items not in the pool.

    Returns
    -------
    net : cymr.network.Network
        Network initialized with pre-experimental weights.
    """
    # set item weights
    weights = param_def.eval_weights(patterns, param, item_index)

    if index_segments is not None:
        # filter item context units to remove unused items
        for connect in ['fc', 'cf']:
            for region, mat in weights[connect].items():
                if region[1] in index_segments:
                    weights[connect][region] = mat[:, item_index]

    # set task units
    for f_sublayer in param_def.sublayers['f']:
        for c_sublayer in param_def.sublayers['c']:
            region = ((f_sublayer, 'start'), (c_sublayer, 'start'))
            weights['fc'][region] = np.array([[1]])
            weights['cf'][region] = np.array([[1]])

    if param_def.options['distraction']:
        # add distraction units
        n_distract = len(item_index) + 1
        for f_sublayer in param_def.sublayers['f']:
            for c_sublayer in param_def.sublayers['c']:
                region = ((f_sublayer, 'distract'), (c_sublayer, 'distract'))
                weights['fc'][region] = np.eye(n_distract)
                weights['cf'][region] = np.eye(n_distract)

    # get all segment definitions
    f_segments = {}
    c_segments = {}
    for region, mat in weights['fc'].items():
        f_region, c_region = region
        f_sublayer, f_segment = f_region
        c_sublayer, c_segment = c_region
        if f_sublayer not in f_segments:
            f_segments[f_sublayer] = {}
        if c_sublayer not in c_segments:
            c_segments[c_sublayer] = {}
        f_segments[f_sublayer][f_segment] = mat.shape[0]
        c_segments[c_sublayer][c_segment] = mat.shape[1]

    # initialize the network
    net = network.Network(f_segments, c_segments)
    for connect in weights.keys():
        for region, mat in weights[connect].items():
            if connect == 'ff':
                f_segment = region
                c_segment = None
            else:
                f_segment, c_segment = region
            net.add_pre_weights(connect, f_segment, c_segment, mat)
    return net


def study_list(param_def, param, item_index, item_input, patterns, item_distract):
    """
    Simulate study of a list.

    Parameters
    ----------
    param_def : cymr.cmr.CMRParameters
        Parameters definition defining network sublayers and weights.

    param : dict of (str: float)
        Parameter values; used to set context evolution and learning.

    item_index : numpy.array
        Indices of presented item patterns.

    item_input : numpy.array
        Input position of presented items.

    patterns : dict
        Item pattern vectors.
    
    item_distract : numpy.array
        Indices of distraction items.

    Returns
    -------
    net : cymr.network.Network
        Network after simulation of the study phase.
    """
    net = init_network(param_def, patterns, param, item_index)
    net.update(('task', 'start', 0), net.c_sublayers)
    if param_def.options['distraction']:
        net.study_distract(
            ('task', 'item'),
            item_input,
            net.c_sublayers,
            param['B_enc'],
            param['Lfc'],
            param['Lcf'],
            ('task', 'distract'),
            item_distract,
            param['B_distract'],
            param['B_retention'],
        )
    else:
        net.study(
            ('task', 'item'),
            item_input,
            net.c_sublayers,
            param['B_enc'],
            param['Lfc'],
            param['Lcf'],
        )
    B_start = param['B_start']
    if isinstance(B_start, np.ndarray) and B_start.ndim == 2:
        B_start = B_start[0]
    net.integrate(('task', 'start', 0), net.c_sublayers, B_start)
    return net


def prepare_list_param(n_item, n_sub, param, param_def, n_recall=None):
    """
    Prepare parameters that vary within list.

    Parameters
    ----------
    n_item : int
        Number of items in the list.
    
    n_sub : int
        Number of sublayers of context.

    param : dict of (str: float)
        Parameter values.

    param_def : cymr.cmr.CMRParameters
        Parameter definitions indicating sublayer parameters.

    n_recall : int
        Number of recalls in the list.

    Returns
    -------
    list_param : dict
        Parameters prepared for changes between sublayer and trials.
    """
    if 'c' in param_def.sublayer_param:
        # evaluate sublayer parameters
        eval_param = param_def.eval_sublayer_param('c', param, n_trial=1)
    else:
        eval_param = param

    # expand trial-specific parameters
    item_params = ['Lfc', 'Lcf', 'B_enc', 'B_distract']
    list_param = param_def.expand_param(eval_param, item_params, n_item, n_sub)
    if n_recall is not None:
        list_param = param_def.expand_param(list_param, ['B_rec'], n_recall, n_sub)

    # apply primacy gradient to Lcf
    list_param['Lcf'] = primacy(
        n_item, list_param['Lcf'], eval_param['P1'], eval_param['P2']
    )

    # determine P(stop) by output position
    list_param['p_stop'] = p_stop_op(n_item, param['X1'], param['X2'])
    return list_param


def get_list_items(item_index, study, recall, list_ind, scope):
    """Get item units to present given the paradigm."""
    if scope == 'list':
        item_pool = study['item_index'][list_ind]
        item_study = study['input'][list_ind]
        item_recall = recall['input'][list_ind]
        item_distract = np.arange(len(item_study) + 1)
    elif scope == 'pool':
        item_pool = item_index
        item_study = study['item_index'][list_ind]
        item_recall = recall['item_index'][list_ind]
        item_distract = np.arange(len(item_study) + 1)
    else:
        raise ValueError(f'Invalid scope: {scope}')
    return item_pool, item_study, item_recall, item_distract


class CMR(Recall):
    """
    Context Maintenance and Retrieval model.

    **Model Parameters**

    Lfc : float
        Learning rate of item-context weights.

    Lcf : float
        Learning rate of context-item weights.

    P1 : float
        Additional context-item learning for first item.

    P2 : float
        Decay rate for primacy learning rate gradient.

    B_enc : float
        Integration rate during encoding.
    
    B_distract : float
        Integration rate of distraction units before each item 
        presentation. Only used if the "distraction" option is set
        to True.
    
    B_retention : float
        Integration rate of distraction units after the last
        item presentation. Only used if the "distraction" option is set
        to True.

    B_start : float
        Integration rate of start context reinstatement.

    B_rec : float
        Integration rate during recall.

    X1 : float
        Probability of not recalling any items.

    X2 : float
        Shape parameter of exponential function increasing stop
        probability by output position.

    **Parameter definition objects**

    Parameters objects are used to indicate sublayers to include
    in the network and to indicate how network weights should be
    initialized. The :code:`sublayers` and :code:`weights` attributes
    must be set.

    Parameters objects may also be used to define parameters that depend
    on other parameters and/or dynamic parameters that depend on columns
    of the input data.

    Finally, Parameters objects are used to define searches, using the
    :code:`fixed` and :code:`free` attributes.

    **Model Patterns**

    Patterns are used to define connections between the item and
    context layers and direct connections between items. Connections
    may be orthonormal as in many published variants of CMR, or they
    may be distributed, overlapping patterns.

    Patterns may include :code:`'vector'` and/or :code:`'similarity'` matrices.
    Vector representations are used to set the :math:`M^{FC}_{pre}`
    and :math:`M^{CF}_{pre}` matrices, while similarity matrices are
    used to set the :math:`M^{FF}_{pre}` matrix.

    Vector and similarity values are dicts of (feature: array) specifying
    an array for one or more named features, with an
    [items x units] array for vector representations, or
    [items x items] for similarity matrices.
    """

    def prepare_sim(self, data, study_keys=None, recall_keys=None):
        study_base = ['input', 'item_index']
        if study_keys is None:
            study_keys = study_base
        else:
            # only add the base key if it isn't already in there
            for term in study_base:
                if term not in study_keys:
                    study_keys += [term]
        recall_base = ['input', 'item_index']
        if recall_keys is None:
            recall_keys = recall_base
        else:
            for term in recall_base:
                if term not in recall_keys:
                    recall_keys += [term]

        study, recall = fit.prepare_lists(
            data, study_keys=study_keys, recall_keys=recall_keys, clean=True
        )
        return study, recall

    def likelihood_subject(self, study, recall, param, param_def=None, patterns=None):
        n_list = len(study['input'])
        if param_def is None:
            raise ValueError('Must provide a Parameters object.')
        n_sub = len(param_def.sublayers['c'])

        item_index = np.arange(len(patterns['items']))
        logl = 0
        n = 0
        for i in range(n_list):
            item_pool, item_study, item_recall, item_distract = get_list_items(
                item_index, study, recall, i, param_def.options['scope']
            )
            n_item = len(item_study)
            n_recall = len(item_recall)
            
            # access the dynamic parameters needed for this list
            list_param = param.copy()
            list_param = param_def.get_dynamic(list_param, i)
            list_param = param_def.eval_dependent(list_param)
            list_param = prepare_list_param(
                n_item, n_sub, list_param, param_def, n_recall
            )

            # simulate study
            net = study_list(
                param_def, list_param, item_pool, item_study, patterns, item_distract
            )

            # get recall probabilities
            p = net.p_recall(
                ('task', 'item'),
                item_recall,
                net.c_sublayers,
                list_param['B_rec'],
                list_param['T'],
                list_param['p_stop'],
            )
            n += p.size
            if np.any(np.isnan(p)):
                # if any response probability is undefined, so is the
                # overall likelihood
                logl = np.nan
                break

            # ensure probabilities are not zero before log transform
            p = np.clip(p, 10e-6, 1)
            logl += np.sum(np.log(p))
        return logl, n

    def generate_subject(
        self, study, recall, param, param_def=None, patterns=None, **kwargs
    ):
        n_list = len(study['input'])
        if param_def is None:
            raise ValueError('Must provide a Parameters object.')
        n_sub = len(param_def.sublayers['c'])

        item_index = np.arange(len(patterns['items']))
        recalls_list = []
        for i in range(n_list):
            item_pool, item_study, item_recall, item_distract = get_list_items(
                item_index, study, recall, i, param_def.options['scope']
            )
            n_item = len(item_study)

            # access the dynamic parameters needed for this list
            list_param = param.copy()
            list_param = param_def.get_dynamic(list_param, i)
            list_param = param_def.eval_dependent(list_param)
            list_param = prepare_list_param(n_item, n_sub, list_param, param_def)

            # simulate study
            net = study_list(
                param_def, list_param, item_pool, item_study, patterns, item_distract
            )

            # simulate recall
            if param_def.options['filter_recalls']:
                recall_index = net.generate_recall(
                    ('task', 'item'),
                    net.c_sublayers,
                    list_param['B_rec'],
                    list_param['T'],
                    list_param['p_stop'],
                    filter_recalls=True,
                    A1=list_param['A1'],
                    A2=list_param['A2'],
                )
            else:
                recall_index = net.generate_recall(
                    ('task', 'item'),
                    net.c_sublayers,
                    list_param['B_rec'],
                    list_param['T'],
                    list_param['p_stop'],
                )

            items = patterns['items'][item_pool]
            recall_items = items[recall_index]
            recalls_list.append(recall_items)
        return recalls_list

    def record_subject(
        self,
        study,
        recall,
        param,
        param_def=None,
        patterns=None,
        index_segments=None,
        include=None,
        exclude=None,
    ):
        n_list = len(study['input'])
        if param_def is None:
            raise ValueError('Must provide a Parameters object.')
        n_sub = len(param_def.sublayers['c'])

        study_state = []
        recall_state = []
        item_index = np.arange(len(patterns['items']))
        for i in range(n_list):
            item_pool, item_study, item_recall, item_distract = get_list_items(
                item_index, study, recall, i, param_def.options['scope']
            )
            n_item = len(item_study)
            n_recall = len(item_recall)

            # access the dynamic parameters needed for this list
            list_param = param.copy()
            list_param = param_def.get_dynamic(list_param, i)
            list_param = param_def.eval_dependent(list_param)
            list_param = prepare_list_param(
                n_item, n_sub, list_param, param_def, n_recall
            )

            # initialize the network
            net = init_network(
                param_def,
                patterns,
                list_param,
                study['item_index'][i],
                index_segments=index_segments,
            )
            net.update(('task', 'start', 0), net.c_sublayers)

            # record study phase
            if param_def.options['distraction']:
                distract_segment = ('task', 'distract')
                distract_B = list_param['B_distract']
                retention_B = list_param['B_retention']
            else:
                distract_segment = None
                distract_B = None
                retention_B = None

            list_study_state = net.record_study(
                ('task', 'item'),
                item_study,
                net.c_sublayers,
                list_param['B_enc'],
                list_param['Lfc'],
                list_param['Lcf'],
                distract_segment=distract_segment,
                distract_list=item_distract,
                distract_B=distract_B,
                retention_B=retention_B,
                include=include,
                exclude=exclude,
            )
            B_start = list_param['B_start']
            if isinstance(B_start, np.ndarray) and B_start.ndim == 2:
                B_start = B_start[0]
            net.integrate(('task', 'start', 0), net.c_sublayers, B_start)

            # record recall phase
            list_recall_state = net.record_recall(
                ('task', 'item'),
                recall['input'][i],
                net.c_sublayers,
                list_param['B_rec'],
                list_param['T'],
                include=include,
                exclude=exclude,
            )
            study_state.append(list_study_state)
            recall_state.append(list_recall_state)
        return study_state, recall_state
