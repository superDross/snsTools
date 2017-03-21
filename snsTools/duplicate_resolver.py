import numpy as np
import logging

def duplicate_resolver(df, col, column_list, dup_ends=['_2','_3', '_pool7A', '_pool10A'], warn=True):
    ''' Identify duplicate values in a given column and forward-fill the 
        missing data in the a given column list and subsequently 
        remove any rows that have missing data in all the cells
        in the column list.
    
    Args:
        df: DataFrame
        col: column of the df to check for duplicates
        column_list: the list of columns to check for missing data
        dup_end: characters which seperate the original and duplicate sample
        warn: print a warning detailing the col values
        
    Returns:
        modified df 
    
    Notes:
        if dup_ends = ['_2'] then GH and GH_2 in the given col would be considered
        duplicates
    '''
    # duplicate samples with different phenotype information are dealt with here 
    df = duplicate_column_checker(df, column_list, column=col)

    # get index numbers for all column in the list and filter out rows that have no data in these fields
    col_list_ix = [df.columns.get_loc(x) for x in column_list]
    remove_rows = df.apply(lambda x: identify_null_data(x, col_list_ix), axis=1)
    new_df = df[remove_rows]
    
    # warn user of removed rows 
    if warn:
        removed_rows_values = " ".join(df[~remove_rows][col].tolist())
        logging.warning("The rows containing the following values in column '{}' have been removed:\n{}".format(col, removed_rows_values))
    
    return new_df


def identify_null_data(x, col_ix):
    ''' Check whether we have any data in the fields in the given column indexes.

    Args:
        col_ix: a list of column indexes to be investigated for differences between duplicate samples
    
    Returns:
        False if only null or dash is present in the rows selected column, else True
    
    Notes:
        This function is intended to be used via the apply function in pandas e.g.
                df.apply(lambda x: identify_null_data(x, col_ix), axis=1)

    '''
    # start from column (index) and convert to a list and filter out duplicate values and NaNs
    column_cells = x[col_ix].tolist()
    all_row_cell_values = set([z for z in column_cells if str(z) != 'nan'])
    
    
    if len(all_row_cell_values) == 1 and "-" in all_row_cell_values:
        return False
    elif len(all_row_cell_values) == 0:
        return False
    else:
        return True



def duplicate_column_checker(df, columns_names, order=False, recurs=2, dup_ends=['_2','_3', '_pool7A', '_pool10A'],
                             column="Sample"):
    ''' Identify duplicate samples and verify whether they have the same data stored in the given columns.
        If one duplicate has NaN in its phenotype fields then copy the phenotype data from the
        other duplicate sample. If there are still differences between them, then report to user.

    Args:
        column_names: a list of column names to be investigated for differences between duplicates
        order: ascending - True or False
        recurs: utilised to stop the recursive function
        dup_end: characters which seperate the original and duplicate sample
        column: column in which to search & identify whether samples are duplicates

    Returns:
        a dataframe in which the duplicates differences in the given columns have been resolved 
        and/or communicated to the user
    '''    
    if recurs < 1:
        return df
    
    # replace all dashes with NaN
    df = df.replace('-', np.nan)
    
    # Identify which samples are duplicates and fill in a new column with the original samples name. This way all duplicates have the orginal sample name in its row.
    for dup in dup_ends:
        cond = ((df[column].str.endswith(dup)) & (df[column].str.len() > 4))
        df.ix[cond, 'same'] = df.ix[cond, column].str[:-(len(dup))]

    # replace NaN in same by entries in column
    df.same = df.same.combine_first(df[column])

    # sort columns first on same then column. column is reversed upon the funcs recursion
    df = df.sort_values(by=['same', column], ascending=[False, order]).reset_index()
    
    # get the clumn indexes for the given column names
    col_ix = [df.columns.get_loc(x) for x in columns_names]
        
    # assess whether the sample names in a row and the following row are duplicates and, if so, forward fill the fields described in column names
    for num in range(0, df.shape[0]-1):
        
        current_sam = df['same'].shift(-(num))[0]
        next_sam = df['same'].shift(-(num+1))[0]

        if current_sam == next_sam:
            
            df.iloc[num:num+2, col_ix] = df.iloc[num:num+2, col_ix].ffill(limit=1)
    
    #remove column index
    df.drop(['index'], axis=1, inplace=True)
    
    # do the same but reverse the order of secondary order
    return duplicate_column_checker(df, columns_names, order=True, recurs=recurs-1, dup_ends=dup_ends)
 
    
    
