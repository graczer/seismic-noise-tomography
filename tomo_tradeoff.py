#!/usr/bin/python -u

from pysismo import pstomo, psutils
import os
import shutil
import glob
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import itertools as it

def plot_tradeoff(parameter, x, y, x_label, y_label, filename, labels=None):
    plt.clf()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.plot(x, y, marker='o', linestyle='-', color='black')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if labels:
        if parameter in ['alpha', 'beta', 'corr_length']:
            parameter_format = ' %d'
        else:
            parameter_format = ' %f'
        for index, xy in enumerate(zip(x,y)):
            ax.annotate(parameter_format % (labels[index]), xy=xy, textcoords='data')
    plt.savefig(TOMO_DIR + '/' + filename,dpi=300)

def tradeoff(parameter, PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS, ALPHAS, BETAS, LAMBDAS):
    p_list = []
    vr_list = []
    tt_L2_list = []
    vel_L2_list = []
    # performing tomographic inversions, systematically
    # varying the inversion parameters
    param_lists = it.product(PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS,
                             ALPHAS, BETAS, LAMBDAS)
    param_lists = list(param_lists)
    for period, grid_step, minspectSNR, corr_length, alpha, beta, lambda_ in param_lists:
        s = ("Period = {} s, grid step = {}, min SNR = {}, corr. length "
             "= {} km, alpha = {}, beta = {}, lambda = {}")
        print s.format(period, grid_step, minspectSNR, corr_length, alpha, beta, lambda_)

        v = pstomo.VelocityMap(dispersion_curves=curves,
                               period=period,
                               verbose=False,
                               lonstep=grid_step,
                               latstep=grid_step,
                               minspectSNR=minspectSNR,
                               correlation_length=corr_length,
                               alpha=alpha,
                               beta=beta,
                               lambda_=lambda_)

        if parameter == 'alpha':
            p_list.append(alpha)
            labels = ALPHAS
        elif parameter == 'beta':
            p_list.append(beta)
            labels = BETAS
        elif parameter == 'corr_length':
            p_list.append(corr_length)
            labels = CORR_LENGTHS
        elif parameter == 'lambda':
            p_list.append(lambda_)
            labels = LAMBDAS
        else:
            print 'tradeoff: no such parameter'
            exit()
        vr_list.append(v.variance_reduction())
        tt_L2_list.append(v.traveltime_residuals_L2())
        vel_L2_list.append(v.velocity_residuals_L2())

    plot_tradeoff(parameter, p_list, vr_list, parameter, 'variance reduction (%)', parameter+'.png')
    plot_tradeoff(parameter, tt_L2_list, vel_L2_list, 'traveltime residual L2 norm [s]', 'velocity L2 norm [km/s]', parameter+'_L2.png', labels)


# parsing configuration file to import dirs
from pysismo.psconfig import FTAN_DIR, TOMO_DIR, TRADEOFF_PERIOD, TRADEOFF_GRID_STEP,\
TRADEOFF_MINPECTSNR, TRADEOFF_ALPHA, TRADEOFF_CORR_LENGTH, TRADEOFF_BETA, TRADEOFF_LAMBDA,\
COMPUTE_TRADEOFF_ALPHA, TRADEOFF_ALPHAS, COMPUTE_TRADEOFF_CORR_LENGTH, TRADEOFF_CORR_LENGTHS,\
COMPUTE_TRADEOFF_BETA, TRADEOFF_BETAS, COMPUTE_TRADEOFF_LAMBDA, TRADEOFF_LAMBDAS 

PERIODS = [TRADEOFF_PERIOD]
GRID_STEPS = [TRADEOFF_GRID_STEP]
MINPECTSNRS = [TRADEOFF_MINPECTSNR]

ALPHAS = [TRADEOFF_ALPHA]
BETAS = [TRADEOFF_BETA]
CORR_LENGTHS = [TRADEOFF_CORR_LENGTH]
LAMBDAS = [TRADEOFF_LAMBDA]

# selecting dispersion curves
flist = sorted(glob.glob(os.path.join(FTAN_DIR, 'FTAN*.pickle*')))
print 'Select file(s) containing dispersion curves to process: [All except backups]'
print '0 - All except backups (*~)'
print '\n'.join('{} - {}'.format(i + 1, os.path.basename(f))
                for i, f in enumerate(flist))

res = raw_input('\n')
if not res:
    pickle_files = [f for f in flist if f[-1] != '~']
else:
    pickle_files = [flist[int(i)-1] for i in res.split()]

# loop on pickled curves
for pickle_file in pickle_files:
    print "\nProcessing dispersion curves of file: " + pickle_file

    f = open(pickle_file, 'rb')
    curves = pickle.load(f)
    f.close()

    if COMPUTE_TRADEOFF_ALPHA:
        ALPHAS = TRADEOFF_ALPHAS 
        tradeoff('alpha', PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS, ALPHAS, BETAS, LAMBDAS)
        ALPHAS = [TRADEOFF_ALPHA]

    if COMPUTE_TRADEOFF_BETA:
        BETAS = TRADEOFF_BETAS 
        tradeoff('beta', PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS, ALPHAS, BETAS, LAMBDAS)
        BETAS = [TRADEOFF_BETA] 

    if COMPUTE_TRADEOFF_CORR_LENGTH:
        CORR_LENGTHS = TRADEOFF_CORR_LENGTHS 
        tradeoff('corr_length', PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS, ALPHAS, BETAS, LAMBDAS)
        CORR_LENGTHS = [TRADEOFF_CORR_LENGTH] 

    if COMPUTE_TRADEOFF_LAMBDA:
        LAMBDAS = TRADEOFF_LAMBDAS 
        tradeoff('lambda', PERIODS, GRID_STEPS, MINPECTSNRS, CORR_LENGTHS, ALPHAS, BETAS, LAMBDAS)
        LAMBDAS = [TRADEOFF_LAMBDA] 
