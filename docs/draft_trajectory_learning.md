# Draft trajectory learning

A creative work is represented as an ordered sequence of states.

\[
D = (d_0, d_1, \dots, d_T)
\]

An encoder maps each state into a latent vector \(z_t\). Draft-Net then learns bridge dynamics conditioned on both endpoints.
