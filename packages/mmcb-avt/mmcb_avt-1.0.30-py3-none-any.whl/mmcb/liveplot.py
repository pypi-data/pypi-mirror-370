#!/usr/bin/env python3
"""
Plots live data outputted by iv.py in a window that persists over multiple
runs of iv.py.

Uses ZeroMQ REQ/REP for communication.
"""

import argparse
import gc
import itertools
import multiprocessing as mp    # Process, Queue
import sys
import threading
import time

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import EngFormatter
import zmq


##############################################################################
# command line option handler
##############################################################################

def check_arguments():
    """
    handle command line options

    --------------------------------------------------------------------------
    args : none
    --------------------------------------------------------------------------
    returns : bool
        True if the user has used the --forwardbias command line option,
        False otherwise.
    --------------------------------------------------------------------------
    """
    parser = argparse.ArgumentParser(
        description='This is an optional companion script for iv.py. It plots\
        IV data broadcast by iv.py as it is acquired; the plot\
        window persists over multiple runs of iv.py, until it is terminated\
        by the user. This script communicates with iv.py using ZeroMQ on\
        local TCP port 5555.')
    parser.add_argument(
        '--forwardbias',
        action='store_true',
        help='Use this option if iv.py has been called with --forwardbias to\
        allow it to use positive voltages. This will prevent this script from\
        inverting the plot axes.')

    args = parser.parse_args()

    return args.forwardbias


##############################################################################
# threads
##############################################################################

def liveplot(pipeline):
    """
    Receive data packets from iv.py via ZeroMQ REQ/REP, and place them on a
    queue for processing later.

    To avoid dropped data packets ZeroMQ REQ/REP is the pattern used, though
    the desired behaviour is really PUB/SUB. PUB/SUB is unreliable in its
    basic form, and can't be used. With REQ/REP this thread is obliged to
    reply to the message iv.py sends, but since that reply will be discarded
    by iv.py, only send the most minimal reply.

    This activity is run in thread to decouple receiving data packets from the
    live-plotting process.

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
    --------------------------------------------------------------------------
    returns : no explicit return
        pipeline.packet : multiprocessing.Queue()
            shared repository for received data packets
    --------------------------------------------------------------------------
    """
    # configure communication with iv.py
    # Use REP/REQ (with handshaking) instead of PUB/SUB to avoid packet loss
    context = zmq.Context(1)
    socket = context.socket(zmq.REP)
    try:
        socket.bind("tcp://*:5555")
    except zmq.error.ZMQError:
        pass
    else:
        while pipeline.terminate_liveplot.empty():
            # receive message from iv.py
            message = socket.recv_json()

            pipeline.packet.put(message)

            # send a minimal message back to iv.py for handshake
            socket.send_json(None)


##############################################################################
# utilities
##############################################################################

def collect_data_packets(pipeline):
    """
    Given that data packets should arrive at a fairly low rate (one
    data packet per power supply channel per second), in typical usage this
    function is unlikely to return more than one data packet per plot
    interval.

    In larger test environments with several devices under test (and given
    that power supply channels are tested asynchronously), or when using test
    scripts, it's plausible that more than one data packet may arrive per
    plot interval, and this function manages this eventuality.

    Regarding iv.py sending reset packets to clear the plot: this function is
    called by animate() at the interval specified by the call to
    animation.FuncAnimation() (specified with interval=..., the default is
    every 200ms). Therefore, any data packets received before a reset will be
    discarded, since there's little point live-plotting data that will
    be visible for 200ms. This is a corner case, since for this to occur
    one invocation of iv.py would have to terminate, and another one start
    within the narrow call interval, which can only be achieved with a test
    script, and not through normal operation.

    --------------------------------------------------------------------------
    args
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
    --------------------------------------------------------------------------
    returns
        packets : iterator
            e.g. ('reset', 'debug 1234567,0.0,-0.0,False')
    --------------------------------------------------------------------------
    """
    packets = []

    # get all packets from the queue
    # this function is the only one that reads from this queue so get() should
    # never block
    while not pipeline.packet.empty():
        packets.append(pipeline.packet.get())

    # discard any packets received before the last reset packet, always
    # retaining the last 'reset' packet itself
    try:
        rindex = -packets[::-1].index('reset') - 1
    except ValueError:
        pass
    else:
        packets = packets[rindex:]

    return packets


##############################################################################
# plot
##############################################################################

