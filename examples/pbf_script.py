import numpy as np
from ldpc.decoder import PbfDecoder, PbfVariant, GalBfDecoder
from ldpc.encoder import EncoderWiFi
from ldpc.wifi_spec_codes import WiFiSpecCode
from ldpc.utils import QCFile
import matplotlib.pyplot as plt


# parity check matrix
h = QCFile.from_file("../ldpc/code_specs/ieee802.11/N648_R12.qc").to_array()
# create decoders
p_vector = np.zeros(14)
for i in range(2, 13):
    p_vector[i] = p_vector[i-1] + 1/12
p_vector[1] = p_vector[2]/2
p_vector[-1] = 1
pbf_decoder = PbfDecoder(h=h, max_iter=1000, decoder_variant=PbfVariant.PPBF, p_vector=p_vector)
bf_decoder = GalBfDecoder(h=h, max_iter=300)

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

# consider BPSK signaling
baseband = 1 - 2 * encoded
rng = np.random.default_rng()

snr_db = np.arange(5.5, 6.6)
pbf_fer = np.zeros(len(snr_db))
pbf_ber = np.zeros(len(snr_db))
bf_fer = np.zeros(len(snr_db))
bf_ber = np.zeros(len(snr_db))

for idx, snr in enumerate(snr_db):
    snr_linear = 10 ** (snr / 10)
    noise_power = 1 / snr_linear
    sigma = np.sqrt(noise_power / 2)
    noisy = baseband + sigma*rng.normal(size=len(baseband))
    for frame_idx in range(len(encoded) // enc.n):
        hard_demod = np.array(noisy[frame_idx * enc.n: (frame_idx + 1) * enc.n] < 0, dtype=np.int_)
        errors = hard_demod^ encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n]
        d = bf_decoder.decode(hard_demod)[0]
        bf_ber[idx] += np.sum(d ^ encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        bf_fer[idx] += np.any(d ^ encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        d = pbf_decoder.decode(hard_demod,1)[0]
        pbf_ber[idx] += np.sum(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        pbf_fer[idx] += np.any(d^encoded[frame_idx * enc.n: (frame_idx + 1) * enc.n])
        if frame_idx % 10 == 0:
            print(f"SNR: {snr} dB, frame: {frame_idx}")
    print(f"SNR: {snr} dB")
    print(f"PPBF BER: {pbf_ber[idx] / len(encoded)}")
    print(f"PPBF FER: {pbf_fer[idx] / (len(encoded) // enc.n)}")


pbf_fer /= (len(encoded) // enc.n)
pbf_ber /= len(encoded)

# plot BER and FER curves for different decoders vs SNR

fig, ax = plt.subplots(nrows=1, ncols=1)
ax.semilogy(snr_db, pbf_fer, color='red', linestyle='-', label='PPBF-FER')
ax.semilogy(snr_db, pbf_ber, color='red', linestyle='--', label='PPBF-BER')
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
fig.savefig("buffer_success_rate_vs_snr.eps", dpi=150)
plt.show()
