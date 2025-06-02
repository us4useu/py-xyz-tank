import ctypes
import numpy as np
from picosdk.ps5000a import ps5000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
import picosdk.constants as psconst

class ScopePS5000a :

    def __init__(self) :
        #Initialize variables
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.preTriggerSamples = 0
        self.postTriggerSamples = 0
        self.maxSamples = 0
        self.bufferAMax = (ctypes.c_int16 * self.maxSamples)()
        self.bufferAMin = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example
        self.bufferBMax = (ctypes.c_int16 * self.maxSamples)()
        self.bufferBMin = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example
        self.overflow = 0
        self.cmaxSamples = 0
        self.maxADC = 0
        self.chARange = 0
        self.chBRange = 0
        self.timebase = 0

        # Open 5000 series PicoScope
        # Resolution set to 12 Bit
        resolution =ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]
        # Returns handle to chandle for use in future API functions
        self.status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, resolution)

        try:
            assert_pico_ok(self.status["openunit"])
        except: # PicoNotOkError:

            powerStatus = self.status["openunit"]

            if powerStatus == psconst.pico_num("PICO_POWER_SUPPLY_CONNECTED"): # powered from 5V DC supply
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerStatus)
            elif powerStatus == psconst.pico_num("PICO_POWER_SUPPLY_NOT_CONNECTED"): # powered from USB
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, powerStatus)
            else:
                raise

            assert_pico_ok(self.status["changePowerSource"])

    def configChannelA(self, enabled = 1) :
        # Set up channel A
        # handle = chandle
        channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
        # enabled = 1
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        self.chARange = ps.PS5000A_RANGE["PS5000A_500mV"]
        # analogue offset = 0 V
        self.status["setChA"] = ps.ps5000aSetChannel(self.chandle, channel, enabled, coupling_type, self.chARange, 0)
        assert_pico_ok(self.status["setChA"])

        self.status["setBWChA"] = ps.ps5000aSetBandwidthFilter(self.chandle, channel, 1)
    
    def configChannelB(self, enabled = 1) :
        # Set up channel B
        # handle = chandle
        channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
        # enabled = 1
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        self.chBRange = ps.PS5000A_RANGE["PS5000A_20V"]
        # analogue offset = 0 V
        self.status["setChB"] = ps.ps5000aSetChannel(self.chandle, channel, enabled, coupling_type, self.chBRange, 0)
        assert_pico_ok(self.status["setChB"])

    def configChannelC(self, enabled = 1) :
        # Set up channel B
        # handle = chandle
        channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_C"]
        # enabled = 1
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        self.chCRange = ps.PS5000A_RANGE["PS5000A_5V"]
        # analogue offset = 0 V
        self.status["setChC"] = ps.ps5000aSetChannel(self.chandle, channel, enabled, coupling_type, self.chCRange, 0)
        assert_pico_ok(self.status["setChC"])

    def configChannelD(self, enabled = 1) :
        # Set up channel B
        # handle = chandle
        channel = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_D"]
        # enabled = 1
        coupling_type = ps.PS5000A_COUPLING["PS5000A_DC"]
        self.chDRange = ps.PS5000A_RANGE["PS5000A_5V"]
        # analogue offset = 0 V
        self.status["setChD"] = ps.ps5000aSetChannel(self.chandle, channel, enabled, coupling_type, self.chDRange, 0)
        assert_pico_ok(self.status["setChD"])
    
    def configTrigger(self) :
        # find maximum ADC count value
        # handle = chandle
        # pointer to value = ctypes.byref(maxADC)
        self.maxADC = ctypes.c_int16()
        self.status["maximumValue"] = ps.ps5000aMaximumValue(self.chandle, ctypes.byref(self.maxADC))
        assert_pico_ok(self.status["maximumValue"])

        # Set up single trigger
        # handle = chandle
        # enabled = 1
        source = ps.PS5000A_CHANNEL["PS5000A_EXTERNAL"]
        threshold = int(mV2adc(500, self.chARange, self.maxADC))
        # direction = PS5000A_RISING = 2
        # delay = 0 s
        # auto Trigger = 1 ms
        self.status["trigger"] = ps.ps5000aSetSimpleTrigger(self.chandle, 1, source, threshold, 2, 0, 0)
        assert_pico_ok(self.status["trigger"])

    def setAcquisition(self, samples, offset, timebase) :
        # Set number of pre and post trigger samples to be collected
        self.preTriggerSamples = offset 
        self.postTriggerSamples = samples - self.preTriggerSamples
        self.maxSamples = self.preTriggerSamples + self.postTriggerSamples

        # Get timebase information
        # Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.  
        # To access these Timebases, set any unused analogue channels to off.
        # handle = chandle
        self.timebase = timebase # 1 = 2ns, 2 = 4ns, 3 = 8ns, 4 = 16ns, 5 = 32ns, 6 = 48ns, 7 = 64ns, 8 = 80ns
        # noSampzzzzzzzzzzzzzzzzzzzzzzzzzzles = maxSamples
        # pointer to timeIntervalNanoseconds = ctypes.byref(timeIntervalns)
        # pointer to maxSamples = ctypes.byref(returnedMaxSamples)
        # segment index = 0
        timeIntervalns = ctypes.c_float()
        returnedMaxSamples = ctypes.c_int32()
        self.status["getTimebase2"] = ps.ps5000aGetTimebase2(self.chandle, self.timebase, self.maxSamples, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
        assert_pico_ok(self.status["getTimebase2"])

        self.cmaxSamples = ctypes.c_int32(self.maxSamples)

        return self.cmaxSamples.value, timeIntervalns.value

    def runBlockAcquisition(self, segments = 1) :
        # if segments > 1
        if segments > 1:
            # Handle = Chandle
            # nSegments = 10
            # nMaxSamples = ctypes.byref(cmaxSamples)
            self.status["MemorySegments"] = ps.ps5000aMemorySegments(self.chandle, segments, ctypes.byref(self.cmaxSamples))
            assert_pico_ok(self.status["MemorySegments"])

            # sets number of captures
            self.status["SetNoOfCaptures"] = ps.ps5000aSetNoOfCaptures(self.chandle, segments)
            assert_pico_ok(self.status["SetNoOfCaptures"])

        # Run block capture
        # handle = chandle
        # number of pre-trigger samples = preTriggerSamples
        # number of post-trigger samples = PostTriggerSamples
        # timebase = 8 = 80 ns (see Programmer's guide for mre information on timebases)
        # time indisposed ms = None (not needed in the example)
        # segment index = 0
        # lpReady = None (using ps5000aIsReady rather than ps5000aBlockReady)
        # pParameter = None
        self.status["runBlock"] = ps.ps5000aRunBlock(self.chandle, self.preTriggerSamples, self.postTriggerSamples, self.timebase, None, 0, None, None)
        assert_pico_ok(self.status["runBlock"])

        # Check for data collection to finish using ps5000aIsReady
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(ready))


        # Create buffers ready for assigning pointers for data collection
        self.bufferAMax = []
        self.bufferAMin = []
        #self.bufferBMax = []
        #self.bufferBMin = []

        for n in range(segments) :

            self.bufferAMax.append((ctypes.c_int16 * self.maxSamples)())
            self.bufferAMin.append((ctypes.c_int16 * self.maxSamples)()) # used for downsampling which isn't in the scope of this example
            #self.bufferBMax[n] = (ctypes.c_int16 * self.maxSamples)()
            #self.bufferBMin[n] = (ctypes.c_int16 * self.maxSamples)() # used for downsampling which isn't in the scope of this example

            # Set data buffer location for data collection from channel A
            # handle = chandle
            source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"]
            # pointer to buffer max = ctypes.byref(bufferAMax)
            # pointer to buffer min = ctypes.byref(bufferAMin)
            # buffer length = maxSamples
            # segment index = 0
            # ratio mode = PS5000A_RATIO_MODE_NONE = 0
            self.status["setDataBuffersA"] = ps.ps5000aSetDataBuffers(self.chandle, source, ctypes.byref(self.bufferAMax[n]), ctypes.byref(self.bufferAMin[n]), self.maxSamples, n, 0)
            assert_pico_ok(self.status["setDataBuffersA"])

            # Set data buffer location for data collection from channel B
            # handle = chandle
            #source = ps.PS5000A_CHANNEL["PS5000A_CHANNEL_B"]
            # pointer to buffer max = ctypes.byref(bufferBMax)
            # pointer to buffer min = ctypes.byref(bufferBMin)
            # buffer length = maxSamples
            # segment index = 0
            # ratio mode = PS5000A_RATIO_MODE_NONE = 0
            #self.status["setDataBuffersB"] = ps.ps5000aSetDataBuffers(self.chandle, source, ctypes.byref(self.bufferBMax), ctypes.byref(self.bufferBMin), self.maxSamples, n, 0)
            #assert_pico_ok(self.status["setDataBuffersB"])

            # create overflow loaction
            self.overflow = ctypes.c_int16()
            # create converted type maxSamples

    def waitDataReady(self) :
        # Checks data collection to finish the capture
        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)

        while ready.value == check.value:
            self.status["isReady"] = ps.ps5000aIsReady(self.chandle, ctypes.byref(ready))

    def getData(self, segments = 1) :

        if segments > 1 :
            self.status["GetValuesBulk"] = ps.ps5000aGetValuesBulk(self.chandle, ctypes.byref(self.cmaxSamples), 0, (segments-1), 0, 0, ctypes.byref(self.overflow))
            assert_pico_ok(self.status["GetValuesBulk"])
        # Retried data from scope to buffers assigned above
        # handle = chandle
        # start index = 0
        # pointer to number of samples = ctypes.byref(cmaxSamples)
        # downsample ratio = 0
        # downsample ratio mode = PS5000A_RATIO_MODE_NONE
        # pointer to overflow = ctypes.byref(overflow))
        self.status["getValues"] = ps.ps5000aGetValues(self.chandle, 0, ctypes.byref(self.cmaxSamples), 0, 0, 0, ctypes.byref(self.overflow))
        assert_pico_ok(self.status["getValues"])

        adc2mVChAMax = []
        #adc2mVChBMax = []

        for n in range(segments) :
            # convert ADC counts data to mV
            adc2mVChAMax.append(adc2mV(self.bufferAMax[n], self.chARange, self.maxADC))
            #adc2mVChBMax.append(adc2mV(self.bufferBMax, self.chBRange, self.maxADC))

        return adc2mVChAMax#, adc2mVChBMax
    
    def close(self) : 
        # Stop the scope
        # handle = chandle
        self.status["stop"] = ps.ps5000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

        # Close unit Disconnect the scope
        # handle = chandle
        self.status["close"]=ps.ps5000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])

        # display status returns
        print(self.status)