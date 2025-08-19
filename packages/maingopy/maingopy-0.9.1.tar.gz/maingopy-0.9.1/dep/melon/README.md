# ![MeLOn](doc/images/MeLOn_Logo.png) <br> MeLOn - Machine Learning models for Optimization

Thank you for using the beta version of MeLOn! If you have any issues, concerns, or comments, please communicate them using the "Issues" functionality in [GitLab](https://git.rwth-aachen.de/avt.svt/public/MAiNGO.git) or send an e-mail to artur.schweidtmann@rwth-aachen.de.

## About

MeLOn provides scripts for the training of various machine-learning models and their C++ implementation which can be used in the open-source solver [MAiNGO](http://permalink.avt.rwth-aachen.de/?id=729717).  The machine-learning module git repository currently contains the following models:

* Feedforward neural network for regression
* Gaussian process for regression (Kriging)
* Multifidelity Gaussian process for regression
* Support vector machine for regression
* Support vector machine for outlier detection (one class support vector machine)
* Convex hull of point cloud

For more information, an installation guide and an API overview, please refer to the [MeLOn documentation](https://avt-svt.pages.rwth-aachen.de/public/melon).

## Optimization Methods

* Deterministic global optimization with neural networks embedded [(Schweidtmann and Mitsos, 2019)](#Schweidtmann2019ANN_Opt_Method)
* Deterministic global optimization with Gaussian processes embedded [(Schweidtmann et al., 2020)](#Schweidtmann2020GP_Opt_Method)
* Obey validity domain of data-driven models [(Schweidtmann et al., 2020b)](#Schweidtmann2020ValidityDomain)

## Example Applications
The proposed machine-learning models have been used in various applications.

**Applications of deterministic global optimization with artificial neural networks embedded**

* Hybrid modeling of chemical processes and process optimization [(Schweidtmann and Mitsos, 2019)](#Schweidtmann2019ANN_Opt_Method)

* Rational design of ion separation membranes ([Rall et al., 2019](#Rall2019RationalMembraneDesign), [Rall et al., 2020](#Rall2020SimultaniousProcessAndMembrane),[Rall et al., 2020b](#Rall2020MultiScale))

* Optimization of energy processes where accurate thermodynamic is learned by neural networks. Applications to organic Rankine cycle optimization ([Schweidtmann et al., 2019](#Schweidtmann2019AccurateTD), [Huster et al., 2019](#Huster2019ORC_impact)), working fluid selection ([Huster et al., 2019](#Huster2020ORC_WF_Selection)), working fluid mixtures ([Huster et al., 2020b](#Huster2020ORC_WF_Mixture)), superstructure ([Huster et al., 2020c](#Huster2020ORC_ORC_Superstructure))

* Using of neural networks as a surrogate with a guaranteed accuracy with application to flash models ([Schweidtmann et al., 2019](#Schweidtmann2019Flash))

* Scheduling of a compressed air energy storage system where the efficiency map of compressors and turbines is learned by neural networks ([Schäfer et al., 2020](#Schweidtmann2019ANN_Opt_Method))

* Design of multistage layer melt crystallization  where the crystal growth is learned by neural networks ([Kunde et al., 2022](#Kunde2022))

**Applications of deterministic global optimization with Gaussian processes embedded**

* Chance-constrained programming with Gaussian processes ([Schweidtmann et al., 2020](#Schweidtmann2020GP_Opt_Method))

* Bayesian optimization with global optimization of the acquisition function ([Schweidtmann et al., 2020](#Schweidtmann2020GP_Opt_Method))

## How to Cite This Work


```
@article{schweidtmann2019deterministic,
  title={Deterministic global optimization with artificial neural networks embedded},
  author={Schweidtmann, Artur M and Mitsos, Alexander},
  journal={Journal of Optimization Theory and Applications},
  volume={180},
  number={3},
  pages={925--948},
  year={2019},
  publisher={Springer},
  doi={10.1007/s10957-018-1396-0},
  url={https://doi.org/10.1007/s10957-018-1396-0}
}

```

## References
* Rall, D., Menne, D., Schweidtmann, A. M., Kamp, J., von Kolzenberg, L., Mitsos, A., & Wessling, M. (2019). Rational design of ion separation membranes. Journal of membrane science, 569, 209-219. [https://doi.org/10.1016/j.memsci.2018.10.013](https://doi.org/10.1016/j.memsci.2018.10.013)

<a name="Rall2019RationalMembraneDesign">
</a>

* Rall, D., Schweidtmann, A. M., Aumeier, B. M., Kamp, J., Karwe, J., Ostendorf, K., Mitsos, A. & Wessling, M. (2020). Simultaneous rational design of ion separation membranes and processes. Journal of Membrane Science, 117860. [https://doi.org/10.1016/j.memsci.2020.117860](https://doi.org/10.1016/j.memsci.2020.117860) 

<a name="Rall2020SimultaniousProcessAndMembrane">
</a>

* Rall, D., Schweidtmann, A. M., Kruse, M., Evdochenko, E., Mitsos, A. & Wessling, M. (2020). Multi-scale membrane process optimization with high-fidelity ion transport models through machine learning. Journal of Membrane Science, In Press. [https://doi.org/10.1016/j.memsci.2020.117860](https://doi.org/10.1016/j.memsci.2020.118208) 

<a name="Rall2020MultiScale">
</a>

* Schweidtmann, A. M., & Mitsos, A. (2019). Deterministic global optimization with artificial neural networks embedded. Journal of Optimization Theory and Applications, 180(3), 925-948. [https://doi.org/10.1007/s10957-018-1396-0](https://doi.org/10.1007/s10957-018-1396-0)

<a name="Schweidtmann2019ANN_Opt_Method">
</a>

* Schweidtmann, A. M., Huster, W. R., Lüthje, J. T., & Mitsos, A. (2019). Deterministic global process optimization: Accurate (single-species) properties via artificial neural networks. Computers & Chemical Engineering, 121, 67-74. [https://doi.org/10.1016/j.compchemeng.2018.10.007](https://doi.org/10.1016/j.compchemeng.2018.10.007)

<a name="Schweidtmann2019AccurateTD">
</a>

* Schweidtmann, A. M., Bongartz, D., Huster, W. R., & Mitsos, A. (2019). Deterministic Global Process Optimization: Flash Calculations via Artificial Neural Networks. In Computer Aided Chemical Engineering (Vol. 46, pp. 937-942). Elsevier. [https://doi.org/10.1016/B978-0-12-818634-3.50157-0](https://doi.org/10.1016/B978-0-12-818634-3.50157-0) 

<a name="Schweidtmann2019Flash">
</a>

* Schweidtmann, A. M., Bongartz, D., Grothe, D., Kerkenhoff, T., Lin, X., Najman, J., & Mitsos, A. (2020). Global optimization of Gaussian processes. Submitted. Preprint available on [https://arxiv.org/abs/2005.10902](https://arxiv.org/abs/2005.10902).

<a name="Schweidtmann2020GP_Opt_Method">
</a>

* Schweidtmann, A. M., Weber, J., Wende, C., Netze, L., & Mitsos, A. (2020). Obey validity domains of data-driven models. Submitted. Preprint available on [https://arxiv.org/abs/2010.03405](https://arxiv.org/abs/2010.03405).

<a name="Schweidtmann2020ValidityDomain">
</a>


* Huster, W. R., Schweidtmann, A. M., & Mitsos, A. (2019). Impact of accurate working fluid properties on the globally optimal design of an organic Rankine cycle. In Computer Aided Chemical Engineering (Vol. 47, pp. 427-432). Elsevier.[https://doi.org/10.1016/B978-0-12-818597-1.50068-0](https://doi.org/10.1016/B978-0-12-818597-1.50068-0)

<a name="Huster2019ORC_impact">
</a>

* Huster, W. R., Schweidtmann, A. M., & Mitsos, A. (2020). Working fluid selection for organic rankine cycles via deterministic global optimization of design and operation. Optimization and Engineering, (Vol. 21, pp. 517-536).[https://doi.org/10.1007/s11081-019-09454-1](https://doi.org/10.1007/s11081-019-09454-1)

<a name="Huster2020ORC_WF_Selection">
</a>

* Huster, W. R., Schweidtmann, A. M., & Mitsos, A. (2020). Globally optimal working fluid mixture composition for geothermal power cycles. Energy, (Vol. 212).[https://doi.org/10.1016/j.energy.2020.118731](https://doi.org/10.1016/j.energy.2020.118731)

<a name="Huster2020ORC_WF_Mixture">
</a>

* Huster, W. R., Schweidtmann, A. M., & Mitsos, A. (2020). Deterministic global superstructure-based optimization of an organic Rankine cycle. Computers and Chemical Engineering, (Vol. 141).[https://doi.org/10.1016/j.compchemeng.2020.106996](https://doi.org/10.1016/j.compchemeng.2020.106996)

<a name="Huster2020ORC_ORC_Superstructure">
</a>

* Schäfer, P., Schweidtmann, A. M., Lenz, P. H., Markgraf, H. M., & Mitsos, A. (2020). Wavelet-based grid-adaptation for nonlinear scheduling subject to time-variable electricity prices. Computers & Chemical Engineering, 132, 106598. [https://doi.org/10.1016/j.compchemeng.2019.106598](https://doi.org/10.1016/j.compchemeng.2019.106598) 

<a name="Schäfer2020GridAdaption">
</a>

* Kunde, C., Mendez, R., & Kienle, A. (2022). Deterministic global optimization of multistage layer melt crystallization using surrogate models and reduced space formulations. In Computer Aided Chemical Engineering (Vol. 51, pp. 727-732). Elsevier.[https://doi.org/10.1016/B978-0-323-95879-0.50122-3](https://doi.org/10.1016/B978-0-323-95879-0.50122-3)
<a name="Kunde2022">
</a>






