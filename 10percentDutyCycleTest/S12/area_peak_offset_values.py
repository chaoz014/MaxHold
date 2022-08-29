#!/usr/bin/env python2

# example of running the script
#
# ./plot_spectrum.py --samp-rate=19660800 /mnt/storage/projects/skylight/captures/evdo_detect_seq_and_vectors_2017-02-01/captures/cell_pwr_-50_f=888900000_r=19660800_n=9830400_g=76.a1
# python plot_spectrum.py --samp-rate=1.02e7 --lo-freq 4e9 s12_AgilentRFGen_10A.bin.a1
# python plot_spectrum.py --samp-rate=1.02e7 s12_AgilentRFGen_10A.bin.a1
# python plot_spectrum.py --lo-freq 4000000000 --samp-rate=10200000 s12_AgilentRFGen_10A.bin.a1

# 5-7-21_D
#python output_peak_values.py --samp-rate=625000 --lo-freq=1000000000 --n-bits-iq 12 s12_Test_5-7-21_On_1D.bin

# 5-7-21 E
#python output_peak_values.py --samp-rate=625000 --lo-freq=1000000000 --n-bits-iq 12 s12_Test_5-7-21_On_1E.bin

# 6/7/21
# python area_peak_offset_values.py --samp-rate=625000 --lo-freq=1000000000 --n-bits-iq 12 s12_Test_6-7-21_On_1H.bin

# 6/23/21
# python area_peak_offset_values.py --samp-rate=625000 --lo-freq=1000000000 --n-bits-iq 12 s12_Test_6-7-21_On_1H.bin
# cd C:\Users\berrios1\Documents\ARMR\Test_June\AreaTest\S12 Data

import sys
import numpy as np
from myFunctions import getFileNames, splitOnOffFileNames, writeValues
from scipy.integrate import simps

filenamespath = "testFileNames.txt"


def read_iq_from_file(filename):
    with open(filename, 'rb') as fp:    
        tmp = np.fromfile(fp, dtype=np.uint32)
    tmp.dtype = np.int16
    return tmp[1::2] + 1j*tmp[0::2]


def compute_mag_spectrum(x, samp_rate_hz, fft_len):
    # bin frequencies
    t_samp = 1./samp_rate_hz
    bin_freq_hz = np.fft.fftfreq(fft_len, t_samp)

    # get mag spectrum of windowed zero-padded input
    window = np.hamming(len(x))
    x_zp = np.zeros((fft_len,), dtype=np.complex)
    x_zp[:len(x)] = x * window
    mag_spectrum = np.abs(np.fft.fft(x_zp, norm='ortho'))**2

    # figure out scale factor (each factor is squared since applied to mag spectrum)
    # so that 0 dBFS sinusoid will have mag spectrum peak at 0 dB
    xlen_factor = len(x)
    window_factor = 1./(window.sum()**2)
    zp_factor = fft_len/len(x)
    scale = xlen_factor * window_factor * zp_factor

    return (np.fft.fftshift(bin_freq_hz), np.fft.fftshift(scale*mag_spectrum))

def calcPeak(bin_mag, bin_freq):
    bin_mag_db = 10*np.log10(bin_mag)

    # find top peak and plot
    idx = np.argmax(bin_mag_db)
    peak_db = bin_mag_db[idx]
    peak_freq_hz = bin_freq[idx]
    peak_abs_freq_hz = lo_freq + peak_freq_hz
    title = 'peak: {:.1f} dBFS at {:.3f} MHz ({:.3f} kHz offset)'.format(peak_db,
                                                                        peak_abs_freq_hz/1e6,
                                                                        peak_freq_hz/1e3)
                                                                        
    return peak_db, peak_abs_freq_hz

