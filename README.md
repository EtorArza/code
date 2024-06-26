## Setup

Tested working on Pop!_OS 22.04 LTS with python 3.8, should also work on Ubuntu 22.04. 


### Step 1: Create python virtual environment

The first step is to create a python environment. There are two options: 

#### option A: using `airframes` environment with NVIDIA GPU
If using environment `airframes` with a NVIDIA GPU, just follow the instructions there and that will create a conda environment (rlgpu).

First, follow the installation instructions in
https://github.com/ntnu-arl/aerial_gym_simulator and https://github.com/ntnu-arl/aerial_gym_dev. Requires a NVIDIA gpu and installing drivers, `CUDA`, `isaacgym` and all of that fun stuff.

Finally, change the first line in `src/problem_airframes.py` with the path of `aerial_gym_dev` source. Without this change it will not work.

Remember to activate conda environment before executing the experiments:
```
conda activate rlgpu
```

Install python dependencies:
```
pip install -U "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
pip install cvxopt
pip install gym
pip install qpth
```


#### option B: wihtout `airframes` and CPU only

In this case, you need to create a python virtual environment.
```
sudo apt install venv
python3 -m venv venv
source venv/bin/activate
pip3 install -U pip
```


Remember to activate conda environment before executing the experiments:
```
source venv/bin/activate
```


--------------------------------------------------------------------------------------

### Step 2: Install python packages


```
# These are customized forks of the original, and are a requirement.
pip install git+https://github.com/EtorArza/supervenn.git#egg=supervenn
pip install git+https://github.com/EtorArza/scikit-quant.git#egg=scikit-quant
```

```
# Also required.
pip install cobyqa #requires python>=3.8
pip install tqdm
pip install matplotlib
```

--------------------------------------------------------------------------------------

### Step 3: Other specific requirements


#### airframes
Already done if you chose option A in step 1 above.

#### windflo
Already provided in this repo. Just need to build the binary:
```
sudo apt install gfortran
sudo apt install gfortran-10
sudo apt install g++
sudo apt install g++-10

cd other_src/WindFLO/release/
make OS=LINUX MAIN=main
cd ../../../
```

#### pyOpt
```
pip install swig
cd other_src/pyOpt
python setup.py install
../../
```


