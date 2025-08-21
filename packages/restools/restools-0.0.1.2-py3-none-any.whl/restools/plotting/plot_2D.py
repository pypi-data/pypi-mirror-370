import sys
import os
import numpy
import argparse
import datetime
import matplotlib.pyplot as plt

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    from math import factorial
    try:
        window_size = numpy.abs(numpy.int32(window_size))
        order = numpy.abs(numpy.int32(order))
    except Exception as e:
        raise ValueError("window_size and order have to be of type int", e)
    
    window_size = min(window_size, len(y) // 4 * 2 + 1)

    assert window_size > 0, "Window size must be greater than zero"
    assert window_size % 2 == 1, "Window size must be odd"
    assert window_size >= order + 2, "Window size is too small for the polynomials order"

    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = numpy.asmatrix([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = numpy.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)

    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[1:half_window+1][::-1]
    lastvals = y[-half_window-1:-1][::-1]
    y = numpy.concatenate((firstvals, y, lastvals))
    return numpy.convolve( m[::-1], y, mode='valid')

def plot_2D(ax, x, y, color, lab, y_min=None, y_max=None, y_var=None, is_smoothed=False, line_type='line', alpha=1.0, smooth_window=100):
    if(y_min is None):
        clip_min = -1.0e+10
    else:
        clip_min = y_min

    if(y_max is None):
        clip_max = 1.0e+10
    else:
        clip_max = y_max

    if(is_smoothed):
        y_mean = savitzky_golay(y, smooth_window + 1, 3)
    else:
        y_mean = y

    if(is_smoothed and y_var is not None):
        print("Setting both is_smoothed and is_shaded to true is not recommended")

    if(line_type == 'line'):
        lt = '-'
    elif(line_type == 'dot'):
        lt = '.'
    else:
        raise Exception(f"No such line type {line_type}")

    ax.plot(x, numpy.clip(y_mean, clip_min, clip_max), lt, color=color, label=lab, alpha=alpha)
    if(is_smoothed):
        ax.plot(x, numpy.clip(y, clip_min, clip_max), lt, color=color, alpha=0.10)

    if(y_var is not None):
        ax.fill_between(x,
            numpy.clip(y_mean - y_var, clip_min, clip_max),
            numpy.clip(y_mean + y_var, clip_min, clip_max),
            color=color, alpha=0.15)

def extract_from_file(file_name, x_col=None, y_col=None, x_min=None, x_max=None, y_var_col=None, separator=None):
    x_arr = []
    y_arr = []

    if(y_var_col is None):
        y_var_arr = None
    else:
        y_var_arr = []

    if(y_col is None):
        print("Y Column can not be None, Set To Column 0")
        y_col = 0
    max_col = y_col
    if(x_col is not None):
        max_col = max(x_col, max_col)
        use_line_x = False
    else:
        print("X Column not specified, use the line number as default")
        use_line_x = True
    if(y_var_col is not None):
        max_col = max(y_var_col, max_col)

    if(x_min is None):
        x_min = -1.0e+10
    if(x_max is None):
        x_max = 1.0e+10

    with open(file_name, "r") as fin:
        line_idx = 0
        for line in fin.readlines():
            line_idx += 1
            toks = line.strip().split(separator)
            if(len(toks) < max_col):
                print(f"Encountering number of tokens < columns used in line {line_idx}, skip")
                continue
            try:
                if(use_line_x):
                    x = line_idx
                else:
                    x = float(toks[x_col])
                if(x < x_min or x > x_max):
                    print(f"Skipping {x} which is not between x_min={x_min} and x_max={x_max}")
                    continue
                x_arr.append(x)
                y_arr.append(float(toks[y_col]))
                if(y_var_col is not None):
                    y_var_arr.append(float(toks[y_var_col]))
            except Exception:
                print(f"Unexpected Error in {line_idx}, skip")
                continue
    xs = numpy.array(x_arr)
    ys = numpy.array(y_arr)
    if(y_var_col is None):
        yvs = None
    else:
        yvs = numpy.array(y_var_arr)
    return xs, ys, yvs

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--outputs', type=str, default="output.pdf", help="output file name")
    parser.add_argument('--inputs', nargs='*', help="List of all inputs, in the format of filename:x_col:y_col:y_var:label:color")
    parser.add_argument('--xlabel', type=str, default=None, help="Label of X axis, if None it is empty")
    parser.add_argument('--ylabel', type=str, default=None, help="Label of Y axis, if None it is empty")
    parser.add_argument('--xscale', type=str, choices=['linear', 'log'], default='linear', help="Linear/Log Axis, default is Linear")
    parser.add_argument('--yscale', type=str, choices=['linear', 'log'], default='linear', help="Linear/Log Axis, default is Linear")
    parser.add_argument('--separator', type=str, default=None, help="Separator for columns")
    parser.add_argument('--x_min', type=float, default=None, help="Skip the data points < x_min")
    parser.add_argument('--x_max', type=float, default=None, help="Skip the data points > x_max")
    parser.add_argument('--y_min', type=float, default=None, help="Skip the data points < x_min")
    parser.add_argument('--y_max', type=float, default=None, help="Skip the data points > x_max")
    parser.add_argument('--x_axis', type=str, default=None, help="Speicify the range of x axis, e.g., 1,1000")
    parser.add_argument('--y_axis', type=str, default=None, help="Speicify the range of y axis, e.g., 0,10")
    parser.add_argument('--title', type=str, default=None, help="Specify the titles")
    parser.add_argument('--opacity', type=float, default=1.0, help="Specify the opacity, default is 1.0")
    parser.add_argument('--linetype', type=str, choices=['line', 'dot'], default='line', help="Specify the line type, default is line")
    parser.add_argument('--labelfont', type=int, default=16, help="Specify the font of labels (axis)")
    parser.add_argument('--legendfont', type=int, default=16, help="Speicify the font of legend")
    parser.add_argument('--titlefont', type=int, default=16, help="Speicify the font of title")
    parser.add_argument('--smooth', type=str, choices=['true','false'], default='false', help="whether to run savitzky golay smooth for the curve")
    parser.add_argument('--smooth_window', type=int, default=100, help="window size for Savitzky Golay Smooth")


    args = parser.parse_args()

    default_color = ["red", "green", "blue", "black", "purple", "brown", "gray", "orange"]

    if(args.inputs is None):
        raise Exception("Must specify --inputs to plot")

    fig, ax = plt.subplots()
    ax.set_xscale(args.xscale)
    ax.set_yscale(args.yscale)
    ax.set_xlabel(args.xlabel, fontsize=args.labelfont)
    ax.set_ylabel(args.ylabel, fontsize=args.labelfont)

    if(args.y_axis is not None):
        y_tok = list(map(float, args.y_axis.split(",")))
        plt.ylim(y_tok[0], y_tok[1])

    if(args.x_axis is not None):
        x_tok = list(map(float, args.x_axis.split(",")))
        plt.xlim(x_tok[0], x_tok[1])

    for cmd_idx, cmd in enumerate(args.inputs):
        input_tok = cmd.split(":")
        if(len(input_tok) != 6):
            raise Exception(f"Commands ({cmd}) is not in the format of file_name:x_col:y_col:y_var:label:color")
        file_name = input_tok[0]
        if(len(input_tok[1].strip())<1):
            x_col = None
        else:
            x_col = int(input_tok[1])
        if(len(input_tok[2].strip())<1):
            y_col = None
        else:
            y_col = int(input_tok[2])
        if(len(input_tok[3].strip())<1):
            y_var = None
        else:
            y_var = int(input_tok[3])
        label = input_tok[4]
        if(len(input_tok[5].strip())<1):
            color = default_color[cmd_idx]
            print(f"Color not specified, use default color {color} for {file_name}:{x_col}:{y_col}")
        else:
            color = input_tok[5]

        # Extract Relative Information
        x, y, yvar = extract_from_file(file_name, x_col=x_col, y_col=y_col, x_min=args.x_min, x_max=args.x_max, y_var_col=y_var, separator=args.separator)

        # Plot the 2D Curve
        if(args.smooth == 'false'):
            smooth = False
        else:
            smooth = True
        plot_2D(ax, x, y, color, label, 
                y_min=args.y_min, 
                y_max=args.y_max, 
                y_var=yvar, 
                is_smoothed=smooth, 
                line_type=args.linetype, 
                alpha=args.opacity,
                smooth_window=args.smooth_window)

    handles, labels = ax.get_legend_handles_labels()

    if(args.legendfont > 0):
        ax.legend(handles, labels)
        ax.legend(fontsize=args.legendfont)

    if(args.title is not None):
        ax.set_title(args.title, fontsize=args.titlefont)

    plt.tight_layout()
    plt.savefig(args.outputs)