def mag_spectrum(filename):
    # read, scale, truncate IQ sequence
    x = read_iq_from_file(filename)
    full_scale_mag = 2.**(n_bits_iq-1)       
    x /= full_scale_mag
    x = x[:iq_len]

    # calc spectrum
    bin_freq, bin_mag = compute_mag_spectrum(x, samp_rate, fft_len)
    
    return bin_freq, bin_mag



def getValues(filenames):
    areaList = []
    peakList = []
    offSetList = []
    allValues = []
    allValues.append("area" + "\t" + "peak_db" + "\t" + "peak_abs_freq_hz")
    
    print("\n" + "area" + "\t\t\t" + "peak_db" + "\t\t\t" + "peak_abs_freq_hz")
    
    for filename in filenames:
        
        bin_freq, bin_mag = mag_spectrum(filename)
        
        # Calculate area under the curve
        area = simps(bin_mag, bin_freq)
        area_dB = 10*np.log10(area)

        peak_db, peak_abs_freq_hz = calcPeak(bin_mag, bin_freq)
        
        # Append values to lists
        areaList.append(area_dB)
        peakList.append(peak_db)
        offSetList.append(peak_abs_freq_hz)
        allValues.append(str(area_dB) + "\t" + str(peak_db) + "\t" + str(peak_abs_freq_hz))

        print(str(area_dB) + "\t" + str(peak_db) + "\t" + str(peak_abs_freq_hz))     
    
    writeValues("AllValues.txt", allValues)
    
    return areaList, peakList, offSetList
    
    
lo_freq = ''
samp_rate = ''
n_bits_iq = ''
iq_len = ''
fft_len = ''

def main(argv=None):
    global lo_freq
    global samp_rate
    global n_bits_iq
    global iq_len
    global fft_len
    global filenamespath
    
    import argparse
  
    if argv is None:
        argv = sys.argv
        
  
    parser = argparse.ArgumentParser(description='quick spectrum app')
    parser.add_argument('--lo-freq', type=float, default=0, help='LO freq of capture in Hz')
    parser.add_argument('--samp-rate', type=float, required=True, help='sample rate in Hz')
    parser.add_argument('--n-bits-iq', type=int, default=12, help='number of bits per I or Q sample (12 or 16)')
    parser.add_argument('--iq-len', type=int, default=10000, help='first iq-len samples from file are used')
    parser.add_argument('--fft-len', type=int, default=2**17, help='FFT length; usually power of 2 and larger than iq-len')
    parser.add_argument('capture', help='filename of capture in rx_samples format')
  
    args = parser.parse_args(argv[1:])

    lo_freq = int(args.lo_freq)
    samp_rate = int(args.samp_rate)
    n_bits_iq = args.n_bits_iq
    iq_len = args.iq_len
    fft_len = args.fft_len

    
    # onPath  = "OnList.txt"
    # offPath = "OffList.txt"
    onAreaListOutputFilePath    = "OnAreaListOutputFile.txt"      # The output path to write the calculated value to
    onPeakListOutputFilePath    = "OnPeakListOutputFile.txt"      # The output path to write the calculated value to
    onFreqOffsetOutputFilePath  = "OnFreqOffsetOutputFile.txt"    # The output path to write the calculated value to
    offAreaListOutputFilePath   = "OffAreaListOutputFile.txt"     # The output path to write the calculated value to    
    offPeakListOutputFilePath   = "OffPeakListOutputFile.txt"     # The output path to write the calculated value to
    offFreqOffsetOutputFilePath = "offFreqOffsetOutputFile.txt"   # The output path to write the calculated value to
    
    onListFileNames, offListFileNames = splitOnOffFileNames(filenamespath)  # Clean list of data file names
    
    # Get Area, peak value, and frequency offset of peak values
    onAreaValueList, onPeakValueList, onOffSetValueList    = getValues(onListFileNames)     # Get on values
    offAreaValueList, offPeakValueList, offOffSetValueList = getValues(offListFileNames)    # Get off values

if __name__ == '__main__':
      sys.exit(main())
