import numpy as np
from ldpc.decoder import DecoderWiFi, awgn_llr, GalBfDecoder, WbfDecoder, WbfVariant, PbfDecoder, PbfVariant
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.utils import QCFile
import matplotlib.pyplot as plt
import datetime

# create encoder with frame of 648 bits, and rate 1/2. Possible rates and frame sizes are per the ieee802.11n spec.
enc = EncoderWiFi(WiFiSpecCode.N1944_R23)
# create information bearing bits
rng = np.random.default_rng()
info_bits = np.unpackbits(np.frombuffer(rng.bytes(2*10**4), dtype=np.uint8))
# trim some bits to get full frames, we use code with k=324
info_bits = info_bits[:-(len(info_bits) % enc.k)]

# encode bits
encoded = np.zeros(2*len(info_bits), dtype=np.int_)
for frame_idx in range(len(info_bits)//enc.k):
    encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n] = enc.encode(info_bits[frame_idx * enc.k: (frame_idx + 1) * enc.k])

# parity check matrix
h = QCFile.from_file("../ldpc/code_specs/ieee802.11/N1944_R23.qc").to_array()

snr_db = np.arange(-3, 1, 0.5)
# create decoders
bp = True
if bp:
    spa_decoder = DecoderWiFi(spec=WiFiSpecCode.N1944_R23, max_iter=20)
    ms_decoder = DecoderWiFi(spec=WiFiSpecCode.N1944_R23, max_iter=20, decoder_type="MS")
    spa_fer = np.zeros(len(snr_db))
    ms_fer = np.zeros(len(snr_db))
    spa_ber = np.zeros(len(snr_db))
    ms_ber = np.zeros(len(snr_db))
bf_decoder = GalBfDecoder(h=h, max_iter=300)
wbf_decoder = WbfDecoder(h=h, max_iter=300, decoder_variant=WbfVariant.WBF)
mwbf_decoder = WbfDecoder(h=h, max_iter=300, decoder_variant=WbfVariant.MWBF, confidence_coefficient=1)
mwbf_no_loops_decoder = WbfDecoder(h=h, max_iter=300, decoder_variant=WbfVariant.MWBF_NO_LOOPS, confidence_coefficient=1)
p_len = 10
p_vector = np.zeros(p_len)
# p has exponential form p[n] = C(exp(n*tau)-1) where C is a normalization constant such that p[end] = 1
# and tau is a parameter that controls the rate of increase of p
tau = 0.3
c = 1/(np.exp((p_len-1)*tau)-1)
for i in range(p_len):
    p_vector[i] = c*(np.exp(i*tau)-1)
p_vector[-1] = 1
ppbf_decoder = PbfDecoder(h=h, max_iter=1000, decoder_variant=PbfVariant.PPBF, p_vector=p_vector)

# consider BPSK signaling
baseband = 1 - 2 * encoded
rng = np.random.default_rng()


bf_fer = np.zeros(len(snr_db))
wbf_fer = np.zeros(len(snr_db))
mwbf_fer = np.zeros(len(snr_db))
mwbf_no_loops_fer = np.zeros(len(snr_db))
pbf_fer = np.zeros(len(snr_db))

uncoded_ber = np.zeros(len(snr_db))
bf_ber = np.zeros(len(snr_db))
wbf_ber = np.zeros(len(snr_db))
mwbf_ber = np.zeros(len(snr_db))
mwbf_no_loops_ber = np.zeros(len(snr_db))
pbf_ber = np.zeros(len(snr_db))

