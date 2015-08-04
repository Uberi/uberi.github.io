---
title: Telemetry Demystified
date: 2015-08-04
layout: post
---

[Mozilla Telemetry](http://telemetry.mozilla.org/) is a measurement and analytics platform used at Mozilla, for products such as [Firefox](https://www.mozilla.org/en-US/firefox/desktop/) and [Fennec](https://wiki.mozilla.org/Mobile/Fennec).

This post is intended to be a high level overview of the systems we have in place. It is targeted toward people who haven't worked with Telemetry systems much before, but want to use it to answer questions.

Glossary
--------

### Telemetry v2, Pipeline v2, Old pipeline

At the time of this writing, v2 Telemetry is the primary backend for data collection and processing. This covers everything from the servers that collect data submitted by Mozilla products, to the Javascript libraries that expose a high level API to manipulate the aggregated data.

A more detailed description of this pipeline can be found [here](http://jonasfj.dk/2013/11/telemetry-rebooted-analysis-future/).

See also:

* [Telemetry-server](https://github.com/mozilla/telemetry-server) - the server that actually receives Telemetry pings from products, compresses them, and stores them.
* [Telemetry-aggregator](https://github.com/mozilla/telemetry-aggregator) - the module that, when driven by Telemetry-server, aggregates data and publishes it.
* Telemetry.js (v1) - Javascript library for accessing data from the v2 pipeline.

### Unified Telemetry/FHR, Pipeline v4, New pipeline

A rewrite of the v2 Telemetry pipeline to support changing requirements and additional functionality/flexibility. This project covers the same requirements as the v2 pipeline, but in a more clean, elegant, and flexible way.

Unified telemetry also includes [Firefox Health Report (FHR)](https://support.mozilla.org/en-US/kb/firefox-health-report-understand-your-browser-perf) pings, so it's really a one-stop shop for all your data collection needs. A detailed description of this pipeline can be found [here](http://robertovitillo.com/2015/07/02/telemetry-metrics-roll-ups/).

See also:

* [Project wiki page](https://wiki.mozilla.org/Unified_Telemetry) - high level project information, like deliverables, timelines, and so on.
* [v4 pipeline aggregator](https://github.com/vitillo/python_mozaggregator) - aggregator, database, and API server for unified Telemetry/FHR.
* Telemetry.js (v2) - Javascript library for accessing data from the v4 pipeline.

### Telemetry.js (v1)

[Telemetry.js](http://telemetry.mozilla.org/docs.html) is a Javascript library for accessing data from the v2 pipeline. As of this writing, when people say "Telemetry.js", they usually mean v1. This library powers the v2 pipeline dashboards on [Mozilla Telemetry](http://telemetry.mozilla.org/) (at the moment, v2 pipeline dashboards are the default, while v4 pipeline dashboards are explicitly marked as such).

This library is the **only officially supported way of accessing v2 pipeline data** - the storage format on the backend is subject to change without warning. This can be used with Node.js with [telemetry-js-node](https://www.npmjs.com/package/telemetry-js-node), which takes care of downloading the latest version of the library and making sure things work properly outside the browser.

See also:

* [Source code](https://github.com/mozilla/telemetry-dashboard/tree/master/v1)
* Telemetry.js (v2) - Javascript library for accessing data from the v4 pipeline.

### Telemetry.js (v2)

Telemetry.js v2 is a Javascript library for accessing data from the v4 pipeline. As of this writing, this is still under active development, but is quite stable already. This library powers the v4 pipeline dashboards on [Mozilla Telemetry](http://telemetry.mozilla.org/).

This library is the easiest way of accessing v4 pipeline data from Javascript, but the v4 pipeline also provides a more general [HTTP API](https://github.com/vitillo/python_mozaggregator#api). The library is intended for use in the browser, but can also work with Node.js using [telemetry-next-node](https://www.npmjs.com/package/telemetry-next-node), which takes care of downloading the latest version of the library and making sure things work properly in the Node.js environment.

This library is **recommended over Telemetry.js v1 for new projects**.

Telemetry.js v2 is **not backwards compatible with Telemetry.js v1**, since the v4 pipeline differs significantly in structure from the v2 pipeline. However, if you have a Telemetry.js v1 application and really don't want to convert the code over, there is now a [v1 shim available](https://github.com/Uberi/telemetry-dashboard/blob/v1-shim/v2/v1-shim.js) that allows you to use Telemetry.js v2 with the v1 API (with certain limitations).

See also:

* [Source code](https://github.com/mozilla/telemetry-dashboard/tree/master/v2)
* Telemetry.js (v1) - Javascript library for accessing data from the v2 pipeline.

How to answer questions with Telemetry
--------------------------------------

### Dashboards

[Mozilla Telemetry](http://telemetry.mozilla.org/) has a whole bunch of dashboards available for answering questions.

On that page, the left column has the **Histogram and Evolution dashboards**, which are used for everything from finding the median startup time to comparing error rates across OSs. There are also v4 versions of these dashboards, which are the same thing, but use the v4 pipeline instead of the v2 pipeline under the hood. The v4 dashboards also have more features since they can take advantage of the additional capabilities in the v4 pipeline.

Using the Histogram and Evolution dashboards are hopefully pretty self-explanatory, but there is also a [detailed tutorial](http://telemetry.mozilla.org/tutorial.html) for using these dashboards to answer questions. For example, to find the average startup time on the latest nightly, one would go to the histogram dashboard, select "SIMPLE_MEASURES_FIRSTPAINT distribution for nightly 42, on any OS for any architecture", and read the result off either the histogram, or the summary statistics on the right.

There are also various other dashboards for more specialized purposes, listed on the right pane of the main landing page. For example, the [Background Hang Reporting](http://telemetry.mozilla.org/hang/bhr) dashboard shows common sources of hangs, and [Graphics Telemetry](http://people.mozilla.org/~danderson/moz-gfx-telemetry/www/) breaks down submissions by OS, product version, and more.

Not all of these dashboards are documented, but you can probably find a few tips and tricks from the `#perf` and `#telemetry` channels on the [Mozilla IRC](https://wiki.mozilla.org/IRC).

### Custom Dashboards

If none of the existing dashboards can answer your questions, a custom dashboard might. Dashboards using Telemetry.js actually do significant amount of processing on the data before it's shown to the user, and along the way some of the information gets filtered out.

For Telemetry.js v1, there's a nice tutorial for writing custom dashboards [here](http://jonasfj.dk/2014/01/custom-telemetry-dashboards/). This information is also applicable to Telemetry.js v2, but with the new API instead.

For help with creating custom dashboards, make sure to check out the `#perf` and `#telemetry` channels on the [Mozilla IRC](https://wiki.mozilla.org/IRC).

### Custom Analyses

To do custom analyses, you **must have an @mozilla.com email address**. Custom analyses are the most flexible option, but also require more familiarity with the underlying systems.

For each custom analysis, a new AWS instance is provisioned specifically for it containing our analysis environment, accessible via SSH. Custom analyses have access to individual pings, as well as the full power of Apache Spark and IPython. They also require the most resources to run.

A step-by-step guide to running custom analyses can be found [here](http://robertovitillo.com/2015/01/16/next-gen-data-analysis-framework-for-telemetry/). More information about what's going on under the hood can be found [here](http://robertovitillo.com/2015/06/27/a-glance-at-unified-fhrtelemetry/).

Again, for help with performing custom analyses, the `#perf` and `#telemetry` channels on the [Mozilla IRC](https://wiki.mozilla.org/IRC) are quite helpful.
