
from .tmcodes import TmCodes
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from sklearn.preprocessing import StandardScaler

import pandas as pd
from bokeh.plotting import figure

from statsmodels.tsa.seasonal import seasonal_decompose, STL
from statsmodels.tsa.x13 import x13_arima_analysis, x13_arima_select_order
class TmDataTools:
    
    def __init__(self, figsize=(12,7)):
        self._codes   = TmCodes()
        self._figsize = figsize


    def plot_recessions(self, ax, dtype=float):
        """ Overplot the recession regions
            
        Parameters
        ----------
        ax : matplotlib plot axes
            Axes objects of current plot
        """
        # Load the recession data
        self._codes._load_recessions()

        # Get the x,y axis limits
        ylims = ax.get_ylim()
        xlims = ax.get_xlim()

        # Plot the recession regions
        for index, row in self._codes._recessions.iterrows():
            if dtype is float:
                tmp_xlims = [row.start, row.stop]
            elif dtype is dt.datetime:
                tmp_xlims = [dt.datetime(row.start_year, row.start_month, 15),
                             dt.datetime(row.stop_year, row.stop_month, 15)]
            plt.fill_between(tmp_xlims, [ylims[0],ylims[0]], [ylims[1],ylims[1]], 
                             color='lightgray')
        
        # Reset the plot limits
        ax.set_ylim(ylims)
        ax.set_xlim(xlims)

        return

    def deseason(self, dframe, method='stl', doplot=False):
        """ Compute and remove seasonal effects in the data.

        Parameters
        ----------
        dframe: pandas.DataFrame
            Pandas DataFrame with aggregations applied
        method: str
            Method for removing seasonal variations in the data. Acceptable
            values include: 
            * `stl` : (Default) Use `statsmodels.tsa.seasonal.STL` method
            * `x13` : Use US Census Bureau X-13ARIMA-SEATS software (see note 2)
            * `None`: Return the raw aggregated data
        
        Returns
        -------
        Pandas.DataFrame with seasonal affects removed as best as possible

        Notes
        -----
        1. It's best to supply as much data as possible to this method
        2. When using `method='x13'` the data must be aggregated either monthly
           (`agg='M'`) or quarterly (`agg='Q'`). This method also requires 
           installing the X-13ARIMA-SEATS software and the `statsmodels` python
           module.
        """
        # Do nothing if method is None
        if method is None:
            return dframe

        # Remove seasonal affects in the data
        for col in dframe.columns:
            
            # Interface to the US Census Bureau seasonal adjustment software
            if method.lower() == 'x13':
                results = x13_arima_analysis(dframe[col], trading=False)
                dframe[col] = results.trend
                if doplot:
                    results.plot()
            # Interface to 'statsmodels.tsa.seasonal.STL'
            elif method.lower() == 'stl':
                results = STL(dframe[col], robust=False, seasonal=3).fit()
                dframe[col] = dframe[col]-results.seasonal

                if doplot:
                    results.plot()
        
        return dframe


    def scale_data(self, dframe):
        """ Apply a StandardScaler to each column in dataframe

        Parameters
        ----------
        dframe: pandas.DataFrame
            Pandas DataFrame whos colums will be scaled
        
        Returns
        -------
        Pandas DataFrame with columns scaled
        """
        # Define the scaler object
        scaler = StandardScaler(with_mean=False)
        for col in dframe.columns:
            dframe[col] = scaler.fit_transform(dframe[col].values.reshape(-1,1))

        return dframe


    def get_industries(self, dframe, min_date=None, max_date=None,
                       agg='W', aggmethod='sum',
                       norm=True, method='stl', industries=None,
                       plot_deseason=True):
        """ Get the industry breakdown with options. The process is as follows:

        Parameters
        ----------
        dframe: pd.DataFrame
            Pandas DataFrame object containing industry counts data
        min_date: datetime.datetime
            Minimum date (inclusive) for keeping data (default: None)
        max_date: datetime.datetime
            Maximum date (exclusive) for keeping data (default: None)
        agg: str
            Aggregation metric passed to `pandas.DataFrame.resample`.
        norm: bool
            Whether to normalize the final distributions
        industries: list
            List of specific industries to evaluate
        method: str
            Method for removing seasonal variations in the data (see `TmPlotter.deseason()`).

        Returns
        -------
        Pandas DataFrame containing aggregated, formatted data
        """
        # Get the subset of industries to be plotted
        if (industries is not None) and (industries):
            if dframe.index.name != 'fileDate':
                processed_data = dframe[industries+['fileDate']]
            else:
                processed_data = dframe[industries]
        else:
            processed_data = dframe

        # Set 'fileDate' as index
        if 'fileDate' in processed_data.columns:
            processed_data = processed_data.set_index('fileDate')

        # Trim dates
        if max_date:
            processed_data = processed_data[(processed_data.index < max_date)]
        if min_date:
            processed_data = processed_data[(processed_data.index >= min_date)]

        # Aggregate
        if agg:
            if aggmethod == 'sum':
                processed_data = processed_data.resample(agg).sum()
            elif aggmethod == 'mean':
                processed_data = processed_data.resample(agg).mean()
            elif aggmethod == 'last':
                processed_data = processed_data.resample(agg).last()

        # Remove seasonal affects in the data
        processed_data = self.deseason(processed_data, method=method, 
                                       doplot=plot_deseason)

        # Check if we want to normalize
        if norm:
            processed_data = self.scale_data(processed_data)

        return processed_data

    def plot_industries(self, dframe, recess=True, norm=False, highlight=None):
        """ Plot the industry breakdown with options. The process is as follows:

        Parameters
        ----------
        dframe: pd.DataFrame
            Pandas DataFrame object containing industry counts data
        recess: bool
            Overplot recession dates
        """
        # normalize if requested
        plot_data = dframe.copy()
        if norm:
            plot_data = self.scale_data(plot_data) 

        # Now do the plotting
        if highlight is None:
            ax = plot_data.plot(figsize=self._figsize)
        else:
            name_color = highlight.split(':')
            highlight_col = plot_data[[highlight]]
            plot_data = plot_data.drop([highlight], axis=1)
            ax = plot_data.plot(figsize=self._figsize, color='gray',legend=False)
            highlight_col.plot(ax=ax, color='red')

        # Add y-grid lines
        ax.yaxis.grid()

        # Add x-axis labels
        plt.xlabel(plot_data.index.name)

        # Plot recession dates on the plot
        if recess:
            self.plot_recessions(ax, dtype=dt.datetime)

        return ax


    #def get_subset(self, df,nrows,min_date, max_date):



    def get_subsets(self, primary_df,
                    nrows_primary=3,
                    min_date=dt.datetime(1980,1,1),
                    max_date=None):
        """ Chop data from each dataset up into datasets

        Parameters
        ----------
        primary_df: pandas.DataFrame()
            Primary dataframe
        nrows_primary: int
            Number of rows 
        Returns
        -------
        """
        pdf_cpy = primary_df.copy()

        # Normalize the values in the primary dataframe
        for d,date in enumerate(pdf_cpy.index):
            if d == 0:
                continue
            # Precompute the scaled data values
            pdf_cpy.iloc[d] = (primary_df.iloc[d] - primary_df.iloc[d-1]) / abs(primary_df.iloc[d-1])
            
        # Slice the data into subsets
        datasets = []
        dates    = []
        for d,date in enumerate(pdf_cpy.index):
            
            # Skip it if date is too low
            if date < min_date:
                continue
            # Finish if date is too large
            elif (max_date is not None) and date >= max_date:
                break
            
            # Compute the distribution of the lastest nrows
            start = d-nrows_primary
            ind_values = []
            for c,col in enumerate(pdf_cpy.columns):

                primary_vals = pdf_cpy.iloc[start:d,c].values
                ind_values.append(primary_vals.reshape(-1))
                dates.append(date)
                
            datasets.extend(ind_values)
        return np.array(datasets), dates


    def market_change(self, markets, dates, 
                      forecast_time=dt.timedelta(weeks=0),
                      backcast_time=dt.timedelta(weeks=0),
                      up_or_down=True,
                      norm=True):

        # Normalize the market data
        if norm:
            normed = self.scale_data(markets)
        else:
            normed = markets

        labels = np.zeros(len(dates))

        # Return the requested values
        for d,date in enumerate(dates):
            backcast = date + backcast_time
            forecast = date + forecast_time
            
            # Average of the market indices
            cur_val = np.mean(normed[normed.index >= backcast].iloc[0].values)
            future_val = np.mean(normed[normed.index >= forecast].iloc[0].values)
            labels[d] = future_val-cur_val

            #print(backcast, forecast, labels[d])

        # Check if we just want the up or down status of the indices
        if up_or_down:
            labels = np.array([int(l<=0) for l in labels])

        return labels