def animate(_, pipeline, plotdata, collut, colors, axis, forwardbias):
    """
    Obtain new data from iv.py via ZeroMQ and plot graph with updated data.

    --------------------------------------------------------------------------
    args
        _ : int
            frame counter (ignore)
        pipeline : instance of class Production
            contains all the queues through which the production pipeline
            processes communicate
        plotdata : dict
        collut : dict
        colors : list of tuples (R, G, B, A)
            e.g.
            [(0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0),
             (1.0, 0.4980392156862745, 0.054901960784313725, 1.0), ...]
        axis : matplotlib.axes._subplots.AxesSubplot
        forwardbias : bool
            True if the user has used the --forwardbias command line option,
            False otherwise.
    --------------------------------------------------------------------------
    returns : none
    --------------------------------------------------------------------------
    """
    messages = collect_data_packets(pipeline)
    if not messages:
        return

    # process data packets received this interval
    for message in messages:
        try:
            # string, float, float, bool
            ident, volt, curr, rev = message
        except (ValueError, AttributeError):
            if message == 'reset':
                print('packet: start new plot')
                plotdata.clear()
                collut.clear()
        else:
            print(f'packet: {message}')

            suffix = 'return' if rev else 'outbound'
            label = f'{ident} {suffix}'

            # first data point for this power supply: initialise data structure
            if plotdata.get(label) is None:
                plotdata[label] = [[], [], ident]
            if collut.get(ident) is None:
                collut[ident] = None

            plotdata[label][0].append(volt)
            plotdata[label][1].append(curr)

    # plot
    if plotdata:
        # pair line colour with psu channel ident
        for lut, col in zip(collut, itertools.cycle(colors)):
            if collut[lut] is None:
                collut[lut] = col

        axis.clear()
        for label, (volt, curr, pid) in plotdata.items():
            linetype = '.-' if 'outbound' in label else '.--'
            axis.plot(volt, curr, linetype,
                      label=label, linewidth=0.5,
                      markersize=1, color=collut[pid])

        if not forwardbias:
            axis.invert_yaxis()
            axis.invert_xaxis()

        axis.set_xlabel('bias voltage (V)')
        axis.set_ylabel('leakage current (A)')
        axis.set_title('IV Liveplot')
        axis.legend(loc='lower right')
        axis.yaxis.set_major_formatter(EngFormatter(places=1))
        axis.xaxis.set_major_formatter(EngFormatter(places=1))
        axis.yaxis.tick_left()
        axis.xaxis.tick_bottom()
        plt.tight_layout()

    # This is to address Raspberry Pi OS's use of legacy matplotlib 3.0.2
    # which seems to accumulate lots of memory over time. No harm in calling
    # this for other configurations.
    gc.collect()


##############################################################################
# main
##############################################################################

def main():
    """
    Plots live data outputted by iv.py in a window that persists over multiple
    runs of iv.py.
    """
    forwardbias = check_arguments()

    ##########################################################################
    # matplotlib
    ##########################################################################

    # set matplotlib defaults
    matplotlib.rcParams.update({
        # remove chartjunk
        'axes.spines.top': False,
        'axes.spines.right': False,
        # fontsize of the x any y labels
        'axes.labelsize': 'medium',
        # fontsize of the axes title
        'axes.titlesize': 'medium',
        # fontsize of the tick labels
        'xtick.labelsize': 'small',
        'ytick.labelsize': 'small',
        # fontsize of plot-line labels
        'legend.fontsize': 'x-small'})

    fig = plt.figure(num='liveplot.py (receives data from iv.py)')
    axis = fig.add_subplot(1, 1, 1)

    ##############################################################################
    # set up resources for threads
    ##############################################################################

    # define data structures for processes to use
    class Production:
        """Queues to support production pipeline"""
        terminate_liveplot = mp.Queue()
        packet = mp.Queue()

    pipeline = Production()

    # livp: collect sampled data points sent from iv.py
    livp = threading.Thread(target=liveplot, args=(pipeline, ))
    livp.start()

    # allow some time before checking if the thread has exited, to give enough
    # time for binding to the desired port to fail
    time.sleep(0.1)
    if not livp.is_alive():
        sys.exit('liveplot.py may already be running')

    ##############################################################################
    # liveplot
    ##############################################################################

    # create list of colours from a ten-entry colour map
    colors = [plt.cm.tab10(x) for x in range(10)]
    plotdata = {}
    collut = {}

    print('waiting for data packets')
    ani = animation.FuncAnimation(fig, animate,
                                  fargs=(pipeline, plotdata, collut, colors, axis, forwardbias))

    plt.show()

    ##########################################################################
    # release resources for threads
    ##########################################################################

    pipeline.terminate_liveplot.put(True)
    livp.join()


##############################################################################
if __name__ == '__main__':
    main()
