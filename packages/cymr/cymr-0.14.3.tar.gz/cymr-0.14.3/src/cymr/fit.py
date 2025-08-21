"""Simulate free recall experiments."""

from importlib import resources
from abc import ABC, abstractmethod
import numpy as np
from scipy import optimize
import pandas as pd
from joblib import Parallel, delayed
from psifr import fr

from cymr import parameters


def sample_data(study):
    """Read sample data."""
    ref = resources.files("cymr").joinpath(f"data/{study}.csv")
    with resources.as_file(ref) as data_file:
        df = pd.read_csv(data_file)
    return df


def prepare_lists(data, study_keys=None, recall_keys=None, clean=True):
    """
    Prepare study and recall data for simulation.

    Return data information split by list. This format is similar to
    frdata structs used in EMBAM.

    Parameters
    ----------
    data : pandas.DataFrame
        Free recall data in Psifr format.

    study_keys : list of str, optional
        Columns to export for study list data. Default is:
        ['input', 'item_index']. Input position is assumed to be
        one-indexed.

    recall_keys : list of str, optional
        Columns to export for recall list data. Default is:
        ['input', 'item_index']. Input position is assumed to be
        one-indexed.

    clean : bool, optional
        If true, repeats and intrusions will be removed.

    Returns
    -------
    study : dict of (str: list of numpy.array)
        Study columns in list format.

    recall : dict of (str: list of numpy.array)
        Recall columns in list format.
    """
    if study_keys is None:
        study_keys = ['input', 'item_index']

    if recall_keys is None:
        recall_keys = ['input', 'item_index']

    s_keys = study_keys.copy()
    s_keys.remove('input')
    r_keys = recall_keys.copy()
    r_keys.remove('input')
    if 'item_index' in r_keys:
        r_keys.remove('item_index')
    merged = fr.merge_free_recall(data, study_keys=s_keys, recall_keys=r_keys)
    if clean:
        merged = merged.query('~intrusion and repeat == 0')

    study = fr.split_lists(merged, 'study', study_keys)
    recall = fr.split_lists(merged, 'recall', recall_keys)

    for i in range(len(study['input'])):
        if 'input' in study_keys:
            study['input'][i] = study['input'][i].astype(int) - 1
        if 'item_index' in study_keys:
            study['item_index'][i] = study['item_index'][i].astype(int)

        if 'input' in recall_keys:
            recall['input'][i] = recall['input'][i].astype(int) - 1
        if 'item_index' in recall_keys:
            recall['item_index'][i] = recall['item_index'][i].astype(int)

    n = np.unique([len(items) for items in study['input']])
    if len(n) > 1:
        raise ValueError('List length must not vary.')
    return study, recall


def prepare_study(study_data, study_keys=None):
    """
    Prepare study phase data for simulation.

    Parameters
    ----------
    study_data : pandas.DataFrame
        Study list data. Position is assumed to be one-indexed.

    study_keys : list of str
        Columns to export to split list format.

    Returns
    -------
    study : dict of (str: numpy.array)
        Study columns in split list format.
    """
    if study_keys is None:
        study_keys = ['position', 'item_index']

    study = fr.split_lists(study_data, 'raw', study_keys)
    for i in range(len(study['position'])):
        if 'position' in study_keys:
            study['position'][i] = study['position'][i].astype(int) - 1
        if 'item_index' in study_keys:
            study['item_index'][i] = study['item_index'][i].astype(int)
    return study


