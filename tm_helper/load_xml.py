

# Import XML parsing module
import pandas as pd
import datetime as dt
import re

class TmParser():

    def __init__(self, verbose=True):
        self.verbose = verbose

    def parse_text(self, tag, text):
        """ Parse out string between a given `<tag>text</tag>` text

        Parameters
        ----------
        tag : str
            XML tag name
        text : str
            text to extract from
        """
        # Define the regex
        rtag = f'.*?<{tag}>(.*?)</{tag}>'
        regex = re.compile(rtag)

        # Join all matches into a single string
        return regex.match(text).groups()        


    def parse_case(self, case_txt):
        """ Parse the case text 
        
        Parameters
        ----------
        case_txt : str
            String of text to be parsed
        """
        # Get the default column name
        row = self.col_dict()

        # ==========
        # Serial number (this is mandatory for all trademarks)
        # ==========
        row['serialNum'] = int(self.parse_text('serial-number', case_txt)[0])
        
        # ==========
        # Status code
        # ==========
        try:
            status = int(self.parse_text('status-code', case_txt)[0])

            # Handle bad status codes
            if status in []:
                return None
            else:
                row['status'] = status
        except:
            row['status'] = None

        # ==========
        # Filing date (may not be valid)
        # ==========
        try:
            date_time_str = self.parse_text('filing-date', case_txt)[0]
            #row['fileDate'] = date_time_str
            row['fileDate'] = dt.datetime.strptime(date_time_str, '%Y%m%d')
        except:
            row['fileDate'] = None

        # ==========
        # Registration date (may not be valid)
        # ==========
        try:
            date_time_str = self.parse_text('registration-date', case_txt)[0]
            row['registrationDate'] = dt.datetime.strptime(date_time_str, '%Y%m%d')
        except:
            row['registrationDate'] = None

        # ==========
        # Extract mark ID (may not be present)
        # ==========
        try:
            #raise ValueError
            row['markId'] = self.parse_text('mark-identification', case_txt)[0]
        except:
            row['markId'] = None

        # ==========
        # Statements
        # ==========
        try:
            stmts = self.parse_text('case-file-statement', case_txt)
            stmts_txt = '; '.join([self.parse_text('text',s)[0] for s in stmts])
            row['descrip'] = stmts_txt
        except:
            row['descrip'] = None

        # ==========
        # Location
        # ==========
        
        try:
            # Get the case-owner text (just get the first)
            case_owner = self.parse_text('case-file-owner', case_txt)[0]

            # City
            row['city'] = self.parse_text('city', case_owner)[0]

            # State
            regex = re.compile(f'.*</city><state>(.*)</state>')
            m = regex.search(case_owner)
            if m:
                row['state'] = m.groups()[0]
            else:
                row['state'] = None

            # Country
            regex = re.compile(f'.*</city><country>(.*)</country>')
            m = regex.search(case_owner)
            if m:
                row['country'] = m.groups()[0]
            else:
                row['country'] = 'US'
        except:
            # No case owner found
            row['city']    = None
            row['state']   = None
            row['country'] = None

        # ==========
        # Classifications
        # ==========
        try:
            #classes = case.select('classifications classification')
            classes = self.parse_text('classification', case_txt)
            clss_list = []
            for clss in classes:
                # Sometimes the code doesn't make sense, so skip it when it doesn't
                #clss_int = int(clss.find('primary-code').text)
                clss_int = int(self.parse_text('primary-code', clss)[0])
                if clss_int > 0 and clss_int < 46:
                    clss_list.append(clss_int)
            
            row['niceClass'] = clss_list
        except:
            # No associated classifications
            row['niceClass'] = None

        return row


    def parse_cases(self, filename):
        # Initialize the dataframe to store the result
        data = dict()

        # Loop through all the cases
        cnt = 0

        # Various regex catches
        open_tag = re.compile(r'<case-file>')
        close_tag = re.compile(r'</case-file>')
        
        # Loop through the file
        with open(filename, 'r') as f:
            case_txt = ''
            for line in f:
                line = line.strip()
                
                # Check if open tag is on the line
                if open_tag.match(line):
                    case_txt = ''

                # Check if open tag is on the line
                elif close_tag.match(line):
                    row = self.parse_case(case_txt)
                    
                    if row is not None:
                        # Append the row using the serial number as the index
                        serialNum = row.pop('serialNum')
                        data[serialNum] = row

                    cnt += 1
                    if (cnt % 100 == 0) and self.verbose:
                        print(f'\rProcessed: {cnt: 8}', end='', flush=True)
                else:
                    case_txt += line

        # Write the final number processed
        if self.verbose:
            print(f'\rFINAL processed: {cnt}')

        #df = pd.DataFrame.from_dict(df, orient='index')

        return data


    def col_names(self):
        """
        """
        # Define the column names
        col_names = ['fileDate','registrationDate','status','serialNum','markId','descrip','niceClass','city','state','country']
        # for i in range(1,46):
        #     col_names.append(f'{i:03d}')
        return col_names


    def col_dict(self):
        """ Return a dict object with associated columns
        """
        # Get the column names
        cols = self.col_names()
        
        # Create the return dict object
        ret = dict()
        for name in cols:
            ret[name] = 0
        return ret


    def init_dataframe(self):
        """
        Build the DataFrame
        """
        #
        df = pd.DataFrame(columns=self.col_names())
        return df
