# Spectral Refinement

Draft-Net models painting trajectories as coarse-to-fine processes. Each progress image is encoded with low-order color statistics, edge summaries, a foreground occupancy estimate, and normalized spectral band energies obtained from the image Fourier transform.

A reverse painting plan is estimated by repeatedly extracting lower-frequency approximations of the final image. Early stages preserve large color masses and atmospheric gradients, while later stages recover edges, shadows, and highlights.
