import os
import glob
import pickle
import pysismo

from pysismo.psconfig import FTAN_DIR, TOMO_DIR,\
CHECKERBOARD_VMID, CHECKERBOARD_VMIN, CHECKERBOARD_VMAX,\
CHECKERBOARD_PERIODS, CHECKERBOARD_SQUARESIZES

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

    for squaresize in CHECKERBOARD_SQUARESIZES:
        for period in CHECKERBOARD_PERIODS:
            vmap = pysismo.pstomo.VelocityMap(curves,period=period)
            vmap.plot_checkerboard(CHECKERBOARD_VMID,
                                    CHECKERBOARD_VMIN,
                                    CHECKERBOARD_VMAX,
                                    squaresize,
                                    outfile=TOMO_DIR+'/checkerboard_'+pickle_file.split('/')[-1][5:-7]+'/'+\
                                    'checkerboard_%02ds_%03dkm.png' % (period,squaresize))
