======================================================================================
bisos.vagrantBaseBoxes: Facilities for Creating and Managing Vagrant Packer Base Boxes
======================================================================================

.. contents::
   :depth: 3
..

Overview
========

*bisos.dockerProc* provides various facilities for creation and
management of Vagrant Packer Base Boxes.

*bisos.dockerProc* is a python package that uses the
`PyCS-Framework <https://github.com/bisos-pip/pycs>`__ for its
implementation. It is a BISOS-Capability and a Standalone-BISOS-Package.

| *bisos.dockerProc* is data driven. By itself it is incomplete. It
  operates on well structured directories which contain packer base box
  specifications. Separating packer specifications from the
  bisos.dockerProc package allows for wide usage. BISOS-related packer
  specifications that can be processed with bisos.dockerProc are
  available at:
| https://github.com/bxObjects/bro_vagrantDebianBaseBoxes

Package Documentation At Github
===============================

The information below is a subset of the full of documentation for this
bisos-pip package. More complete documentation is available at:
https://github.com/bisos-pip/capability-cs

.. _table-of-contents:

Table of Contents TOC
=====================

-  `Overview <#overview>`__
-  `Package Documentation At
   Github <#package-documentation-at-github>`__
-  `A Standalone Piece of BISOS — ByStar Internet Services Operating
   System <#a-standalone-piece-of-bisos-----bystar-internet-services-operating-system>`__
-  `Installation of bisos.dockerProc
   Package <#installation-of-bisosdockerproc-package>`__

   -  `Installation With pip <#installation-with-pip>`__
   -  `Installation With pipx <#installation-with-pipx>`__

-  `Usage of bisos.dockerProc
   Package <#usage-of-bisosdockerproc-package>`__

   -  `First Install the packer box
      specifications. <#first-install-the-packer-box-specifications>`__
   -  `vagrantBoxProc.cs Menu <#vagrantboxproccs-menu>`__
   -  `Build, Add, Run and then Clean All Base Boxes with
      vagrantBoxProc.cs <#build-add-run-and-then-clean-all-base-boxes-with-vagrantboxproccs>`__
   -  `Build, Add, Run and then Clean a Specific Base Box with vagBox.cs
      (a planted vagrantBoxProc.cs
      seed) <#build-add-run-and-then-clean-a-specific-base-box-with-vagboxcs-a-planted-vagrantboxproccs-seed>`__

-  `BISOS Use of Built Vagrant
   Boxes <#bisos-use-of-built-vagrant-boxes>`__
-  `Support <#support>`__

A Standalone Piece of BISOS — ByStar Internet Services Operating System
=======================================================================

| Layered on top of Debian, **BISOS**: (By\* Internet Services Operating
  System) is a unified and universal framework for developing both
  internet services and software-service continuums that use internet
  services. See `Bootstrapping ByStar, BISOS and
  Blee <https://github.com/bxGenesis/start>`__ for information about
  getting started with BISOS.
| **BISOS** is a foundation for **The Libre-Halaal ByStar Digital
  Ecosystem** which is described as a cure for losses of autonomy and
  privacy in a book titled: `Nature of
  Polyexistentials <https://github.com/bxplpc/120033>`__

bisos.dockerProc is a standalone piece of BISOS. It can be used as a
self-contained Python package separate from BISOS. Follow the
installation and usage instructions below for your own use.

Installation of bisos.dockerProc Package
========================================

The sources for the bisos.dockerProc pip package are maintained at:
https://github.com/bisos-pip/dockerProc.

The bisos.dockerProc pip package is available at PYPI as
https://pypi.org/project/bisos.dockerProc

You can install bisos.dockerProc with pip or pipx.

Installation With pip
---------------------

If you need access to bisos.dockerProc as a python module, you can
install it with pip:

.. code:: bash

   pip install bisos.dockerProc

See below for this packages list of commands.

Installation With pipx
----------------------

If you only need access to bisos.dockerProc on command-line, you can
install it with pipx:

.. code:: bash

   pipx install bisos.dockerProc

The following commands are made available:

-  dockerProc-sbom.cs (Software Bill of Material for vagrant and packer)
-  vagrantBoxProc.cs (The primary command line for building, adding,
   running and cleaning base boxes.)\\ (Also a seed for vagBox.cs)
-  exmpl-vagBox.cs (Example for planting based on the vagrantBoxProc.cs
   as seed.)
-  vagrantCommonCmnds.cs (A cheat sheet for common vagrant commands.)

Usage of bisos.dockerProc Package
=================================

First Install the packer box specifications.
--------------------------------------------

Clone the packer box specifications somewhere. Perhaps in your home
directory.

.. code:: bash

   git clone https://github.com/bxObjects/bro_vagrantDebianBaseBoxes.git

For BISOS we use the /bisos/git/bxRepos/bxObjects canonical directory as
a base for cloning bro\ :sub:`vagrantDebianBaseBoxes`.

vagrantBoxProc.cs Menu
----------------------

Run:

.. code:: bash

   vagrantBoxProc.cs

Without any parameters and arguments, vagrantBoxProc.cs gives you a menu
of common invokations.

Build, Add, Run and then Clean All Base Boxes with vagrantBoxProc.cs
--------------------------------------------------------------------

Run:

.. code:: bash

   find  /bisos/git/bxRepos/bxObjects/bro_vagrantDebianBaseBoxes/qemu -print | grep pkr.hcl |  vagrantBoxProc.cs --force="t"  -i vagBoxPath_buildAddRun

That will build, then add the boxes and then do a vagrant up on each of
pkr.hcl files in the bro\ :sub:`vagrantDebianBaseBoxes`/qemu directory
hierarchy.

Next verify that all the boxes have been built properly by visiting them
as VMs.

To clean them all – get rid of the build artifacts and vagrant destroy
the machines – run:

.. code:: bash

   find  /bisos/git/bxRepos/bxObjects/bro_vagrantDebianBaseBoxes/qemu -print | grep pkr.hcl |  vagrantBoxProc.cs --force="t"  -i vagBoxPath_clean

Build, Add, Run and then Clean a Specific Base Box with vagBox.cs (a planted vagrantBoxProc.cs seed)
----------------------------------------------------------------------------------------------------

Go to:

.. code:: bash

   cd /bisos/git/bxRepos/bxObjects/bro_vagrantDebianBaseBoxes/qemu/debian/13/trixie/amd64/netinst

In there run:

.. code:: bash

   vagBox.cs

vagBox.cs gives you a menu of common invokations.

To Build, Add and Run just the us.pkr.hcl box, execute:

.. code:: bash

   vagBox.cs --force="t"  -i vagBoxPath_buildAddRun us.pkr.hcl

Next verify that your specific box has been built properly by visiting
it as a VM.

To clean it – git rid of the build artifacts and vagrant destroy the
machines – run:

.. code:: bash

   vagBox.cs --force="t"  -i vagBoxPath_clean us.pkr.hcl

BISOS Use of Built Vagrant Boxes
================================

In BISOS, we start from a Debian Vagrant Box which we consider as "fresh
Debian" and we augment it to to become "Raw-BISOS". This process is
described in: https://github.com/bxgenesis/start

Based on a platform BPO (ByStar Portable Object), Raw-BISOS can then be
further augmented to become a reproducible specific BISOS-Platform.

Support
=======

| For support, criticism, comments, and questions, please contact the
  author/maintainer
| `Mohsen Banan <http://mohsen.1.banan.byname.net>`__ at:
  http://mohsen.1.banan.byname.net/contact