def add_recalls(study, recalls_list):
    """
    Add recall sequences to a study DataFrame.

    Parameters
    ----------
    study : pandas.DataFrame
        Study list data.

    recalls_list : list of numpy.array
        Recalled items for each list in output order.

    Returns
    -------
    data : pandas.DataFrame
        Complete free recall DataFrame suitable for analysis.
    """
    lists = study['list'].unique()
    subjects = study['subject'].unique()
    if len(subjects) > 1:
        raise ValueError('Unpacking multiple subjects not supported.')
    subject = subjects[0]

    # initialize recall trials DataFrame
    n_recall = np.sum([len(r) for r in recalls_list])
    recall = pd.DataFrame(
        {
            'subject': subject,
            'list': np.zeros(n_recall, dtype=int),
            'trial_type': 'recall',
            'position': np.zeros(n_recall, dtype=int),
            'item': '',
        }
    )

    # set basic information (list, item, position)
    n = 0
    for i, seq in enumerate(recalls_list):
        for j, item in enumerate(seq):
            recall.loc[n, 'list'] = lists[i]
            recall.loc[n, 'item'] = item
            recall.loc[n, 'position'] = j + 1
            n += 1
    data = pd.concat((study, recall), axis=0, ignore_index=True)
    data = data.sort_values(['list', 'trial_type'], ascending=[True, False])
    return data


def get_best_results(results):
    """Get best results from a repeated search."""
    df = []
    subjects = results.index.get_level_values('subject').unique()
    for subject in subjects:
        res = results.loc[subject].reset_index()
        subject_best = res.loc[[res['logl'].argmax()]]
        df.append(subject_best)
    best = pd.concat(df, axis=0)
    best.index = subjects
    best.index.rename('subject', inplace=True)
    return best


