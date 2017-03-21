from scipy import stats
import plot_manipulations as pm

def grouped_piechart(df, group, qual, font_size=13, title="",
                   colors=['salmon', 'turquoise',  'silver', 'white'], 
                   outfile=None):
    ''' Split a dataframe into two groups and plot the data from the given column (qual)
        on a piechart side-by-side and perform the appropriate statistical test to get a
        pvalue.
    
    Args: 
        df: Pandas DataFrame
        group: a column in df containing categorical data that has two unique values
        qual: a column in df containing categorical data
        font_size: fontsize for labels
        title: title of plot
        colors: list of colors for piechart segments to parse to matplotlib
        outfile: image output file name
    
    Returns:
        matplotlib piechart
    '''
    # drop rows without values in group and fill in missing data in qual
    df = df.dropna(subset = [group])
    df[qual] = df[qual].fillna(value='Unknown')
    
    # figure size, background color to white (0), title, label font sizez and get labels
    ax = plt.figure(figsize=(15,12), facecolor="1").gca()
    plt.tick_params(axis='both', which='major', labelsize=13.5) # xtick label sizes
    plt.title(title, fontsize=font_size*2) 
    mpl.rcParams['font.size'] = font_size
    divisions = df[qual].unique()
    
    # get the percentages of the qual counts in each group, remove if qual not present in group, and plot them as piecharts
    group1 = df[df[group] == df[group].unique()[0]]
    group1_percent = [len(group1[group1[qual] == x]) / len(group1) for x in divisions]
    group1_percent, names = remove_zeros(group1_percent, divisions)
    ax.pie(group1_percent, labels=names,
            colors=colors, shadow=False, autopct='%1.1f%%', 
            center=(0,0), startangle=90) 
    
    group2 = df[df[group] == df[group].unique()[1]]
    group2_percent = [len(group2[group2[qual] == x]) / len(group2) for x in divisions]
    group2_percent, names = remove_zeros(group2_percent, divisions)
    ax.pie(group2_percent, labels=names,
           colors=colors, shadow=False, autopct='%1.1f%%', 
           center=(2.5,0), startangle=90)
        
    # set the x ticks and labels 
    ax.axis('equal')
    ax.set_xticks([0, 2.5])
    xticklabels = ["{}:\nn = {}".format(x,len(df[df[group] == x ])) for x in df[group].unique()]
    ax.set_xticklabels(xticklabels)
    ax.tick_params(labelsize=font_size)
    
    # create a table for statistical testing and generate pvalue between the two groups
    table = df.groupby([group, qual]).size().unstack(1).fillna(0.0)
    array = table.values.tolist()
    if len(divisions) == 2:
        oddsratio, pvalue = stats.fisher_exact(array)
    else:
        chi2, pvalue, dof, expected = stats.chi2_contingency(array)
        
    pm.lines_between_plots(df, 0,2.5,1.5, 0.1, "l", "p = "+str(round(pvalue,3)))

    # decide whether to save or not
    if outfile:
        ax.figure.savefig(outfile)
        pass
    

    
def remove_zeros(percent, strings):
    ''' Identify any zeros in percent, get their
        indexes and remove the values in percent 
        and strings with said indexes.
    
    Args:
        percent: list of integers
        strings: list of strings
    '''
    if 0 in percent:
        index = [x[0] for x in enumerate(percent) if x[1] == 0][0]
        strings = list(strings[:index]) + list(strings[index+1 :])
        percent = percent[:index] + percent[index+1:]
        return remove_zeros(percent, strings)

    else:
        return (percent, strings)


