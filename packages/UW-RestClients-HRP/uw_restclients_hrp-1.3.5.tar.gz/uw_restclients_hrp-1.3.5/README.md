# REST client for the UW HRP Web Service
# UW-RestClients-HRP

[![Build Status](https://github.com/uw-it-aca/uw-restclients-hrp/workflows/tests/badge.svg)](https://github.com/uw-it-aca/uw-restclients-hrp/actions)
[![Coverage Status](https://coveralls.io/repos/uw-it-aca/uw-restclients-hrp/badge.svg?branch=main)](https://coveralls.io/r/uw-it-aca/uw-restclients-hrp?branch=main)
[![PyPi Version](https://img.shields.io/pypi/v/uw-restclients-hrp.svg)](https://pypi.python.org/pypi/uw-restclients-hrp)
![Python versions](https://img.shields.io/pypi/pyversions/uw-restclients-hrp.svg)

Installation:

    pip install UW-RestClients-HRP

To use this client, you'll need these settings in your application or script:

   RESTCLIENTS_HRPWS_HOST='https://...'

Optional settings:

    # Customizable parameters for urllib3
    RESTCLIENTS_HRPWS_TIMEOUT=60
    RESTCLIENTS_HRPWS_POOL_SIZE=10
