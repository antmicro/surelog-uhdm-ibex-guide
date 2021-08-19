Prepare env
-----------

.. code-block:: bash

   mkdir install
   # Yosys, Yosys plugins and Surelog will be installed in the $PREFIX location
   export PREFIX=$(pwd)/install
   # This variable is required in Yosys build system to link against Surelog and UHDM
   export UHDM_INSTALL_DIR=$PREFIX

   export PATH=$PREFIX/bin:$PATH

The steps below are optional - they install and enable Python virtualenv

.. code-block:: bash

   pip3 install virtualenv
   virtualenv env
   source env/bin/activate

Clone, build and install Surelog
--------------------------------

.. code-block:: bash

   git clone https://github.com/chipsalliance/Surelog --recurse-submodules
   cd Surelog && git checkout a0ada942dd92cab5ebd6c66761b0cee7925b0de3
   cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PREFIX -DCMAKE_POSITION_INDEPENDENT_CODE=ON -S . -B build
   cmake --build build -j $(nproc)
   cmake --install build
   cd -

Clone, build and install Yosys
------------------------------

.. code-block:: bash

   git clone https://github.com/yosyshq/yosys
   cd yosys && git checkout 3806b073031f1782f41762ebb6080a07e4182e95
   patch -p1 < /path/to/uhdm.patch
   make -j$(nproc) install
   cd -

Clone, build and install Yosys plugins
--------------------------------------

.. code-block:: bash

   git clone https://github.com/antmicro/yosys-symbiflow-plugins
   cd yosys-symbiflow-plugins && git checkout 40780913afdba950802a24f3724c13b46e69ccdc
   make install -j$(nproc)
   cd -

Get LowRisc toolchain
---------------------

.. code-block:: bash

   wget https://raw.githubusercontent.com/lowRISC/opentitan/master/util/get-toolchain.py
   python3 get-toolchain.py -i lowrisc-toolchain
   export PATH=$(realpath lowrisc-toolchain/bin):$PATH

Clone ibex
----------

.. code-block:: bash

   git clone https://github.com/lowrisc/ibex
   cd ibex && git checkout 3f9022a16d7b8e82deb1272d767d9e9e766d0e0f
   cd -

Build Ibex Firmware
-------------------

The following requires the srec_cat (typically from srecord package) binary:

.. code-block:: bash

   cd ibex/examples/sw/led/
   make
   cd -

Install Ibex deps
-----------------

.. code-block:: bash

   pip3 install -r ibex/python-requirements.txt
   pip3 install git+https://github.com/antmicro/edalize@uhdm_support

Add Surelog/UHDM target to the core file
----------------------------------------

.. code-block:: bash

   cd ibex && git am /path/to/0001-add-synth-surelog-target.patch
   cd -


Synthesize the design
---------------------

The command below will sythesize the design using Yosys/Surelog-UHDM flow.

.. code-block:: bash

   source /opt/Xilinx/Vivado/2020.1/settings64.sh

   fusesoc --cores-root=$(realpath ibex) run --build --tool yosys \
   --target=synth lowrisc:ibex:top_artya7_surelog \
   --SRAMInitFile="$(realpath ibex/examples/sw/led/led.vmem)"

The resulting edif file will be located in the ``build/lowrisc_ibex_top_artya7_surelog_0.1/synth-yosys/lowrisc_ibex_top_artya7_surelog_0.1.edif`` file
