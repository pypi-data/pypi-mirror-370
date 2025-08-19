# handsonmachinelearn: new machine learning models

Author: Kaike Sa Teles Rocha Alves

    Author: Kaike Sa Teles Rocha Alves (PhD)
    Email: kaikerochaalves@outlook.com or kaike.alves@estudante.ufjf.br

Github repository: https://github.com/kaikerochaalves/handsonmachinelearn.git

## Instructions

To install the library use the command: 

    pip install handsonmachinelearn

The library provides data-driven fuzzy models, evolving Fuzzy Systems (eFS), and kernel recursive least squares (KRLS), as follows:

-----------------------------------------------------
Packages included:
-----------------------------------------------------

## NFISiS: new fuzzy inference systems

NFISiS (new fuzzy inference systems) is a collection that contains new machine learning models developed by Kaike Alves during his PhD research. 

Doi for preprint: http://dx.doi.org/10.48550/arXiv.2506.06285

Doi to cite the code: http://dx.doi.org/10.5281/zenodo.15746843

Github repository: https://github.com/kaikerochaalves/NFISiS_PyPi

Doi for the thesis: http://dx.doi.org/10.13140/RG.2.2.25910.00324

It provides:

1. New Mamdani Classifier: NewMamadaniClassifier
2. New Mamdani Regressor: NewMamdaniRegressor
3. New Takagi-Sugeno-Kang: NTSK
4. Genetic NMR: GEN_NMR
5. Genetic NTSK: GEN_NTSK
6. Random NMR: R_NMR
7. Random NTSK: R_NTSK

Cite: SA TELES ROCHA ALVES, K., & Pestana de Aguiar, E. (2025). NFISiS: new fuzzy inference systems. Zenodo. https://doi.org/10.5281/zenodo.15746843

Description:

NFISiS: A Novel Python Models for Interpretable Time Series Forecasting and Classification

