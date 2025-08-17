"""
Machine learning pipeline for biomarker discovery
"""

from sklearn.model_selection import cross_val_score
from sklearn import metrics, linear_model
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.pipeline import Pipeline
from sklearn.utils import resample
import numpy as np
import pandas as pd
import math
from tqdm import tqdm

class FeatureSelector(object):
    """Feature selection using regularized logistic regression with automatic C parameter tuning.
    
    Attributes:
    -----
        data : array-like or pd.DataFrame
            Feature matrix (n_samples, n_features)
        target : array-like
            Binary target vector (n_samples,)
        C : float, optional
            Regularization strength (inverse of regularization). 
            If None, will be automatically determined from C_space.
        C_space : array-like, optional
            Search space for C values (default: 20 values from 0.0001 to 1)
        C_finder_iter : int, optional
            Number of bootstrap iterations for C optimization (default: 100)
        C_tol : float, optional
            Tolerance for derivative to consider the optimization plateau (default: 0.005)
        cut_off_w_feature : float, optional
            Fraction cutoff for model coefficients (default: 0)
        cut_off_w_estimation : bool, optional
            Whether to estimate optimal cutoff fraction (default: False)
        cut_off_estim_params : dict, optional
            Parameters for cutoff w estimation. If None, uses:
            {'inner_loop': 10, 'max_iter': 10, 'cut_off_feature_value': 0.1, 'max_feature': None, optimal_method': 'first'}
            inner_loop:
                The number of simulations of the inner loop when evaluating cut_off_level. The number of repetitions of train_test_splits to evaluate the quality of a model with a given set of features.
            max_iter:
                Number of simulations when adding each feature during cut-off search. The total number of simulations is max_iter*inner_loop.
            cut_off_feature_value:
                The minimum proportion of models that a feature must be included in for it to be considered in further simulations
            max_feature : int, optional 
                Can be restrict the feature space to n-top features. If "None", then the search is carried out over the entire feature space. 
            optimal_method: str, ['first', 'median']
                How optimal cut-off level will be get. Default = 'first'.
            feature_resample: int, optional (default=0)
                Resampling of features. If 0, the full feature space is considered at each train_test_split, 
                otherwise the feature space is also sampled in batches of size "feature_resample"
        pipeline_steps : list, optional
            Custom pipeline steps for the classifier. If None, uses:
            [StandardScaler(), LogisticRegression(penalty='l1', solver='liblinear')]
        scoring : str, optional
            Scoring metric for model evaluation. Must be from sklearn.metrics.SCORERS.keys()
            (default: 'roc_auc')
    
    Notes
    -----
        - When C=None, performs bootstrap-based optimization to find optimal regularization strength
        - Final model selects features with non-zero coefficients
    
    Examples
    --------
    >>> FS_model = FeatureSelector(X, y,
                                   C = 0.04, 
                                   C_space=np.linspace(0.0001, 1, 20),
                                   C_finder_iter=10,
                                   cut_off_w_estimation=False,
                                   cut_off_w_feature=0.95,
                                   cut_off_estim_params={'max_feature': 50})
    >>> FS_model.fit(max_iter=32000, log=True, feature_resample=10)
    >>> FS_model.best_features # return dict of selected best features {feature: w}
    >>> FS_model.all_features # return dict of all features with w > cut_off_feature_value (default > 0.1)
        
    """
    def __init__(self, data, target, 
                 C=None, C_space=np.linspace(0.0001, 1, 20), C_finder_iter=100, C_tol = 0.005, 
                 cut_off_w_feature=0, cut_off_w_estimation=True, cut_off_estim_params=None,
                 pipeline_steps=None, scoring='roc_auc'):
        
        self.best_features = dict()
        """dict(feature: weight), The best features that were selected. Available after fit"""
        self.C_finder_iter = C_finder_iter
        """Number of bootstrap iterations for C optimization (default: 100)"""
        self.C_space = C_space
        """Search space for C values (default: 20 values from 0.0001 to 1)"""
        self.data = data
        """array-like or pd.DataFrame. Feature matrix (n_samples, n_features)"""
        self.target = target
        """array-like. Binary target vector (n_samples,)"""
        self.cut_off_w_feature = cut_off_w_feature
        """cutoff for w feature (default: 0). All features with w > cut_off_w_feature would be included to analysis"""
        self.scoring = scoring
        """Scoring metric for model evaluation. Must be from sklearn.metrics.SCORERS.keys(). default: 'roc_auc'"""
        self.cut_off_estim_params = cut_off_estim_params
        """ dict, optional
            Parameters for cutoff w estimation. 
            
            If None, uses:
            {'inner_loop': 10, 
            'max_iter': 10, 
            'cut_off_feature_value': 0.1, 
            'max_feature': None, 
            optimal_method': 'first'}
            ---------------
            inner_loop:
                The number of simulations of the inner loop when evaluating cut_off_level. 
                The number of repetitions of train_test_splits to evaluate the quality of 
                a model with a given set of features.
            max_iter:
                Number of simulations when adding each feature during cut-off search. 
                The total number of simulations is max_iter*inner_loop.
            cut_off_feature_value:
                The minimum proportion of models that a feature must be included in for it to be considered 
                in further simulations
            max_feature : int, optional 
                Can be restrict the feature space to n-top features. 
                If "None", then the search is carried out over the entire feature space. 
            optimal_method: str, ['first', 'median']
                How optimal cut-off level will be get. Default = 'first'.
            feature_resample: int, optional (default=0)
                Resampling of features. If 0, the full feature space is considered at each train_test_split, 
                otherwise the feature space is also sampled in batches of size "feature_resample"
        """

        # variable for logging and plotting
        self._n_model = 0
        self._score_list = list()
        self._best_feature_progress = list()
        self._old_top = set()
        self._top_update = list()
        self._top_weights = list()
        self._top_fearures_progress = list()
        self._plot_params = dict()
        self._plot_params['cutoff_searching'] = {'cut_of_list': None, 
                                                'roc_train_list': None, 
                                                'roc_test_list': None, 
                                                'arg_max_list': None}
        self.__C_space_iter = None
        

        # Default parameters for cut_off_estim_params
        default_cut_off_params = {
            'inner_loop': 10,
            'max_iter': 10,
            'cut_off_feature_value': 0.1,
            'max_feature': None, # Feature space can be restrict to n-top features. If "None", then the search is carried out over the entire feature space. 
            'optimal_method': 'first',
            'feature_resample': 0
        }
        if self.cut_off_estim_params is not None:
            default_cut_off_params.update(self.cut_off_estim_params)

        # Defining pipeline steps
        if not C:
            print('The regularization coefficient was not specified, the search for the optimal C was started')
            self.C = self.get_optimal_C(tol=C_tol)
            """Regularization strength (inverse of regularization). 
            If None, will be automatically determined from C_space."""
            print('Optimal regularization coefficient (С) = ', round(self.C, 3))
        else:
            self.C = C
        if pipeline_steps:
            self.pipeline = Pipeline(pipeline_steps)
            """sklearn.pipeline.Pipeline. A sequence of data transformers with an optional final predictor."""
        else:
            steps = [
                ('scaler', StandardScaler()),
                ('log_reg', linear_model.LogisticRegression(penalty='l1', C=self.C, solver='liblinear', random_state=42))
            ]
            # Creating a pipeline
            self.pipeline = Pipeline(steps)
        if cut_off_w_estimation:
            print()
            print('Prefit model for cutoff weight level estimation')
            self.fit()
            print('Prefit done')
            self.cut_off_w_feature = self._get_optimal_cut_off_level(**cut_off_estim_params)

    def get_optimal_C(self, tol=0.005):
        """
        The function searches for the optimal regularization parameter
        """
        X = self.data
        y = self.target
        
        result_df_train = pd.DataFrame()

        for a in tqdm(range(0, self.C_finder_iter), desc='processing: '):
            for _ in range(self.C_finder_iter):
                X_train, _, y_train, _ = train_test_split_res(X, y)
                if _count_min_class(y_train) > 3:
                    break
            roc_auc_train = list()
            for i in self.C_space:
                steps = [
                    ('scaler', StandardScaler()),
                    ('log_reg', linear_model.LogisticRegression(penalty='l1', C=i, solver='liblinear', random_state=42))
                ]
                # Creating a pipeline
                pipeline = Pipeline(steps)
                pipeline.fit(X_train, y_train)        
                roc_auc_train.append(np.mean(cross_val_score(pipeline, X_train, y_train, cv=3, scoring=self.scoring)))
            result_df_train[a] = roc_auc_train

        _y = result_df_train.apply(np.mean, axis=1)
        _x = range(0, len(_y))

        der_y = np.diff(_y)
        max_der_y = np.where(der_y == max(der_y))[0][0]
        arg_plateau = max_der_y + np.where(der_y[max_der_y:] < tol)[0][0]

        self._C_space_mean = _y
        self._C_space_iter = _x
        self._C_arg_plateau = arg_plateau

        return self.C_space[arg_plateau]

    def fit(self,
            max_iter: int = 3000,
            cut_off_score: float = 0.6,
            log: bool = True,
            feature_resample: int = 0):
        """
        Train the feature selection model and identify significant features.
        
        Parameters
        ----------
        max_iter : int, optional (default=3000)
            Maximum number of iterations for the optimization solver.
            Must be positive. Consider increasing for complex datasets.
            
        cut_off_score : float, optional (default=0.6)
            Minimum importance score (scorer_metrics [ROC-AUC] * proportion-of-models-that-include-the-feature) 
            threshold for feature selection (range: 0-1).
            Features with scores below this threshold will be discarded.
            
        log : bool, optional (default=True)
            If True, enables verbose output during training.
            Recommended for monitoring convergence.
            
        feature_resample : int, optional (default=0)
            Resampling of features. If 0, the full feature space is considered at each train_test_split, 
            otherwise the feature space is also sampled in batches of size "feature_resample"

        Returns
        -------
        self : FeatureSelector
            The fitted estimator instance enabling method chaining.

        Examples
        --------
        >>> selector = FeatureSelector(X, y)
        >>> selector.fit(max_iter=5000)
        """
        roc_auc_scorer = metrics.make_scorer(metrics.roc_auc_score)
        self.best_features = dict()
        """dict(feature: weight), The best features that were selected. Available after fit"""
        self.all_features = dict()
        """dict(feature: weight), All features that w > cut_off_feature_value"""
        self._best_feature_progress = list()
        self._top_update = list()
        self._top_weights = list()
        self._top_fearures_progress = list()
        self._old_top = set()
        self._n_model = 0
        self._best_features_counter = dict()

        for itr in tqdm(range(1, max_iter+1), desc='fit model: '):
            # model
            for _ in range(max_iter):
                X_train, X_test, y_train, y_test = train_test_split_res(self.data, self.target, feature_resample=feature_resample)
                if _count_min_class(y_train) > 3:
                    if len(set(y_test)) > 1:
                        break
            if feature_resample:                
                for i in X_train.columns:
                    if i in self._best_features_counter:
                        self._best_features_counter[i] += 1
                    else:
                        self._best_features_counter[i] = 1
            self.pipeline.fit(X_train, y_train)
            mask = self.pipeline.named_steps['log_reg'].coef_[0] != 0
            score = roc_auc_scorer(self.pipeline, X_test, y_test)
            self._score_list.append(roc_auc_scorer(self.pipeline, X_test, y_test))
            if score < cut_off_score or np.isnan(score):
                continue
            else:
                self._n_model += 1
            for i in X_train.columns[mask]:
                if i in self.best_features:
                    self.best_features[i]+=1*score
                else:
                    self.best_features[i]=1*score

            # loging
            if log:
                if feature_resample:
                    top_feat = set([k for k, v in self.best_features.items() if v/self._best_features_counter[k] > self.cut_off_w_feature])
                else:
                    top_feat = set([k for k, v in self.best_features.items() if v/self._n_model > self.cut_off_w_feature])
                ft_prog = len(top_feat)
                if top_feat - self._old_top:
                    self._top_update.append(1)
                else:
                    self._top_update.append(0)
                self._old_top = top_feat
                self._best_feature_progress.append(len(self.best_features))
                self._top_fearures_progress.append(ft_prog)
                self._top_weights.append(sum([v for k, v in self.best_features.items() if k in top_feat]))

        for  k, v in self.best_features.items():
            if feature_resample:
                self.best_features[k] = v/self._best_features_counter[k]
            else:
                self.best_features[k] = v/self._n_model
        
        self.all_features = dict(sorted(self.best_features.items(), key=lambda item: item[1], reverse=True))
        self.best_features = {k:v for k, v in self.all_features.items() if v > self.cut_off_w_feature}

    def _get_optimal_cut_off_level(self, X=None, y=None, best_features=None, self_data=True, inner_loop=20, max_iter=10, cut_off_feature_value=0.1, max_feature=None, optimal_method='first', feature_resample=0):
            
            _cut_of_list = list()
            _roc_train_list = list()
            _roc_test_list = list()
            _arg_max_list = list()
            if self_data:                    
                X = self.data
                y = self.target
            else:
                self.best_features = best_features
            roc_auc_scorer = metrics.make_scorer(metrics.roc_auc_score)
            
            print('Serching cutoff level for feature weights...', end=' ')
            for i in range(max_iter):
                print(i, end=' ')
                sorted_feature = {k: v for k, v in sorted(self.best_features.items(), 
                                                        key=lambda item: item[1], reverse=True)}

                rocauc_mean_train = list()
                rocauc_mean_test = list()
                _feature = list()
                for i in tqdm(sorted_feature.keys(), desc='feature space analysis: '):
                    if sorted_feature[i] < cut_off_feature_value:
                        break
                    roc_auc_train = list()
                    roc_auc_test = list()
                    _feature.append(i)
                    if max_feature:
                        if len(_feature) > max_feature:
                            break
                    tmp_X = X.loc[:,_feature]
                    
                    for _ in range(inner_loop):
                        for _ in range(inner_loop):
                            X_train, X_test, y_train, y_test = train_test_split_res(tmp_X, y, feature_resample=feature_resample)
                            if _count_min_class(y_train) > 3: # so that the number of observations in the minimum class is greater than the number of splits in the CV
                                if len(set(y_test)) > 1:
                                    break
                        steps = [
                            ('scaler', StandardScaler()),
                            ('log_reg', linear_model.LogisticRegression(penalty='l2', C=1, solver='liblinear', random_state=42))
                        ]
                        # Creating a pipeline
                        pipeline = Pipeline(steps)
                        pipeline.fit(X_train, y_train)        
                        roc_auc_train.append(np.mean(cross_val_score(pipeline, X_train, y_train, cv=3, scoring=self.scoring)))
                        roc_auc_test.append(roc_auc_scorer(pipeline, X_test, y_test))
                    rocauc_mean_train.append(np.mean(roc_auc_train))
                    rocauc_mean_test.append(np.mean(roc_auc_test))
                
                rc = np.array(rocauc_mean_test)
                arg_max = np.where(rc == max(rc))[0][0]
                last_feature = list(sorted_feature.keys())[arg_max]
                cut_off_level = math.floor((sorted_feature[last_feature])*100)/100
                _cut_of_list.append(cut_off_level)
                _roc_train_list.append(rocauc_mean_train)
                _roc_test_list.append(rocauc_mean_test)
                _arg_max_list.append(arg_max)
                
            self._plot_params['cutoff_searching'] = {'cut_of_list': _cut_of_list, 
                                                    'roc_train_list': _roc_train_list, 
                                                    'roc_test_list': _roc_test_list, 
                                                    'arg_max_list': _arg_max_list}
            if optimal_method=='first':
                optimal_cut_off = sorted(_cut_of_list, reverse=True)[0]
            if optimal_method=='median':
                optimal_cut_off = np.median(_cut_of_list)
            print('optimal cut of weight level = ', optimal_cut_off)
            return optimal_cut_off
        
