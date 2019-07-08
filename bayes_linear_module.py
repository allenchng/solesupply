class ProbabilisticLinear(object):
    def __init__(self):
        self.weights_dict = {'w': None, 'b': None}

    def train(self):
        """Train a Bayesian linear model.

        Args:
            train: A dataframe of training data.
            labels: A numpy array of labels.

        Returns:
            fit: A fitted Stan model.  
        """

        features, labels = input_fn()

        start = time.time()

        stan_datadict = {}
        stan_datadict['N'] = train_features.shape[0]
        stan_datadict['K'] = train_features.shape[1]
        stan_datadict['X'] = train_features.values
        stan_datadict['y'] = train_labels

        model = pystan.StanModel(model_code=lin_reg_normal)

        fit = model.sampling(data=stan_datadict,
                        warmup=250,
                        iter = 1000, 
                        verbose = True,
                        control={'max_treedepth': 15})

        end = time.time()
        print('Time to fit model ' + str(end-start) + ' seconds.')
        return fit

    def diagnose(self, fit):
        
        """Test for divergences in the sampling procedure.

        Calls diagnostics.py, a script that examines the sampling chains for errors and divergences.

        Args:
            fit: A fitted Stan model.

        Returns:
            Prints % of trees in which depth is exceeded and divergences in sampling.
        """
        
        print(diagnostics.check_treedepth(fit))
        print(diagnostics.check_energy(fit))
        print(diagnostics.check_div(fit))

    def evaluate(self, fit):
        
        """Evaluate performance of fitted model.

        Args:
            fit: A fitted Stan model.
            features: A dataframe for held out values to test.
            labels: A numpy array for the true labels.

        Returns:
            Prints the percent error of the fitted Stan model as well as the percent error of the persistence model. 
        """
        
        features, labels = input_fn()
        
        b = fit.extract(['alpha'])['alpha'].mean()
        w = fit.extract(['beta'])['beta'].mean(axis=0)

        predictions = test_features@w + b
        
        numer_test_features = test_features.loc[:, ('volume', 'rolling_mean_week', 'rolling_median_week', 
                        'rolling_max_week')]
        
        unscale_test = pd.concat([numer_test_features, predictions],axis=1)
        unscale_test.columns = ['volume', 'rolling_mean_week', 'rolling_median_week', 'rolling_max_week', 'projected_volume']
        unscaled_predictions = scaler.inverse_transform(unscale_test)
        unscale_test.loc[:,:] = unscaled_predictions
        unscaled_predictions = unscale_test.projected_volume
        
        test_labels_df = pd.Series(test_labels)
        test_labels_df.index = numer_test_features.index
        unscale_labels = pd.concat([numer_test_features, test_labels_df],axis=1)
        unscale_labels.columns = ['volume', 'rolling_mean_week', 'rolling_median_week', 'rolling_max_week', 'projected_volume']

        unscaled_test_labels = scaler.inverse_transform(unscale_labels)
        unscale_labels.loc[:,:] = unscaled_test_labels
        
        observed = unscale_labels.projected_volume
        persistance_prediction = unscale_labels.volume
        
        print('Mean Absolute Percentage Error - Baseline:', round(np.mean(np.abs((observed - persistance_prediction) / observed)) * 100))
        print('Mean Absolute Percentage Error - Bayes:', round(np.mean(np.abs((observed - unscaled_predictions) / observed)) * 100))

    def visualize_weights(self, fit):
        
        """Visualize the posterior distribution of model features.

        Args:
            fit: A fitted Stan model.
            selected_features: A list of strings indicating which features to visualize.

        Returns:
            Saves PNG's of the posterior distribution for all the weights and a selected 
        """
        
        samples = fit.extract()
        beta = samples['beta']
        
        col_names = test_features.columns
        weights = pd.DataFrame(beta)
        weights.columns = col_names
        melted_weights = weights.melt()
        
        # Visualize and save posteriors for all predictors
        a = sns.FacetGrid(melted_weights, col='variable', col_wrap=5, sharex=False, sharey=False)
        a = a.map(sns.distplot, "value")
        a.savefig('./figures/all_variable_posteriors.png', dpi = 400)
        
        # Visualize and save posteriors for selected features
        desired_features = ['volume', 'rolling_mean_week', 'is_retro', 'is_yeezy']
        posterior_features = melted_weights[melted_weights['variable'].isin(desired_features)]
        g = sns.FacetGrid(posterior_features, col='variable', sharex=False, sharey=False)
        g = g.map(sns.distplot, "value")
        g.savefig('./figures/selected_variable_posteriors.png', dpi = 400)
        
