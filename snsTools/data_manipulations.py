''' Collection of functions to manipulate common tasks in Pandas DataFrames
'''
import pandas as pd

def convert2category(column, label_order):
    ''' convert column to a category and set the order of the labels
    '''
    convert = pd.Series(column, dtype="category")
    structured_cat = convert.cat.set_categories(label_order)
    return structured_cat

def replace_series_strings(df, col, dic, substring=True):
    ''' Replace the the keys with the items of the given 
        dictionary for all strings or substrings in a
        given column

    Args:
        col: column name to replace strings
        dic: dictionary where the key is the string to replace with the item
        substrings: search and replace for either substrings (True) or any cell 
                    containing the given key (False)

    Returns:
        dataframe with the given column having all the
        entries identified as the key in the given dict
        replaced with the item in said dict
    '''
    if not isinstance(substring, bool):
        raise TypeError("substring argument must equal True or False")

    for string, correction in dic.items():
        if substring is True:
            df[col] = df[col].str.replace(string, correction)
        elif substring is False:
            df[col] = df[col].replace(".*"+string+".*", correction, regex=True)

    return df

