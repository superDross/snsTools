''' Alter or add elements of/to a seaborn plot
'''
import matplotlib as mpl
# allows one to run matplotlib and seaborn headless (Cygwin)
mpl.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import PIL
import textwrap
from PIL import ImageDraw, ImageFont, Image
import logging


def rename_xtick(df, col, counts=True,  name2label={}, order=[]):
    ''' Get the value counts of each unique entry in the given column
        and store it in a list along with the values name.
        
    Args:
        df: DataFrame
        col: column/category to extract xtick labels and counts from
        counts: whether to display the value counts or not
        order: manually sets the order in which the xticks appear in the plot
        name2label: a dictionary where the key is the current x label and
                    the item is the label to rename it to
        
    Returns:
        list of xtick labels and their value counts 
    
    Notes:
        order only works if the parsed column is not already a category
    
    Example:
        df = sns.load_dataset("tips")
        n = rename_xtick(df, col='day', counts=True)
        ax = sns.violinplot(x="day", y="total_bill", data=df)
        ax.set_xticklabels(n)
    '''
    if not order:
        order = df[col].unique()
   
    if df[col].dtypes.name != 'category':
        df[col] = convert2category(df[col], order)
    
    # store the value counts of the col entries
    sizes = df.groupby(col).size().iteritems()
    
    if counts is True:
        name_count = [(name+"\n"+"n = "+str(n)) for name, n in sizes]
    else:
        name_count = [(name+"\n") for name, n in sizes]
    
    name_change = []
    for info in name_count:
        name = info.split("\n")[0]
        if name in list(name2label.keys()):
            new_name = info.replace(name, name2label.get(name))
            name_change.append(new_name)
        else:
            name_change.append(info)
            
    logging.warning("Ensure xticks are renamed as expected!")                    
    return name_change




def lines_between_plots(df, x1, x2, height, vertical, column, value): 
    ''' Place floating lines between two plots at a given
        height and line height and place a given value about 
        said line.

    Args: 
        x1: x-pos to start from 
        x2: x-pos to end at
        height: y-pos at which the vertical line will begin from
        vertical: length of the vertical lines
        columns: DataFrame column name
        value: string to place atop the horizontal line
        
    Notes:
        taken from http://tinyurl.com/zpjtbjz
    
    Returns:
        lines between two points on an existing plot which uses
        the given df and column data
    '''
    y, h, col = height, vertical, 'k'
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
    plt.text((x1+x2)*.5, y+h, value, ha='center', va='bottom', color=col)



def RoundToSigFigs( x, sigfigs ):
    ''' Rounds the value(s) in x to the number of significant figures in sigfigs.
    
    Args:
        x: float
        sigfigs: number of significant figures

    Note:
        sigfigs must be an integer type and store a positive value.
        x must be a real value or an array like object containing only real values.
    '''
    __logBase10of2 = 3.010299956639811952137388947244930267681898814621085413104274611e-1
    if not ( type(sigfigs) is int or np.issubdtype(sigfigs, np.integer)):
        raise TypeError( "RoundToSigFigs: sigfigs must be an integer." )

    if not np.all(np.isreal( x )):
        raise TypeError( "RoundToSigFigs: all x must be real." )

    if sigfigs <= 0:
        raise ValueError( "RoundtoSigFigs: sigfigs must be positive." )

    mantissas, binaryExponents = np.frexp( x )

    decimalExponents = __logBase10of2 * binaryExponents
    intParts = np.floor(decimalExponents)

    mantissas *= 10.0**(decimalExponents - intParts)

    return np.around( mantissas, decimals=sigfigs - 1 ) * 10.0**intParts



