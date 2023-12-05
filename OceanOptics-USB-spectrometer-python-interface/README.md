# Usage

This is a custom open source python interface to run an OCEAN OPTICS USB4000 fibre USB spectrometer and it can also be made to work for similar spectrometers, such as the 2000 series models.

# Installation instructions for windows
  
* install seabreaze library for having python driver to use spectrometer
  
  `pip install seabreeze`
  
* install wx library for graphical interface

   `pip install wxpython`

* install python librearies used for the interface if not already running on your system: scipy matplotlib

# Installation instructions for MacOS (using mamba, micromamba or conda)

*  create and activate your dedicated python environment, e.g. spectrometer_env

  `mamba create -n spectrometer_env`
  
  `mamba activate spectrometer_env`

* Using mamba, install the packages listed under the windows installation in your environment
  
* Also install this wx version, using pip:

  `pip install -U wxPython`

* Connect your spectrometer by USB to your computer, navigate to your code containing folder (`cd <filepath>`) and call the interface (still from within your environment):

  `python ocean_optics.py`
  
