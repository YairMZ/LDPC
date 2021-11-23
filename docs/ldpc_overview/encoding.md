---
title: Encoding
last_modified_date: 2021-11-23
last_edit_by: yairmazal
layout: default
parent: LDPC Overview
nav_order: 3
usemathjax: true
---
# {{ page.title }}

This page describes the encoding challenge of LDPC codes
{: .fs-6 .fw-300 }

---
Even though the parity check matrix of an LDPC code is sparse, the same does not generally hold for the generator matrix
$G$. Correspondingly, encoding via matrix multiplication, i.e., via $c=uG$, incurs a computational cost of 
$\mathcal{O}(n^2)$.

{% assign richardson = site.bib_sources | where:"id","richardson" %}
{% assign cai = site.bib_sources | where:"id","Cai" %}

Better solutions with faster encoding were found by encoding using the parity check matrix itself, using back 
substitution algorithms. A well cited work on this is the work by [{{richardson[0].author }}]({{richardson[0].url}}).
Alternatively, a more compact solution (around the same lines) which is limited to IEEE802.11 LDPC codes can be found 
[here]({{cai[0].url}}).