def create_subplot(files, outfile, size=(2000,1600), sub_fig=None, font="Verdana.ttf"):
    ''' Merge multiple images of similar size into one image 
        
    Args:
        files: list of files to merge
        outfile: name of output file
        size: pixel size of the output (width, height)
        sub_fig: add figure number to the corner of each subplot 
        font: font used for sub_fig markings
        
    Returns:
        An image/canvas with all the parsed subplots appended together
        
    Notes:
        sub_fig only works for upto 4 subplots
        
    '''
    # Correct the resolution size given based on average dimensions of all imgs in files
    w, h = correct_size(files, size)
    
    # canvas in which all subplots will be placed upon
    canvas = PIL.Image.new("RGB", (w, h), 'white')
    
    for index, f in enumerate(files):
        # open each individual plot
        img = PIL.Image.open(f)
        
        # alter the height and width for each plot so they can fit snuggly on the canvas
        sub_h = int(h/2) 
        sub_w = int(w/(len(files)/2))
        img.thumbnail((sub_w, sub_h), PIL.Image.ANTIALIAS)
        
        # estimate where the plot will be placed on the canvas
        x = index // 2 * sub_w 
        y = index % 2 * sub_h
        img_w, img_h = img.size # these measurements are diff from sub_h and sub_w, no idea why
        print('pos {0},{1} size {2},{3}'.format(x, y, img_w, img_h))
        canvas.paste(img, (x, y, x + img_w, y + img_h))

    if sub_fig:
        fnt_size = int((w+h)/120)
        fnt = PIL.ImageFont.truetype(font, fnt_size)
        PIL.ImageDraw.Draw(canvas).text((sub_w/40, 0), "a", fill=0, font=fnt)
        PIL.ImageDraw.Draw(canvas).text((sub_w+(sub_w/20), 0), "c", fill=0, font=fnt)
        PIL.ImageDraw.Draw(canvas).text((sub_w/40,sub_h), "b", fill=0, font=fnt)
        PIL.ImageDraw.Draw(canvas).text((sub_w+(sub_w/20),sub_h), "d", fill=0, font=fnt)

    canvas.save(outfile)


def correct_size(f, size):
    ''' Adjust the given size so that the given files can fit 
        closely side by side within a subplot.
    
    Args:
        f: list of image files
        size: resoltion in pixels in a tuple (width, height)
    
    Returns:
        altered size in a tuple
    
    '''
    # get the average width and height for all parsed image files
    avg_w = sum([Image.open(size).size[0]for size in f]) /len(f)
    avg_h = sum([Image.open(size).size[1]for size in f]) /len(f)
    
    # calulate the ratio of width to height and use ratio to recalculate height
    r = avg_w/avg_h
    w, h = size
    h = int((w/r)*(4/len(f)))
    
    return (w, h)
    

def figure_box(f, msg, outfile, extend=100, font="Verdana.ttf", font_size=20, x_text=0):
    ''' Add a figure box label below the given image

    Args:
        f: filename of the image which will be used as input
        msg: message to place in the figure box
        outfile: name of output
        extend: increase the y-axis of the image f by the given number
        font: font type to use
        font_size: font size
        x_text: specify the position where the text begins on the x-axis
    
    '''
    img = PIL.Image.open(f)
    x, y = img.size
    result = PIL.Image.new("RGB", (x, y+extend), 'white')
    result.paste(img, (0, 0))

    fnt = PIL.ImageFont.truetype(font, font_size)
    draw_word_wrap(img=result, text=msg, 
                   xpos=0+x_text, ypos=y, 
                   max_width=x-(x_text*2), font=fnt)


    result.save(outfile)



def draw_word_wrap(img, text, xpos=0, ypos=0, max_width=130, fill=(0,0,0), 
                   font=ImageFont.truetype("Verdana.ttf", 50)):
    ''' Draw the given ``text`` to the x and y position of the image, using
        the minimum length word-wrapping algorithm to restrict the text to
        a pixel width of ``max_width.``

    Args:
        img: image to draw/write upon
        text: message to draw/write
        xpos: x position to begin writing
        ypos: y position to begin writing
        max_width: maximum length on y-axis before text wrapping begins
        fill: text colour
        font: font and font size
    
    Notes:
        Taken from: https://gist.github.com/atorkhov/5403562
    '''

    draw = PIL.ImageDraw.Draw(img)
    text_size_x, text_size_y = draw.textsize(text, font=font)
    remaining = max_width
    space_width, space_height = draw.textsize(' ', font=font)

    # use this list as a stack, push/popping each line
    output_text = []

    # split on whitespace...    
    for word in text.split(None):
        word_width, word_height = draw.textsize(word, font=font)
        if word_width + space_width > remaining:
            output_text.append(word)
            remaining = max_width - word_width
        else:
            if not output_text:
                output_text.append(word)
            else:
                output = output_text.pop()
                output += ' %s' % word
                output_text.append(output)
            remaining = remaining - (word_width + space_width)

    for text in output_text:
        draw.text((xpos, ypos), text, font=font, fill=fill)
        ypos += text_size_y


def convert2grayscale(f):
    ''' Convert a colour image to grascale
    
    Args:
        f: absolute path to file to be converted
        
    Notes:
        This overwrites the original file
    '''
    img = Image.open(f).convert('LA')
    img.save(f)


