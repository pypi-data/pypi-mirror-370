"""Manage statistical measures."""

import importlib
import json
import pandas as pd
import polars as pl


def read_json(json_file):
    """Read statistics definition from a JSON file."""
    with open(json_file, "r") as f:
        stat_dict = json.load(f)
    
    stat = Statistics(**stat_dict["options"])
    for key, val in stat_dict["stats"].items():
        stat.set_stat(key, **val)
    return stat


class Analysis(object):
    """
    Manage analysis specification.

    Attributes
    ----------
    function : str
        Path to a function, in the form "package.module:function".
        Must take free-recall data in merged Psifr format as the first
        argument.
    
    independent : list of str
        List of expected columns with independent variables.
    
    dependent : str
        Expected column with dependent variable.
    
    level : str
        Level of the analysis. May be "group" or "subject". If "group",
        the result will be averaged across subjects.
    
    args : list
        Positional arguments for the function, after data.
    
    kwargs : dict
        Keyword arguments for the function.
    
    conditions : list of str
        Data columns to group by when running the analysis.
    """

    def __init__(
        self, 
        function,
        independent,
        dependent,
        level,
        args=None, 
        kwargs=None, 
        conditions=None,
    ):
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.independent = independent
        self.dependent = dependent
        self.conditions = conditions
        self.level = level
    
    def __repr__(self):
        fields = [
            "function", 
            "args", 
            "kwargs", 
            "independent", 
            "dependent", 
            "conditions", 
            "level",
        ]
        d = {f: getattr(self, f) for f in fields}
        s = "\n".join([f"{key}={val}" for key, val in d.items()])
        return s

    def to_dict(self):
        d = {
            "function": self.function, 
            "args": self.args,
            "kwargs": self.kwargs,
            "independent": self.independent,
            "dependent": self.dependent,
            "conditions": self.conditions,
            "level": self.level
        }
        return d
    
    def eval(self, data):
        """
        Evaluate an analysis on a dataset.

        Parameters
        ----------
        data : pandas.DataFrame
            Free-recall data in merged Psifr format.
        
        Returns
        -------
        stat : pandas.DataFrame
            Dependent variables by condition, subject, and independent
            variables, in standardized format.
        
        result : pandas.DataFrame
            Raw result from the analysis.

        Examples
        --------
        >>> from cymr.analysis import Analysis
        >>> from cymr import fit
        >>> from psifr import fr
        >>> ana = Analysis("psifr.fr:spc", ["input"], "recall", "group")
        >>> raw = fit.sample_data("sample1")
        >>> data = fr.merge_free_recall(raw)
        >>> stat, result = ana.eval(data)
        >>> stat
          condition_vars conditions subject independent_vars independent dependent_var  dependent
        0            n/a        n/a     n/a            input           1        recall        0.5
        1            n/a        n/a     n/a            input           2        recall        0.5
        2            n/a        n/a     n/a            input           3        recall        1.0
        >>> result
           input  recall
        0      1     0.5
        1      2     0.5
        2      3     1.0
        """
        # get the callable to run
        mod, fun = self.function.split(":")
        f = getattr(importlib.import_module(mod), fun)

        if self.conditions is not None:
            # apply the analysis to each cond
            res = data.groupby(self.conditions).apply(
                f, *self.args, **self.kwargs, include_groups=False
            )
            res.index = res.index.droplevel(-1)
            res = res.reset_index().convert_dtypes()

            if self.level == "group":
                # average over subjects
                res = res.groupby(
                    self.independent + self.conditions
                )[self.dependent].mean().reset_index()
            
            # get the group labels and values
            conds = res[self.conditions].apply(
                lambda df: ",".join(df.values.astype(str)), axis=1
            )
            cond_vars = ",".join(self.conditions)
        else:
            # apply the analysis to the whole dataset
            res = f(data, *self.args, **self.kwargs).convert_dtypes()
            conds = "n/a"
            cond_vars = "n/a"
            if self.level == "group":
                res = res.groupby(
                    self.independent
                )[self.dependent].mean().reset_index()
        
        if self.level == "group":
            subject = "n/a"
            independent_cols = self.independent
        else:
            subject = res["subject"].astype(str)
            independent_cols = self.independent

        # get the dependent variable        
        y = res[self.dependent]

        # get independent variable names and values
        independent = res[independent_cols].apply(
            lambda df: ",".join(df.values.astype(str)), axis=1
        )
        names = ",".join(independent_cols)

        # package results in a standardized condensed data frame
        stat = pd.DataFrame(
            {
                "condition_vars": cond_vars,
                "conditions": conds,
                "subject": subject,
                "independent_vars": names,
                "independent": independent,
                "dependent_var": self.dependent,
                "dependent": y
            }
        )
        return stat, res


