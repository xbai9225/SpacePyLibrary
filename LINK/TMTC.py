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
# Link Simulation - Telemetry and Telecommand Channels                        *
#******************************************************************************
import array
from UTIL.SYS import Error, LOG, LOG_INFO, LOG_WARNING, LOG_ERROR
import CCSDS.ASSEMBLER, CCSDS.CLTU, CCSDS.FRAME, CCSDS.PACKET, CCSDS.SEGMENT, CCSDS.SEGMENThelpers
import GRND.IF
import LINK.IF
import SPACE.IF
import UTIL.SYS, UTIL.TASK, UTIL.TIME

#############
# constants #
#############
CHECK_CYCLIC_PERIOD_MS = 100
UPLINK_DELAY_SEC = 2
DOWNLINK_DELAY_SEC = 2

###########
# classes #
###########
# =============================================================================
class CCSDSgroundSpace(CCSDS.ASSEMBLER.Assembler, LINK.IF.SpaceLink, LINK.IF.GroundLink):
  """
  Implementation of the space and packet link,
  connects the ground segment with the space segment
  """
  # ---------------------------------------------------------------------------
  def __init__(self):
    """Initialise parent class and attributes"""
    CCSDS.ASSEMBLER.Assembler.__init__(self)
    self.segmentDus = []
    self.uplinkQueue = {}
    self.downlinkQueue = {}
    self.ertUTC = None
    self.tmFrameFlowMs = int(UTIL.SYS.s_configuration.TM_FRAME_FLOW_MS)
    self.checkTMflowCallback()
    self.checkCyclicCallback()
  # ---------------------------------------------------------------------------
  def getUplinkQueue(self):
    """
    returns the uplink queue:
    implementation of LINK.IF.SpaceLink.getUplinkQueue
    """
    return self.uplinkQueue
  # ---------------------------------------------------------------------------
  def getDownlinkQueue(self):
    """
    returns the downlink queue:
    implementation of LINK.IF.SpaceLink.getDownlinkQueue
    """
    return self.downlinkQueue
  # ---------------------------------------------------------------------------
  def pushTCcltu(self, cltu):
    """
    consumes a command link transfer unit:
    implementation of LINK.IF.SpaceLink.pushTCcltu
    """
    # extract the frame from the CLTU
    frame = CCSDS.CLTU.decodeCltu(cltu)
    if frame == None:
      LOG_ERROR("CLTU decoding failed", "LINK")
      return
    tcFrameDu = CCSDS.FRAME.TCframe(frame)
    # remove the fill bytes from the end of the frame
    frameLength = tcFrameDu.frameLength + 1
    if frameLength > len(tcFrameDu):
      LOG_ERROR("invalid TC frame length", "LINK")
      return
    tcFrameDu.setLen(frameLength)
    # check the frame
    if CCSDS.FRAME.CRC_CHECK:
      if not tcFrameDu.checkChecksum():
        LOG_ERROR("invalid TC frame CRC", "LINK")
        return
    # put the TC frame into the uplink queue to simulate the uplink delay
    receptionTime = UTIL.TIME.getActualTime() + UPLINK_DELAY_SEC
    self.uplinkQueue[receptionTime] = tcFrameDu
    UTIL.TASK.s_processingTask.notifyGUItask("TC_FRAME")
  # ---------------------------------------------------------------------------
  def pushTMpacketAndERT(self, tmPacketDu, ertUTC):
    """
    consumes a telemetry packet with ERT
    implementation of LINK.IF.GroundLink.pushTMpacketAndERT
    """
    self.ertUTC = ertUTC
    CCSDS.ASSEMBLER.Assembler.pushTMpacket(self, tmPacketDu.getBuffer())
  # ---------------------------------------------------------------------------
  def notifyTMframeCallback(self, tmFrameDu):
    """
    notifies when the next TM frame is assembled:
    implementation of CCSDS.ASSEMBLER.Assembler.notifyTMframeCallback
    """
    # put the TM frame into the downlink queue to simulate the downlink delay
    receptionTime = UTIL.TIME.getActualTime() + DOWNLINK_DELAY_SEC
    self.downlinkQueue[receptionTime] = (tmFrameDu, self.ertUTC)
    UTIL.TASK.s_processingTask.notifyGUItask("TM_FRAME")
  # ---------------------------------------------------------------------------
  def checkTMflowCallback(self):
    """
    timer triggered: check cyclic TM flow shall be performed
    """
    UTIL.TASK.s_processingTask.createTimeHandler(self.tmFrameFlowMs,
                                                 self.checkTMflowCallback)
    if LINK.IF.s_configuration.enableTMflow:
      self.flushTMframeOrIdleFrame()
  # ---------------------------------------------------------------------------
  def checkCyclicCallback(self):
    """
    timer triggered: check if the uplink and downlink simulation indicates that
    the uplink / downlink of frames is completed
    """
    actualTime = UTIL.TIME.getActualTime()
    UTIL.TASK.s_processingTask.createTimeHandler(CHECK_CYCLIC_PERIOD_MS,
                                                 self.checkCyclicCallback)
    # check if uplink times in the uplink queue are expired
    receptionTimes = self.uplinkQueue.keys()
    receptionTimes = sorted(receptionTimes)
    tcFramesDeleted = False
    for receptionTime in receptionTimes:
      if receptionTime <= actualTime:
        # reception time has expired ---> process TC frame
        tcFrameDu = self.uplinkQueue[receptionTime]
        self.receiveTCframe(tcFrameDu)
        # remove TC frame
        del self.uplinkQueue[receptionTime]
        tcFramesDeleted = True
      else:
        break
    if tcFramesDeleted:
      UTIL.TASK.s_processingTask.notifyGUItask("TC_FRAME")
    # check if downlink times in the downlink queue are expired
    receptionTimes = self.downlinkQueue.keys()
    receptionTimes = sorted(receptionTimes)
    tmFramesDeleted = False
    for receptionTime in receptionTimes:
      if receptionTime <= actualTime:
        # reception time has expired ---> process TM frame
        tmFrameDu, ertUTC = self.downlinkQueue[receptionTime]
        self.receiveTMframe(tmFrameDu, ertUTC)
        # remove TM frame
        del self.downlinkQueue[receptionTime]
        tmFramesDeleted = True
      else:
        break
    if tmFramesDeleted:
      UTIL.TASK.s_processingTask.notifyGUItask("TM_FRAME")
  # ---------------------------------------------------------------------------
  def receiveTCframe(self, tcFrameDu):
    """TC frame received"""
    sequenceNumber = tcFrameDu.sequenceNumber
    if LINK.IF.s_configuration.enableCLCW:
      # set the sequenceNumber for the next CLCWs that are sent to ground
      # (e.g. with TC acknowledgements)
      sequenceNumber = (sequenceNumber + 1) % 256
      self.setCLCWcount(sequenceNumber)
    # used to update the GUI
    UTIL.TASK.s_processingTask.notifyGUItask("TC_FRAME")
    # extract the segment from the frame
    try:
      segment = tcFrameDu.getSegment()
    except Exception as ex:
      LOG_ERROR("segment extraction failed: " + str(ex), "LINK")
      return
    self.receiveTCsegment(segment)
  # ---------------------------------------------------------------------------
  def receiveTCsegment(self, tcSegment):
    """TC segment received"""
    tcSegmentDu = CCSDS.SEGMENT.TCsegment(tcSegment)
    # collect the segmentDus
    mergeSegments = False
    if tcSegmentDu.sequenceFlags == CCSDS.SEGMENT.FIRST_PORTION:
      if len(self.segmentDus) != 0:
        LOG_ERROR("invalid order of segmentDus, 1st portion received", "LINK")
        self.segmentDus = []
        return
      # collect the segment
      self.segmentDus.append(tcSegmentDu)
    elif tcSegmentDu.sequenceFlags == CCSDS.SEGMENT.MIDDLE_PORTION:
      if len(self.segmentDus) == 0:
        LOG_ERROR("invalid order of segmentDus, middle portion received", "LINK")
        self.segmentDus = []
        return
      # collect the segment
      self.segmentDus.append(tcSegmentDu)
    elif tcSegmentDu.sequenceFlags == CCSDS.SEGMENT.LAST_PORTION:
      if len(self.segmentDus) == 0:
        LOG_ERROR("invalid order of segmentDus, last portion received", "LINK")
        self.segmentDus = []
        return
      # collect the segment
      self.segmentDus.append(tcSegmentDu)
      mergeSegments = True
    else:
      # UNSEGMENTED
      if len(self.segmentDus) != 0:
        LOG_ERROR("invalid order of segmentDus, unsegmented received", "LINK")
        self.segmentDus = []
        return
      # collect the segment
      self.segmentDus.append(tcSegmentDu)
      mergeSegments = True
    # extract the packet data only if correct amount of segments are available
    if not mergeSegments:
      # wait for further segments
      return
    # all segments are available ---> merge
    packetData = array.array("B")
    for segmentDu in self.segmentDus:
      # extract the packet data from the segment
      try:
        packetData += segmentDu.getTCpacketData()
      except Exception as ex:
        LOG_ERROR("TC packet data extraction failed: " + str(ex), "LINK")
        self.segmentDus = []
        return
    # packet data are merged
    self.segmentDus = []
    tcPacketDu = CCSDS.PACKET.TCpacket(packetData)
    SPACE.IF.s_onboardComputer.pushTCpacket(tcPacketDu)
  # ---------------------------------------------------------------------------
  def receiveTMframe(self, tmFrameDu, ertUTC):
    """TM frame received"""
    GRND.IF.s_tmMcsLink.pushTMframe(tmFrameDu, ertUTC)

#############
# functions #
#############
def init():
  """initialise singleton(s)"""
  LINK.IF.s_groundLink = CCSDSgroundSpace()
  LINK.IF.s_spaceLink = LINK.IF.s_groundLink
