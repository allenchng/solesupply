import seaborn as sns
import pandas as pd
import numpy as np
import pystan
import time
import diagnostics
import density_intervals as di

from sklearn.preprocessing import StandardScaler

class ProbabilisticLinear(object):
    def __init__(self):
        self.weights_dict = {'w': None, 'b': None}

    def input_data(self, model_df, train_pct):
        """ Transform data for modeling.

        Args:
            model_df: A dataframe of preprocessed data.

        Returns:
            train_features: A dataframe of training set features.
            train_labels: A dataframe of training set labels.
            test_features: A dataframe of test set features.
            test_labels: A Numpy array of test set labels
        """

        cat_bool = ['day_of_week', 'month', 'year', 'holiday', 'date', 
                    'is_retro', 'is_yeezy', 'is_travis_scott', 'is_off_white']

        cat_df = model_df.loc[:, (cat_bool)]
        
        numeric_features = model_df.loc[:, ('volume', 'rolling_mean_week', 'rolling_median_week', 
                        'rolling_max_week', 'total_release', 'projected_volume')]

        scaler = StandardScaler() 
        scaled_values = scaler.fit_transform(numeric_features) 
        numeric_features.loc[:,:] = scaled_values

        # Store scaler for use later on during test

        self.scaler = scaler
        
        model_df = pd.concat([cat_df, numeric_features], axis=1, sort=False)
        model_df.date = pd.to_datetime(model_df.date)
        
        model_df = model_df[model_df['date'] > '2017-10-30']
        data = model_df.drop("date", axis=1)
        
        rf_df = pd.get_dummies(data)
        rf_df = rf_df.dropna()
        rf_df = rf_df.reset_index(drop = True)

        labels = np.array(rf_df['projected_volume'])

        # Remove the labels from the features
        features= rf_df.drop('projected_volume', axis = 1)

        # Saving feature names for later use
        feature_list = list(features.columns)

        # Convert to numpy array
        features = np.array(features)
        
        split_axis = round(len(model_df) * train_pct)
        
        train = rf_df[:split_axis]
        test = rf_df[split_axis:-6]

        train_labels = np.array(train['projected_volume'])
        train_features = train.drop('projected_volume', axis = 1)

        test_labels = np.array(test['projected_volume'])
        test_features = test.drop('projected_volume', axis = 1)

        return train_features, train_labels, test_features, test_labels

    def train(self, train_features, train_labels, stan_model_spec):
        """Train a Bayesian linear model.

        Args:
            train: A dataframe of training data.
            labels: A numpy array of labels.

        Returns:
            fit: A fitted Stan model.  
        """

        start = time.time()

        stan_datadict = {}
        stan_datadict['N'] = train_features.shape[0]
        stan_datadict['K'] = train_features.shape[1]
        stan_datadict['X'] = train_features.values
        stan_datadict['y'] = train_labels

        model = pystan.StanModel(model_code=stan_model_spec)

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

    def evaluate(self, fit, test_features, test_labels):
        
        """Evaluate performance of fitted model.

        Args:
            fit: A fitted Stan model.
            features: A dataframe for held out values to test.
            labels: A numpy array for the true labels.

        Returns:
            Prints the percent error of the fitted Stan model as well as the percent error of the persistence model. 
        """
        
        b = fit.extract(['alpha'])['alpha'].mean()
        w = fit.extract(['beta'])['beta'].mean(axis=0)

        predictions = test_features@w + b
        
        numer_test_features = test_features.loc[:, ('volume', 'rolling_mean_week', 'rolling_median_week', 
                                                    'total_release', 'rolling_max_week')]

        scaler = self.scaler
        
        unscale_test = pd.concat([numer_test_features, predictions],axis=1)
        unscale_test.columns = ['volume', 'rolling_mean_week', 'rolling_median_week',
                                'rolling_max_week', 'total_release', 'projected_volume']
        unscaled_predictions = scaler.inverse_transform(unscale_test)
        unscale_test.loc[:,:] = unscaled_predictions
        unscaled_predictions = unscale_test.projected_volume
        
        test_labels_df = pd.Series(test_labels)
        test_labels_df.index = numer_test_features.index
        unscale_labels = pd.concat([numer_test_features, test_labels_df],axis=1)
        unscale_labels.columns = ['volume', 'rolling_mean_week', 'rolling_median_week', 
                                  'rolling_max_week', 'total_release', 'projected_volume']

        unscaled_test_labels = scaler.inverse_transform(unscale_labels)
        unscale_labels.loc[:,:] = unscaled_test_labels
        
        observed = unscale_labels.projected_volume
        persistance_prediction = unscale_labels.volume
        
        print('Mean Absolute Percentage Error - Baseline:', round(np.mean(np.abs((observed - persistance_prediction) / observed)) * 100))
        print('Mean Absolute Percentage Error - Bayes:', round(np.mean(np.abs((observed - unscaled_predictions) / observed)) * 100))

    def visualize_weights(self, fit, test_features, selected_features):
        
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
        print('Posterior distribution figure saved for all variables.')
        
        # Visualize and save posteriors for selected features
        posterior_features = melted_weights[melted_weights['variable'].isin(selected_features)]
        g = sns.FacetGrid(posterior_features, col='variable', sharex=False, sharey=False)
        g = g.map(sns.distplot, "value")
        g.savefig('./figures/selected_variable_posteriors.png', dpi = 400)
        print('Posterior distribution figure saved for all variables.')
        
