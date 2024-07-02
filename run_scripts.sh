#! /bin/bash
# Switch to dokcer group to have permission to the docker
#newgrp docker
# Ensure base environment is not auto-activated
conda config --set auto_activate_base false
source ~/miniconda3/etc/profile.d/conda.sh  # Adjust the path if necessary
conda activate qgis_env

cd /home/emad47_n7/python_codes

python join_tables.py

python change_color.py


