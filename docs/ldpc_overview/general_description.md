---
title: General Description
last_modified_date: 2021-11-13
position: 1
layout: default
parent: LDPC Overview
nav_order: 1
usemathjax: true
---

# {{ page.title }}
Low Density Parity Check (LDPC) codes are a class of linear block ECC which provide near capacity performance. They 
utilize sparse encoding matrices, and relatively large block sizes (typically the number of $$1$$’s is linear in $$n$$).
They are widely used in standards, for instance:
 - IEEE802.3an-2006 (10GBASE-T Ethernet over copper wires)
 - DVB-S2 (video broadcasts)
 - IEEE.802.11n & IEEE.802.11ac (Wi-Fi standards 5&6). Here the use is optional in the HT (high throughput) 
 - specification, where they replace convolutional codes otherwise used.
 - The codes will also be used in the 5G cellular standard.

From a historic point of view, the codes were initially invented by Gallager in 1960 and were later forgotten as they 
weren't technologically viable at the time. Later, in 1981 Tanner found a generalized representation of the codes in 
the form of Tanner graphs. Further studies by Niel, Mackay and others, followed in the 1990's at which point the codes
were eventually used.