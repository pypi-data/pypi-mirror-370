.. _sc-paracrystal:

sc_paracrystal
=======================================================

Simple cubic lattice with paracrystalline distortion

=========== ================================= ============ =============
Parameter   Description                       Units        Default value
=========== ================================= ============ =============
scale       Scale factor or Volume fraction   None                     1
background  Source background                 |cm^-1|              0.001
dnn         Nearest neighbor distance         |Ang|                  220
d_factor    Paracrystal distortion factor     None                  0.06
radius      Radius of sphere                  |Ang|                   40
sld         Sphere scattering length density  |1e-6Ang^-2|             3
sld_solvent Solvent scattering length density |1e-6Ang^-2|           6.3
theta       c axis to beam angle              degree                   0
phi         rotation about beam               degree                   0
psi         rotation about c axis             degree                   0
=========== ================================= ============ =============

The returned value is scaled to units of |cm^-1| |sr^-1|, absolute scale.


**Definition**

Calculates the scattering from a **simple cubic lattice** with
paracrystalline distortion. Thermal vibrations are considered to be
negligible, and the size of the paracrystal is infinitely large.
Paracrystalline distortion is assumed to be isotropic and characterized
by a Gaussian distribution.

The scattering intensity $I(q)$ is calculated as

.. math::

    I(q) = \frac{\text{scale}}{V_p} V_\text{lattice} P(q) Z(q) + \text{background}

where *scale* is the volume fraction of crystal in the sample volume,
$V_\text{lattice}$ is the volume fraction of spheres in the crystal, $V_p$ is
the volume of the primary particle, $P(q)$ is the form factor of the sphere
(normalized), and $Z(q)$ is the paracrystalline structure factor for a
simple cubic structure.

.. note::
    At this point the GUI does not return $V_\text{lattice}$ separately so that
    the user will need to calculate it from the equation given and the
    appropriate returned parameters.

.. warning::
    As per the equations below, this model will return I(q)=0 for all q if the
    distortion factor is equal to 0. The model is not meant to support perfect
    crystals.