NFISiS (New Fuzzy Inference Systems) is a groundbreaking Python library available on PyPI (https://pypi.org/project/nfisis/ or https://pypi.org/project/handsonml) that introduces a suite of advanced fuzzy inference systems. This library is specifically designed to tackle the complexities of time series forecasting and classification problems by offering machine learning models that prioritize both high accuracy and enhanced interpretability/explainability.

At its core, NFISiS features novel data-driven Mamdani and Takagi-Sugeno-Kang (TSK) fuzzy models. These models are further empowered by the integration of cutting-edge techniques, including:

*- Genetic Algorithms: Employed for intelligent feature selection, optimizing model performance, and boosting interpretability by identifying the most relevant attributes in complex datasets.*

*- Ensemble Methods: Utilized to combine multiple fuzzy models, leading to superior predictive accuracy and increased robustness against overfitting.*

Unlike many black-box machine learning approaches, NFISiS stands out by providing clear, understandable insights into its decision-making process. This unique combination of advanced fuzzy logic, genetic algorithms, and ensemble techniques allows NFISiS to achieve superior performance across various challenging datasets, including renewable energy, finance, and cryptocurrency applications.

Choose NFISiS to develop powerful and transparent machine learning solutions for your time series analysis needs.

### NewMamdaniClassifier (NMC)

NewMamdaniClassifier is based on Mamdani and applied for classification problems

To import the NewMamdaniClassifier (NMC), simply type the command:

    from handsonmachinelearn.fuzzy import NewMamdaniClassifier as NMC

Hyperparameters:

rules : int, default=5 - Number of fuzzy rules that will be created.

fuzzy_operator : {'prod', 'max', 'min', 'minmax'}, default='prod'
Choose the fuzzy operator:

*- 'prod' will use :`product`*

*- 'max' will use :class:`maximum value`*

*- 'min' will use :class:`minimum value`*

*- 'minmax' will use :class:`minimum value multiplied by maximum`*

Both hyperparameters are important for performance

Example of NewMamdaniClassifier (NMC):

    from handsonmachinelearn.fuzzy import NewMamdaniClassifier as NMC
    model = NMC(rules = 4, fuzzy_operator = "min")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### NewMamdaniRegressor (NMR)

To import the NewMamdaniRegressor (NMR), simply type:

    from handsonmachinelearn.fuzzy import NewMamdaniRegressor as NMR

Hyperparameters
    
rules : int, default=5
Number of fuzzy rules that will be created.

fuzzy_operator : {'prod', 'max', 'min', 'equal'}, default='prod'
Choose the fuzzy operator:

*- 'prod' will use :`product`*

*- 'max' will use :class:`maximum value`*

*- 'min' will use :class:`minimum value`*

*- 'minmax' will use :class:`minimum value multiplied by maximum`*

*- 'equal' use the same firing degree for all rules*

ponder : boolean, default=True
ponder controls whether the firing degree of each fuzzy rule 
is weighted by the number of observations (data points) 
associated with that rule during the tau calculation.
Used to avoid the influence of less representative rules

Example of NewMamdaniRegressor (NMR):

    from handsonmachinelearn.fuzzy import NewMamdaniRegressor as NMR
    model = NMR(rules = 4, fuzzy_operator = "max", ponder=False)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### New Takagi-Sugeno-Kang (NTSK)

To import the NTSK (New Takagi-Sugeno-Kang), type:

    from handsonmachinelearn.fuzzy import NTSK

Hyperparameters
    
rules : int, default=5
Number of fuzzy rules will be created.

lambda1 : float, possible values are in the interval [0,1], default=1
Defines the forgetting factor for the algorithm to estimate the consequent parameters.
This parameters is only used when RLS_option is "RLS"

adaptive_filter : {'RLS', 'wRLS'}, default='RLS'
Algorithm used to compute the consequent parameters:

*- 'RLS' will use :class:`RLS`*

*- 'wRLS' will use :class:`wRLS`*

fuzzy_operator : {'prod', 'max', 'min', 'minmax'}, default='prod'
Choose the fuzzy operator:

*- 'prod' will use :`product`*

*- 'max' will use :class:`maximum value`*

*- 'min' will use :class:`minimum value`*

*- 'minmax' will use :class:`minimum value multiplied by maximum`*

omega : int, default=1000
Omega is a parameters used to initialize the algorithm to estimate
the consequent parameters

ponder : boolean, default=True
ponder controls whether the firing degree of each fuzzy rule 
is weighted by the number of observations (data points) 
associated with that rule during the tau calculation.
Used to avoid the influence of less representative rules

NTSK usually have lower errors than NMR because it uses polynomial functions, however it tends to be less explainable.

Notes: 

1. When using adaptive_filter = "RLS", all rules have the same consequent parameters.
2. When using adaptive_filter="wRLS", the consequent parameters of each rule is adjusted differently by a factor weight.
3. Only use lambda1 when you choose adaptive_filter = 'RLS'.
4. omega is not very relevant for performance.

Example of NTSK (RLS):

    from handsonmachinelearn.fuzzy import NTSK
    model = NTSK(rules = 4, lambda1= 0.99, adaptive_filter = "RLS", fuzzy_operator = "minmax", ponder=False)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

Example of NTSK (wRLS):

    from handsonmachinelearn.fuzzy import NTSK
    model = NTSK(rules = 4, adaptive_filter = "wRLS", fuzzy_operator = "prod", ponder=False)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

NewMandaniClassifier, NewMamdaniRegressor, and NTSK are new data-driven fuzzy models that automatically create fuzzy rules and fuzzy sets. You can learn more about this models in papers: https://doi.org/10.1016/j.engappai.2024.108155, https://doi.org/10.1007/s10614-024-10670-w, http://dx.doi.org/10.48550/arXiv.2506.06285, and http://dx.doi.org/10.13140/RG.2.2.25910.00324

The library nfisis also includes the NTSK and NMR (NewMandaniRegressor) with genetic-algorithm as attribute selection. At this time, the paper containing the proposal of these models are fourthcoming.

### Genetic NMR (GEN-NMR)

To import GEN-NMR type:

    from handsonmachinelearn.genetic import GEN_NMR

Hyperparameters
    
rules : int, default=5
Number of fuzzy rules that will be created.

fuzzy_operator : {'prod', 'max', 'min', 'equal'}, default='prod'
Choose the fuzzy operator:

*- 'prod' will use :`product`*

*- 'max' will use :class:`maximum value`*

*- 'min' will use :class:`minimum value`*

*- 'minmax' will use :class:`minimum value multiplied by maximum`*

*- 'equal' use the same firing degree for all rules*

ponder : boolean, default=True
If True, the firing degree of each fuzzy rule will be weighted by the number of observations
associated with that rule. This gives more influence to rules derived from a larger
number of training data points. If False, all rules contribute equally regardless
of their observation count.

num_generations : int, default=10
Number of generations the genetic algorithm will run. A higher number of generations
allows the algorithm to explore more solutions and potentially find a better one,
but increases computation time.

num_parents_mating : int, default=5
Number of parents that will be selected to mate in each generation.
These parents are chosen based on their fitness values to produce offspring.

sol_per_pop : int, default=10
Number of solutions (individuals) in the population for the genetic algorithm.
A larger population can increase the diversity of solutions explored,
but also increases computational cost per generation.

error_metric : {'RMSE', 'NRMSE', 'NDEI', 'MAE', 'MAPE'}, default='RMSE'
The error metric used as the fitness function for the genetic algorithm.
The genetic algorithm aims to minimize this metric (by maximizing its negative value).

*- 'RMSE': Root Mean Squared Error.*

*- 'NRMSE': Normalized Root Mean Squared Error.*

*- 'NDEI': Non-Dimensional Error Index.*

*- 'MAE': Mean Absolute Error.*

*- 'MAPE': Mean Absolute Percentage Error.*


print_information : bool, default=False
If True, information about the genetic algorithm's progress (e.g., generation number,
current fitness, and fitness change) will be printed during the `fit` process.

parallel_processing : list or None, default=None
Configuration for parallel processing using PyGAD's capabilities.
Refer to PyGAD's documentation for valid formats. If None, parallel processing
is not used. 

*- parallel_processing=None: no parallel processing is applied,*

*- parallel_processing=['process', 10]: applies parallel processing with 10 processes,*

*- parallel_processing=['thread', 5] or parallel_processing=5: applies parallel processing with 5 threads.*


