Prepare env
-----------

.. code-block:: bash

   mkdir install
   # Yosys and Surelog will be installed in the $PREFIX location
   export PREFIX=$(pwd)/install
   # This variable is required in Yosys build system to link against Surelog and UHDM
   export UHDM_INSTALL_DIR=$(pwd)/install

   export PATH=$PREFIX/bin:$PATH

Bellow steps are optional - they install and enable Python virtualenv

.. code-block:: bash

   pip3 install virtualenv
   virtualenv env
   source env/bin/activate

Clone, build and install Surelog
--------------------------------

.. note::

   The steps bellow were tested with Surelog commit ca5cbc993d82e7ba1de1ea47f04684d1ef5b58d3

.. code-block:: bash

   git clone https://github.com/alainmarcel/Surelog --recurse-submodules
   cd Surelog && make release install
   cd -

Clone, build and install Yosys
------------------------------

.. note::

   The steps bellow were tested with Yosys commit 6ffa45e45c45f5fbc945463c8900bba0adbd04e0

.. code-block:: bash

   git clone https://github.com/antmicro/yosys -b uhdm-yosys
   cd yosys && make -j$(nproc) install
   cd -

Get LowRisc toolchain
---------------------

.. code-block:: bash

   wget https://raw.githubusercontent.com/lowRISC/opentitan/master/util/get-toolchain.py
   python3 get-toolchain.py -i lowrisc-toolchain
   export PATH=$(realpath lowrisc-toolchain/bin):$PATH

Clone ibex
----------

.. note::

   The flow was tested with Ibex commit 0199bbae665b9b142144e6688279e2ecef7d83a0

.. code-block:: bash

   git clone https://github.com/lowrisc/ibex

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
   pip3 install git+https://github.com/antmicro/edalize@surelog

Add Surelog/UHDM target to the core file
----------------------------------------

.. code-block:: bash

   cd ibex && git am /path/to/0001-add-synth-surelog-target.patch
   cd -


Build bitstream
---------------

The command bellow will sythesize the design using Yosys/Surelog-UHDM flow, and place and route it with Vivado

.. note::

   The flow was tested with Vivado 2020.1 (adjust the bellow path if using different version)

.. code-block:: bash

   source /opt/Xilinx/Vivado/2020.1/settings64.sh

   fusesoc --cores-root=$(realpath ibex) run --build --tool vivado \
   --target=synth_surelog lowrisc:ibex:top_artya7 \
   --library_files="${PREFIX}/share/yosys/xilinx/cells_xtra_surelog.v" \
   --SRAMInitFile="$(realpath ibex/examples/sw/led/led.vmem)" --part xc7a35ticsg324-1L 

Resulting bitstream will be in the ``build/lowrisc_ibex_top_artya7_0.1/synth_surelog-vivado/lowrisc_ibex_top_artya7_0.1.bit`` file
