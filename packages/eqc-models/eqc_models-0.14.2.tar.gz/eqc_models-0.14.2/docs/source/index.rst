..  -*- coding: utf-8 -*-

.. _contents:


====================
Getting Started
====================

Introduction
====================

Entropy Quantum Computing (EQC) from Quantum Computing Inc. (QCi) can be used to solve combinatorial optimization problems as well as approximation of continuous solution spaces. The EQC device series developed by QCi utilizes nanophotonic measurement to implement an optimzation solver. 

The `eqc-models` package is provided to support the translation of well known optimization and machine learning models into formulations which run on EQC devices. There are two intended patterns of usage for the classes provided. The optimization models follow a pattern of

1. build the model
2. solve the concrete model
3. analyze the results.

While machine learning models follow the pattern

1. build the model
2. fit the model
3. predict with the fitted model.

Underneath, the same method of interaction is performed. All models have some formulation of an unconstrained (except in domain) polynomial. Sometimes the polynomial is a quadratic, sometimes it is higher order. There are some device specifics that require additional details to be considered.

Installation
===============

Python package is availble from PyPI repository and can be installed by:

.. code-block:: bash

  pip install eqc-models

Table of Contents
=================

.. toctree::
   :maxdepth: 3

   self
   usage
   modules
   dependencies