class Recall(ABC):
    """
    Base class for evaluating a model of free recall.

    Common Parameters
    -----------------
    study : pandas.DataFrame
        Study list information.

    recall : pandas.DataFrame
        Recall period information for each list.

    param : dict
        Model parameter values.

    patterns : dict
        May include keys: 'vector' and/or 'similarity'. Vectors are
        used to set distributed model representations. Similarity
        matrices are used to set item connections. Vector and
        similarity values are dicts of (feature: array) specifying
        an array for one or more named features, with an
        [items x units] array for vector representations, or
        [items x items] for similarity matrices.
    """

    @abstractmethod
    def prepare_sim(self, subject_data, study_keys=None, recall_keys=None):
        """
        Prepare data for simulation.

        Exporting data in DataFrame format to list format for
        simulation takes time, so this is only done once before running
        a parameter search.

        Parameters
        ----------
        subject_data : pandas.DataFrame
            Data for one subject.

        study_keys : list of str
            Data columns to include in the study data.

        recall_keys : list of str
            Data columns to include in the recall data.

        Returns
        -------
        study : dict of (str: list of numpy.array)
            Information about the study phase in list format.

        recall : dict of (str: list of numpy.array)
            Information about recalled items in list format.
        """
        pass

    def prepare_subject(
        self,
        subject,
        data,
        group_param,
        subj_param=None,
        param_def=None,
        study_keys=None,
        recall_keys=None,
    ):
        """
        Prepare parameters and data for a subject.

        Parameters
        ----------
        subject : str or int
            Identifier for the subject to be simulated.

        data : pandas.DataFrame
            Full dataset with all subjects.

        group_param : dict of (str: float)
            Values of parameters that apply to all subjects.

        subj_param : dict of (str: dict of (str: float)), optional
            Values of subject parameters, indexed by subject ID.

        param_def : cymr.parameters.Parameters, optional
            Parameter definition object specifying dependent and
            dynamic parameters.

        study_keys : list of str, optional
            Columns to export for study list data.

        recall_keys : list of str, optional
            Columns to export for recall list data.

        Returns
        -------
        study : dict of (str: list of numpy.array)
            Study columns in list format.

        recall : dict of (str: list of numpy.array)
            Recall columns in list format.

        param : dict of (str: float or numpy.array)
            Parameters with dependent and dynamic parameters evaluated.
        """
        param = group_param.copy()
        if subj_param is not None:
            param.update(subj_param[subject])

        # filter the data events for this subject
        subject_data = data.loc[data['subject'] == subject]

        # convert subject dataframe to list format
        study, recall = self.prepare_sim(
            subject_data, study_keys=study_keys, recall_keys=recall_keys
        )

        # evaluate dependent and dynamic parameters
        if param_def is not None:
            param = param_def.eval_dependent(param)
            param = param_def.eval_dynamic(param, study, recall)
        return study, recall, param

    @abstractmethod
    def likelihood_subject(self, study, recall, param, param_def=None, patterns=None):
        """
        Log likelihood of data for one subject based on a given model.

        Parameters
        ----------
        study : dict of (str: list of numpy.array)
            Information about the study phase in list format.

        recall : dict of (str: list of numpy.array)
            Information about recalled items in list format.

        param : dict of (str: float)
            Model parameter values.

        param_def : cymr.parameters.Parameters, optional
            Parameter definition object; used to interpret parameters.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        Returns
        -------
        logl : float
            Total log likelihood of data for this subject.

        n : int
            Number of evaluated data points.
        """
        pass

    def eval_model_stats(
        self, 
        data, 
        study, 
        recall, 
        param, 
        param_def, 
        patterns, 
        stats_def, 
        stats_data,
        n_stats_rep=1,
    ):
        """
        Simulate data and evaluate fit to summary statistics.

        Parameters
        ----------
        data : pandas.DataFrame
            Data for one subject.

        study : dict of (str: list of numpy.array)
            Information about the study phase in list format.

        recall : dict of (str: list of numpy.array)
            Information about recall trials in list format.

        param : dict of (str: float)
            Model parameter values.

        param_def : cymr.parameters.Parameters
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        stats_def : cymr.statistics.Statistics
            Statistics to use when evaluating the model fit. If None,
            will evaluate based on likelihood.

        stats_data : pandas.DataFrame
            Summary statistics for the comparison data. Must have been
            evaluated using the same stat_def.
        
        n_stats_rep : int, optional
            Number of times to replicate generation and stat 
            evaluation.
        """
        stats_fit_rep = []
        for i in range(n_stats_rep):
            # generate simulated data
            recalls_list = self.generate_subject(study, recall, param, param_def, patterns)
            study_data = data[data['trial_type'] == 'study']
            full_data = add_recalls(study_data, recalls_list)

            # calculate summary stats
            merged = fr.merge_free_recall(full_data)
            stats_fit, _ = stats_def.eval_stats(merged)
            stats_fit_rep.append(stats_fit)

        # calculate mean over replications        
        reps = list(range(n_stats_rep))
        group_vars = ["stat", "point", "conditions", "subject", "independent"]
        stats_mean = (
            pd.concat(stats_fit_rep, axis=0, keys=reps, names=["rep", "point"])
            .groupby(group_vars)["dependent"]
            .mean()
            .reset_index()
        )

        # compare to data being fitted
        error_stat = stats_def.compare_stats(stats_data, stats_mean)
        return error_stat


    def likelihood(
        self,
        data,
        group_param,
        subj_param=None,
        param_def=None,
        patterns=None,
        study_keys=None,
        recall_keys=None,
    ):
        """
        Log likelihood summed over all subjects.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to fit. Must include a 'subject' column.

        group_param : dict of (str: float)
            Parameters that are fixed at the group level.

        subj_param : dict of (str: dict of (str: float))
            Parameters that vary by subject, indexed by subject.

        param_def : cymr.parameters.Parameters
            Parameter definitions (used to set dependent and dynamic).

        patterns : dict of (str: dict of (str: numpy.array))
            Patterns to use in the model.

        study_keys : list of str
            Fields to include in study data.

        recall_keys : list of str
            Fields to include in recall data.

        Returns
        -------
        stats : pandas.DataFrame
            Statistics related to model fitness. Includes logl, the
            log likelihood for each subject, and n, the number of data
            points for each subject.
        """
        # get the list of subjects
        subjects = data['subject'].unique()
        logl = np.empty(len(subjects))
        n = np.empty(len(subjects), int)
        for i, subject in enumerate(subjects):
            # prepare subject for simulation
            study, recall, param = self.prepare_subject(
                subject,
                data,
                group_param,
                subj_param,
                param_def,
                study_keys,
                recall_keys,
            )

            # run subject-specific likelihood function
            subject_logl, subject_n = self.likelihood_subject(
                study, recall, param, param_def=param_def, patterns=patterns
            )
            logl[i] = subject_logl
            n[i] = subject_n
        results = pd.DataFrame({'logl': logl, 'n': n}, index=subjects)
        results.index.rename('subject', inplace=True)
        return results

    def fit_subject(
        self, 
        subject_data, 
        param_def, 
        patterns=None, 
        study_keys=None, 
        recall_keys=None, 
        stats_def=None, 
        n_stats_rep=1,
        method='de', 
        **kwargs,
    ):
        """
        Fit a model to data for one subject.

        Parameters
        ----------
        subject_data : pandas.DataFrame
            Data for one subject.

        param_def : cymr.parameters.Parameters
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        study_keys : list of str
            Fields to include in study data.

        recall_keys : list of str
            Fields to include in recall data.

        stats_def : cymr.statistics.Statistics
            Statistics to use when evaluating the model fit. If None,
            will evaluate based on likelihood.
        
        n_stats_rep : int, optional
            Number of times to replicate generation and stat 
            evaluation.

        method : str, optional
            Search method for fitting the parameters.

        kwargs
            Additional keyword arguments for the search method.

        Returns
        -------
        param : dict of (str: float)
            Best-fitting parameters, including fixed, free, and
            dependent parameters.

        logl : float
            Log likelihood for the best-fitting parameters.

        n : int
            Number of data points evaluated.

        k : int
            Number of free parameters.
        """
        study, recall = self.prepare_sim(subject_data, study_keys, recall_keys)
        var_names = list(param_def.free.keys())
        if stats_def is not None:
            # evaluate stats on data to fit
            subject_merged = fr.merge_free_recall(subject_data)
            stats_data, _ = stats_def.eval_stats(subject_merged)

        def eval_fit(x):
            eval_param = param_def.fixed.copy()
            eval_param.update(dict(zip(var_names, x)))
            eval_param = param_def.eval_dependent(eval_param)
            eval_param = param_def.eval_dynamic(eval_param, study, recall)
            
            if stats_def is not None:
                # generate data, calculate stats, compare to data stats
                error_stat = self.eval_model_stats(
                    subject_data, 
                    study, 
                    recall, 
                    eval_param, 
                    param_def, 
                    patterns, 
                    stats_def, 
                    stats_data,
                    n_stats_rep,
                )
            else:
                # calculate log likelihood of recall sequences
                eval_logl, _ = self.likelihood_subject(
                    study, recall, eval_param, param_def, patterns
                )
                if np.isnan(eval_logl):
                    eval_logl = -10e6
                error_stat = -eval_logl
            return error_stat

        group_lb = [param_def.free[k][0] for k in var_names]
        group_ub = [param_def.free[k][1] for k in var_names]
        bounds = optimize.Bounds(group_lb, group_ub)
        if method == 'de':
            res = optimize.differential_evolution(eval_fit, bounds, **kwargs)
        elif method == 'shgo':
            b = [(lb, ub) for lb, ub in zip(bounds.lb, bounds.ub)]
            res = optimize.shgo(eval_fit, b, **kwargs)
        else:
            raise ValueError(f'Invalid method: {method}')

        # get fitted parameters
        param = param_def.fixed.copy()
        param.update(dict(zip(var_names, res['x'])))
        param = param_def.eval_dependent(param)
        param_dynamic = param_def.eval_dynamic(param, study, recall)

        # evaluate fitted parameters, get number of fitted points
        if stats_def is not None:
            fit_stat = self.eval_model_stats(
                subject_data, 
                study, 
                recall, 
                param_dynamic, 
                param_def, 
                patterns, 
                stats_def, 
                stats_data,
                n_stats_rep,
            )
            n = sum(len(r) + 1 for r in recall['input'])
        else:
            logl, n = self.likelihood_subject(
                study, recall, param_dynamic, param_def, patterns
            )
            assert logl == -res['fun']
            fit_stat = logl
        k = len(param_def.free)
        return param, fit_stat, n, k

    def _run_fit_subject(
        self, 
        data, 
        subject, 
        param_def, 
        patterns=None, 
        study_keys=None, 
        recall_keys=None, 
        stats_def=None, 
        n_stats_rep=1,
        method='de', 
        **kwargs,
    ):
        """Apply fitting to one subject."""
        subject_data = data.loc[data['subject'] == subject]
        param, fit_stat, n, k = self.fit_subject(
            subject_data, 
            param_def, 
            patterns, 
            study_keys, 
            recall_keys, 
            stats_def, 
            n_stats_rep, 
            method, 
            **kwargs,
        )
        if stats_def is None:
            results = {**param, 'logl': fit_stat, 'n': n, 'k': k}
        else:
            results = {
                **param, stats_def.options['error_stat']: fit_stat, 'n': n, 'k': k
            }
        return results

    def fit_indiv(
        self,
        data,
        param_def,
        patterns=None,
        study_keys=None,
        recall_keys=None,
        stats_def=None, 
        n_stats_rep=1,
        n_jobs=None,
        method='de',
        n_rep=1,
        **kwargs,
    ):
        """
        Fit parameters to individual subjects.

        Parameters may be estimated either based on evaluating the
        overall likelihood of recall sequences in the observed data,
        or based on specific summary statistics. 
        
        To fit to summary statistics, simulated data must be generated 
        first so they can be analyzed. Note that simulated data are 
        stochastic, and any variability in summary statistics may 
        complicate the parameter search. To help stabalize summary 
        statistics, simulated data may optionally replicate the study 
        multiple times.

        Parameters
        ----------
        data : pandas.DataFrame
            Data for one or more subjects.

        param_def : cymr.parameters.Parameters
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        study_keys : list of str
            Fields to include in study data.

        recall_keys : list of str
            Fields to include in recall data.

        stats_def : cymr.analysis.Statistics
            Statistics to use when evaluating the model fit. If None,
            the fit will be evaluated based on the overall likelihood
            of the observed recall sequences. If a stats_def is 
            specified, simulated data will be generated and used to 
            calculate the statistics, which will be compared to the 
            observed data.
        
        n_stats_rep : int, optional
            Number of times to replicate generation and stat 
            evaluation. Only used if stats_def is not None.

        n_jobs : int, optional
            Number of processes to use for fitting subjects in
            parallel.

        method : str, optional
            Search method for fitting the parameters.

        n_rep : int, optional
            Number of times to repeat each search.

        kwargs
            Additional keyword arguments for the search method.

        Returns
        -------
        results : pandas.DataFrame
            Best-fitting parameters, log likelihood (:code:`logl`)
            or error statistic specified by stats_def, number of data 
            points (:code:`n`), and number of free parameters 
            (:code:`k`) for each subject.
        """
        subjects = data['subject'].unique()
        full_subjects = np.repeat(subjects, n_rep)
        full_reps = np.tile(np.arange(n_rep), len(subjects))
        if n_jobs == 1:
            full_results = [
                self._run_fit_subject(
                    data, 
                    subject, 
                    param_def, 
                    patterns, 
                    study_keys, 
                    recall_keys, 
                    stats_def,
                    n_stats_rep,
                    method, 
                    **kwargs,
                )
                for subject in full_subjects
            ]
        else:
            full_results = Parallel(n_jobs=n_jobs)(
                delayed(self._run_fit_subject)(
                    data, 
                    subject, 
                    param_def, 
                    patterns, 
                    study_keys, 
                    recall_keys, 
                    stats_def,
                    n_stats_rep,
                    method, 
                    **kwargs,
                )
                for subject in full_subjects
            )
        d = {
            (subject, rep): res
            for subject, rep, res in zip(full_subjects, full_reps, full_results)
        }
        results = pd.DataFrame(d).T
        results.index.rename(['subject', 'rep'], inplace=True)
        results = results.astype({'n': int, 'k': int})
        return results

    @abstractmethod
    def generate_subject(
        self, study, recall, param, param_def=None, patterns=None, **kwargs
    ):
        """
        Generate simulated data for one subject.

        Parameters
        ----------
        study : dict of (str: list of numpy.array)
            Information about the study phase in list format.

        recall : dict of (str: list of numpy.array)
            Information about recall trials in list format.

        param : dict of (str: float)
            Model parameter values.

        param_def : cymr.parameters.Parameters, optional
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        Returns
        -------
        recalls_list : list of numpy.array
            Recalled items for each simulated list.
        """
        pass

    def generate(
        self,
        data,
        group_param,
        subj_param=None,
        param_def=None,
        patterns=None,
        study_keys=None,
        recall_keys=None,
        n_rep=1,
    ):
        """
        Generate simulated data for all subjects.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to guide simulation. Must include a 'subject' column.
            May include dummy recall events if there is a dynamic
            recall parameter.

        group_param : dict of (str: float)
            Values of parameters that apply to all subjects.

        subj_param : dict of (str: dict of (str: float))
            Parameters that vary by subject, indexed by subject.

        param_def : cymr.parameters.Parameters, optional
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        study_keys : list of str
            Data columns to include for the study phase.

        recall_keys : list of str
            Data columns to include for the recall phase.

        n_rep : int
            Number of times to repeat the simulation for each subject.

        Returns
        -------
        sim_data : pandas.DataFrame
            Simulated data for each subject.
        """
        # get the list of subjects
        subjects = data['subject'].unique()
        data_list = []
        for subject in subjects:
            # filter the data events for this subject
            subject_data = data.loc[data['subject'] == subject]

            # prepare data and parameters
            study, recall, param = self.prepare_subject(
                subject,
                subject_data,
                group_param,
                subj_param,
                param_def,
                study_keys,
                recall_keys,
            )

            max_list = subject_data['list'].max()
            # iterate over repetitions for this subject
            for i in range(n_rep):
                # run subject-specific generation function
                rep_recalls_list = self.generate_subject(
                    study, recall, param, param_def, patterns=patterns
                )
                rep_data = subject_data.copy()
                rep_data['list'] = i * max_list + subject_data['list']

                # strip off the dummy recall events
                rep_data = rep_data[rep_data['trial_type'] == 'study']
                rep_data = add_recalls(rep_data, rep_recalls_list)
                data_list.append(rep_data)
        sim_data = pd.concat(data_list, axis=0, ignore_index=True)
        return sim_data

    @abstractmethod
    def record_subject(
        self, study, recall, param, param_def=None, patterns=None, **kwargs
    ):
        """
        Record model state during simulation of data for one subject.

        Parameters
        ----------
        study : dict of (str: list of numpy.array)
            Information about the study phase in list format.

        recall : dict of (str: list of numpy.array)
            Information about recalled items in list format.

        param : dict of (str: float)
            Model parameter values.

        param_def : cymr.parameters.Parameters, optional
            Parameter definition object; used to interpret parameters.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        Returns
        -------
        study_state : list of lists
            Recorded state for each study trial.

        recall_state : list of lists
            Recorded state for each recall attempt.
        """

    def record(
        self,
        data,
        group_param,
        subj_param=None,
        param_def=None,
        patterns=None,
        study_keys=None,
        recall_keys=None,
        **kwargs,
    ):
        """
        Record model states during a simulation.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to guide simulation. Must include a 'subject' column.
            May include dummy recall events if there is a dynamic
            recall parameter.

        group_param : dict of (str: float)
            Values of parameters that apply to all subjects.

        subj_param : dict of (str: dict of (str: float))
            Parameters that vary by subject, indexed by subject.

        param_def : cymr.parameters.Parameters, optional
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        study_keys : list of str
            Data columns to include for the study phase.

        recall_keys : list of str
            Data columns to include for the recall phase.

        Returns
        -------
        states : list
            List of model states.
        """
        # get the list of subjects
        subjects = data['subject'].unique()
        states = []
        for subject in subjects:
            # filter the data events for this subject
            subject_data = data.loc[data['subject'] == subject]

            # prepare data and parameters
            study, recall, param = self.prepare_subject(
                subject,
                subject_data,
                group_param,
                subj_param,
                param_def,
                study_keys,
                recall_keys,
            )

            # record study and recall states
            study_state, recall_state = self.record_subject(
                study, recall, param, param_def=param_def, patterns=patterns, **kwargs
            )

            # combine states into a flat list
            for study_list, recall_list in zip(study_state, recall_state):
                for trial_state in study_list:
                    states.append(trial_state)
                for trial_state in recall_list:
                    states.append(trial_state)
        return states

    def _run_parameter_recovery(
        self, data, param_def, patterns=None, method='de', n_rep=1, **kwargs
    ):
        """Run a parameter recovery test."""
        # generate parameters
        param = param_def.fixed.copy()
        sampled = parameters.sample_parameters(param_def.free)
        param.update(sampled)

        # generate simulated data
        sim = self.generate(
            data, param, None, param_def, patterns=patterns, n_rep=n_rep
        )

        # fit the simulated data
        fitted_param, logl, n, k = self.fit_subject(
            sim, param_def, patterns=patterns, method=method, **kwargs
        )

        # store results
        df_sim = pd.DataFrame(param, index=['sim'])
        df_fit = pd.DataFrame(fitted_param, index=['fit'])
        df_sample = pd.concat((df_sim, df_fit), axis=0)
        return df_sample

    def parameter_recovery(
        self,
        data,
        n_sample,
        param_def,
        patterns=None,
        method='de',
        n_rep=1,
        n_jobs=None,
        **kwargs,
    ):
        """Run multiple iterations of parameter recovery."""
        results_list = Parallel(n_jobs=n_jobs)(
            delayed(self._run_parameter_recovery)(
                data, param_def, patterns, method, n_rep, **kwargs
            )
            for i in range(n_sample)
        )
        results = pd.concat(results_list, axis=0, keys=np.arange(n_sample))
        return results

    def parameter_sweep(
        self,
        data,
        group_param,
        subj_param,
        sweep_param,
        param_def,
        patterns=None,
        n_rep=1,
    ):
        """
        Simulate data with varying parameters.

        Parameters
        ----------
        data : pandas.DataFrame
            Data to guide simulation. Must include a 'subject' column.
            May include dummy recall events if there is a dynamic
            recall parameter.

        group_param : dict of (str: float)
            Values of parameters that apply to all subjects.

        subj_param : dict of (str: dict of (str: float))
            Parameters that vary by subject, indexed by subject.

        sweep_param : dict of (str: numpy.ndarray)
            Parameter values to sweep over.

        param_def : cymr.parameters.Parameters, optional
            Parameter definitions.

        patterns : dict of (str: dict of (str: numpy.array)), optional
            Patterns to use in the model.

        n_rep : int
            Number of times to repeat the simulation for each subject.

        Returns
        -------
        results : pandas.DataFrame
            Simulated data for each combination of sweep parameters.
        """
        index = pd.MultiIndex.from_product(
            sweep_param.values(), names=sweep_param.keys()
        )
        df_list = []
        for idx in index:
            param = group_param.copy()
            param.update(dict(zip(sweep_param.keys(), idx)))
            sim = self.generate(
                data, param, subj_param, param_def, patterns=patterns, n_rep=n_rep
            )
            df_list.append(sim)
        results = pd.concat(df_list, axis=0, keys=index)
        results = results.droplevel(len(sweep_param.keys()))
        results.index.rename(sweep_param.keys(), inplace=True)
        return results
