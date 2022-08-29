#!/usr/bin/env python3

# example of running the script
#
# ./plot_spectrum.py --samp-rate=19660800 /mnt/storage/projects/skylight/captures/evdo_detect_seq_and_vectors_2017-02-01/captures/cell_pwr_-50_f=888900000_r=19660800_n=9830400_g=76.a1
# python plot_spectrum.py --samp-rate=1.02e7 s12_AgilentRFGen_10A.bin.a1

# cd C:\Users\berrios1\Documents\ARMR\Test_June\AreaTest\E310 Data
# python area_peak_offset_values.py --samp-rate=625000 --lo-freq=1000000000 --n-bits-iq 12 E310_Test_6-23-21_On_1I.dat

import sys
import numpy as np
import matplotlib.pyplot as plt


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


def main(argv=None):
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

    # read, scale, truncate IQ sequence
    x = read_iq_from_file(args.capture)
    full_scale_mag = 2.**(n_bits_iq-1)     
    x /= full_scale_mag
    x = x[:iq_len]

    # calc spectrum
    bin_freq, bin_mag = compute_mag_spectrum(x, samp_rate, fft_len)
    print("bin_freq:",len(bin_freq))
    bin_mag_db = 10*np.log10(bin_mag)

    # find top peak and plot
    idx = np.argmax(bin_mag_db)
    peak_db = bin_mag_db[idx]
    peak_freq_hz = bin_freq[idx]
    peak_abs_freq_hz = lo_freq + peak_freq_hz
    title = 'peak: {:.1f} dBFS at {:.3f} MHz ({:.3f} kHz offset)'.format(peak_db,
                                                                        peak_abs_freq_hz/1e6,
                                                                        peak_freq_hz/1e3)

    min_bin_mag_db = min(bin_mag_db)
    plt.figure(1)
    plt.clf()
    plt.plot((lo_freq + bin_freq)/1000, bin_mag_db)
    plt.xlabel('freq [kHz]')
    plt.ylabel('dBFS')
    plt.grid(True)
    plt.ylim((min(filter(lambda f: f > 0.9 * min_bin_mag_db, bin_mag_db)), 0))
    plt.title(title)
    plt.show()


if __name__ == '__main__':
      sys.exit(main())