.. figure:: img/sc_crystal_geometry.jpg

    Simple cubic (SC) lattice taken from reference [#Matsuoka1987]_.

Following the derivation from reference [#Matsuoka1987]_, as corrected in
reference [#Matsuoka1990]_, and based on the above figure, the
primitive unit cell vectors are $\vec{a_1},\vec{a_2}$, and $\vec{a_3}$ which
in this case are the same as the conventional unit cell vectors ($\vec{b_1}$,
$\vec{b_2}$, and $\vec{b_3}$) so that

.. math::
    \vec{a_1} &= \vec{b_1} = a \hat{\textbf{x}} \\
    \vec{a_2} &= \vec{b_2} = a \hat{\textbf{y}} \\
    \vec{a_3} &= \vec{b_3} = a \hat{\textbf{z}}.


where $a$ is the lattice parameter which is also in this case the nearest
neighbor distance $D$.

The volume fraction ($V_{lattice}$) of spherical particles with
radius $R$ sitting on the sc lattice is then given by:

.. math::
    V_{lattice} = \frac{4/3 \pi R^3}{D^3}

Now, continuing to follow [#Matsuoka1987]_, the structure (lattice)
factor $Z(\vec{q})$ for a 3D paracrystal can be written as:

.. math::
    Z(\vec{q}) = \prod_{k=1}^{3}Z_k(\vec{q})

with

.. math::
    Z_k(\vec{q}) = \frac{1-|F_k|^2}{1-2|F_k|\cos(\vec{a_k}\cdot\vec{q})+|F_k|^2}

and where $F_k(\vec{q})$ is the structure factor of the primitive unit cell
defined as:

.. math::
    F_k(\vec{q}) = e^{-\frac{1}{2} \Delta a^2_k q^2} \times e^{-i\vec{q}\cdot\vec{a_k}}.

Here, $\vec{a_k}$ are the primitive unit cell vectors $\vec{a_1}$, $\vec{a_2}$,
and $\vec{a_3}$. Furthermore, $\Delta a_k$ is the isotropic distortion of the
lattice point from its ideal position and can be defined by a constant factor
$g=\Delta a / |\vec{a_1}| = \Delta a / |\vec{a_2}| = \Delta a / |\vec{a_3}|=\Delta a/D$.

Finally, assuming the definitions presented in this document, the authors of
reference [#Matsuoka1987]_ have derived the lattice factors which, substituting
$D$ for the lattice parameter $a$, are given by:

.. math::
    Z_1(q,\theta,\phi)&=[1-e^{-q^2\Delta a^2}]/\{1-2e^{-\frac{1}{2}q^2\Delta a^2}\cos(-qD \sin\theta \cos\phi ) + e^{-q^2\Delta a^2}\}\\
    Z_2(q,\theta,\phi)&=[1-e^{-q^2\Delta a^2}]/\{1-2e^{-\frac{1}{2}q^2\Delta a^2}\cos(qD \sin\theta \sin\phi) + e^{-q^2\Delta a^2}\}\\
    Z_3(q,\theta,\phi)&=[1-e^{-q^2\Delta a^2}]/\{1-2e^{-\frac{1}{2}q^2\Delta a^2}\cos(qD \cos\theta) + e^{-q^2\Delta a^2}\}.\\


Finally, the position of the Bragg peaks for the sc lattice are indexed by (reduced q-values):

.. math::
    \frac{qa}{2\pi}=\frac{qD}{2\pi} = \sqrt{h^2+k^2+l^2}

where for a simple cubic lattice there are **no** selection rules for h, k, l
so that all permutations of them give constructive interference. Thus the peak
positions correspond to (just the first 5)

.. math::
    :nowrap:

    \begin{align*}
    q/q_0 \quad & \quad 1
                & \sqrt{2} \quad
                & \quad  \sqrt{3} \quad
                & \sqrt{4} \quad
                & \quad \sqrt{5}\quad \\
    Indices \quad & (100)
                  & \quad (110) \quad
                  & \quad (111)
                  & (200) \quad
                  & \quad (210)
    \end{align*}

.. note::

  The calculation of $Z(q)$ is a double numerical integral that must be
  carried out with a high density of points to properly capture the sharp
  peaks of the paracrystalline scattering. So be warned that the calculation
  is slow. Fitting of any experimental data must be resolution smeared for
  any meaningful fit. This makes a triple integral which may be very slow.
  If a double-precision GPU with OpenCL support is available this may improve
  the speed of the calculation.

The 2D (Anisotropic model) is based on the reference below where *I(q)* is
approximated for 1d scattering. Thus the scattering pattern for 2D may not
be accurate particularly at low $q$. For general details of the calculation
and angular dispersions for oriented particles see :ref:`orientation`.
Note that we are not responsible for any incorrectness of the
2D model computation.

.. figure:: img/parallelepiped_angle_definition.png

    Orientation of the crystal with respect to the scattering plane, when
    $\theta = \phi = 0$ the $c$ axis is along the beam direction (the $z$ axis).


.. figure:: img/sc_paracrystal_autogenfig.png

    1D and 2D plots corresponding to the default parameters of the model.


**Source**

:download:`sc_paracrystal.py <src/sc_paracrystal.py>`
$\ \star\ $ :download:`sc_paracrystal.c <src/sc_paracrystal.c>`
$\ \star\ $ :download:`gauss150.c <src/gauss150.c>`
$\ \star\ $ :download:`sphere_form.c <src/sphere_form.c>`
$\ \star\ $ :download:`sas_3j1x_x.c <src/sas_3j1x_x.c>`

**Reference**

.. [#Matsuoka1987] Hideki Matsuoka et. al. *Physical Review B*, 36 (1987)
   1754-1765 (Original Paper)
.. [#Matsuoka1990] Hideki Matsuoka et. al. *Physical Review B*, 41 (1990)
   3854-3856 (Corrections to FCC and BCC lattice structure calculation)

**Authorship and Verification**

* **Author:** NIST IGOR/DANSE **Date:** pre 2010
* **Last Modified by:** Paul Butler **Date:** Oct 27, 2022
* **Last Reviewed by:** Jonathan Gaudet **Date:** Nov 2, 2022

