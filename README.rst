Requirements
------------
This guide requires installed ``git`` version to be at least ``2.13``.

Prepare env
-----------

.. code-block:: bash

   mkdir install
   # Yosys, Yosys plugins and Surelog will be installed in the $PREFIX location
   export PREFIX=$(pwd)/install
   # This variable is required in Yosys build system to link against Surelog and UHDM
   export UHDM_INSTALL_DIR=$(pwd)/install

   export PATH=$PREFIX/bin:$PATH

The steps below are optional - they install and enable Python virtualenv

.. code-block:: bash

   pip3 install virtualenv
   virtualenv env
   source env/bin/activate

Clone, build and install Surelog
--------------------------------

.. code-block:: bash

   git clone https://github.com/alainmarcel/Surelog --recurse-submodules
   cd Surelog && git checkout b1d3c0efc11ed2f37091b7d10b06f5a36ba6d984 --recurse-submodules
   cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PREFIX -DCMAKE_POSITION_INDEPENDENT_CODE=ON -S . -B build
   cmake --build build -j $(nproc)
   cmake --install build
   cd -

Clone, build and install Yosys
------------------------------

.. code-block:: bash

   git clone https://github.com/yosyshq/yosys
   cd yosys && git checkout 1cac671c70bc3da9808ceb3add15686da4a5d82e
   patch -p1 < /path/to/uhdm.patch
   make -j$(nproc) install
   cd -

Clone, build and install Yosys plugins
--------------------------------------

.. code-block:: bash

   git clone https://github.com/antmicro/yosys-symbiflow-plugins
   cd yosys-symbiflow-plugins && git checkout 4cab7813de5b295f6caabc01795c8c53d3befd69
   git submodule update --init --recursive
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

Currently, Yosys doesn't support 2 port BRAM cells (current status can be tracked in the [issue](https://github.com/YosysHQ/yosys/issues/1959))
The patches change the default Ibex configuration usind dual port RAM (``ram_2p``) to use two single ports memories (``ram_1p``).
They also add Surelog/UHDM ``fusesoc`` targets.

.. code-block:: bash

   cd ibex && git am /path/to/0001-add-synth-surelog-target.patch && git am /path/to/0002-ibex-change-ram_2p-to-ram_1p.patch
   cd -


Synthesize the design
---------------------

The command below will sythesize the design using Yosys/Surelog-UHDM flow.

.. code-block:: bash

   fusesoc --cores-root=$(realpath ibex) run --build --tool yosys \
   --target=synth lowrisc:ibex:top_artya7_surelog \
   --SRAMInitFile="$(realpath ibex/examples/sw/led/led.vmem)"

The resulting edif file will be located in the ``build/lowrisc_ibex_top_artya7_surelog_0.1/synth-yosys/lowrisc_ibex_top_artya7_surelog_0.1.edif`` file

Build the bistream
------------------

The command below will sythesize the design using Yosys/Surelog-UHDM, place & route and generate bistream using Vivado.
Before running the command bellow ensure Vivado accessible in your PATH.

.. code-block:: bash

   fusesoc --cores-root=$(realpath ibex) run --build --tool vivado \
   --target=synth lowrisc:ibex:top_artya7_surelog \
   --SRAMInitFile="$(realpath ibex/examples/sw/led/led.vmem)"

The resulting bitstream file will be located in the ``build/lowrisc_ibex_top_artya7_surelog_0.1/synth-vivado/lowrisc_ibex_top_artya7_surelog_0.1.bit`` file

