import numpy as np
from ldpc.decoder import DecoderWiFi, awgn_llr, GalBfDecoder, WbfDecoder, WbfVariant
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.utils import QCFile
import matplotlib.pyplot as plt

# create encoder with frame of 648 bits, and rate 1/2. Possible rates and frame sizes are per the ieee802.11n spec.
enc = EncoderWiFi(WiFiSpecCode.N648_R12)
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
h = QCFile.from_file("../ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()

# create decoders
spa_decoder = DecoderWiFi(spec=WiFiSpecCode.N648_R12, max_iter=20)
ms_decoder = DecoderWiFi(spec=WiFiSpecCode.N648_R12, max_iter=20, decoder_type="MS")
bf_decoder = GalBfDecoder(h=h, max_iter=300)
wbf_decoder = WbfDecoder(h=h, max_iter=200, decoder_variant=WbfVariant.WBF)
mwbf_decoder = WbfDecoder(h=h, max_iter=300, decoder_variant=WbfVariant.MWBF, confidence_coefficient=1)
mwbf_no_loops_decoder = WbfDecoder(h=h, max_iter=300, decoder_variant=WbfVariant.MWBF_NO_LOOPS, confidence_coefficient=1)

# consider BPSK signaling
baseband = 1 - 2 * encoded
rng = np.random.default_rng()

snr_db = np.arange(-2, 5)
spa_fer = np.zeros(len(snr_db))
ms_fer = np.zeros(len(snr_db))
bf_fer = np.zeros(len(snr_db))
wbf_fer = np.zeros(len(snr_db))
mwbf_fer = np.zeros(len(snr_db))
mwbf_no_loops_fer = np.zeros(len(snr_db))

spa_ber = np.zeros(len(snr_db))
ms_ber = np.zeros(len(snr_db))
bf_ber = np.zeros(len(snr_db))
wbf_ber = np.zeros(len(snr_db))
mwbf_ber = np.zeros(len(snr_db))
mwbf_no_loops_ber = np.zeros(len(snr_db))

for idx, snr in enumerate(snr_db):
    snr_linear = 10 ** (snr / 10)
    noise_power = 1 / snr_linear
    sigma = np.sqrt(noise_power / 2)
    channel = awgn_llr(sigma=sigma)
    noisy = baseband + sigma*rng.normal(size=len(baseband))
    for frame_idx in range(len(encoded) // enc.n):
        d = spa_decoder.decode(channel(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n]))[0]
        spa_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        spa_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = ms_decoder.decode(channel(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n]))[0]
        ms_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        ms_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = bf_decoder.decode(channel(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n]))[0]
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
        if frame_idx % 10 == 0:
            print(f"SNR: {snr} dB, frame: {frame_idx}")
    print(f"SNR: {snr} dB")
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

spa_fer /= (len(encoded) // enc.n)
ms_fer /= (len(encoded) // enc.n)
bf_fer /= (len(encoded) // enc.n)
wbf_fer /= (len(encoded) // enc.n)
mwbf_fer /= (len(encoded) // enc.n)
mwbf_no_loops_fer /= (len(encoded) // enc.n)
spa_ber /= len(encoded)
ms_ber /= len(encoded)
bf_ber /= len(encoded)
wbf_ber /= len(encoded)
mwbf_ber /= len(encoded)
mwbf_no_loops_ber /= len(encoded)

# plot BER and FER curves for different decoders vs SNR

fig, ax = plt.subplots(nrows=1, ncols=1)
ax.semilogy(snr_db, spa_fer, color='red', linestyle='-', label='SPA-FER')
ax.semilogy(snr_db, ms_fer, color='blue', linestyle='-', label='MS-FER')
ax.semilogy(snr_db, bf_fer, color='green', linestyle='-', label='BF-FER')
ax.semilogy(snr_db, wbf_fer, color='orange', linestyle='-', label='WBF-FER')
ax.semilogy(snr_db, mwbf_fer, color='purple', linestyle='-', label='MWBF-FER')
ax.semilogy(snr_db, mwbf_no_loops_fer, color='black', linestyle='-', label='MWBF NO LOOPS-FER')
ax.semilogy(snr_db, spa_ber, color='red', linestyle='--', label='SPA-BER')
ax.semilogy(snr_db, ms_ber, color='blue', linestyle='--', label='MS-BER')
ax.semilogy(snr_db, bf_ber, color='green', linestyle='--', label='BF-BER')
ax.semilogy(snr_db, wbf_ber, color='orange', linestyle='--', label='WBF-BER')
ax.semilogy(snr_db, mwbf_ber, color='purple', linestyle='--', label='MWBF-BER')
ax.semilogy(snr_db, mwbf_no_loops_ber, color='black', linestyle='--', label='MWBF NO LOOPS-BER')
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
fig.savefig("ber_fer_vs_snr.eps", dpi=150)
plt.show()