class Statistics(object):
    """
    Manage statistics specifications.

    Attributes
    ----------
    options : dict
        Options for comparing statistics. The "error_stat" 
        (default "rmsd") defines the error statistic to calculate.
        The "weighting" (default: "point") defines how individual
        error statistics are combined when calculating the mean
        error. Allowed values are "point", "statistic", and
        "condition".
    
    stats : dict of (str: Analysis)
        Analysis specification for each statistic.
    """

    def __init__(self, error_stat="rmsd", weighting="point"):
        self.options = {"error_stat": error_stat, "weighting": weighting}
        self.stats = {}

    def __repr__(self):
        parts = {}
        for name in ["options", "stats"]:
            obj = getattr(self, name)
            if isinstance(obj, dict):
                fields = [f"\n{key}:\n{value}" for key, value in obj.items()]
                parts[name] = "\n".join(fields)
            else:
                parts[name] = obj
        s = "\n\n".join([f"{name}:\n{f}" for name, f in parts.items()])
        return s
    
    def to_json(self, json_file):
        """
        Write statistics definitions to a JSON file.
        
        Parameters
        ----------
        json_file : str
            Path to file to save json data.
        """
        data = {
            "options": self.options, 
            "stats": {stat: val.to_dict() for stat, val in self.stats.items()},
        }
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)

    def set_stat(self, stat, *args, **kwargs):
        """
        Configure an analysis to generate a statistic.
        
        Parameters
        ----------
        stat : str
            Name of the statistic.
        
        function : str
            Path to a function, in the form "package.module:function".
            Must take free-recall data in merged Psifr format as the first
            argument.
        
        independent : list of str
            List of expected columns with independent variables.
        
        dependent : str
            Expected column with dependent variable.
        
        level : str
            Level of the analysis. May be "group" or "subject". If "group",
            the result will be averaged across subjects.
        
        args : list
            Positional arguments for the function, after data.
        
        kwargs : dict
            Keyword arguments for the function.
        
        conditions : list of str
            Data columns to group by when running the analysis.
        
        Examples
        --------
        >>> from cymr import analysis
        >>> stat_def = analysis.Statistics()
        >>> stat_def.set_stat("spc", "psifr.fr:spc", ["input"], "recall", "group")
        """
        self.stats[stat] = Analysis(*args, **kwargs)
    
    def eval_stats(self, data):
        """
        Evaluate all statistics.

        Parameters
        ----------
        data : pandas.DataFrame
            Free-recall data in merged Psifr format.
        
        Returns
        -------
        stats : pandas.DataFrame
            All statistics in standardized format, concatenated with
            one row per dependent variable.
        
        results : list of pandas.DataFrame
            All results in raw format.
        """
        results = {}
        stat_list = []
        for stat_name, stat_def in self.stats.items():
            stat, res = stat_def.eval(data)
            stat["stat"] = stat_name
            stat_list.append(stat)
            results[stat_name] = res
        stats = pd.concat(stat_list, ignore_index=True)
        return stats, results
    
    def compare_stats(self, stats1, stats2):
        """
        Compare statistics.

        Parameters
        ----------
        stats1 : pandas.DataFrame
            Statistics in standardized format.
        
        stats2 : pandas.DataFrame
            Statistics in standardized format.
        
        Returns
        -------
        error_stat : float
            Error statistic.
        """
        stats1 = pl.from_pandas(stats1)
        stats2 = pl.from_pandas(stats2)
        comb = stats1.join(
            stats2, 
            on=["stat", "conditions", "subject", "independent"], 
            how="left", 
            suffix="2",
        )
        
        # formula for the statistic of interest
        if self.options["error_stat"] == "rmsd":
            err = ((pl.col("dependent") - pl.col("dependent2")) ** 2).mean().sqrt()
        else:
            raise ValueError(f"Unknown error statistic: {self.options['error_stat']}")
        
        # calculate with specified weighting
        if self.options["weighting"] == "point":
            comp_stat = comb.select(err)[0, 0]
        elif self.options["weighting"] == "statistic":
            comp_stat = comb.group_by("stat").agg(err).select("dependent").mean()[0, 0]
        elif self.options["weighting"] == "condition":
            comp_stat = comb.group_by(
                "stat", "conditions"
            ).agg(err).select("dependent").mean()[0, 0]
        else:
            raise ValueError(f"Unknown weighting type: {self.weighting}")
        return comp_stat
