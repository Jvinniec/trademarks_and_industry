import os
import pandas as pd


class TmCodeError(ValueError):
    pass


class TmCodes:

    def __init__(self):
        """ Create storage objects for all of the codes
        """
        self._countries    = None
        self._nice_classes = None
        self._industries   = None
        self._recessions   = None
        self._status       = None

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


    def _load_nice_classes(self):
        """ Loads the nice classifications
        """
        # Check if the nice classifications have been loaded
        if self._nice_classes is None:
            self._nice_classes = self._load_codes('nice_classifications.csv',
                                                  index_col='id')
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
        return


    def _load_status(self):
        """ Load data on USPTO trademark status codes
        """
        # Check if status codes have been loaded
        if self._status is None:
            self._status = self._load_codes('status_codes.csv', 
                                            index_col='code')
        return

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
            industry_code = int(self._nice_classes.loc[nice_code, 'industry_id'])
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
