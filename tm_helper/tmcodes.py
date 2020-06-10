import os
import pandas as pd
import numpy as np
import datetime as dt


class TmCodeError(ValueError):
    pass


class TmCodes:

    def __init__(self):
        """ Create storage objects for all of the codes
        """
        self._countries    = None
        self._states       = None
        self._nice_classes = None
        self._industries   = None
        self._recessions   = None
        self._status       = None

        # Some helper things
        self._nice_to_ind = None

        # Define the directory containing the codes
        self.codes_dir = os.path.dirname(os.path.abspath(__file__)) + '/codes/'


    def _load_codes(self, filename, index_col=None):
        """ Loads the codes from `filename` into a pandas dataframe

        Parameters
        ----------
        filename: `str`
            Filename for codes to be loaded
        index_col: `str` or `int`
            Which column in file to use as index column
        
        Returns
        -------
        Extracted code parameters in a `pandas.DataFrame` object
        """
        return pd.read_csv(self.codes_dir + filename, 
                           index_col=index_col,
                           skipinitialspace=True) 


    def _load_countries(self):
        """ Loads the country codes
        """
        # Load the country if 
        if self._countries is None:
            self._countries = self._load_codes('country_codes.csv', 
                                               index_col='code')
        return

    def _load_states(self):
        """ Loads the country codes
        """
        # Load the country if 
        if self._states is None:
            self._states = self._load_codes('state_codes.csv')
        return


    def _load_nice_classes(self):
        """ Loads the nice classifications
        """
        # Check if the nice classifications have been loaded
        if self._nice_classes is None:
            print('LOADING NICE CLASSIFICATIONS')
            self._nice_classes = self._load_codes('nice_classifications.csv',
                                                  index_col='id')
            # Convenience for nice_class -> industry
            self._nice_to_ind = [int(self._nice_classes.loc[n,'industry_id']) for n in self._nice_classes.index]
        return


    def _load_industries(self):
        """ Loads the nice industry classifications
        """
        # Check if nice industry codes have been loaded
        if self._industries is None:
            self._industries = self._load_codes('nice_industry.csv', 
                                                index_col='id')
        return


    def _load_recessions(self):
        """ Load data on recent major market drops
        """
        # Check if recession data has been loaded
        if self._recessions is None:
            self._recessions = self._load_codes('recessions.csv', 
                                                index_col=None)

            # Define a few start/stop year values
            start,stop = [],[]
            for i in self._recessions.index:
                # Start time
                start_y = self._recessions.loc[i,'start_year']
                start_m = self._recessions.loc[i,'start_month'] - 0.5
                start.append(start_y + start_m/12)
                
                # Stop time
                stop_y = int(self._recessions.loc[i,'stop_year'])
                stop_m = int(self._recessions.loc[i,'stop_month'] - 0.5)
                stop.append(stop_y + stop_m/12)
            
            self._recessions['start'] = start
            self._recessions['stop'] = stop

        return


    def _load_status(self):
        """ Load data on USPTO trademark status codes
        """
        # Check if status codes have been loaded
        if self._status is None:
            self._status = self._load_codes('status_codes.csv', 
                                            index_col='code')
        return

    def state_id(self, abbrv):
        """ Returns a country name from a 2-letter abbreviation

        Parameters
        ----------
        abbrv: `str`
            2-letter state abbreviation
        
        Returns
        -------
        id associated with state
        """
        # Load the state codes
        self._load_states()

        # Try to extract the state id
        try:
            state_id = (self._states['abbr'] == abbrv)[0]
            return state_id
        except Exception as e:
            raise TmCodeError(e)

    def country(self, abbrv):
        """ Returns a country name from a 2-letter abbreviation

        Parameters
        ----------
        abbrv: `str`
            2-letter country abbreviation
        
        Returns
        -------
        Full name of country associated with `abbrv`
        """
        # Load the country codes
        self._load_countries()

        # Try to extract the country code
        try:
            country = str(self._countries.loc[abbrv, 'country'])
        except Exception as e:
            raise TmCodeError(e)

        return country


    def industry(self, ind_code):
        """ Returns a short name of industry associated with `industry_code`

        Parameters
        ----------
        ind_code : `int`
            Integer representing industry code

        Returns
        -------
        String containing a name of the supplied `ind_code`
        """
        # Load the nice classifications
        self._load_industries()

        # Extract the industry name
        try:
            ind_name = str(self._industries.loc[ind_code, 'name'])
        except Exception as e:
            raise TmCodeError(e)

        return ind_name


    def nice_to_industry(self, nice_code):
        """ Returns an industry code from a Nice Classification code. A short 
        description of the industry can be obtained using:
            TmCodes().industry(code)

        Parameters
        ----------
        nice_code : `int`
            Integer representing Nice Classification code

        Returns
        -------
        Industry code associated with `nice_code`
        """
        # Load the nice classification codes
        self._load_nice_classes()
        
        # Try to extract the industry code
        try:
            industry_code = self._nice_to_ind[nice_code-1]
        except Exception as e:
            raise TmCodeError(e)

        return industry_code


    def nice_class_descrip(self, nice_code):
        """ Return a description given a nice_code.

        Parameters
        ----------
        nice_code : `int`
            Integer representing Nice Classification code

        Returns
        -------
        String containing a description of the supplied `nice_code`
        """
        # Load the nice classifications
        self._load_nice_classes()

        # Extract the classification description
        try:
            descrip = str(self._nice_classes.loc[nice_code, 'classDescrip'])
        except Exception as e:
            raise TmCodeError(e)

        return descrip


    def is_recession(self, dates, forecast_time=dt.timedelta(days=0)):
        """ Return a list of whether the `dates+forecast_time` is during a recession

        Parameters
        ----------
        dates: list of datetime.datetime
            Dates to query
        forecast_time: datetime.timedelta
            Forecast timeline
        
        Returns
        -------
        List of 1/0 if `dates+forecast_time` is/isn't during a recession
        """
        # Load recession data
        self._load_recessions()

        # Make the dates a list object
        if not isinstance(dates, list):
            dates = [dates]

        # Define the results list
        results = np.zeros(len(dates), dtype=int)

        # Loop on all passed dates
        for d,date in enumerate(dates):
            # Get the date to forecast
            test_date = date + forecast_time

            # Loop on all the recession dates
            for index, row in self._recessions.iterrows():
                start = dt.datetime(row.start_year, row.start_month, 1)
                stop  = dt.datetime(row.stop_year, row.stop_month, 28)

                # Check if test_date falls in this recession
                if start < test_date < stop:
                    results[d] = 1
                    break

        return results