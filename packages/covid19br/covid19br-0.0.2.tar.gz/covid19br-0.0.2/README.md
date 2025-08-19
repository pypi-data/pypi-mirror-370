# covid19br

<!-- badges: start -->


<!-- badges: end -->

Set of functions to import COVID-19 pandemic data into python. 
The Brazilian COVID-19 data, obtained from the official Brazilian 
repository at <https://covid.saude.gov.br/>, is available at the 
country, region, state, and city levels. The package also 
downloads world-level COVID-19 data from Johns Hopkins University's 
repository. COVID-19 data is available from the start of follow-up 
until to May 5, 2023, when the World Health Organization (WHO) 
declared an end to the Public Health Emergency of International 
Concern (PHEIC) for COVID-19.

## Installation

You can install the development version of covid19br like so:

``` python
pip install covid19br
```

## Example

Downloading Lotofacil winners data:

``` python
from covid19br import download_covid19
br = download_covid19("brazil")
```