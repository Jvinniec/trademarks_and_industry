

# Import XML parsing module
import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt


def load_cases(filename):
    """
    Load data from an xml object downloaded from the USPTO website

    Parameters
    ----------
    filename: str
        Name of the xml file to read from
    """
    # Extract the tree from the file
    tree = ET.parse(filename)
    
    # Drill down to the case files
    app_info = tree.getroot().find('application-information')
    file_seg = app_info.find('file-segments')
    act_keys = file_seg.find('action-keys')
    
    # Return the actual case files
    return act_keys.findall('case-file')


def col_names():
    """
    """
    # Define the column names
    col_names = ['fileDate','serialNum','markId','descrip']
    for i in range(1,46):
        col_names.append(f'{i:03d}')
    return col_names


def col_dict():
    """ Return a dict object with associated columns
    """
    # Get the column names
    cols = col_names()
    
    # Create the return dict object
    ret = dict()
    for name in cols:
        ret[name] = 0
    return ret


def init_dataframe():
    """
    Build the DataFrame
    """
    #
    df = pd.DataFrame(columns=col_names())
    return df


def parse_cases(filename):
    """
    Parse the case files into individual entries in a Pandas.DataFrame
    """
    # Load the individual case files
    #tree  = load_xml(filename)
    cases = load_cases(filename)

    # Initialize the dataframe to store the result
    df = init_dataframe()

    # Loop through all the cases
    cnt = 0
    for case in cases:
        # Get the default column name
        row = col_dict()

        # Serial number
        row['serialNum'] = int(case.find('serial-number').text)

        # Filing date (may not be valid)
        header = case.find('case-file-header')
        try:
            date_time_str = header.find('filing-date').text
            row['fileDate'] = dt.datetime.strptime(date_time_str, '%Y%m%d')
        except:
            row['fileDate'] = None

        # Extract mark ID (may not be present)
        try:
            raise ValueError
            row['markId'] = header.find('mark-identification').text
        except:
            row['markId'] = None

        # Statements
        try:
            raise ValueError
            statements = case.find('case-file-statements').findall('case-file-statement')
            row['descrip'] = ' '.join([statement.find('text').text for statement in statements])
        except:
            row['descrip'] = None

        # Classifications
        try:
            classes = case.find('classifications').findall('classification')
            for clss in classes:
                # Sometimes the code doesn't make sense, so skip it when it doesn't
                clss_txt = clss.find('primary-code').text
                if clss_txt in row:
                    row[clss_txt] = 1
        except:
            # No associated classifications
            pass

        cnt += 1
        if cnt % 100 == 0:
            print(row['serialNum'])
        
        # Append the row using the serial number as the index
        df.loc[row['serialNum']] = row
        
        
    return df
 