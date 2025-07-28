import numpy as np
import matplotlib.pyplot as plt

# Simulation Parameters
T = 1000         # Total simulation time in ms
dt = 1           # Time step in ms
time = np.arange(0, T, dt)

# STDP Parameters
A_plus = 0.01    # Learning rate for Long-Term Potentiation (LTP)
A_minus = 0.012  # Learning rate for Long-Term Depression (LTD)
tau_plus = 20.0  # Time constant for LTP in ms
tau_minus = 20.0 # Time constant for LTD in ms

# Initialize synaptic weight array (simulate memristor-based weight)
w = np.zeros_like(time, dtype=float)
w[0] = 0.5     # Initial synaptic weight

# Generate pre- and post-synaptic spike trains as binary sequences.
# For simplicity, we use a low probability to simulate approximately 10 Hz firing rate.
p_pre = 0.01   # Probability of pre-synaptic spike at any ms
p_post = 0.01  # Probability of post-synaptic spike at any ms

np.random.seed(42)  # Seed for reproducibility
pre_spikes = np.random.rand(len(time)) < p_pre
post_spikes = np.random.rand(len(time)) < p_post

# Simulation: Update synaptic weight based on pair-based STDP.
# We use a fixed pairing window (ms) to check for nearby spikes.
window = 50  # ms window for pairing spikes

for t in range(1, len(time)):
    current_weight = w[t-1]
    delta_w = 0.0
    
    # LTP: If a pre-synaptic spike occurs, look ahead for post-synaptic spikes
    if pre_spikes[t]:
        for dt_offset in range(1, window):
            if t + dt_offset < len(time) and post_spikes[t + dt_offset]:
                delta_t = dt_offset  # Positive time difference: pre before post
                delta_w += A_plus * np.exp(-delta_t / tau_plus)
    
    # LTD: If a post-synaptic spike occurs, look back for pre-synaptic spikes
    if post_spikes[t]:
        for dt_offset in range(1, window):
            if t - dt_offset >= 0 and pre_spikes[t - dt_offset]:
                delta_t = dt_offset  
                delta_w -= A_minus * np.exp(-delta_t / tau_minus)
    
    # Update synaptic weight while keeping it within the range [0, 1]
    new_weight = current_weight + delta_w
    w[t] = np.clip(new_weight, 0, 1)

# Visualization
plt.figure(figsize=(12, 10))

# Plot Synaptic Weight Evolution
plt.subplot(3, 1, 1)
plt.plot(time, w, color='blue', lw=2)
plt.xlabel('Time (ms)')
plt.ylabel('Synaptic Weight')
plt.title('Evolution of Synaptic Weight (Memristor Conductance)')
plt.grid(True)

# Plot Pre-Synaptic Spike Train
plt.subplot(3, 1, 2)
pre_spike_times = time[pre_spikes]
plt.eventplot(pre_spike_times, colors='black', lineoffsets=0.5)
plt.xlabel('Time (ms)')
plt.ylabel('Pre-Synaptic Spikes')
plt.title('Pre-Synaptic Spike Train')
plt.xlim(0, T)
plt.ylim(0, 1.5)
plt.grid(True)

# Plot Post-Synaptic Spike Train
plt.subplot(3, 1, 3)
post_spike_times = time[post_spikes]
plt.eventplot(post_spike_times, colors='red', lineoffsets=0.5)
plt.xlabel('Time (ms)')
plt.ylabel('Post-Synaptic Spikes')
plt.title('Post-Synaptic Spike Train')
plt.xlim(0, T)
plt.ylim(0, 1.5)
plt.grid(True)

plt.tight_layout()
plt.show()
