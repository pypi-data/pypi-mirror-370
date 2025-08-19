# Frequenz Electricity Trading API

[![Build Status](https://github.com/frequenz-floss/frequenz-api-electricity-trading/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-api-electricity-trading/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-api-electricity-trading)](https://pypi.org/project/frequenz-api-electricity-trading/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-api-electricity-trading/)

## Introduction

Specification for Electricity Trading API.

## Overview

The Frequenz API offers a robust set of operations for managing electricity trading orders within Gridpools.
A Gridpool is an aggregation of multiple microgrids into a virtual power pool, designed to ensure the balancing
of electricity supply and demand in real time.

## Objective

The primary aim of this API is to streamline the process of electricity trading within balancing groups.
A balancing group is a network configuration that includes multiple electricity producers and consumers.
Grid stability relies on maintaining a balance between supply and demand within these groups. Participants
causing imbalances can face financial penalties. Using this API, individual participants can trade electricity
efficiently, ensuring they meet both their operational needs and financial objectives, while also contributing to
the overall grid stability.

## Key Features

- Order Placement: Facilitates the creation, modification, and deletion of trading orders.
- Real-Time Matching: Enables real-time order matching within the Gridpool.
- Order Tracking: Allows users to track the status of their orders, providing transparency and control.
- Public Order Book: Provides access to a list of public orders for market visibility and analysis.

## Target Audience

This API is primarily designed for application developers in the energy sector who focus on electricity
trading, grid management, and related services. While the API covers complex energy market operations,
its design aims to be as developer-friendly as possible, requiring no specialized knowledge in energy systems.

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
