Requirements
------------
This guide requires installed ``git`` version to be at least ``2.13``.

Prepare env
-----------

.. code-block:: bash
   :name: install-paths

   mkdir -p install
   # Yosys, Yosys plugins and Surelog will be installed in the $PREFIX location
   export PREFIX=$(pwd)/install
   # This variable is required in Yosys build system to link against Surelog and UHDM
   export UHDM_INSTALL_DIR=$(pwd)/install

   export PATH=$PREFIX/bin:$PATH

The steps below are optional - they install and enable Python virtualenv

.. code-block:: bash
   :name: virtualenv

   pip3 install virtualenv
   virtualenv env
   source env/bin/activate

Clone, build and install Surelog
--------------------------------

.. code-block:: bash

   git clone https://github.com/chipsalliance/Surelog --recurse-submodules
   cd Surelog && git checkout bf19da37874169891b928419a721176219222f68 --recurse-submodules
   pip3 install orderedmultidict
   cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$PREFIX -DCMAKE_POSITION_INDEPENDENT_CODE=ON -S . -B build
   cmake --build build -j $(nproc)
   cmake --install build
   cd -

Clone, build and install Yosys
------------------------------

.. code-block:: bash

   git clone https://github.com/yosyshq/yosys
   cd yosys && git checkout 4da3f2878bb873726c6ac9233fe937d8c788993c
   make -j$(nproc) install
   cd -

Clone, build and install Yosys plugins
--------------------------------------

.. code-block:: bash

   git clone https://github.com/SymbiFlow/yosys-symbiflow-plugins
   cd yosys-symbiflow-plugins && git checkout 536c987f6b8e38f192e4c86f4468a4fd9280d7cc
   git submodule update --init --recursive
   make install -j$(nproc)
   cd -

Get LowRisc toolchain
---------------------

.. code-block:: bash
   :name: lowrisc-toolchain

   wget https://raw.githubusercontent.com/lowRISC/opentitan/master/util/get-toolchain.py -O get-toolchain.py
   python3 get-toolchain.py --update -i lowrisc-toolchain
   export PATH=$(realpath lowrisc-toolchain/bin):$PATH

Clone ibex
----------

.. code-block:: bash

   git clone https://github.com/lowrisc/ibex
   cd ibex && git checkout bbc48a0c34342935b5bd326bb8351168d6258ec7
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

Currently, Yosys doesn't support 2 port BRAM cells (current status can be tracked in the `issue <https://github.com/YosysHQ/yosys/issues/1959>`_)
The patches change the default Ibex configuration using dual port RAM (``ram_2p``) to use two single ports memories (``ram_1p``).
They also add Surelog/UHDM ``fusesoc`` targets.

Specify or replace ``$PATCH_DIR`` with the path to where this repository was checked out.

.. code-block:: bash

   cd ibex \
   && git am $PATCH_DIR/0001-add-synth-surelog-target.patch \
   && git am $PATCH_DIR/0002-ibex-change-ram_2p-to-ram_1p.patch
   cd -


Synthesize the design
---------------------

The command below will sythesize the design using Yosys/Surelog-UHDM flow.

.. code-block:: bash
   :name: ibex-build

   fusesoc --cores-root=$(realpath ibex) run --build --tool yosys \
   --target=synth lowrisc:ibex:top_artya7_surelog \
   --SRAMInitFile="$(realpath ibex/examples/sw/led/led.vmem)"

The resulting edif file will be located in the ``build/lowrisc_ibex_top_artya7_surelog_0.1/synth-yosys/lowrisc_ibex_top_artya7_surelog_0.1.edif`` file

Build the bitstream
-------------------

The command below will sythesize the design using Yosys/Surelog-UHDM, place & route and generate bistream using Vivado.
Before running the command bellow ensure Vivado accessible in your PATH.

.. code-block:: bash
   :name: vivado-ibex-build

   fusesoc --cores-root=$(realpath ibex) run --build --tool vivado \
   --target=synth lowrisc:ibex:top_artya7_surelog --part xc7a35ticsg324-1L \
   --SRAMInitFile="$(realpath ibex/examples/sw/led/led.vmem)"

The resulting bitstream file will be located in the ``build/lowrisc_ibex_top_artya7_surelog_0.1/synth-vivado/lowrisc_ibex_top_artya7_surelog_0.1.bit`` file