for idx, snr in enumerate(snr_db):
    snr_linear = 10 ** (snr / 10)
    noise_power = 1 / snr_linear
    sigma = np.sqrt(noise_power / 2)
    channel = awgn_llr(sigma=sigma)
    noisy = baseband + sigma*rng.normal(size=len(baseband))
    for frame_idx in range(len(encoded) // enc.n):
        hard_demod = np.array(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n] < 0, dtype=np.int_)
        errors = hard_demod ^ encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n]
        uncoded_ber[idx] += np.sum(errors)
        if bp:
            d = spa_decoder.decode(channel(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n]))[0]
            spa_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
            spa_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
            d = ms_decoder.decode(channel(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n]))[0]
            ms_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
            ms_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = bf_decoder.decode(hard_demod)[0]
        bf_ber[idx] += np.sum(d ^ encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        bf_fer[idx] += np.any(d ^ encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = wbf_decoder.decode(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n])[0]
        wbf_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        wbf_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = mwbf_decoder.decode(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n])[0]
        mwbf_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        mwbf_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = mwbf_no_loops_decoder.decode(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n])[0]
        mwbf_no_loops_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        mwbf_no_loops_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = ppbf_decoder.decode(hard_demod,3)
        d=d[0]
        pbf_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        pbf_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        if frame_idx % 10 == 0:
            print(f"SNR: {snr} dB, frame: {frame_idx}")
    print(f"SNR: {snr} dB")
    print(f"Uncoded BER: {uncoded_ber[idx] / len(encoded)}")
    if bp:
        print(f"SPA BER: {spa_ber[idx] / len(encoded)}")
        print(f"SPA FER: {spa_fer[idx] / (len(encoded) // enc.n)}")
        print(f"MS BER: {ms_ber[idx] / len(encoded)}")
        print(f"MS FER: {ms_fer[idx] / (len(encoded) // enc.n)}")
    print(f"BF BER: {bf_ber[idx] / len(encoded)}")
    print(f"BF FER: {bf_fer[idx] / (len(encoded) // enc.n)}")
    print(f"WBF BER: {wbf_ber[idx] / len(encoded)}")
    print(f"WBF FER: {wbf_fer[idx] / (len(encoded) // enc.n)}")
    print(f"MWBF BER: {mwbf_ber[idx] / len(encoded)}")
    print(f"MWBF FER: {mwbf_fer[idx] / (len(encoded) // enc.n)}")
    print(f"MWBF no loops BER: {mwbf_no_loops_ber[idx] / len(encoded)}")
    print(f"MWBF no loops FER: {mwbf_no_loops_fer[idx] / (len(encoded) // enc.n)}")
    print(f"PPBF BER: {pbf_ber[idx] / len(encoded)}")
    print(f"PPBF FER: {pbf_fer[idx] / (len(encoded) // enc.n)}")

if bp:
    spa_fer /= (len(encoded) // enc.n)
    ms_fer /= (len(encoded) // enc.n)
    spa_ber /= len(encoded)
    ms_ber /= len(encoded)

bf_fer /= (len(encoded) // enc.n)
wbf_fer /= (len(encoded) // enc.n)
mwbf_fer /= (len(encoded) // enc.n)
mwbf_no_loops_fer /= (len(encoded) // enc.n)
pbf_fer /= (len(encoded) // enc.n)

uncoded_ber /= len(encoded)
bf_ber /= len(encoded)
wbf_ber /= len(encoded)
mwbf_ber /= len(encoded)
mwbf_no_loops_ber /= len(encoded)
pbf_ber /= len(encoded)

# plot BER and FER curves for different decoders vs SNR

fig, ax = plt.subplots(nrows=1, ncols=1)
if bp:
    ax.semilogy(snr_db, spa_fer, color='red', linestyle='-', label='SPA-FER')
    ax.semilogy(snr_db, ms_fer, color='blue', linestyle='-', label='MS-FER')
ax.semilogy(snr_db, bf_fer, color='green', linestyle='-', label='BF-FER')
ax.semilogy(snr_db, wbf_fer, color='orange', linestyle='-', label='WBF-FER')
ax.semilogy(snr_db, mwbf_fer, color='purple', linestyle='-', label='MWBF-FER')
ax.semilogy(snr_db, mwbf_no_loops_fer, color='black', linestyle='-', label='MWBF NO LOOPS-FER')
ax.semilogy(snr_db, pbf_fer, color='magenta', linestyle='-', label='PPBF-FER')

ax.semilogy(snr_db, uncoded_ber, color='yellow', linestyle='--', label='Uncoded-BER')
if bp:
    ax.semilogy(snr_db, spa_ber, color='red', linestyle='--', label='SPA-BER')
    ax.semilogy(snr_db, ms_ber, color='blue', linestyle='--', label='MS-BER')
ax.semilogy(snr_db, bf_ber, color='green', linestyle='--', label='BF-BER')
ax.semilogy(snr_db, wbf_ber, color='orange', linestyle='--', label='WBF-BER')
ax.semilogy(snr_db, mwbf_ber, color='purple', linestyle='--', label='MWBF-BER')
ax.semilogy(snr_db, mwbf_no_loops_ber, color='black', linestyle='--', label='MWBF NO LOOPS-BER')
ax.semilogy(snr_db, pbf_ber, color='magenta', linestyle='--', label='PPBF-BER')
ax.set_xlabel('SNR (dB)')
ax.set_ylabel('BER/FER')
ax.set_title('BER/FER vs SNR')
ax.grid(True)
#ax.legend()
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.2,
                 box.width, box.height * 0.8])
# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=3)
timestamp = f'{str(datetime.date.today())}_{datetime.datetime.now().hour}_{datetime.datetime.now().minute}_' \
                f'{datetime.datetime.now().second}'
fig.savefig(f"{timestamp}_ber_fer_vs_snr.eps", dpi=150)
plt.show()
