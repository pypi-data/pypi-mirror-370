# GAICo Intermediate Examples

The Python notebooks in this directory serve as basic examples of using the GAICo library for various domains, such as time series, planning, election, etc.

### 1. [`example-timeseries.ipynb`](example-timeseries.ipynb): Time Series Analysis

- Evaluation and perturbation of time series using GAICo's time series specific metrics.

### 2. [`example-planning.ipynb`](example-planning.ipynb): Automated Planning Analysis

- Evaluation of various travel plans using GAICo's planning specific metrics.

### 3. [`example-finance.ipynb`](example-finance.ipynb): Finance Dataset Analysis

- Evaluating models on various questions from the finance domain by iterating on the dataset with the `Experiment` class.

### 4. [`example-recipes.ipynb`](example-recipes.ipynb): Recipe Dataset Analysis

- Evaluating models on various questions from the recipe domain by iterating on the dataset with the `Experiment` class. Further uses parallelization of the comparisons using `joblib`.

### 5. [`example-election.ipynb`](example-election.ipynb): Election Dataset Analysis

- Evaluating models on various questions from the election domain by using the `calculate()` metric method.

### 6. [`DeepSeek-example.ipynb`](example-DeepSeek.ipynb): Testing _DeepSeek R1_

- The aim for this notebook was to aid with evaluating DeepSeek R1 for [AI4Society's Point of View (POV)](https://drive.google.com/file/d/1ErR1xT7ftvmHiUyYrdUbjyd4qCK_FxKX/view?usp=sharing).
- **Note**: All results remove the `<think>` tags for the DeepSeek models.

### 7. [`example-audio_data.ipynb`](example-audio_data.ipynb): Advanced Audio Analysis & Multi-format Processing

- Demonstrates audio evaluation across different formats (MP3/WAV) and format-independent processing capabilities.
- Provides interpretation frameworks for both fidelity tasks (TTS) and creative generation (music), with detailed quality analysis.
