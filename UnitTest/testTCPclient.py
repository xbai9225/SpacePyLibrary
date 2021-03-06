#!/usr/bin/env python3
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
import os, sys
from UTIL.SYS import Error, LOG, LOG_INFO, LOG_WARNING, LOG_ERROR
import UTIL.SYS, UTIL.TASK, UTIL.TCP

#############
# functions #
#############
# -----------------------------------------------------------------------------
def initConfiguration():
  """initialise the system configuration"""
  UTIL.SYS.s_configuration.setDefaults([
    ["HOST", "127.0.0.1"],
    ["SERVER_PORT", "1234"]])
# -----------------------------------------------------------------------------
def createClient():
  """create the TCP client"""
  client = UTIL.TCP.Client(UTIL.TASK.s_processingTask)
  if not client.connectToServer(
    UTIL.SYS.s_configuration.HOST,
    int(UTIL.SYS.s_configuration.SERVER_PORT)):
    sys.exit(-1)
  return client

########
# main #
########
if __name__ == "__main__":
  # initialise the system configuration
  initConfiguration()
  # initialise the console handler
  consoleHandler = UTIL.TASK.ConsoleHandler()
  # initialise the model
  modelTask = UTIL.TASK.ProcessingTask(isParent=True)
  # register the console handler
  modelTask.registerConsoleHandler(consoleHandler)
  # create the TCP client
  LOG("Open the TCP client")
  client = createClient()
  # force termination of the server
  LOG("force server termination...")
  client.send("quit\n".encode())
