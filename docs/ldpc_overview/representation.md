---
title: Representation
position: 3
layout: default
parent: LDPC Overview
nav_order: 1
usemathjax: true
---

# {{ page.title }}

This page describes various representations of LDPC codes
{: .fs-6 .fw-300 }

---
## Matrix Representation
### Generator based representation
As with all linear codes, every codeword $c\in C$ of an $(n,k)$ code belongs to a $k$ dimensional linear subspace of 
$F^n$. As such, a base for the subspace may be found, and every codeword may be expressed using a generator matrix via: 
$c=uG$, where $u\in F^k$ is some vector holding information, and $G$ is a matrix whose rows are the base of the 
subspace. 

The $(n-k)$ dimensional null space of $G$, denoted as $C^\perp$ whose vectors adhere to $xG=0$, also has a base. The 
rows of the parity check matrix $H$, are made of these base vectors (the choice isn't unique). In turn, each row of the
$(n-k)$ rows of $H$ defines a specific parity check equation as for every legitimate codeword $c\in C$, we have 
$Hc^T=0$.

A low density parity check code is defined via a sparse matrix $H$. For a *regular* LDPC code the weight (number of bob 
zero values) of each column is the same and equal to some $w_c$, while the weight of each row is
$w_r= w_c\left(\frac{n}{m}\right)$. Typically, $H$ is of full rank which implies $n-k=m$, in which case the rate of the
code depends on the wights via $R=\frac{k}{n}=1-\frac{w_c}{w_r}$.