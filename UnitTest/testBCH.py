#!/usr/bin/env python
#******************************************************************************
# (C) 2018, Stefan Korner, Austria                                            *
#                                                                             *
# The Space Python Library is free software; you can redistribute it and/or   *
# modify it under under the terms of the MIT License as published by the      *
# Massachusetts Institute of Technology.                                      *
#                                                                             *
# The Space Python Library is distributed in the hope that it will be useful, *
# but WITHOUT ANY WARRANTY; without even the implied warranty of              *
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT License    *
# for more details.                                                           *
#******************************************************************************
# Unit Tests                                                                  *
#******************************************************************************
from __future__ import print_function
import UTIL.BCH, testData

#############
# functions #
#############
def test_BCHoperations():
  """function to test the BCH encoding operations"""
  sreg = UTIL.BCH.encodeStart()
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[0])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[1])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[2])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[3])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[4])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[5])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_01[6])
  code = UTIL.BCH.encodeStop(sreg)
  if code != testData.BCH_BLOCK_01[7]:
    print("BCH code wrong:", ("%02X" % code), "- should be", ("%02X" % testData.BCH_BLOCK_01[7]))
    return False
  sreg = UTIL.BCH.encodeStart()
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[0])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[1])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[2])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[3])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[4])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[5])
  sreg = UTIL.BCH.encodeStep(sreg, testData.BCH_BLOCK_02[6])
  code = UTIL.BCH.encodeStop(sreg)
  if code != testData.BCH_BLOCK_02[7]:
    print("BCH code wrong:", ("%02X" % code), "- should be", ("%02X" % testData.BCH_BLOCK_02[7]))
    return False
  return True

########
# main #
########
if __name__ == "__main__":
  print("***** test_BCHoperations() start")
  retVal = test_BCHoperations()
  print("***** test_BCHoperations() done:", retVal)
