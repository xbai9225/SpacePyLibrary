::*****************************************************************************
:: (C) 2018, Stefan Korner, Austria                                           *
::                                                                            *
:: The Space Python Library is free software; you can redistribute it and/or  *
:: modify it under under the terms of the MIT License as published by the     *
:: Massachusetts Institute of Technology.                                     *
::                                                                            *
:: The Space Python Library is distributed in the hope that it will be useful,*
:: but WITHOUT ANY WARRANTY; without even the implied warranty of             *
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the MIT License   *
:: for more details.                                                          *
::*****************************************************************************
:: Start scrip for the SCOE.                                                  *
::*****************************************************************************
set EGSE_PROTOCOL=EDEN
set HOST=127.0.0.1
set CCS_SERVER_PORT2=48570
set TC_ACK_ACCEPT_SUCC_MNEMO=ACK1
set TC_ACK_ACCEPT_FAIL_MNEMO=NAK1
set TC_ACK_EXESTA_SUCC_MNEMO=ACK2
set TC_ACK_EXESTA_FAIL_MNEMO=NAK2
set TC_ACK_EXEPRO_SUCC_MNEMO=ACK3
set TC_ACK_EXEPRO_FAIL_MNEMO=NAK3
set TC_ACK_EXECUT_SUCC_MNEMO=ACK4
set TC_ACK_EXECUT_FAIL_MNEMO=NAK4
set TC_ACK_APID_PARAM_BYTE_OFFSET=18
set TC_ACK_SSC_PARAM_BYTE_OFFSET=20
set TC_FKT_ID_BYTE_OFFSET=10
set TC_FKT_ID_BYTE_SIZE=4
set TM_TT_TIME_FORMAT=CUC4
set TM_TT_TIME_BYTE_OFFSET=10
set TM_CYCLIC_MNEMO=TM_PKT1
set TESTENV=C:\Programming\SpacePyLibrary\TESTENV
set PYTHONPATH=C:\Programming\SpacePyLibrary
python3 SCOE.py dummy
