#!/bin/sh

##  The purpose of this script is to find the total number of chars in 
##  all the txt files in a directory.

##  You need this script to find out the size of a text dataset in terms
##  of the total number of characters in it for training babyGPT

##  NOTE NOTE:  The answer returned is in the format
##
##                 total_lines    total_words    total_chars

find -name '*.txt' | xargs cat | wc
