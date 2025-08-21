#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Save TOD data to fits file

input files:
 - 

output files:
 - 

verbose output files:
 - out/SaveFits_TOD_%04d.png : TOD plots

"""

import os
import sys
import shutil
import copy

import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

def main(argv=None):
    parser = argparse.ArgumentParser(formatter_class=myHelpFormatter, description=__doc__)
    parser.add_argument('--down-sampling', type=int, default=1,
                        help="the number of rebinning")
    parser.add_argument('--baseline-thresh', type=float, default=6.0)
    parser.add_argument('--glitch-thresh', type=float, default=5.0)
    parser.add_argument('--clusterize-thresh', type=float, default=2)
    parser.add_argument('--plot-tod-ratio', type=float, default=0.25,
                        help="the portion of TOD to use in FFT plot")
    parser.add_argument('--verbose', type=int, default=default_verbose_level,
                        help="""
                        verbose level. 0: won't plot result.
                        1: plot result.""")
    parser.add_argument('--mode', choices=['both', 'plot', 'calc'], default='calc',
                        help="""select do calulation only,
                        do plotting data (calculated before), or both""")
    parser.add_argument('--force', action='store_true') # for analysis & plot
    parser.add_argument('--blindtone', action='store_true') # for plot blindtones
    parser.add_argument('--test', action='store_true') # for plot
    parser.add_argument('--ncpu', type=int, default=1,
                        help="")

    args = parser.parse_args(argv)
    if args.mode == 'both':
        do_calc = True
        do_plot = True
    elif args.mode == 'calc':
        do_calc = True
        do_plot = False
    elif args.mode == 'plot':
        do_calc = False
        do_plot = True

    if do_calc:
        Calc(kids, args.down_sampling, args.verbose,
             args.baseline_thresh, args.glitch_thresh, args.clusterize_thresh,
             args.force)

    if do_plot:
        Plot(kids, args.plot_tod_ratio, args.ncpu, args.force, args.blindtone, args.test)


def Calc(kids, rebin, verbose,
         baseline_thresh, glitch_thresh, clusterize_thresh,
         force):
    ## read tod files and KidFitResult objects
    print( 'creating new fitsfile...' )

    ofname = os.path.join(outdir, 'reduced_' + os.path.basename(kids._tods_path))
    #datadir = os.path.dirname(kids._tods_path)
    #ofname = os.path.join(datadir, 'reduced_' + os.path.basename(kids._tods_path))
    if os.path.exists(ofname):
        print( 'The file %s already exists...' %ofname )

        if force:
            print( 'Over write %s...' %ofname )
            try:
                os.remove(ofname)
            except OSError:
                pass
        else:
            print( 'Quit' )
            sys.exit(1)

    from util import rebin_array, createBinTableHDU, readout_dict, kids_dict
    
    #####
    ##### deglitch settings
    interp_offset = 0

    ## amp, ph, linph = 4Qr*(f-fr)/fr
    ## fshift ~ df/fr can be calculated: (linph-linyfc)/4Qr = (f-fr)/fr - (fc-fr)/fr = (f-fc)/fr
    ## fshift (w.r.t Room chopper): (linph-linyfc)/4Qr + (fr-fr_room)/fr = (f-fc + fr-fr_room)/fr
    r_dict = readout_dict()
    r_dict['hdr_val_lis'][1] = os.path.basename(kids._tods_path)

    k_dict = kids_dict()
    k_dict['hdr_val_lis'][1] = os.path.basename(kids._sweeps_path)

    pixelid = 0
    nkid = 0
    fit_info = []
    for i, k in kids.items():
        fc = k.get_fcarrier() # GHz
        pread = k.readpower

        if k.enabled:
            ##### fit info
            if k.has_cache('fit_roomchopper'):
                r_room   = k.get_cache('fit_roomchopper')
                fr_room  = r_room.params['fr'].value; dfr_room = r_room.params['fr'].stderr # GHz
            else:
                fr_room  = np.nan; dfr_room = np.nan
            ##
            r   = k.get_cache('fit')
            fr  = r.params['fr'].value; dfr = r.params['fr'].stderr # GHz
            Qr = r.params['Qr'].value; dQr = r.params['Qr'].stderr
            Qc = r.params['Qc'].value; dQc = r.params['Qc'].stderr
            Qi = r.params['Qi'].value; dQi = r.params['Qi'].stderr

            swp = k.get_cache('raw_sweep')
            rw_s = r.rewind(swp.x, swp.iq)
            rw_f = r.rewind(swp.x, r.fitted(swp.x))
            
            phase_s = -np.angle(-rw_s) ## sweep
            phase_f = -np.angle(-rw_f) ## fit

            ## spline interpolation
            from scipy import interpolate
            tck = interpolate.splrep(swp.x, phase_s, s=0)
            yfc = interpolate.splev(fc, tck, der=0) # phase of carrier f
            yfr = interpolate.splev(fr, tck, der=0) # phase of resonance f
            linyfc = k.convert_to_fshift(yfc, opt='linphase')

            fit_info.append( [i, pread, fc, yfc, linyfc, fr, dfr, Qr, dQr, Qc, dQc, Qi, dQi, fr_room, dfr_room] )
            #####

            #ts, ampl, phase = k.get_cache('deglitch').unpack()
            bad = k.find_glitch(baseline_thresh, glitch_thresh, clusterize_thresh, interp_offset)
            ts, ampl, phase = k.deglitch(bad).unpack()            
            linphase = k.convert_to_fshift(phase, opt='linphase') # 4Qr*(f-fr)/fr, shift w.r.t. sky fr
            
            ts = rebin_array(ts, rebin)
            ampl = rebin_array(ampl, rebin)
            phase = rebin_array(phase, rebin)
            linphase = rebin_array(linphase, rebin)
        else:
            ##### fit info
            fit_info.append( [i, pread, fc, np.nan, np.nan, np.nan, np.nan,
                              np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan] )
            #####

            ts = kids.raw_tods().timestamp[:kids.raw_tods().offset]
            ts = rebin_array(ts, rebin)

            ampl = np.array( [np.nan for j in range(len(ts))] )
            phase = np.array( [np.nan for j in range(len(ts))] )
            linphase = np.array( [np.nan for j in range(len(ts))] )
        
        if len( r_dict['cols_data_lis'] )==0:
            framenr = kids.raw_tods().framenr
            timestamp = kids.raw_tods().timestamp[:kids.raw_tods().offset]
            print( len(framenr), len(timestamp), len(ts) )

            r_dict['cols_data_lis'].append(timestamp)
            r_dict['cols_data_lis'].append( np.ones( len(timestamp) )*pixelid )

        #r_dict['cols_key_lis'].append( 'Amp, Ph, linPh %d' %i )
        #r_dict['cols_data_lis'].append( np.array( [ampl, phase, linphase] ).T )
        #r_dict['tform'].append( '3E' )
        r_dict['cols_key_lis'].append( 'Amp, linPh %d' %i )
        r_dict['cols_data_lis'].append( np.array( [ampl, linphase] ).T )
        r_dict['tform'].append( '2E' )
        r_dict['tunit'].append( None )

        r_dict['hdr_com_lis'].append('label for field %d' %(i+2))
        r_dict['hdr_com_lis'].append('data format of field %d' %(i+2))

        nkid += 1
        if i%100==0:
            print( 'done for kid[%d]' %i )

        for tmp0, tmp1 in k.__dict__.copy().items():
            if tmp0[:6] == '_data_':
                del k.__dict__[tmp0]

    r_dict['hdr_val_lis'][2] = kids.header['framert']
    r_dict['hdr_val_lis'][3] = kids.header['npoints']
    r_dict['hdr_val_lis'][4] = rebin
    r_dict['hdr_key_lis'].append('NKID%d' %pixelid)
    r_dict['hdr_val_lis'].append(nkid)
    r_dict['hdr_com_lis'].insert(5, 'number of KIDs (pixel %d)' %pixelid)

    k_dict['hdr_key_lis'].append('NKID%d' %pixelid)
    k_dict['hdr_val_lis'].append(nkid)
    k_dict['hdr_com_lis'].insert(2, 'number of KIDs (pixel %d)' %pixelid)

    k_dict['cols_data_lis'].append( np.ones(nkid)*pixelid )
    kidid_, pread_, fc_, yfc_, linyfc_, fr_, dfr_, Qr_, dQr_, Qc_, dQc_, Qi_, dQi_, fr_room_, dfr_room_\
        = [np.array(fit_info)[:,i] for i in range(15)]
    k_dict['cols_data_lis'].append( kidid_ )
    k_dict['cols_data_lis'].append( pread_ )
    k_dict['cols_data_lis'].append( fc_ )
    k_dict['cols_data_lis'].append( np.array([yfc_, linyfc_]).T )
    k_dict['cols_data_lis'].append( np.array([fr_, dfr_]).T )
    k_dict['cols_data_lis'].append( np.array([Qr_, dQr_]).T )
    k_dict['cols_data_lis'].append( np.array([Qc_, dQc_]).T )
    k_dict['cols_data_lis'].append( np.array([Qi_, dQi_]).T )
    k_dict['cols_data_lis'].append( np.array([fr_room_, dfr_room_]).T )

    ##### save to fits file
    hdus = fits.HDUList()
    hdus.append( fits.PrimaryHDU() ) # Primary
    hdus.append( createBinTableHDU(k_dict) )
    #hdus.append( createBinTableHDU(r_dict) ) # this takes time...
    hdus.writeto(ofname)
    hdus.close()
        
    ##hdus = fits.open(ofname, mode='append', memmap=True)
    r_hdu =  createBinTableHDU(r_dict) # this takes time...
    fits.append(ofname, r_hdu.data, r_hdu.header, memmap=True)
    ##hdus.close()


def Plot(kids, plot_tod_ratio, NCPU, force, blindtone, test):
    plotdir = os.path.join(outdir, 'figSaveFits')
    blinddir = os.path.join(outdir, 'figSaveFits.Blindtone')
    if not blindtone:
        if force:
            try:
                shutil.rmtree(plotdir)
            except OSError:
                pass
        #### make plot output directory
        try:
            os.mkdir(plotdir)
        except:
            pass

    if blindtone:
        if force:
            try:
                shutil.rmtree(blinddir)
            except OSError:
                pass
        #### make plot output directory
        try:
            os.mkdir(blinddir)
        except:
            pass

    #### read fits file
    ifname = os.path.join(outdir, 'reduced_' + os.path.basename(kids._tods_path))
    #datadir = os.path.dirname(kids._tods_path)
    #ifname = os.path.join(datadir, 'reduced_' + os.path.basename(kids._tods_path))
    hdu = fits.open(ifname)
    rebin = hdu['READOUT'].header['DSAMPLE']
    #dt = 1/kids.header['framert'] * rebin
    dt = 1/hdu['READOUT'].header['FRAMERT'] * rebin
    ts = copy.deepcopy(hdu['READOUT'].data['timestamp'])
    
    params_list = []
    for i, kid in kids.items():
        if not kid.enabled: continue

        if test and i>10: break
        ampl, linphase = copy.deepcopy(hdu['READOUT'].data['Amp, linPh %d' %i].T)
        yfc, linyfc = copy.deepcopy(hdu['KIDSINFO'].data['yfc, linyfc'][i])
        params_list.append( {'i': i, 'kid': kid, 'plot_tod_ratio': plot_tod_ratio, 'blindtone': blindtone, 'test':test,
                             'plotdir':plotdir, 'blinddir': blinddir,
                             'rebin': rebin, 'dt': dt, 'ts': ts, 'ampl': ampl, 'linphase': linphase, 'linyfc': linyfc} )
    
    from multiprocessing import Pool
    p = Pool(NCPU)
    result = p.map(plot_multi, params_list)


def plot_multi(params):
    i = params['i']
    kid = params['kid']
    plot_tod_ratio = params['plot_tod_ratio']
    blindtone = params['blindtone']
    test = params['test']
    plotdir = params['plotdir']
    blinddir = params['blinddir']
    rebin = params['rebin']
    dt = params['dt']
    
    bPrint = False
    if test:
        bPrint = True
    else:
        if i%50==0: bPrint = True
    if bPrint: print( 'plotting KID[%d]' %i )

    import mkid_data as md
    fc = kid.get_fcarrier() # GHz
    r   = kid.get_cache('fit')
    swp = kid.get_cache('raw_sweep')
    
    fr = r.params['fr'].value # GHz
    rw_s = r.rewind(swp.x, swp.iq)
    rw_f = r.rewind(swp.x, r.fitted(swp.x))
    
    phase_s = -np.angle(-rw_s) ## sweep
    phase_f = -np.angle(-rw_f) ## fit
    
    ## spline interpolation
    from scipy import interpolate
    tck = interpolate.splrep(swp.x, phase_s, s=0)
    yfc = interpolate.splev(fc, tck, der=0) # phase of carrier f
    yfr = interpolate.splev(fr, tck, der=0) # phase of resonance f
    linyfc = kid.convert_to_fshift(yfc, opt='linphase')
    #####
    #ts, ampl, phase = kid.get_cache('deglitch').unpack()
    ts, ampl, phase = kid.get_cache('rewind_tod').unpack()
    linphase = kid.convert_to_fshift(phase, opt='linphase')
    ts = ts - ts[0]

    if not blindtone:
        ## output TOD plot figure
        if bPrint:
            print( 'KID[%d]:' % i, 'plotting TOD...' )
            #sys.stdout.flush()
        fig = plt.figure(figsize=(8,10))
        plt.subplot(311)
        plt.title('KID[%d]' % i)
        plt.plot(ts, ampl, 'r', label='ampl. (from cache)')
        plt.plot(ts, linphase, 'b', label='linearized phase (from cache)')
#        plt.plot(ts, phase, 'b', lw=3, alpha=0.3, label='phase (from cache)')
        plt.plot(ts, np.ones(len(ts))*linyfc, 'c--', lw=1, label='carrier linphase (from cache)')
#        plt.plot(ts, np.ones(len(ts))*yfc, 'c--', lw=3, alpha=0.3, label='carrier phase (from cache)')
        #plt.xlabel('Time [s]')
        plt.ylabel('Normalized Response')
        plt.grid()
        plt.legend(loc='best')

        #####
        #ts = hdu['READOUT'].data['timestamp']
        #ampl, phase, linphase = hdu['READOUT'].data['Amp, Ph, linPh %d' %i].T
        #ampl, linphase = hdu['READOUT'].data['Amp, linPh %d' %i].T
        #yfc, linyfc = hdu['KIDSINFO'].data['yfc, linyfc'][i]
        ts = params['ts']
        ampl = params['ampl']
        linphase = params['linphase']
        linyfc = params['linyfc']
        
        ts = ts - ts[0]
        plt.subplot(312)
        #plt.title('KID[%d]' % i)
        plt.plot(ts, ampl, 'r', label='ampl. (deglitch from fits)')
        plt.plot(ts, linphase, 'b', label='linearized phase (deglitch from fits)')
#        plt.plot(ts, phase, 'b', lw=3, alpha=0.3, label='phase (deglitch from fits)')
        plt.plot(ts, np.ones(len(ts))*linyfc, 'c--', lw=1, label='carrier linphase (from fits)')
#        plt.plot(ts, np.ones(len(ts))*yfc, 'c--', lw=3, alpha=0.3, label='carrier phase (from fits)')
        plt.xlabel('Time [s]')
        plt.ylabel('Normalized Response')
        plt.grid()
        plt.legend(loc='best')
            
        ## output PSD plot figure
        if bPrint:
            print( 'plotting PSD...' )
            #sys.stdout.flush()
        size = 2**int(np.floor(np.log2(len(ts)*plot_tod_ratio)))
        f_, ampl_ = md.power_spectrum_density(ampl[:size], dt, 7, window=None, overwrap_half=True)
#        f_, phase_ = md.power_spectrum_density(phase[:size], dt, 7, window=None, overwrap_half=True)
        f_, linphase_ = md.power_spectrum_density(linphase[:size], dt, 7, window=None, overwrap_half=True)
        plt.subplot(313)
        #plt.title('KID[%d]' % i)
        plt.semilogx(f_, np.log10(ampl_)*10.0, 'r', label='ampl. (from fits)')
        plt.semilogx(f_, np.log10(linphase_)*10.0, 'b', label='linearized phase (from fits)')
#        plt.semilogx(f_, np.log10(phase_)*10.0, 'g', lw=3, alpha=0.3, label='phase (from fits)')
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('PSD [dBk/Hz]')
        plt.grid()
        plt.ylim(-110.,-50.)
        #plt.ylim(-100.,0.)
        plt.legend(loc='best')
            
        plt.savefig(os.path.join(plotdir, 'SaveFits_%04d.png' % i))
        #plt.close(fig)
        plt.clf()
        plt.close()
        
        for tmp0, tmp1 in kid.__dict__.copy().items():
            if tmp0[:6] == '_data_':
                del kid.__dict__[tmp0]

    #####
    ##### plot for blind tones
    if blindtone:
        bink = kid.bin
        binl = kid.bin_l
        binr = kid.bin_r
        ts, il, ql = kid.get_cache('blind_tone_left').unpack()
        ts, ir, qr = kid.get_cache('blind_tone_right').unpack()
        
        ## output TOD plot figure
        if bPrint:
            print( 'plotting Blind TOD...' )
            #sys.stdout.flush()
        fig = plt.figure(figsize=(8,10))
        plt.subplot(211)
        plt.title('KID[%d]: %d' % (i, bink))
        plt.plot(ts, il, 'r', label='I Left (%d)' %binl)
        plt.plot(ts, ql, 'b', label='Q Left (%d)' %binl)
        plt.plot(ts, ir, 'm', label='I Right (%d)' %binr)
        plt.plot(ts, qr, 'c', label='Q Right (%d)' %binr)
        #plt.xlabel('Time [s]')
        plt.ylabel('Raw Data')
        plt.grid()
        plt.legend(loc='best')
        
        ## output PSD plot figure
        if bPrint:
            print( 'plotting Blind PSD...' )
            #sys.stdout.flush()
            
        norml = np.sqrt( np.average(il)**2 + np.average(ql)**2 )
        normr = np.sqrt( np.average(ir)**2 + np.average(qr)**2 )
        
        size = 2**int(np.floor(np.log2(len(ts)*plot_tod_ratio)))
        f_, il_ = md.power_spectrum_density(il[:size]/norml, dt, 7, window=None, overwrap_half=True)
        f_, ql_ = md.power_spectrum_density(ql[:size]/norml, dt, 7, window=None, overwrap_half=True)
        f_, ir_ = md.power_spectrum_density(ir[:size]/normr, dt, 7, window=None, overwrap_half=True)
        f_, qr_ = md.power_spectrum_density(qr[:size]/normr, dt, 7, window=None, overwrap_half=True)
        plt.subplot(212)
        #plt.title('KID[%d]' % i)
        plt.semilogx(f_, np.log10(il_)*10.0, 'r', label='I Left (%d)' %binl)
        plt.semilogx(f_, np.log10(ql_)*10.0, 'b', label='Q Left (%d)' %binl)
        plt.semilogx(f_, np.log10(ir_)*10.0, 'm', label='I Right (%d)' %binr)
        plt.semilogx(f_, np.log10(qr_)*10.0, 'c', label='Q Right (%d)' %binr)
        plt.xlabel('Frequency [Hz]')
        plt.ylabel('PSD [dBc/Hz]')
        plt.grid()
        plt.ylim(-110.,-50.)
        plt.legend(loc='best')
        
        plt.savefig(os.path.join(blinddir, 'CalibTOD.Blindtone_%04d.png' % i))
        #plt.close(fig)
        plt.clf()
        plt.close()

        for tmp0, tmp1 in kid.__dict__.copy().items():
            if tmp0[:6] == '_data_':
                del kid.__dict__[tmp0]
    pass


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    libpath = os.path.join(os.path.dirname(script_dir), 'libs')
    sys.path.append(libpath)
        
    from common import *
    from astropy.io import fits
    main()