Example of GEN-NMR:

    from handsonmachinelearn.genetic import GEN_NMR
    model = GEN_NMR(rules = 3, fuzzy_operator = "minmax", ponder = False, num_generations = 20, num_parents_mating = 10, sol_per_pop = 10, error_metric = "MAE", print_information=True, parallel_processing=5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### Genetic NTSK (GEN-NTSK)

To import GEN-NTSK type:

    from handsonmachinelearn.genetic import GEN_NTSK

Hyperparameters
    
rules : int, default=5
Number of fuzzy rules will be created.

lambda1 : float, possible values are in the interval [0,1], default=1
Defines the forgetting factor for the algorithm to estimate the consequent parameters.
This parameters is only used when RLS_option is "RLS"

adaptive_filter : {'RLS', 'wRLS'}, default='wRLS'
Algorithm used to compute the consequent parameters:

*- 'RLS' will use :class:`RLS`*

*- 'wRLS' will use :class:`wRLS`*


fuzzy_operator : {'prod', 'max', 'min', 'minmax'}, default='prod'
Choose the fuzzy operator:

*- 'prod' will use :`product`*

*- 'max' will use :class:`maximum value`*

*- 'min' will use :class:`minimum value`*

*- 'minmax' will use :class:`minimum value multiplied by maximum`*

omega : int, default=1000
Omega is a parameters used to initialize the algorithm to estimate
the consequent parameters

ponder : bool, default=True
If True, the firing degree of each fuzzy rule will be weighted by the number of observations
associated with that rule. This gives more influence to rules derived from a larger
number of training data points. If False, all rules contribute equally regardless
of their observation count.

num_generations : int, default=10
Number of generations the genetic algorithm will run. A higher number of generations
allows the algorithm to explore more solutions and potentially find a better one,
but increases computation time.

num_parents_mating : int, default=5
Number of parents that will be selected to mate in each generation.
These parents are chosen based on their fitness values to produce offspring.

sol_per_pop : int, default=10
Number of solutions (individuals) in the population for the genetic algorithm.
A larger population can increase the diversity of solutions explored,
but also increases computational cost per generation.

error_metric : {'RMSE', 'NRMSE', 'NDEI', 'MAE', 'MAPE'}, default='RMSE'
The error metric used as the fitness function for the genetic algorithm.
The genetic algorithm aims to minimize this metric (by maximizing its negative value).

*- 'RMSE': Root Mean Squared Error.*

*- 'NRMSE': Normalized Root Mean Squared Error.*

*- 'NDEI': Non-Dimensional Error Index.*

*- 'MAE': Mean Absolute Error.*

*- 'MAPE': Mean Absolute Percentage Error.*


print_information : bool, default=False
If True, information about the genetic algorithm's progress (e.g., generation number,
current fitness, and fitness change) will be printed during the `fit` process.

parallel_processing : list or None, default=None
Configuration for parallel processing using PyGAD's capabilities.
Refer to PyGAD's documentation for valid formats. If None, parallel processing
is not used. 

*- parallel_processing=None: no parallel processing is applied,*

*- parallel_processing=['process', 10]: applies parallel processing with 10 processes,*

*- parallel_processing=['thread', 5] or parallel_processing=5: applies parallel processing with 5 threads.*


Example of GEN-NTSK:

    from handsonmachinelearn.genetic import GEN_NTSK
    model = GEN_NTSK(rules = 6, error_metric = "MAE", print_information=True)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

Finally, one last inovation of this library that was part of the reasearch of the PhD of Kaike Alves and it is in his forthcoming thesis is the ensemble model with fuzzy systems, reffered as to R_NMR and R_NTSK:

### Random NMR (R-NMR)

    from handsonmachinelearn.ensemble import R_NMR

Hyperparameters:

n_estimators : int, default=100
The number of individual models (estimators) that will be generated
and combined to form the ensemble. A higher number of estimators
generally leads to a more robust and accurate ensemble but increases
training time. Think of this as how many "experts" you're gathering
to make a final decision.

n_trials : int, default=5
For each estimator in the ensemble, this parameter specifies the
number of attempts (trials) to find the best-performing underlying
model and its optimal feature subset. More trials increase the
chances of discovering a better individual model, but it also means
more computational effort.

combination : {'mean', 'median', 'weighted_average'}, default='mean'
This hyperparameter dictates the technique used to combine the
predictions from all the individual estimators in the ensemble into
a single final prediction.

*- 'mean': The final prediction is the simple average of all individual
model predictions. This is a straightforward and often effective method.*

*- 'median': The final prediction is the median of all individual model
predictions. This can be more robust to outliers in individual
predictions than the mean.*

*- 'weighted_average': The final prediction is a weighted average of the
individual model predictions. Models that performed better during their
training (i.e., had lower errors) are given a higher weight, allowing
more "reliable" experts to influence the final outcome more significantly.*


