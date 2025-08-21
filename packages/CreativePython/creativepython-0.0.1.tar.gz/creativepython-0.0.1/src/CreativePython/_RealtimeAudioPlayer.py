#######################################################################################
# RealtimeAudioPlayer.py       Version 1.0     19-May-2025
# Trevor Ritchie, Taj Ballinger, and Bill Manaris
#
#######################################################################################
#
# [LICENSING GOES HERE]
#
#######################################################################################
#
#
#######################################################################################

import sounddevice as sd  # for audio playback
import soundfile as sf    # for audio file reading
import numpy as np        # for array operations
import os                 # for file path operations
import math               # for logarithmic calculations in pitch/frequency conversions
import time               # for timing operations

# helper functions
def noteToFreq(pitch):
   """Converts a MIDI pitch to frequency. A4=69 is 440Hz."""
   return 440.0 * (2**((pitch - 69) / 12.0))

def freqToNote(hz):
   """Converts frequency in Hz to MIDI pitch (float for microtonal accuracy)."""
   if hz <= 0: return 0.0
   return 69.0 + 12.0 * math.log2(hz / 440.0)

class _RealtimeAudioPlayer:
   def __init__(self, filepath, loop=False, actualPitch=69, chunkSize=1024):
      if not os.path.isfile(filepath):
         raise ValueError(f"File not found: {filepath}")

      self.filepath = filepath

      try:
         self.audioData, self.sampleRate = sf.read(filepath, dtype='float32')
      except Exception as e:
         print(f"Error loading audio file with soundfile: {e}")
         raise

      if self.audioData.ndim == 1:
         self.numChannels = 1
         self.numFrames = len(self.audioData)
      elif self.audioData.ndim == 2:
         self.numChannels = self.audioData.shape[1]
         self.numFrames = self.audioData.shape[0]
         if self.numChannels > 2:   # ensure we only handle mono or stereo for now
            raise ValueError(f"Unsupported number of channels: {self.numChannels}. Max 2 channels supported.")
      else:
         raise ValueError(f"Unexpected audio data dimensions: {self.audioData.ndim}")

      if self.numFrames == 0:
         print(f"Warning: Audio file '{os.path.basename(self.filepath)}' contains zero audio frames and is unplayable.")

      # playback state attributes
      self.isPlaying = False
      self.playbackPosition = 0.0   # in frames
      self.looping = loop
      self.rateFactor = 1.0
      self.volumeFactor = 1.0

      # panning
      self.panTargetFactor = 0.0
      self.currentPanFactor = 0.0
      self.panInitialFactor = 0.0
      self.panSmoothingDurationMs = 100
      self.panSmoothingTotalFrames = max(1, int(self.sampleRate * (self.panSmoothingDurationMs / 1000.0)))
      self.panSmoothingFramesProcessed = self.panSmoothingTotalFrames   # start as if complete

      # pitch/frequency
      validPitchProvided = False
      if isinstance(actualPitch, (int, float)):
         tempPitch = float(actualPitch)
         if 0 <= tempPitch <= 127:
            self.basePitch = tempPitch
            self.baseFrequency = noteToFreq(self.basePitch)
            validPitchProvided = True

      if not validPitchProvided:
         # This case handles:
         # 1. Invalid types for actualPitch.
         # 2. MIDI pitches (int or float) outside the 0-127 range.
         print(f"Warning: Invalid or out-of-range actualPitch ({actualPitch}) provided for '{os.path.basename(self.filepath)}'. Expected MIDI pitch (int/float) 0-127. Defaulting to A4 (69 / 440Hz).")
         self.basePitch = 69.0 # default MIDI A4
         self.baseFrequency = noteToFreq(self.basePitch) # default 440 Hz

      # fades (master)
      self.fadeInDurationMs = 30
      self.fadeInTotalFrames = max(1, int(self.sampleRate * (self.fadeInDurationMs / 1000.0)))
      self.fadeInFramesProcessed = 0
      self.isApplyingFadeIn = False

      self.fadeOutDurationMs = 50
      self.fadeOutTotalFrames = max(1, int(self.sampleRate * (self.fadeOutDurationMs / 1000.0)))
      self.fadeOutFramesProcessed = 0
      self.isApplyingFadeOut = False
      self.isFadingOutToStop = False

      # fades (seek)
      self.isFadingOutToSeek = False
      self.seekTargetFrameAfterFade = 0.0

      # sounddevice stream
      self.sdStream = None
      self.chunkSize = chunkSize

      # internal
      self.playbackEndedNaturally = False
      self.playDurationSourceFrames = -1.0 # added for specific play duration
      self.targetEndSourceFrame = -1.0     # added for specific play duration

      # loop control attributes
      self.loopRegionStartFrame = 0.0
      self.loopRegionEndFrame = -1.0 # -1 means to end of file for looping
      self.loopCountTarget = -1 # -1 for infinite, 0 means no loop (play once), 1+ for specific counts
      self.loopsPerformed = 0
      if self.looping and self.loopCountTarget == -1: # default constructor loop is infinite
         pass # loopCountTarget remains -1
      elif not self.looping:
         self.loopCountTarget = 0 # play once then stop if loop=False initially

      # print(f"For '{os.path.basename(self.filepath)}', BasePitch={self.basePitch:.2f}, BaseFreq={self.baseFrequency:.2f}Hz.")

   def _findNextZeroCrossing(self, startFrameFloat, searchWindowFrames=256):
      """
      Finds the nearest zero-crossing at or after startFrameFloat.
      Looks within a small window to avoid long searches.
      Returns the frame index (float) of the sample that is at or just after the zero-crossing.
      If no crossing is found within the window, returns the original startFrame, clamped to audio bounds.
      """
      startFrame = int(math.floor(startFrameFloat))
      startFrame = max(0, min(startFrame, self.numFrames - 1))

      # ensure search does not go out of bounds
      endSearchFrame = min(self.numFrames - 1, startFrame + searchWindowFrames)

      if startFrame >= self.numFrames -1:   # if already at or past the second to last frame
         return float(min(startFrame, self.numFrames -1))

      for i in range(startFrame, endSearchFrame):
         currentSample = 0.0
         nextSample = 0.0

         if self.numChannels == 1:
            currentSample = self.audioData[i]
            if i + 1 < self.numFrames:
               nextSample = self.audioData[i+1]
            else:
               return float(i) # reached end
         elif self.numChannels >= 2:   # use left channel for stereo or more
            currentSample = self.audioData[i, 0]
            if i + 1 < self.numFrames:
               nextSample = self.audioData[i+1, 0]
            else:
               return float(i) # reached end

         if currentSample == 0.0:
            return float(i)
         if (currentSample > 0 and nextSample <= 0) or \
            (currentSample < 0 and nextSample >= 0):
            # choose the one closer to zero, or simply i+1
            # for simplicity, return i+1 as it's after the crossing
            return float(i + 1)

      return float(startFrame)   # no crossing found in window

   def setRateFactor(self, factor):
      if not isinstance(factor, (int, float)):
         return
      if factor <= 0:
         self.rateFactor = 0.00001   # avoid zero or negative, effectively silent/pause
      else:
         self.rateFactor = float(factor)
      # print(f"Set to {self.rateFactor:.4f}")

   def getRateFactor(self):
      return self.rateFactor

   def setVolumeFactor(self, factor):
      if not isinstance(factor, (int, float)):
         self.volumeFactor = 1.0
         return
      self.volumeFactor = max(0.0, min(1.0, float(factor)))
      # print(f"Set to {self.volumeFactor:.3f}")

   def getVolumeFactor(self):
      return self.volumeFactor

   def setPanFactor(self, panFactor):
      if not isinstance(panFactor, (int, float)):
         clampedPanFactor = 0.0
      else:
         clampedPanFactor = max(-1.0, min(1.0, float(panFactor)))

      if abs(self.panTargetFactor - clampedPanFactor) > 0.001:   # if target changes significantly
         self.panTargetFactor = clampedPanFactor
         self.panInitialFactor = self.currentPanFactor   # store current actual pan as start of ramp
         self.panSmoothingFramesProcessed = 0   # reset to start smoothing ramp

   def getPanFactor(self):
      return self.panTargetFactor

   def setFrequency(self, targetFrequencyHz):
      if not isinstance(targetFrequencyHz, (int, float)):
         return
      if self.baseFrequency <= 0:
         return
      if targetFrequencyHz <= 0:
         self.setRateFactor(0.00001)
         return
      newRateFactor = targetFrequencyHz / self.baseFrequency
      self.setRateFactor(newRateFactor)

   def getFrequency(self):
      return self.baseFrequency * self.rateFactor

   def setPitch(self, midiPitch):
      if not (isinstance(midiPitch, (int, float)) and 0 <= midiPitch <= 127):
         return
      targetFrequencyHz = noteToFreq(float(midiPitch))
      self.setFrequency(targetFrequencyHz)

   def getPitch(self):
      currentFreq = self.getFrequency()
      return freqToNote(currentFreq)

   def getActualPitch(self):
      return self.basePitch

   def getActualFrequency(self):
      return self.baseFrequency

   def getFrameRate(self):
      return self.sampleRate

   def getCurrentTime(self):
      return self.playbackPosition / self.sampleRate

   def setCurrentTime(self, timeSeconds):
      """Sets the current playback position.
      Full fade-seek-fade logic will be implemented later.
      For now, directly sets position and finds zero-crossing.
      """
      if not isinstance(timeSeconds, (int, float)) or timeSeconds < 0:
         timeSeconds = 0.0

      originalTargetFrameFloat = timeSeconds * self.sampleRate

      # basic ZC adjustment for now, will be enhanced with fade-seek-fade
      actualTargetFrame = self.findNextZeroCrossing(originalTargetFrameFloat)

      # if playing and conditions met for smooth seek (TODO: full logic from plan)
      # for now, direct set:
      if actualTargetFrame >= self.numFrames and not self.looping:
         self.playbackPosition = float(self.numFrames -1)
         self.playbackEndedNaturally = True
      else:
         self.playbackPosition = actualTargetFrame
         self.playbackEndedNaturally = False   # reset if jumping

   # --- Playback Control Methods (play, stop, close) and audioCallback will be next ---

   def audioCallback(self, outdata, frames, time, status):
      """
      This is the core audio processing callback.
      It's called by sounddevice when it needs more audio data.

      Parameters:
      outdata (numpy.ndarray): A NumPy array that this function needs to fill with audio data.
                               This is what will be sent to the sound card.
                               Its shape is (frames, numOutputChannels).
      frames (int): The number of audio frames (samples per channel) that sounddevice expects
                    this function to produce.
      time (sounddevice. beggeback object): Contains various timestamps related to the audio stream.
                                      `time.currentTime` is the time at the sound card when the first
                                      sample of `outdata` will be played.
                                      `time.inputBufferAdcTime` is the capture time of the first input sample (if input stream).
                                      `time.outputBufferDacTime` is the time the first output sample will be played.
      status (sounddevice.CallbackFlags): Flags indicating if any stream errors (e.g., input overflow,
                                         output underflow) have occurred. It's good practice to check
                                         this, though for simplicity in many examples it might be ignored.
      """
      if status:
         # print(f"Status flags: {status}") # keep this commented unless debugging status
         pass # pass for now to avoid console noise unless specific status handling is added

      # failsafe for zero-frame audio, though play() should prevent this stream from starting.
      if self.numFrames == 0:
         outdata.fill(0) # fill the output buffer with silence.
         if self.isPlaying: # this should ideally not be true if play() did its job
            self.isPlaying = False # ensure playback state is consistent.
         raise sd.CallbackStop # stop the callback immediately, as there's no audio to play.

      # If not playing or rate is effectively zero, output silence.
      # This handles cases where playback is paused, explicitly stopped, or the playback rate
      # is so low that it's practically silent. This is a quick way to silence output
      # without needing to go through the whole processing loop.
      if not self.isPlaying or self.rateFactor <= 0.000001:
         outdata.fill(0) # fill the output buffer with silence.
         if self.isApplyingFadeOut and self.isFadingOutToStop and self.rateFactor <= 0.000001:
            # If a fade-out to stop was in progress and the rate also became zero (e.g. set externally),
            # ensure the player state is fully stopped.
            self.isPlaying = False
            self.isApplyingFadeOut = False
            self.isFadingOutToStop = False
            # no need to raise CallbackStop here, as returning normally from a callback while
            # the stream is active and isPlaying is false will lead to it being stopped by play/stop logic.

         return # exit the callback early, providing silence.

      numOutputChannels = outdata.shape[1]
      # initialize chunkBuffer matching the output stream's channel count and frame count for this callback.
      # This buffer will be filled with processed audio samples one by one before being copied to `outdata`.
      # Using an intermediate buffer like this is common for clarity and for complex processing steps.
      chunkBuffer = np.zeros((frames, numOutputChannels), dtype=np.float32)

      for i in range(frames): # per-sample processing loop
         if not self.isPlaying: # check if stop was called or playback ended within the loop
            # If isPlaying became false (e.g., due to a fade-out completing and setting isPlaying to False,
            # or an external stop() call), we should fill the rest of this chunk with silence
            # and then break out of this sample-processing loop.
            chunkBuffer[i:] = 0.0 # fill remaining part of the buffer with silence
            break # exit per-sample loop

         # --- Determine current sample value with interpolation (and hard loop if enabled) ---
         # To play audio at different speeds (self.rateFactor != 1.0) or for smooth playback,
         # we often need a sample value that lies *between* two actual data points in our audioData.
         # Linear interpolation is a common way to estimate this value.
         readPosFloat = self.playbackPosition # This is a floating-point number indicating the conceptual read position.
         readPosInt1 = int(math.floor(readPosFloat)) # The integer part, an index to an actual sample.
         readPosInt2 = readPosInt1 + 1 # The next actual sample index.
         fraction = readPosFloat - readPosInt1 # The fractional part, how far between readPosInt1 and readPosInt2 we are.

         # Clamp read positions to be safe for array access, *after* potential looping adjustment
         # This ensures that we don't try to read outside the bounds of our audioData array.
         readPosInt1 = max(0, min(readPosInt1, self.numFrames - 1))
         readPosInt2 = max(0, min(readPosInt2, self.numFrames - 1)) # ensures readPosInt2 is also valid

         # get interpolated sample from self.audioData
         currentSampleArray = np.zeros(self.numChannels, dtype=np.float32)
         if self.numChannels == 1: # mono audio source
            sampleValue1 = self.audioData[readPosInt1]
            # handle the case where audioData might only have one frame. If so, sampleValue2 is the same as sampleValue1.
            sampleValue2 = self.audioData[readPosInt2 if self.numFrames > 1 else readPosInt1] # avoid reading past if only 1 frame
            # linear interpolation: V = V1 + (V2 - V1) * fraction
            currentSampleArray[0] = sampleValue1 + (sampleValue2 - sampleValue1) * fraction
         else: # stereo source
            # for stereo, we interpolate each channel (Left and Right) independently.
            sampleValue1_L = self.audioData[readPosInt1, 0] # Left channel, first sample
            sampleValue2_L = self.audioData[readPosInt2 if self.numFrames > 1 else readPosInt1, 0] # Left channel, second sample
            currentSampleArray[0] = sampleValue1_L + (sampleValue2_L - sampleValue1_L) * fraction # Interpolated Left channel

            sampleValue1_R = self.audioData[readPosInt1, 1] # right channel, first sample
            sampleValue2_R = self.audioData[readPosInt2 if self.numFrames > 1 else readPosInt1, 1] # Right channel, second sample
            currentSampleArray[1] = sampleValue1_R + (sampleValue2_R - sampleValue1_R) * fraction # Interpolated Right channel

         # --- Apply Volume --- (Volume is applied first before fades)
         # the overall volume of the sample is scaled by self.volumeFactor
         processedSample = currentSampleArray * self.volumeFactor

         # --- Apply Master Fades (Fade-in and Fade-out) ---
         # Fades are applied by smoothly changing a gain envelope from 0 to 1 (fade-in)
         # or 1 to 0 (fade-out) over a specified number of frames.
         gainEnvelope = 1.0 # start with full gain, adjust if fading.
         if self.isApplyingFadeIn:
            if self.fadeInFramesProcessed < self.fadeInTotalFrames:
               # Calculate gain based on how many fade-in frames have been processed.
               # This creates a linear ramp from 0.0 to 1.0.
               gainEnvelope *= (self.fadeInFramesProcessed / self.fadeInTotalFrames) # ramp from 0 to 1
               self.fadeInFramesProcessed += 1
            else: # fade-in complete
               self.isApplyingFadeIn = False # Stop applying fade-in for subsequent samples.
               # gainEnvelope is already 1.0, fadeInFramesProcessed is capped by play() or setter

         if self.isApplyingFadeOut:
            if self.fadeOutFramesProcessed < self.fadeOutTotalFrames:
               currentFadeOutProgress = self.fadeOutFramesProcessed / self.fadeOutTotalFrames
               # Calculate gain based on how many fade-out frames have been processed.
               # This creates a linear ramp from 1.0 down to 0.0.
               gainEnvelope *= (1.0 - currentFadeOutProgress) # ramp from 1 to 0
               self.fadeOutFramesProcessed += 1
            else: # fade-out complete
               gainEnvelope = 0.0 # ensure silence
               self.isApplyingFadeOut = False # stop applying fade-out.
               if self.isFadingOutToStop:
                  # If this fade-out was intended to stop playback (e.g., user called stop()),
                  # set isPlaying to False. This will be caught at the start of the next
                  # sample processing iteration or at the end of this audio block.
                  self.isPlaying = False # this will be caught at start of next sample or end of block
                  self.isFadingOutToStop = False
                  self.targetEndSourceFrame = -1.0 # reset here
                  self.playDurationSourceFrames = -1.0 # reset here

         processedSample *= gainEnvelope # apply the combined fade gain to the sample.

         # --- Apply Panning --- (To the already faded and volume-adjusted sample)
         finalOutputSample = np.zeros(numOutputChannels, dtype=np.float32)
         if numOutputChannels == 2: # stream is stereo
            panValue = self.currentPanFactor # use smoothed value updated at end of block
            # Standard psychoacoustic panning law (constant power)
            # This formula ensures that the total perceived loudness remains relatively constant
            # as the sound is panned from left to right.
            # pan value from -1 (L) to 0 (C) to 1 (R)
            # angle goes from 0 (L) to PI/4 (C) to PI/2 (R)
            panAngleRad = (panValue + 1.0) * math.pi / 4.0 # convert panValue to an angle
            leftGain = math.cos(panAngleRad)  # gain for the left channel
            rightGain = math.sin(panAngleRad) # gain for the right channel

            if self.numChannels == 1: # mono source to stereo output
               # apply panning gains to the single source channel for stereo output
               finalOutputSample[0] = processedSample[0] * leftGain
               finalOutputSample[1] = processedSample[0] * rightGain
            else: # stereo source to stereo output
               # Apply panning gains to each respective channel of the stereo source.
               # Note: This is a simple pan of a stereo source. More sophisticated stereo
               # panners might treat the channels differently (e.g., balance control).
               finalOutputSample[0] = processedSample[0] * leftGain
               finalOutputSample[1] = processedSample[1] * rightGain
         else: # stream is mono
            if self.numChannels == 1: # mono source to mono output
               # no panning needed, just pass the sample through.
               finalOutputSample[0] = processedSample[0]
            else: # stereo source to mono output (mix down)
               # Mix the left and right channels of the stereo source to a single mono channel.
               # The 0.5 factor helps prevent clipping when combining channels.
               finalOutputSample[0] = (processedSample[0] + processedSample[1]) * 0.5 # mixdown with gain to avoid clipping

         chunkBuffer[i] = finalOutputSample

         # --- Advance Playback Position for next sample ---
         # self.playbackPosition is advanced by self.rateFactor. If rateFactor is 1.0, it moves one sample forward.
         # If rateFactor is 0.5, it effectively plays at half speed (each source sample is held for two output samples, due to interpolation).
         # If rateFactor is 2.0, it plays at double speed (skipping source samples, with interpolation filling the gaps).
         self.playbackPosition += self.rateFactor # RESTORED - No more * 0.5 hack

         # This is the point at which we should either loop or stop for the current play segment,
         # so determine the effective end frame for the current segment/loop
         effectiveSegmentEndFrame = self.numFrames -1 # default to end of file

         if self.looping and self.loopRegionEndFrame > 0:
            # if looping and a specific loop region end is defined, that's our segment end
            effectiveSegmentEndFrame = self.loopRegionEndFrame
         elif not self.looping and self.targetEndSourceFrame > 0: # play(size) scenario
            # if not looping, but a specific duration was given (play(size)), that defines the segment end
            effectiveSegmentEndFrame = self.targetEndSourceFrame

         # check for end of segment (loop iteration, play(size) duration, or natural EOF)
         if self.playbackPosition >= effectiveSegmentEndFrame:
            # we've reached or passed the end of the current audio segment
            if self.looping:
               self.loopsPerformed += 1
               if self.loopCountTarget != -1 and self.loopsPerformed >= self.loopCountTarget:
                  # If we've reached the target number of loops (and it's not infinite looping),
                  # stop playback.
                  self.isPlaying = False
                  self.loopsPerformed = 0 # reset for next play call
                  # other loop params (loopCountTarget, loopRegionStartFrame, loopRegionEndFrame) are reset by play()
               else: # continue looping (either infinite or more loops to go)
                  # wrap position back to the start of the loop region
                  # This causes playback to jump back to self.loopRegionStartFrame to continue the loop.
                  self.playbackPosition = self.loopRegionStartFrame

            else: # not looping, and reached end of specified segment or natural EOF
               # this handles both play(size) completion and natural end of a non-looping file.
               self.isPlaying = False # stop playback.
               if self.playbackPosition >= self.numFrames -1: # check if it was natural EOF
                  # If we've also reached or passed the actual end of the audio file data,
                  # mark that playback ended naturally.
                  self.playbackEndedNaturally = True

               # reset play(size) parameters if they were active
               self.targetEndSourceFrame = -1.0
               self.playDurationSourceFrames = -1.0
               # loop counters are reset by play() or if explicitly stopped.
               # self.loopsPerformed = 0 # reset here too just in case.

         # --- Post-loop/end-of-segment logic, check if isPlaying is still true before interpolation ---
         # This check is crucial. If the logic above (loop completion, segment end) set isPlaying to False,
         # we need to fill the rest of the current audio chunk with silence and exit the sample loop.
         if not self.isPlaying:
            chunkBuffer[i:] = 0.0 # fill remaining part of this chunk with silence
            break # exit per-sample loop

      # --- End of per-sample loop (for i in range(frames)) ---

      # --- Update smoothed pan factor (block-level, after all samples in this chunk are processed) ---
      # To avoid abrupt changes in panning, which can sound like clicks or pops,
      # we smoothly transition the self.currentPanFactor towards self.panTargetFactor over
      # a short duration (self.panSmoothingTotalFrames).
      # This calculation is done once per audio block (callback invocation) rather than per sample
      # for efficiency, and because per-sample smoothing might be overkill for panning.
      if self.panSmoothingFramesProcessed < self.panSmoothingTotalFrames:
         self.panSmoothingFramesProcessed += frames # accumulate frames processed in this callback
         if self.panSmoothingFramesProcessed >= self.panSmoothingTotalFrames:
            self.currentPanFactor = self.panTargetFactor # target reached, snap to it.
            self.panSmoothingFramesProcessed = self.panSmoothingTotalFrames # cap it
         else:
            # interpolate current pan factor for the block based on progress
            # t is the fraction of the smoothing duration that has passed.
            t = self.panSmoothingFramesProcessed / self.panSmoothingTotalFrames
            self.currentPanFactor = self.panInitialFactor + (self.panTargetFactor - self.panInitialFactor) * t
      else: # smoothing is complete or wasn't active for this block duration
         self.currentPanFactor = self.panTargetFactor # ensure it's at target if smoothing just finished or was already done

      # --- Copy the fully processed chunkBuffer to the output buffer for sounddevice ---
      # Audio samples should typically be within the range -1.0 to 1.0.
      # np.clip ensures that any values outside this range (due to processing, bugs, or loud source material)
      # are clamped to the min/max, preventing potential distortion or errors in the audio output driver.
      outdata[:] = np.clip(chunkBuffer, -1.0, 1.0)

      # --- Handle stream stopping conditions ---
      # If isPlaying became False during this callback (e.g., by fade-out completion or natural end)
      # raise CallbackStop to tell PortAudio to stop invoking this callback.
      # This is the primary mechanism for cleanly stopping the audio stream from within the callback
      # when playback is logically complete or has been requested to stop.
      if not self.isPlaying:
         raise sd.CallbackStop

   def play(self, startAtBeginning=True, loop=None, playDurationSourceFrames=-1.0,
            loopRegionStartFrame=0.0, loopRegionEndFrame=-1.0, loopCountTarget=None,
            initialLoopsPerformed=0):

      if self.numFrames == 0:
         print(f"Cannot play '{os.path.basename(self.filepath)}' as it contains zero audio frames.")
         self.isPlaying = False # ensure state consistency
         return # do not proceed to start a stream

      if self.isFadingOutToStop:
         self.isApplyingFadeOut = False
         self.isFadingOutToStop = False
         self.fadeOutFramesProcessed = 0

      # determine definitive looping state and count from parameters
      if loop is not None:
         self.looping = bool(loop)
      elif loopCountTarget is not None: # loop is None, derive from loopCountTarget
         self.looping = True if loopCountTarget != 0 else False
      # If both loop and loopCountTarget are None, self.looping is unchanged (relevant if stream is already playing)
      # or takes its initial value from __init__ if stream is being started for the first time.

      if loopCountTarget is not None:
         self.loopCountTarget = loopCountTarget
      elif self.looping: # loopCountTarget is None, but self.looping is True (e.g. from init or previous call)
         self.loopCountTarget = -1 # default to infinite if not specified but looping is true
      else: # loopCountTarget is None and self.looping is False
         self.loopCountTarget = 0 # default to play once

      # ensure consistency: if loopCountTarget implies a certain looping state, it can refine self.looping
      if self.loopCountTarget == 0: # explicitly play once for this segment
         self.looping = False
      elif self.loopCountTarget == -1 or self.loopCountTarget > 0: # infinite or positive count implies looping
         self.looping = True

      # store parameters
      self.playDurationSourceFrames = playDurationSourceFrames # used if not self.looping
      self.loopRegionStartFrame = max(0.0, float(loopRegionStartFrame))
      self.loopRegionEndFrame = float(loopRegionEndFrame) if loopRegionEndFrame is not None else -1.0

      # validate loopRegionEndFrame against numFrames if it's positive
      if self.loopRegionEndFrame > 0:
         self.loopRegionEndFrame = min(self.loopRegionEndFrame, self.numFrames - 1 if self.numFrames > 0 else 0.0)
      # ensure start frame is not after end frame if both are positive and numFrames > 0
      if self.numFrames > 0 and self.loopRegionEndFrame > 0 and self.loopRegionStartFrame >= self.loopRegionEndFrame:
         self.loopRegionStartFrame = 0.0
         self.loopRegionEndFrame = -1.0 # default to full loop


      if self.looping:
         # if looping, playDurationSourceFrames (for play(size)) is ignored in favor of loop settings.
         self.targetEndSourceFrame = -1.0
      elif self.playDurationSourceFrames >= 0: # not looping, but play(size) is active (or 0 duration)
         currentStartForCalc = self.playbackPosition if not startAtBeginning else self.loopRegionStartFrame
         self.targetEndSourceFrame = currentStartForCalc + self.playDurationSourceFrames
         # self.loopCountTarget is already 0 if self.looping is false due to above logic.
      else: # not looping, no specific duration (play once through, natural EOF)
         self.targetEndSourceFrame = -1.0
         # self.loopCountTarget is already 0.

      # handle playback position and loops performed count based on startAtBeginning and initialLoopsPerformed
      if startAtBeginning:
         self.playbackPosition = self.loopRegionStartFrame # start at the beginning of the loop region (or 0 if not specified)
         self.loopsPerformed = initialLoopsPerformed # typically 0 for a fresh start from beginning
      else: # resuming (startAtBeginning=False)
         # playbackPosition is where it was left off by pause or setCurrentTime
         self.loopsPerformed = initialLoopsPerformed # restore from argument

      self.playbackEndedNaturally = False # reset this flag as we are starting/resuming a play action

      # if already playing, these settings will take effect, but stream isn't restarted.
      # if not playing, start the stream.
      if not self.isPlaying:
         if self.playbackPosition >= self.numFrames and not self.looping:
            self.playbackPosition = 0.0 # or self._findNextZeroCrossing(0.0)
         self.playbackEndedNaturally = False

         try:
            # always start with a fade-in when initiating play from a stopped state or from a fade-out-to-stop state
            self.isApplyingFadeIn = True
            self.fadeInFramesProcessed = 0

            if self.sdStream and not self.sdStream.closed:
               # If stream exists but was stopped (e.g. by isPlaying = False in callback)
               # It needs to be closed and reopened, or sounddevice's start() might not work as expected
               # or might resume from an odd state. Safest is to ensure clean start.
               self.sdStream.close() # ensure previous instance is closed


            self.sdStream = sd.OutputStream(
               samplerate=self.sampleRate,
                  blocksize=self.chunkSize,
                  channels=self.numChannels,
                  callback=self.audioCallback,
                  finished_callback=self.onPlaybackFinished
            )
            self.sdStream.start()
            self.isPlaying = True
            self.playbackEndedNaturally = False # reset this flag as we are starting
         except Exception as e:
            print(f"Error starting sounddevice stream: {e}")
            self.isPlaying = False
            if self.sdStream:
               self.sdStream.close() # ensure cleanup if start failed
            self.sdStream = None
            # do not re-raise here, allow AudioSample to handle or log
            return # exit if stream failed to start

         if startAtBeginning and self.isPlaying: # check isPlaying again in case it was set by new stream
            self.isApplyingFadeIn = True
            self.fadeInFramesProcessed = 0

   def onPlaybackFinished(self):
      # This callback is called when the stream is stopped or aborted.
      # self.isPlaying = False # Stream is already stopped, this reflects state
      # Don't reset looping here, it's a persistent setting.
      # Don't reset playbackPosition here, might be needed for resume or query.
      if self.sdStream and not self.sdStream.closed:
         try: # add try-except for robustness during atexit
            self.sdStream.close() # ensure it's closed
         except sd.PortAudioError as pae:
            if pae.args[1] == sd.PaErrorCode.paNotInitialized:
               pass # PortAudio already terminated, expected during atexit
            else:
               print(f"PortAudioError closing stream: {pae}")
         except Exception as e:
            print(f"Generic error closing PortAudio stream: {e}")

      self.sdStream = None # discard stream instance

      # If it was a fade out to stop, the isPlaying should already be false.
      # If it stopped for other reasons (e.g. error, or CallbackStop raised not due to fade),
      # ensure isPlaying is False.
      # However, self.isPlaying is primarily controlled by play() and stop() and callback logic.
      # this finished_callback is more for resource cleanup.

   def getLoopsPerformed(self):
      return self.loopsPerformed

   def stop(self, immediate=False):
      if not self.isPlaying and not self.isApplyingFadeOut: # if already stopped and not in a pending fade-out
         # ensure stream is actually closed if somehow isPlaying is False but stream exists
         if self.sdStream and not self.sdStream.closed:
            try:
               self.sdStream.close()
            except sd.PortAudioError as pae:
               if pae.args[1] == sd.PaErrorCode.paNotInitialized: pass
               else: print(f"Error closing PyAudio stream: {pae}")
            except Exception as e: print(f"Generic error closing PyAudio stream: {e}")
            self.sdStream = None
         self.isPlaying = False # confirm state
         self.targetEndSourceFrame = -1.0 # ensure reset if stopped externally
         self.playDurationSourceFrames = -1.0 # ensure reset
         # reset loop attributes on stop
         self.loopRegionStartFrame = 0.0
         self.loopRegionEndFrame = -1.0
         self.loopCountTarget = -1 if self.looping else 0 # reset to reflect constructor state or play-once
         self.loopsPerformed = 0
         return

      if immediate:
         self.isPlaying = False # signal callback to stop producing audio
         self.isApplyingFadeIn = False # cancel any ongoing fade-in
         self.isApplyingFadeOut = False # cancel any ongoing fade-out (e.g. from pause)
         self.isFadingOutToStop = False # ensure this is reset

         if self.sdStream:
            try:
               # check if stream is active before trying to stop
               if not self.sdStream.stopped:
                  self.sdStream.stop()  # stop the PortAudio stream immediately

               # re-check self.sdStream because .stop() could have called _onPlaybackFinished
               # which sets self.sdStream to None.
               if self.sdStream and not self.sdStream.closed:
                  self.sdStream.close() # close and release resources
            except sd.PortAudioError as pae:
               if pae.args[1] == sd.PaErrorCode.paNotInitialized:
                  pass # PortAudio already terminated, expected during atexit or rapid stop/close
               else:
                  print(f"PortAudioError during immediate stream stop/close: {pae}")
            except Exception as e:
               print(f"Error during immediate stream stop/close: {e}")
            finally:
               self.sdStream = None # discard stream instance
         self.targetEndSourceFrame = -1.0
         self.playDurationSourceFrames = -1.0
         self.loopRegionStartFrame = 0.0
         self.loopRegionEndFrame = -1.0
         self.loopCountTarget = -1 if self.looping else 0
         self.loopsPerformed = 0
      else: # gradual stop (fade out)
         if self.isPlaying or self.isApplyingFadeIn: # only start a fade-out if actually playing or was about to start
            self.isApplyingFadeIn = False # stop any fade-in
            self.isApplyingFadeOut = True
            self.isFadingOutToStop = True # mark that this fade-out is intended to stop playback
            self.fadeOutFramesProcessed = 0
            # isPlaying remains true until fade-out completes in the callback

   def close(self):
      self.isPlaying = False # ensure any playback logic stops

      # cancel any pending fades that might try to operate on a closing stream
      self.isApplyingFadeIn = False
      self.isApplyingFadeOut = False
      self.isFadingOutToStop = False

      if self.sdStream:
         try:
            # check if stream is active before trying to stop
            if self.sdStream and not self.sdStream.stopped: # check self.sdStream first
               self.sdStream.stop() # stop stream activity

            # re-check self.sdStream because .stop() could have called onPlaybackFinished
            if self.sdStream and not self.sdStream.closed: # check self.sdStream first
               self.sdStream.close() # release resources
         except sd.PortAudioError as pae:
            # if PortAudio is already uninitialized (e.g. during atexit), these calls can fail.
            if pae.args[1] == sd.PaErrorCode.paNotInitialized: # paNotInitialized = -10000
               pass # suppress error if PortAudio is already down
            else:
               print(f"PortAudioError during stream stop/close: {pae}")
               # raise # Optionally re-raise if it's a different PortAudio error
            print(f"Generic error during PortAudio stream stop/close: {e}")
            # raise # Optionally re-raise
         finally:
            self.sdStream = None

   def __del__(self):
      # call close() to ensure resources are released
      self.close()
