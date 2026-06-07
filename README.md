# Elliptic-Curves-wowza

This repository contains supporting files for my MATH3030 project on elliptic curves over finite fields and cryptography.

## Contents

- `ECCEncryptDecrypt.py`  
  Implements elliptic curve arithmetic for the simplified encryption example, including modular inverses, point addition, point doubling, scalar multiplication, shared-secret computation, XOR encryption, and decryption.

- `FindPointAndOrder.py`  
  Searches for points on elliptic curves over finite fields, checks non-singularity, counts curve points, computes point orders, and identifies suitable base points.

- `ECC over finite fields.tex`  
  LaTeX source for the final project report.

- `references.bib`  
  Bibliography file used for the report.

## Project curve

The main worked example uses the curve

E: y^2 = x^3 + x + 32 mod 101

with base point

G = (4, 10)

The code verifies that #E(F_101) = 101 and demonstrates that Alice and Bob obtain the same shared point using elliptic-curve Diffie--Hellman.

## Note 1 (the first note, the note that appears before the second note. may not be the last, but at least its the first... i think)

This is an educational toy example. The field size is far too small for real cryptographic security.

## Note 2
Math3030 project... didnt exactly use version control... oopsies. Also most likely hello to Mr Marker (the one i assume reading this), i finally figured out what i wanted to talk about :) 
