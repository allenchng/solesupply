import pandas as pd
import numpy as np

def preproc_data(data_path):

        # Load data

        data = pd.read_csv(data_path, index_col=0)

        # Calculate daily transactions

        data.createdAt = data.createdAt.str.replace('T', ' ')
        
        data.createdAt = data.createdAt.str.split(' ').str[0]
        data.createdAt = pd.to_datetime(data.createdAt)

        time_data = data.loc[:, ('sku', 'createdAt')]
        ordered_data = time_data.sort_values('createdAt')

        daily_count = ordered_data.groupby('createdAt').count()
        daily_count['date'] = daily_count.index
        daily_count = daily_count.reset_index().loc[:, ('sku', 'date')]
        daily_count.columns = ['volume', 'date']
        daily_count.date = pd.to_datetime(daily_count.date)

        return(daily_count)

def make_data(path, days_rolling, days_forward):
    
    daily_transactions = preproc_data(path)
    
    # Extract date information from transaction data

    daily_transactions['day_of_week'] = daily_transactions['date'].dt.day_name()
    daily_transactions['month'] = daily_transactions['date'].dt.month_name()
    daily_transactions['year'] = daily_transactions['date'].dt.year
    daily_transactions['year'] = daily_transactions['year'].astype('category')
    
    # Calculate moving average metrics
    
    daily_transactions['rolling_mean_week'] = daily_transactions['volume'].rolling(days_rolling).mean()
    daily_transactions['rolling_median_week'] = daily_transactions['volume'].rolling(days_rolling).median()
    daily_transactions['rolling_max_week'] = daily_transactions['volume'].rolling(days_rolling).max()
    daily_transactions['projected_volume'] = daily_transactions.volume.shift(-days_forward)
    
    # Create predictor for holidays
    non_federal_holidays = ['2017-10-31', '2018-10-31', '2017-11-24', '2017-11-25', '2017-11-26', '2018-11-23', 
                            '2018-11-24', '2018-11-25', '2017-12-26', '2017-12-27', '2017-12-28', '2017-12-29',
                            '2017-12-30', '2018-12-26', '2018-12-27', '2017-12-28', '2018-12-29', '2017-12-30']
    

    daily_transactions['holiday'] = daily_transactions['date'].isin(non_federal_holidays).astype(int)
    
    # Load sneaker releases data

    sneaker_releases = pd.read_csv('../big_data/sneaker_metadata_collab.csv')
    sneaker_releases['date'] = sneaker_releases.releaseDate.str.split(' ').str[0]
    
    # Create features for special collaborations
    
    sneaker_releases['is_retro'] = sneaker_releases.model.str.contains('Retro').astype(int)
    sneaker_releases['is_yeezy'] = sneaker_releases.model.str.contains('Yeezy').astype(int)
    sneaker_releases['is_travis_scott'] = sneaker_releases.name.str.contains('Travis Scott').astype(int)
    sneaker_releases['is_off_white'] = sneaker_releases.name.str.contains('Off-White').astype(int)
    
    special_releases = sneaker_releases.loc[:, ('is_retro', 'is_yeezy', 'is_travis_scott', 'is_off_white', 'date')]
    
    special_releases = special_releases.groupby('date').sum()
    special_releases['date'] = special_releases.index
    special_releases = special_releases.reset_index(drop=True)
    special_releases.date = pd.to_datetime(special_releases.date)

    # Merge releases with daily transaction data
    
    daily_transactions = pd.merge(daily_transactions, special_releases, how = 'left', on = 'date')

    daily_transactions.is_retro = daily_transactions.is_retro.fillna(0)
    daily_transactions.is_yeezy = daily_transactions.is_yeezy.fillna(0)
    daily_transactions.is_travis_scott = daily_transactions.is_travis_scott.fillna(0)
    daily_transactions.is_off_white = daily_transactions.is_off_white.fillna(0)

    # Shift releases to correspond to prediction

    daily_transactions['is_retro'] = daily_transactions['is_retro'].shift(-days_forward)
    daily_transactions['is_yeezy'] = daily_transactions['is_yeezy'].shift(-days_forward)
    daily_transactions['is_travis_scott'] = daily_transactions['is_travis_scott'].shift(-days_forward)
    daily_transactions['is_off_white'] = daily_transactions['is_off_white'].shift(-days_forward)
    
    # Get total releases on a day

    release_dates = sneaker_releases.loc[:, ('brand', 'releaseDate')]

    release_dates.releaseDate = release_dates.releaseDate.str.split(' ').str[0]
    
    grouped_release = release_dates.groupby('releaseDate').count()
    grouped_release['date'] = grouped_release.index
    grouped_release.date = pd.to_datetime(grouped_release.date)
    grouped_release = grouped_release.reset_index(drop=True)
    grouped_release.columns = ['total_release', 'date']
    
    merged_release = pd.merge(daily_transactions, grouped_release, how = 'left', on='date')
    merged_release.total_release = merged_release.total_release.fillna(0)
    
    merged_release['total_release'] = merged_release['total_release'].shift(-days_forward)

    return merged_release