error_metric : {'RMSE', 'NRMSE', 'NDEI', 'MAE', 'MAPE', 'CPPM'}, default='RMSE'
This is the performance metric used to evaluate and select the best
individual models during the training process. The goal is to minimize 
these error metrics (or maximize CPPM, as it's a "correctness" metric).

*- 'RMSE': Root Mean Squared Error. Penalizes large errors more heavily,
making it sensitive to outliers.*

*- 'NRMSE': Normalized Root Mean Squared Error. RMSE scaled by the range
of the target variable, making it unit-less and easier to compare
across different datasets.*

*- 'NDEI': Non-Dimensional Error Index. Similar to NRMSE but scaled by
the standard deviation of the target variable.*

*- 'MAE': Mean Absolute Error. Represents the average magnitude of the
errors, giving equal weight to all errors. Less sensitive to outliers
than RMSE.*

*- 'MAPE': Mean Absolute Percentage Error. Expresses error as a
percentage, which is often intuitive for business contexts. It can be
problematic with zero or near-zero actual values.*

*- 'CPPM': Correct Percentual Predictions of Movement. Measures the
percentage of times the model correctly predicts the direction of
change (increase or decrease) in the target variable. A higher CPPM
indicates better directional forecasting. For optimization, its
negative value is used as the fitness function.*

parallel_processing : int
This parameter controls whether the training of individual estimators in
the ensemble will be performed in parallel to speed up the process.

*- -1: Utilizes all available CPU cores on your system, maximizing
parallel computation.*

*- 0: Disables parallel processing; training will be performed sequentially.*

*- >0: Uses the exact specified number of CPU cores for parallel execution.
For example, `parallel_processing=4` would use 4 cores.*


Example of R-NMR

    from handsonmachinelearn.ensemble import R_NMR
    model = R_NMR(n_estimators = 50, error_metric = "MAE", parallel_processing=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)


### Random NTSK (R-NTSK)

    from handsonmachinelearn.ensemble import R_NTSK

Hyperparameters:

n_estimators : int, default=100
The number of individual models (estimators) that will be generated
and combined to form the ensemble. A higher number of estimators
generally leads to a more robust and accurate ensemble but increases
training time. Think of this as how many "experts" you're gathering
to make a final decision.

n_trials : int, default=5
For each estimator in the ensemble, this parameter specifies the
number of attempts (trials) to find the best-performing underlying
model and its optimal feature subset. More trials increase the
chances of discovering a better individual model, but it also means
more computational effort.

combination : {'mean', 'median', 'weighted_average'}, default='mean'
This hyperparameter dictates the technique used to combine the
predictions from all the individual estimators in the ensemble into
a single final prediction.
*- 'mean': The final prediction is the simple average of all individual
model predictions. This is a straightforward and often effective method.*

*- 'median': The final prediction is the median of all individual model
predictions. This can be more robust to outliers in individual
predictions than the mean.*

*- 'weighted_average': The final prediction is a weighted average of the
individual model predictions. Models that performed better during their
training (i.e., had lower errors) are given a higher weight, allowing
more "reliable" experts to influence the final outcome more significantly.*

error_metric : {'RMSE', 'NRMSE', 'NDEI', 'MAE', 'MAPE', 'CPPM'}, default='RMSE'
This is the performance metric used to evaluate and select the best
individual models during the training process. The goal is to minimize
these error metrics (or maximize CPPM, as it's a "correctness" metric).

*- 'RMSE': Root Mean Squared Error. Penalizes large errors more heavily,
making it sensitive to outliers.*

*- 'NRMSE': Normalized Root Mean Squared Error. RMSE scaled by the range
of the target variable, making it unit-less and easier to compare
across different datasets.*

*- 'NDEI': Non-Dimensional Error Index. Similar to NRMSE but scaled by
the standard deviation of the target variable.*

*- 'MAE': Mean Absolute Error. Represents the average magnitude of the
errors, giving equal weight to all errors. Less sensitive to outliers
than RMSE.*

*- 'MAPE': Mean Absolute Percentage Error. Expresses error as a
percentage, which is often intuitive for business contexts. It can be
problematic with zero or near-zero actual values.*

*- 'CPPM': Correct Percentual Predictions of Movement. Measures the
percentage of times the model correctly predicts the direction of
change (increase or decrease) in the target variable. A higher CPPM
indicates better directional forecasting. For optimization, its
negative value is used as the fitness function.*

parallel_processing : int
This parameter controls whether the training of individual estimators in
the ensemble will be performed in parallel to speed up the process.

*- -1: Utilizes all available CPU cores on your system, maximizing
parallel computation.*

*- 0: Disables parallel processing; training will be performed sequentially.*

*- >0: Uses the exact specified number of CPU cores for parallel execution.
For example, `parallel_processing=4` would use 4 cores.*

Example of R-NMR

    from handsonmachinelearn.ensemble import R_NTSK
    model = R_NTSK(n_estimators = 200, parallel_processing=-1)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

Extra details

If you want to look closely to the generated rules, you can see the rules typing:

    model.show_rules()

Otherwise, you can see the histogram of the rules by typing:

    model.plot_hist

The fuzzy models are quite fast, but the genetic and ensembles are still a bit slow. If you think you can contribute to this project regarding the code, speed, etc., please, feel free to contact me and to do so.

## evolving Fuzzy Systems (eFS)

Doi for ePL-KRLS-DISCO paper: https://doi.org/10.1016/j.asoc.2021.107764
Doi to cite the code: https://doi.org/10.5281/zenodo.15748291
Git hub repository: https://github.com/kaikerochaalves/evolvingfuzzysystems.git

Cite: SA TELES ROCHA ALVES, K. (2025). Evolvingfuzzysystems: a new Python library. Zenodo. https://doi.org/10.5281/zenodo.15748291

It provides the following models:

1. evolving Participaroty Learning with Kernel Recursive Least Square and Distance Correlation (ePL-KRLS-DISCO)
2. enhanced evolving Participatory Learning (ePL+)
3. evolving Multivariable Gaussian (eMG)
4. evolving Participatory Learning (ePL)
5. extended Takagi-Sugeno (eTS)
6. Simplified evolving Takagi-Sugeno (Simpl_eTS)
7. evolving Takagi-Sugeno (eTS)

*- Note: normalize the data in the range [0,1] for performance*

Summary:

The evolvingfuzzysystems library is a Python package that provides implementations of various Evolving Fuzzy Systems (eFS) models available on (https://pypi.org/project/evolvingfuzzysystems/ or https://pypi.org/project/handsonml). These models are a class of machine learning algorithms capable of adaptively updating their structure in response to data dynamics while maintaining interpretability. The library aims to address the limited public availability of eFS model implementations, thereby fostering broader accessibility and adoption in research and practical applications.

Key features and capabilities of evolvingfuzzysystems include:

- Implemented eFS Models: The library offers several well-established eFS models, such as ePL-KRLS-DISCO, ePL+, eMG, ePL, exTS, SimpleTS, and eTS.

- Adaptive Learning: eFS models can update their internal structure without requiring retraining, which is a significant advantage over traditional machine learning models in dynamic environments. They can autonomously develop their structure, capture data stream dynamics, and produce accurate results even with nonlinear data.

- Interpretability: eFS models offer interpretability, combining accuracy, flexibility, and simplicity.

- Performance Evaluation Tools: The library includes built-in tools for training, visualization, and performance assessment, facilitating model evaluation and comparison.

- Computational Efficiency: Models within the library implement adaptive filters like Recursive Least Squares (RLS) and Weighted Recursive Least Squares (wRLS) for estimating consequent parameters.

- Visualization: The library provides functions to visualize fuzzy rules and their evolution during the training phase, enhancing the interpretability of the models. This includes: show_rules(), plot_rules(), plot_gaussians(), plot_rules_evolution(), and plot_2d_projections().

- Installation: The package can be easily installed using pip with the command: pip install evolvingfuzzysystems.

The library evaluates its models using the California housing dataset, measuring performance with metrics like normalized root-mean-square error (NRMSE), non-dimensional error index (NDEI), and mean absolute percentage error (MAPE). Computational complexity is also analyzed by measuring execution times and rule evolution during training and testing phases. Notably, the ePL model demonstrates a balance between accuracy and computational cost, making it suitable for real-world applications.


### ePL-KRLS-DISCO

To import the ePL-KRLS-DISCO, simply type the command:

    from handsonmachinelearn.eFS import ePL_KRLS_DISCO

Hyperparameters:

    alpha: float, possible values are in the interval [0,1], default=0.001
    This parameter controls the learning rate for updating the rule centers. A higher value means faster adaptation of rule centers to new data.

    beta: float, possible values are in the interval [0,1], default=0.05
    This parameter determines the adaptation rate of the arousal index, which influences the creation of new rules.

    sigma: float, must be a positive float, default=0.5
    This parameter defines the width of the Gaussian membership functions for the antecedent part of the rules. A smaller sigma leads to narrower, more specific fuzzy sets, while a larger sigma creates broader, more general fuzzy sets.

    lambda1: float, possible values are in the interval [0,1], default=0.0000001
    This acts as a regularization parameter in the KRLS algorithm. It helps prevent overfitting and improves the stability of the inverse matrix calculation.
    
    e_utility: float, possible values are in the interval [0,1], default=0.05
    This is the utility threshold for pruning rules. Rules whose utility falls below this value are considered for removal, aiming to maintain a parsimonious model.
    
    tau: float, possible values are in the interval [0,1], default=0.05
    This is the threshold for the arousal index. If the minimum arousal index among all existing rules exceeds tau, a new rule is considered for creation.

    omega: int, must be a positive integer, default=1
    This parameter is used in the initialization of the Q matrix within the KRLS algorithm. It can be seen as an initial regularization term for the covariance matrix estimate.

Examples:

    from handsonmachinelearn.eFS import ePL_KRLS_DISCO
    model = ePL_KRLS_DISCO()
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

Notes:

1. The hyperparameters alpha, beta, and sigma are the most relevant for performance
2. The hyperparameters are in the range [0,1] considering the data are normalized in the range [0.1]

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import ePL_KRLS_DISCO
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = ePL_KRLS_DISCO(alpha = 0.01, beta=0.06, tau=0.04, sigma=10)
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

### ePL+

To import the ePL+, simply type:

    from handsonmachinelearn.eFS import ePL_plus

Hyperparameters:

    alpha: float, possible values are in the interval [0,1], default = 0.001
    This parameter controls the learning rate for updating the rule centers. 
    A smaller alpha means slower adaptation of rule centers to new data, 
    while a larger alpha results in faster adaptation.

    beta: float, possible values are in the interval [0,1], default = 0.1
    This parameter controls the learning rate for updating the arousal index. 
    The arousal index helps determine when a new rule should be created. 
    A higher beta makes the system more responsive to new patterns, 
    potentially leading to more rules.

    tau: float, possible values are in the interval [0,1] or None, 
    default = None (defaults to beta)
    This parameter serves as a threshold for the arousal index to 
    determine whether a new rule needs to be created. If the minimum 
    arousal index among existing rules exceeds tau, a new rule is considered.
    If tau is None, it automatically takes the value of beta.

    e_utility: float, possible values are in the interval [0,1], default = 0.05
    This parameter is a threshold for the utility measure of a rule. R
    ules whose utility (which relates to their contribution over time) 
    falls below this threshold are considered for removal, helping to prune
    redundant or inactive rules.

    pi: float, possible values are in the interval [0,1], default = 0.5
    This parameter is a forgetting factor for updating the rule's radius (sigma). 
    It controls how much influence new observations have on adapting the spread 
    of a rule, balancing between current data and historical information.

    sigma: float, possible values are in the interval [0,1], default = 0.25
    This parameter represents the initial radius or spread for the 
    Gaussian membership functions of new rules. It influences how broadly 
    a new rule covers the input space.

    lambda1: float, possible values are in the interval [0,1], default = 0.35
    This parameter is a threshold for the similarity index. If the 
    compatibility between two rules (or a new data point and an existing rule) 
    is greater than or equal to lambda1, it can trigger rule merging or 
    influence how existing rules are updated.

    omega: int, must be a positive integer, default = 1000
    This parameter is used to initialize the P matrix (covariance matrix inverse) 
    in the weighted Recursive Least Squares (wRLS) algorithm. A larger 
    omega generally indicates less confidence in initial parameters,
    allowing for faster early adaptation.

Notes:

1. The hyperparameters alpha, beta, tau, e_utility, and pi are the most relevant for performance. If tau is None it receives beta value
2. The hyperparameters are in the range [0,1] considering the data are normalized in the range [0.1]

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import ePL_plus
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = ePL_plus(alpha = 0.1, beta=0.2, sigma=0.3)
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

### eMG

To import the eMG, type:

    from handsonmachinelearn.eFS import eMG

Hyperparameters:

    alpha: float, possible values are in the interval [0,1], default = 0.01
    This parameter controls the learning rate for updating the rule centers
    and covariance matrices. A smaller alpha means slower adaptation, 
    while a larger alpha leads to faster changes in rule parameters.

    w: int, must be an integer greater than 0, default = 10
    This parameter defines the window size for computing the arousal index.
    The arousal index, which influences rule creation, is based on the recent 
    history of data points falling within or outside the confidence region 
    of a rule, over this w number of samples.

    sigma: float, must be a positive float, default = 0.05
    This parameter represents the initial diagonal value for the covariance 
    matrix (Sigma) of newly created rules. It essentially defines the initial 
    spread of a new Gaussian rule in each dimension.

    lambda1: float, possible values are in the interval [0,1], default = 0.1
    This parameter defines a significance level for the chi-squared test used 
    to determine the thresholds for rule creation and merging (Tp). 
    It influences how "novel" a data point needs to be to potentially 
    trigger a new rule or how "similar" two rules need to be to be merged.

    omega: int, must be a positive integer, default = 100
    This parameter is used to initialize the Q matrix 
    (inverse of the covariance matrix) in the Recursive Least Squares (RLS) 
    algorithm, which estimates the consequent parameters of each rule. 
    A larger omega implies a larger initial uncertainty in the consequent 
    parameters, allowing for faster early adjustments.

1. The hyperparameters alpha and w are the most relevant for performance. If tau is None it receives beta value
2. The hyperparameters are in the range [0,1] considering the data are normalized in the range [0.1]

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import eMG
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = eMG(alpha = 0.1, w=25)
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

### ePL

To import the ePL, type:

    from handsonmachinelearn.eFS import ePL

Hyperparameters:

    alpha: float, possible values are in the interval [0,1], default = 0.001
    This parameter controls the learning rate for updating the rule centers. 
    A smaller alpha means slower adaptation, while a larger alpha leads to 
    faster changes in rule centers.

    beta: float, possible values are in the interval [0,1], default = 0.5
    This parameter controls the learning rate for updating the arousal index. 
    The arousal index influences the creation of new rules; a higher beta 
    makes the system more sensitive to new patterns and potentially creates 
    new rules more readily.

    tau: float, possible values are in the interval [0,1] or None, default = None (defaults to beta)
    This parameter serves as a threshold for the arousal index. 
    If the minimum arousal index among existing rules exceeds tau, 
    a new rule is considered for creation. If tau is None, it automatically 
    takes the value of beta.

    lambda1: float, possible values are in the interval [0,1], default = 0.35
    This parameter is a threshold for the similarity index. If the compatibility 
    between two rules (or a new data point and an existing rule) is greater 
    than or equal to lambda1, it can trigger rule merging.

    sigma: float, must be a positive float, default = 0.25
    This is the fixed bandwidth parameter for the Gaussian membership functions. 
    It determines the spread of the Gaussian functions; a smaller sigma leads 
    to narrower, more localized rules, while a larger sigma creates broader, 
    more generalized rules.

    omega: int, must be a positive integer, default = 1000
    This parameter is used to initialize the P matrix (covariance matrix inverse) 
    in the weighted Recursive Least Squares (wRLS) algorithm. A larger s generally 
    indicates less confidence in initial parameters, allowing for faster early 
    adaptation.

1. The hyperparameters alpha, beta and tau are the most relevant for performance. If tau is None it receives beta value
2. The hyperparameters are in the range [0,1] considering the data are normalized in the range [0.1]

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import ePL
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = ePL(alpha = 0.1, beta = 0.2, lambda1 = 0.5, sigma = 0.1)
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

### exTS

To import the exTS, type:

    from handsonmachinelearn.eFS import exTS

Hyperparameters:

    rho: float, possible values are in the interval [0,1], default = 1/2 (0.5)
    This parameter is a forgetting factor for updating the rule's radius (sigma). 
    It controls how much influence new observations have on adapting the spread 
    of a rule, balancing between current data and historical information.

    mu: float or int, must be greater than 0, default = 1/3
    This parameter acts as a threshold for the membership degree (mu) 
    of a data point to a rule. If all membership degrees of existing rules 
    are below mu, it indicates a novel data region, potentially leading to 
    the creation of a new rule.

    epsilon: float, possible values are in the interval [0,1], default = 0.01
    This parameter is a threshold for rule removal based on their relative number 
    of observations. Rules whose proportion of total observations falls 
    below epsilon are considered for pruning, aiming to remove underutilized rules.

    omega: int, must be a positive integer, default = 1000
    This parameter is used to initialize the C matrix 
    (covariance matrix inverse) in the weighted Recursive Least Squares (wRLS) 
    algorithm, which estimates the consequent parameters of each rule. 
    A larger omega implies a larger initial uncertainty in the consequent parameters, 
    allowing for faster early adjustments.

1. The hyperparameters rho, mu and epsilon are the most relevant for performance. 
2. The hyperparameters are in the range [0,1] considering the data are normalized in the range [0.1]

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import exTS
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = exTS()
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

### Simpl_eTS

To import the Simpl_eTS, type:

    from handsonmachinelearn.eFS import Simpl_eTS

Hyperparameters:

    r: float or int, must be greater than 0, default = 0.1
    This parameter defines the radius for the Cauchy membership functions. 
    It controls the spread of the membership functions; a smaller r leads 
    to more localized rules, while a larger r creates broader rules. 
    It is also used as a threshold for determining if a data point is 
    close enough to an existing rule to update it.

    epsilon: float, possible values are in the interval [0,1], default = 0.01
    This parameter is a threshold for rule removal based on their relative number 
    of observations. Rules whose proportion of total observations falls below 
    epsilon are considered for pruning, aiming to remove underutilized rules.

    omega: int, must be a positive integer, default = 1000
    This parameter is used to initialize the C matrix (covariance matrix inverse) 
    in the weighted Recursive Least Squares (wRLS) algorithm, which estimates 
    the consequent parameters of each rule. A larger omega implies a larger 
    initial uncertainty in the consequent parameters, allowing for faster early 
    adjustments.

1. The hyperparameters r and epsilon are the most relevant for performance. 
2. The hyperparameters are in the range [0,1] considering the data are normalized in the range [0.1]

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import Simpl_eTS
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = Simpl_eTS(r = 0.2, epsilon=0.01)
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

### eTS

To import the eTS, type:

    from handsonmachinelearn.eFS import eTS

Hyperparameters:

    r: float or int, must be greater than 0, default = 0.1
    This parameter defines the radius for the Gaussian membership functions. 
    It controls the spread of the membership functions; a smaller r leads 
    to more localized rules, while a larger r creates broader rules. 
    It is also used as a threshold in the rule creation logic.

    omega: int, must be a positive integer, default = 1000
    This parameter is used to initialize the C matrix 
    (covariance matrix inverse) in the weighted Recursive Least Squares 
    (wRLS) algorithm, which estimates the consequent parameters of each rule. 
    A larger omega implies a larger initial uncertainty in the consequent parameters,
    allowing for faster early adjustments.

Example:

    from sklearn.preprocessing import MinMaxScaler
    from handsonmachinelearn.eFS import eTS
    scaler = MinMaxScaler()
    scaler.fit(X_train)
    X_test = scaler.transform(X_test)
    model = eTS(r = 0.1)
    model.fit(X_train, y_train)
    model.evolve(X_val, y_val)
    y_pred = model.predict(y_test)

Extra details:

If you want to see how many rules was generated, you can type:

    model.n_rules()

You can see the rules graphically by typing:

    model.plot_rules()

If you want to see all Gaussian fuzzy sets, type:

    model.plot_gaussians()

To see the evolution of the rules along with the training, type:

    model.plot_rules_evolution()

For the eMG model, as it uses covariance matrix to model the distribution of the input vector, if you want to visualize the covariance between two attributes, type:

    model.plot_2d_projections()

These last four function that plots graphics accepts extra arguments:

    grid (boolean): if you want the graphic with grid
    save (boolean): if you want to save the graphic
    format_save (default='eps'): the format you want to save the graphic.
    dpi (integer, default=1200): the resolution to save the graphic

You can learn more about the ePL-KRLS-DISCO and eFSs in the paper: https://doi.org/10.1016/j.asoc.2021.107764.

## KRLS: Kernel Recursive Least Squares

Doi to cite the code: http://dx.doi.org/10.5281/zenodo.15800969

Github repository: https://github.com/kaikerochaalves/KRLS_pypi.git

It provides:

1. Kernel Recursive Least Squares: KRLS
2. Sliding Window Kernel Recursive Least Squares: SW-KRLS
3. Extended Kernel Recursive Least Squares: EX-KRLS
4. Fixed Base Kernel Recursive Least Squares: FB-KRLS
5. Kernel Recursive Least Squares Tracker: KRLS-T
6. Quantized Kernel Recursive Least Squares: QKRLS
7. Adaptive Dynamic Adjustment Kernel Recursive Least Squares: ADA-KRLS
8. Quantized Adaptive Dynamic Adjustment Kernel Recursive Least Squares: QALD-KRLS
9. Light Kernel Recursive Least Squares: Light-KRLS

Cite: SA TELES ROCHA ALVES, K. (2025). KRLS: Kernel Recursive Least Squares. Zenodo. https://doi.org/10.5281/zenodo.15800969

Description:

KRLS: A Novel Python Library for Kernel Recursive Least Squares Model

KRLS (Kernel Recursive Least Squares) is a groundbreaking Python library available on PyPI (https://pypi.org/project/krls/ or https://pypi.org/project/handsonml) that introduces a suite of advanced fuzzy inference systems. This library is specifically designed to tackle the complexities of time series forecasting and classification problems by offering machine learning models that prioritize high accuracy.

At its core, KRLS features data-driven machine learning models. 

Instructions

The library provides 6 models in fuzzy systems, as follows:

### KRLS

To import the KRLS, simply type the command:

    from handsonmachinelearn.krls import KRLS

Hyperparameters:

    nu : float, default=0.01
    Accuracy parameter determining the level of sparsity. Must be a positive float.

    N : int, default=100
    Accuracy parameter determining the level of sparsity. Must be a integer greater 
    than 1.

    kernel_type : str
    The type of kernel function to use. Must be one of: 'Linear', 'Polynomial', 'RBF', 'Gaussian',
    'Sigmoid', 'Powered', 'Log', 'GeneralizedGaussian', 'Hybrid', additive_chi2, and Cosine.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of KRLS:

    from handsonmachinelearn.krls import KRLS
    model = KRLS(nu=0.001, N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### SW-KRLS

To import the SW-KRLS, simply type the command:

    from handsonmachinelearn.krls import SW_KRLS

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. 
    Must be an integer greater than 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    kernel_type : str
    The type of kernel function to use. Must be one of: 'Linear', 'Polynomial', 'RBF', 'Gaussian',
    'Sigmoid', 'Powered', 'Log', 'GeneralizedGaussian', 'Hybrid', additive_chi2, and Cosine.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of SW_KRLS:

    from handsonmachinelearn.krls import SW_KRLS
    model = SW_KRLS(N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### EX-KRLS

To import the EX-KRLS, simply type the command:

    from handsonmachinelearn.krls import EX_KRLS

Hyperparameters:

    alpha : float, default=0.999
    State forgetting factor. Must be a float between 0 and 1.

    beta : float, default=0.995
    Data forgetting factor. Must be a float between 0 and 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    q : float, default=1e-6
    Trade-off between modeling variation and measurement disturbance. Must be a very small float.

    N : int, default=100
    Accuracy parameter determining the level of sparsity. Must be an integer greater than 1.

    kernel_type : str
    The type of kernel function to use. Must be one of: 'Linear', 'Polynomial', 'RBF', 'Gaussian',
    'Sigmoid', 'Powered', 'Log', 'GeneralizedGaussian', 'Hybrid', additive_chi2, and Cosine.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of EX_KRLS:

    from handsonmachinelearn.krls import EX_KRLS
    model = EX_KRLS(kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### FB-KRLS

To import the EX-KRLS, simply type the command:

    from handsonmachinelearn.krls import FB_KRLS

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. 
    Must be an integer greater than 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of FB_KRLS:

    from handsonmachinelearn.krls import FB_KRLS
    model = FB_KRLS(N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### KRLS-T

To import the KRLS-T, simply type the command:

    from handsonmachinelearn.krls import KRLS_T

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. 
    Must be an integer greater than 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of KRLS_T:

    from handsonmachinelearn.krls import KRLS_T
    model = KRLS_T(N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### QKRLS

To import the QKRLS, simply type the command:

    from handsonmachinelearn.krls import QKRLS

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. Must be an integer greater than 1.
        
    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    epsilon : float, default=0.01
    Quantization size. Must be a float between 0 and 1.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of QKRLS:

    from handsonmachinelearn.krls import QKRLS
    model = QKRLS(N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### ADA-KRLS

To import the ADA-KRLS, simply type the command:

    from handsonmachinelearn.krls import ADA_KRLS

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. 
    Must be an integer greater than 1.

    nu : int, default=0.01
    Accuracy parameter determining the level of sparsity. Must be a float between 0 and 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of ADA-KRLS:

    from handsonmachinelearn.krls import ADA_KRLS
    model = ADA_KRLS(N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### QALD-KRLS

To import the QALD-KRLS, simply type the command:

    from handsonmachinelearn.krls import QALD_KRLS

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. 
    Must be an integer greater than 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    nu : int, default=0.01
    Accuracy parameter determining the level of sparsity. 
    Must be a float between 0 and 1.

    epsilon1 : int, default=0.1
    Accuracy parameter determining the level of sparsity. 
    Must be a float between 0 and 1.

    epsilon2 : int, default=0.1
    Accuracy parameter determining the level of sparsity. 
    Must be a float between 0 and 1.

    kernel_type : str, default='Gaussian'
    The type of kernel function to use. Must be one of the 
    supported kernels in `base`.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of QALD-KRLS:

    from handsonmachinelearn.krls import QALD_KRLS
    model = QALD_KRLS(N=500, epsilon1 = 1e-4, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

### Light-KRLS

To import the Light-KRLS, simply type the command:

    from handsonmachinelearn.krls import Light_KRLS

Hyperparameters:

    N : int, default=100
    Accuracy parameter determining the level of sparsity. 
    Must be an integer greater than 1.

    c : float, default=1e-6
    Regularization parameter. Must be a very small float.

    kernel_type : str, default='Gaussian'
    The type of kernel function to use. Must be one of the 
    supported kernels in `base`.

    validate_array : bool
    If True, input arrays are validated before computation.

    kernel_type : str, default='Linear'
    The type of kernel function to use. Must be one of the supported kernels in `base`.

    **kwargs : dict
    Additional hyperparameters depending on the chosen kernel:
    - 'a', 'b', 'd' : Polynomial kernel parameters
    - 'gamma': RBF kernel parameter
    - 'sigma' : Gaussian, and Hybrid kernel parameter
    - 'r' : Sigmoid kernel parameter
    - 'beta' : Powered and Log kernel parameter
    - 'tau' : Hybrid kernel parameter
    - 'lr' : GeneralizedGaussian kernel parameters
    - 'epochs' : GeneralizedGaussian kernel parameters

Example of Light-KRLS:

    from handsonmachinelearn.krls import Light_KRLS
    model = Light_KRLS(N=500, kernel_type="Gaussian", sigma=0.5)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

## Extra details

Code of Conduct

handsonmachinelearn is a library developed by Kaike Alves. Please read the Code of Conduct for guidance.

Call for Contributions

The project welcomes your expertise and enthusiasm!

Small improvements or fixes are always appreciated. If you are considering larger contributions to the source code, please contact by email first.

If you think you can contribute to this project regarding the code, speed, etc., please, feel free to contact me and to do so.