class fsplot(object):
    """
    Implementation of graphics methods for FeatureSelector module logs
    """
    def __init__(self, fs_model, color = [(18/255, 163/255, 173/255, 1), #"green"
                                          (200/255, 13/255, 63/255, 1),  #"red"
                                          (248/255, 155/255, 54/255, 1), #the third color is orange
                                          (242/255, 104/255, 73/255, 1), #fourth color
                                          (65/255, 100/255, 175/255, 1)] #fifth color
                ) -> None:
        
        self.one_color = color[4]
        """first color"""
        self.two_color = color[1]
        """second color"""
        self.third_color = color[2]
        """third color"""
        self.fs_model = fs_model
        """fitted FeatureSelector model"""

    def ROCdistr(self, ax=None, fontsize=20, path=None):
        """plot ROC-AUC distribution histogram. Available after fit FeatureSelector"""
        if ax:
            ax1 = ax
        else:
            _, ax1 = plt.subplots(figsize=(12, 10))
        
        ax1.hist(self.fs_model._score_list, bins=15, color=self.two_color, alpha=1., edgecolor='black')
        ax1.set_xlabel('ROC-AUC', fontsize=fontsize)
        ax1.set_ylabel('Number of models', fontsize=fontsize)
        ax1.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  # Y-axis offset
        ax1.xaxis.labelpad = fontsize  # X-axis offset
        # Remove the top and right borders of the axes
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Save the histogram to a file
        if path:
            plt.savefig(path, dpi=300, bbox_inches='tight')
    
    def feature_selection(self, ax=None, fontsize=20, path=None):
        """plot feature selection dynamic for to assess convergence. 
        Available after fit FeatureSelector"""
        if ax:
            ax1 = ax
        else:
            _, ax1 = plt.subplots(figsize=(12, 10))
        top_ind = np.where(np.diff(self.fs_model._top_update))[0]
        for index in top_ind:
            ax1.vlines(index, 0, 0.5, color=self.two_color, linestyles='dashed', linewidth=4)
        ax1.plot(np.array(self.fs_model._top_fearures_progress[2:]), color=self.third_color, linewidth=4)
        ax1.set_xlabel('Iteration number', fontsize=fontsize)
        ax1.set_ylabel('Number of features included \n in more than {}% models'.format(round(self.fs_model.cut_off_w_feature*100)), fontsize=fontsize)
        ax1.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  # Y-axis offset
        ax1.xaxis.labelpad = fontsize  # X-axis offset
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        if path:
            plt.savefig(path, dpi=300, bbox_inches='tight')
        
    def feature_weights(self, ax=None, fontsize=20, path=None):
        """plot feature weight distribution histogram and cut_off_w_feature level. 
        Available after fit FeatureSelector"""
        if ax:
            ax1 = ax
        else:
            _, ax1 = plt.subplots(figsize=(12, 10))
        value = [v for k, v in self.fs_model.all_features.items()]
        ax1.hist(value, bins=19, color=self.third_color, alpha=1., edgecolor='black')
        ax1.vlines(self.fs_model.cut_off_w_feature, 0, 20, color=self.two_color, linewidth=4)
        ax1.text(self.fs_model.cut_off_w_feature/max(value)+0.02, 0.3, 'cutoff\nlevel = {}'.format(np.round(self.fs_model.cut_off_w_feature, 2)), transform=ax1.transAxes, color=self.two_color, fontsize=fontsize, ha='left', va='center')
        ax1.set_xlabel('Estimated weight', fontsize=fontsize)
        ax1.set_ylabel('Number of features', fontsize=fontsize)
        ax1.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  # Y-axis offset
        ax1.xaxis.labelpad = fontsize  # X-axis offset
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        if path:
            plt.savefig(path, dpi=300, bbox_inches='tight')
        
    def feature_selection_exted(self, ax=None, fontsize=20, path=None):
        """plot feature selection weight dynamic for all- and best-feature comparison. 
        Available after fit FeatureSelector"""
        # Creating a graph
        if ax:
            ax1 = ax
        else:
            fig, ax1 = plt.subplots(figsize=(12, 10))
        # Plotting the first curve
        ax1.plot(np.array(self.fs_model._best_feature_progress), color=self.one_color, linewidth=4)
        ax1.set_xlabel('Iteration number', fontsize=fontsize)
        ax1.set_ylabel('Number of features \n included in at least one model', color=self.one_color, fontsize=fontsize)
        ax1.tick_params(axis='y', colors=self.one_color)
        ax1.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  # Y-axis offset
        ax1.xaxis.labelpad = fontsize  # X-axis offset
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # Create a second y-axis
        ax2 = ax1.twinx()
        ax2.plot(np.array(self.fs_model._top_weights), color=self.third_color, linewidth=4)
        ax2.set_ylabel('Total weight of features \n included in more than {} of models'.format(round(self.fs_model.cut_off_w_feature)), color='black', fontsize=fontsize)
        ax1.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  # Y-axis offset
        ax1.xaxis.labelpad = fontsize  # X-axis offset
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        top_ind = np.where(np.diff(self.fs_model._top_fearures_progress))[0]
        for index in top_ind:
            ax1.vlines(index, 0, 1.7, color=self.two_color, linestyles='dashed', linewidth=4)
        if path:
            plt.savefig(path, dpi=300, bbox_inches='tight')
    
    def C_searching(self, ax=None, fontsize=20, path=None):
        """plot C searching dynamic and C-optimal value. 
        Available after get_optimal_C() procedure"""
        # Creating a graph
        if ax:
            ax1 = ax
        else:
            _, ax1 = plt.subplots(figsize=(12, 10))
        ax1.plot(self.fs_model._C_space_iter, self.fs_model._C_space_mean, color=self.one_color, label='train', linewidth=4)
        ax1.vlines(self.fs_model._C_arg_plateau, min(self.fs_model._C_space_mean), max(self.fs_model._C_space_mean), color=self.two_color, linewidth=4)
        ax1.text(self.fs_model._C_arg_plateau/max(self.fs_model._C_space_iter)+0.03, 0.2, 'optimal\nС = {}'.format(np.round(self.fs_model.C,2)), transform=ax1.transAxes, color=self.two_color, fontsize=fontsize, ha='left', va='center')
        ax1.set_xlabel('Inverse regularization coefficient (С)', fontsize=fontsize)
        ax1.set_ylabel('ROC-AUC train CV', fontsize=fontsize)
        ax1.set_xticks(ticks=self.fs_model._C_space_iter[::4])
        ax1.set_xticklabels(labels=np.round(self.fs_model.C_space[::4],2))
        ax1.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  # Y-axis offset
        ax1.xaxis.labelpad = fontsize  # X-axis offset
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        

        if path:
            plt.savefig(path, dpi=300, bbox_inches='tight')
    
    def weights_cut_of_level_searching(self, ax=None, fontsize=20, path=None):
        """plot cut_off_w_feature searching dynamic and C-optimal value. 
        Available after _get_optimal_cut_off_level() procedure"""

        if ax:
            ax1 = ax
        else:
            _, ax1 = plt.subplots(figsize=(12, 10))

        train_series = np.array(self.fs_model._plot_params['cutoff_searching']['roc_train_list'])
        test_series = np.array(self.fs_model._plot_params['cutoff_searching']['roc_test_list'])
        arg_max_list = np.array(self.fs_model._plot_params['cutoff_searching']['arg_max_list'])
        color_line = [self.one_color, self.two_color] #green, red
        color_hist = self.third_color
        legend = ['train', 'test']

        args = self.fs_model._plot_params['cutoff_searching']['arg_max_list']
        cutoff = self.fs_model._plot_params['cutoff_searching']['cut_of_list']
        dct_labels = dict(zip(args, cutoff))

        s_key = sorted(dct_labels.keys())
        s_y = np.linspace(0.4,0.05,len(dct_labels))
        d_y = dict(zip(s_key, s_y))
        y_text = [d_y[i] for i in dct_labels.keys()]
        #Plotting:
        ax1.hist(arg_max_list, alpha=.7, color=color_hist, density=True)
        ax1.vlines(dct_labels.keys(), 0, y_text, colors=self.two_color)
        # Adding labels above lines
        i=0
        for x, label in dct_labels.items():
            ax1.text(x, y_text[i], label, ha='center', va='bottom', fontsize=(fontsize-9))
            i+=1
        ax2 = ax1.twinx()

        for i, x in enumerate([train_series, test_series]):
            smooth_path    = x.mean(axis=0)
            path_deviation = 2.3 * x.std(axis=0)
            under_line     = (smooth_path-path_deviation)
            over_line      = (smooth_path+path_deviation)
            ax2.plot(smooth_path, linewidth=4, color=color_line[i], label=legend[i]) #mean curve.
            ax2.fill_between(range(smooth_path.shape[0]), under_line, over_line, color=color_line[i], alpha=.1) #std curves.

        ax2.set_ylabel('ROC-AUC', color=self.two_color, fontsize=fontsize)
        ax2.tick_params(axis='y', colors=self.two_color)
        ax1.set_ylabel('Share of simulations', color='black', fontsize=fontsize)
        ax1.set_xlabel('Number of features included in the model', color='black', fontsize=fontsize)
        ax1.tick_params(labelsize=fontsize)
        ax2.tick_params(labelsize=fontsize)
        ax1.yaxis.labelpad = fontsize  
        ax1.xaxis.labelpad = fontsize  
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.yaxis.labelpad = fontsize  
        ax2.yaxis.labelpad = fontsize  
        ax1.xaxis.labelpad = fontsize  
        ax2.legend(fontsize=fontsize, loc='lower right')
        
        if path:
            plt.savefig(path, dpi=300, bbox_inches='tight')
        pass
        
    def plot_all(self, fontsize=20, labels = ['a.', 'b.', 'c.', 'd.', 'e.', 'f.'], left=0.1, right=0.9, top=0.9, bottom=0.1, hspace=0.3, wspace=0.4):
        """
        plot all graphs on one figure
        """
        _, axs = plt.subplots(3, 2, figsize=(24, 30))
        if self.fs_model._C_space_iter:
            self.C_searching(ax=axs[0, 0], fontsize=fontsize)
        else:
            axs[0, 0].text(0.5, 0.5, f"No search for C was performed.\nC = {self.fs_model.C}", 
                           ha='center', va='center', fontsize=fontsize)
        self.ROCdistr(ax=axs[0, 1], fontsize=fontsize)
        if self.fs_model._plot_params['cutoff_searching']['roc_train_list']:
            self.weights_cut_of_level_searching(ax=axs[1, 0], fontsize=fontsize)
        else:
            axs[1, 0].text(0.5, 0.5, f"No cut_of_level search was performed.\ncut_of_level = {self.fs_model.cut_off_w_feature}", 
                           ha='center', va='center', fontsize=fontsize)
        self.feature_weights(ax=axs[1, 1], fontsize=fontsize)
        self.feature_selection(ax=axs[2, 0], fontsize=fontsize)
        self.feature_selection_exted(ax=axs[2, 1], fontsize=fontsize)
        
        # Add letter numbering outside of graphs
        for i, ax in enumerate(axs.flat):
            # Define positions for annotations
            if i % 2 == 0:
                # Left graphs
                x_pos = -.1
            else:
                # Right graphs
                x_pos = -.1
            y_pos = 1.1
            
            ax.annotate(labels[i], xy=(x_pos, y_pos), xycoords='axes fraction', fontsize=fontsize+5,
                        ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', pad=1))
        plt.tight_layout()
        plt.subplots_adjust(left=left, right=right, top=top, bottom=bottom, hspace=hspace, wspace=wspace)

def train_test_split_res(X, y, feature_resample=0):
    """
    train test split with resampling

    Attributes:
    -----
    X : array-like or pd.DataFrame
        Feature matrix (n_samples, n_features)
    y : array-like
        Binary target vector (n_samples,)
    feature_resample: int, optional (default=0)
        Resampling of features. If 0, the full feature space is considered at each train_test_split, 
        otherwise the feature space is also sampled in batches of size "feature_resample"
    """
    N = len(y)
    # resample each class separately to keep their proportions
    train_indx = list(resample(np.where(y)[0])) + list(resample(np.where(np.array(y) == 0)[0]))
    test_indx = list(set(range(N)).difference(train_indx))
    X_train = X.iloc[train_indx,:]
    X_test = X.iloc[test_indx,:]
    y_train = [y[i] for i in train_indx]                    
    y_test = [y[i] for i in test_indx]
    if feature_resample:
        random_columns = np.random.choice(X_train.columns, feature_resample, replace=False)
        X_train = X_train[random_columns]
        X_test = X_test[random_columns]
    return X_train, X_test, y_train, y_test

def get_feature_space(model_list, cut_off_level=0.25):
    """
    the function returns a set of FeatureSelector models that satisfy the condition
    """
    fs = list()
    for model in model_list:
        fs = fs + [k for k, v in model.all_features.items() if v > cut_off_level]
    return set(fs)

def _count_min_class(vector):
    # Convert the list to a NumPy array if it is not already a NumPy array
    vector = np.array(vector)
    # Count the number of 0 and 1
    counts = np.bincount(vector)
    # Return the number of the smallest class
    return np.min(counts)