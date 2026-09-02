# Ramsauer figure source verification

The graph formerly stored as `fig_Ramsauer.jpg` in the AtomicPhys course matches Figure 1 of:

D. D. Reid and J. M. Wadehra, "Scattering of low-energy electrons and positrons by atomic beryllium: Ramsauer-Townsend effect," *Journal of Physics B: Atomic, Molecular and Optical Physics* **47** (2014), 225211. DOI: https://doi.org/10.1088/0953-4075/47/22/225211. Open manuscript: https://arxiv.org/abs/1408.1389.

The paper identifies the graph as a calculated total cross section for low-energy electron scattering from atomic beryllium, not measured argon data. The minimum is `0.016 a0^2` at `0.0029 eV`, where the s-wave phase shift passes through zero. The familiar classic Ramsauer-Townsend experiments concern rare gases and minima at target-dependent sub-eV to roughly eV energies; for argon, Golden and Bandel measured a total-cross-section minimum of `0.125 A^2` at `0.285 eV`: https://doi.org/10.1103/PhysRev.149.58.

Web lookup performed 2026-09-02. The preferred research backend required interactive authentication, so the source was verified through the arXiv manuscript page, DOI metadata, and the American Physical Society abstract.

## Replacement course figure

The beryllium curve is being replaced by a course-generated comparison of the classic noble-gas targets Ar, Kr, and Xe. The numerical curves come from the LXCat SIGLO database records:

- `SIGLO__Ar__Effective__00`: effective momentum-transfer cross section for Ar.
- `SIGLO__Kr__Elastic__17`: elastic momentum-transfer cross section for Kr.
- `SIGLO__Xe__Elastic__32`: elastic momentum-transfer cross section for Xe.

The downloaded source data are preserved in `sources/lxcat_siglo.json`. In this set, the tabulated minima below 5 eV occur at approximately 0.25 eV for Ar, 0.59 eV for Kr, and 0.64 eV for Xe. Dataset: https://www.lxcat.net/SIGLO. Platform citation: L. C. Pitchford et al., "LXCat: an Open-Access, Web-Based Platform for Data Needed for Modeling Low Temperature Plasmas," *Plasma Processes and Polymers* 14, 1600098 (2017), https://doi.org/10.1002/ppap.201600098.

The notebook caption uses the Poisson-Arago spot only as a wave-interference analogy. The optical spot is constructive diffraction in the geometrical shadow, whereas the Ramsauer-Townsend minimum is suppression of electron scattering through partial-wave interference.
