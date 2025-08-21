#######################################################################################
# AudioSample.py       Version 1.0     19-May-2025
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

import os           # for checking file existence and path operations
import math         # for logarithmic calculations in pitch/frequency conversions
import atexit       # For cleanup on exit

from _RealtimeAudioPlayer import _RealtimeAudioPlayer
from timer import *

### helper functions ##############################################################

def noteToFreq(pitch):
   """
   Converts a MIDI pitch to the corresponding frequency.  A4 corresponds to the note number 69
   (concert pitch is set to 440Hz by default).
   """
   concertPitch = 440.0   # 440Hz

   frequency = concertPitch * 2 ** ( (pitch - 69) / 12.0 )

   return frequency

def freqToNote(hz):
   """Converts frequency in Hz to MIDI pitch (float for microtonal accuracy)."""
   if hz <= 0: return 0.0 # MIDI pitch 0 often means silence or unpitched
   return 69.0 + 12.0 * math.log2(hz / 440.0)

# default midi pitch for AudioSample objects
A4 = 69

# keep track of active AudioSample instances for cleanup
_activeAudioSamples = []

### AudioSample Class ##############################################################

class AudioSample:
   """
   Encapsulates a sound object created from an external audio file, which can be played once,
   looped, paused, resumed, and stopped.  Also, each sound has an actual pitch or frequency, namely
   the actual pitch, or fundamental frequency of the recorded sound (default is A4 - 69 or 440.0),
   so we can play other note pitches or frequencies with it (through pitch shifting).
   Also, the sound object allows for polyphony - the default is 16 different voices, which can be played,
   pitch-shifted, looped, etc. indepedently from each other.  This way, we can play chords, etc., which is very nice.
   Finally, we can set/get its volume (0-127), panning (0-127), pitch (0-127), and frequency (in Hz).
   """

   def __init__(self, filename, actualPitch=A4, volume=127, voices=16):
      """Initialize audio sample with the given file and properties."""
      if not os.path.isfile(filename):
         raise FileNotFoundError(f"Audio file '{filename}' not found.")

      self.filename = filename
      self.maxVoices = voices

      # resolve actualPitch to actualPitch (MIDI) and actualFrequency (Hz)
      if isinstance(actualPitch, int) and 0 <= actualPitch <= 127:
         self.actualPitch = float(actualPitch)
         self.actualFrequency = noteToFreq(self.actualPitch)
      elif isinstance(actualPitch, float):
         self.actualFrequency = actualPitch
         self.actualPitch = freqToNote(actualPitch)
         if not (0 <= self.actualPitch <= 127): # check if resulting pitch is valid
            print(f"Warning: Frequency {actualPitch}Hz results in MIDI pitch {self.actualPitch}, which is outside the 0-127 range. Clamping to nearest valid.")
            self.actualPitch = max(0.0, min(127.0, self.actualPitch))
            self.actualFrequency = noteToFreq(self.actualPitch) # recalculate frequency from clamped pitch
      else:
         self.actualPitch = float(A4)
         self.actualFrequency = noteToFreq(self.actualPitch)
         raise TypeError(f"actualPitch ({actualPitch}) must be an int (0-127) or float (Hz). Defaulting to A4.")

      # validate volume (0-127)
      if not (isinstance(volume, int) and 0 <= volume <= 127):
         print(f"Warning: Volume ({volume}) is invalid. Must be an integer between 0 and 127. Defaulting to 127.")
         self.initialVolume = 127
      else:
         self.initialVolume = volume

      self._players = []
      self._currentPitches = []
      self._currentFrequencies = []
      self._currentVolumes = []
      self._currentPannings = []
      self._isPausedFlags = []
      self._currentLoopSettings = []

      for i in range(self.maxVoices):
         try:
            # _RealtimeAudioPlayer's actualPitch should be the base pitch of the sound file
            player = _RealtimeAudioPlayer(filepath=self.filename, actualPitch=self.actualPitch, loop=False)
            self._players.append(player)
         except Exception as e:
            # If a player fails to initialize, we might want to stop initializing this AudioSample
            # or handle it more gracefully. For now, re-raise with context.
            raise RuntimeError(f"Failed to initialize _RealtimeAudioPlayer for voice {i} with file '{self.filename}': {e}")


         # initialize current states for this voice
         self._currentPitches.append(self.actualPitch)
         self._currentFrequencies.append(self.actualFrequency)
         self._currentVolumes.append(self.initialVolume)
         self._currentPannings.append(64) # default API panning: 64 (center)
         self._isPausedFlags.append(False)
         self._currentLoopSettings.append({
            'active': False,
            'loopCountTarget': 0,
            'loopRegionStartFrame': 0.0,
            'loopRegionEndFrame': -1.0,
            'loopsPerformedCurrent': 0,
            'playDurationSourceFrames': -1.0
         })

         # Set initial parameters on the RealtimeAudioPlayer instance
         # Volume: API (0-127) to Factor (0.0-1.0)
         player.setVolumeFactor(self.initialVolume / 127.0)

         # Panning: API (0-127, 64=center) to Factor (-1.0 to 1.0)
         # (api_pan - 63.5) / 63.5
         # For 64: (64 - 63.5) / 63.5 = 0.5 / 63.5 approx 0.0078 (effectively center)
         # For 0 (left): (0 - 63.5) / 63.5 = -1.0
         # For 127 (right): (127 - 63.5) / 63.5 = 63.5 / 63.5 = 1.0
         apiPanValue = 64 # initial center panning
         panFactor = (apiPanValue - 63.5) / 63.5
         player.setPanFactor(panFactor)

         # The player's pitch/frequency is already set via its actualPitch during init
         # and corresponds to basePitch/baseFrequency. No need to call setPitch/setFrequency here
         # unless we wanted it to start differently from its base.

      _activeAudioSamples.append(self)

   def play(self, start=0, size=-1, voice=0):
      """
      Play the corresponding sample once from the millisecond 'start' until the millisecond 'start'+'size'
      (size == -1 means to the end). If 'start' and 'size' are omitted, play the complete sample.
      If 'voice' is provided, the corresponding voice is used to play the sample (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.play: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      if not (isinstance(start, (int, float)) and start >= 0):
         print(f"AudioSample.play: Warning - Invalid start time {start}ms. Must be a non-negative number. Using 0ms.")
         start = 0

      player = self._players[voice]
      start_seconds = start / 1000.0
      startAtBeginning = True

      if start > 0:
         player.setCurrentTime(start_seconds) # Sets player.playbackPosition
         startAtBeginning = False

      calculated_play_duration_source_frames = -1.0
      loop_region_start_f = 0.0
      if player.getFrameRate() > 0:
          loop_region_start_f = (start / 1000.0) * player.getFrameRate() if start > 0 else 0.0

      if size > 0: # size is in ms
         size_seconds = size / 1000.0
         frameRate = player.getFrameRate()
         if frameRate > 0:
            calculated_play_duration_source_frames = size_seconds * frameRate
         else:
            print(f"AudioSample.play: Warning - Could not determine valid frame rate for voice {voice}. 'size' parameter will be ignored.")
      elif size == 0:
         calculated_play_duration_source_frames = 0.0

      # Store non-looping settings (or settings for a single iteration if size is given)
      self._currentLoopSettings[voice] = {
          'active': False, # signifies it's a play-once (or play-duration)
          'loopCountTarget': 0, # ensures it's treated as non-looping by RTA if loop=False
          'loopRegionStartFrame': loop_region_start_f,
          'loopRegionEndFrame': -1.0, # not critical for non-looping, RTA uses targetEndSourceFrame based on duration
          'loopsPerformedCurrent': 0,
          'playDurationSourceFrames': calculated_play_duration_source_frames # store this for resume
      }

      # ensure the player is set to not loop for this single play command.
      player.play(startAtBeginning=startAtBeginning,
                  loop=False,
                  playDurationSourceFrames=calculated_play_duration_source_frames,
                  loopRegionStartFrame=loop_region_start_f
                  # initialLoopsPerformed will be 0 (default) for a new play
                  )

      self._isPausedFlags[voice] = False

   def loop(self, times=-1, start=0, size=-1, voice=0):
      """
      Repeat the corresponding sample indefinitely (times = -1), or the specified number of times
      from millisecond 'start' until millisecond 'start'+'size' (size == -1 means to the end).
      If 'start' and 'size' are omitted, repeat the complete sample.
      If 'voice' is provided, the corresponding voice is used to loop the sample (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.loop: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      if not (isinstance(start, (int, float)) and start >= 0):
         print(f"AudioSample.loop: Warning - Invalid start time {start}ms. Must be a non-negative number. Using 0ms.")
         start = 0

      player = self._players[voice]
      frameRate = player.getFrameRate()

      loopRegionStartFrames = 0.0
      if start > 0:
         if frameRate > 0:
            loopRegionStartFrames = (start / 1000.0) * frameRate
         else:
            print(f"AudioSample.loop: Warning - Invalid frame rate for voice {voice}. 'start' parameter might not work as expected.")

      loopRegionEndFrames = -1.0 # Default to end of file
      if size > 0: # size is in ms
         if frameRate > 0:
            startSeconds = start / 1000.0
            sizeSeconds = size / 1000.0
            loopRegionEndFrames = (startSeconds + sizeSeconds) * frameRate
            # ensure end frame isn't before start frame due to rounding or tiny size
            if loopRegionEndFrames <= loopRegionStartFrames:
               print(f"AudioSample.loop: Warning - Loop 'size' ({size}ms) results in an end point before or at the start point. Will loop entire file from 'start'.")
               loopRegionEndFrames = -1.0 # fallback to loop until end of file from start
         else:
            print(f"AudioSample.loop: Warning - Invalid frame rate for voice {voice}. 'size' parameter will be ignored, looping full file from 'start'.")
      elif size == 0:
         print("AudioSample.loop: Info - 'size=0' is not a valid duration for a loop segment. Looping entire file from 'start'.")
         loopRegionEndFrames = -1.0 # loop entire file if size is 0


      # Determine if player needs to be reset to the beginning of its (new) loop segment.
      # This is generally true unless we are trying to resume a multi-loop sequence, which is not the API here.
      startAtBeginningOfLoopSegment = True
      if start > 0: # If start is specified, we always want to set the current time.
         player.setCurrentTime(start / 1000.0)

      # The `times` parameter from AudioSample API:
      # -1: loop indefinitely (maps to RealtimeAudioPlayer loopCountTarget = -1)
      #  0: play once (maps to RealtimeAudioPlayer loopCountTarget = 0, and loop=False effectively)
      # >0: loop N times (maps to RealtimeAudioPlayer loopCountTarget = N)
      actualLoopCountTarget = times
      playerShouldLoop = True
      if times == 0:
         playerShouldLoop = False
         actualLoopCountTarget = 0 # Play once through the segment
         # print("AudioSample.loop: Info - 'times=0' means play segment once without looping.")

      # print(f"AudioSample.loop: Calling player.play with: loop={player_should_loop}, targetCount={actual_loop_count_target}, regionStartF={loop_region_start_frames}, regionEndF={loop_region_end_frames}")

      # Store loop settings for this voice
      self._currentLoopSettings[voice] = {
          'active': playerShouldLoop,
          'loopCountTarget': actualLoopCountTarget,
          'loopRegionStartFrame': loopRegionStartFrames,
          'loopRegionEndFrame': loopRegionEndFrames,
          'loopsPerformedCurrent': 0, # Reset on new loop command
          'playDurationSourceFrames': -1.0 # Not used for active looping
      }

      player.play(startAtBeginning=startAtBeginningOfLoopSegment, # True to make it start from loop_region_start_frames
                  loop=playerShouldLoop,
                  playDurationSourceFrames=-1.0, # Not used for looping
                  loopRegionStartFrame=loopRegionStartFrames,
                  loopRegionEndFrame=loopRegionEndFrames,
                  loopCountTarget=actualLoopCountTarget)

      self._isPausedFlags[voice] = False

   def stop(self, voice=0):
      """
      Stops sample playback.
      If optional 'voice' is provided, the corresponding voice is stopped (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.stop: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      player = self._players[voice]
      player.stop(immediate=True) # Corresponds to API "Stops sample playback immediately"

      # Reset loop settings for this voice to default non-looping
      self._currentLoopSettings[voice] = {
          'active': False,
          'loopCountTarget': 0,
          'loopRegionStartFrame': 0.0,
          'loopRegionEndFrame': -1.0,
          'loopsPerformedCurrent': 0,
          'playDurationSourceFrames': -1.0
      }
      self._isPausedFlags[voice] = False # Reset pause state on stop

   def isPlaying(self, voice=0):
      """
      Returns True if the sample is still playing, False otherwise.
      If optional 'voice' is provided, the corresponding voice is checked
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.isPlaying: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Returning False.")
         return False

      player = self._players[voice]
      # player.isPlaying directly reflects if the RealtimeAudioPlayer is active.
      # this will be False if stopped, paused (as pause calls player.stop(immediate=False)),
      # or if playback naturally ended.
      return player.isPlaying

   def isPaused(self, voice=0):
      """
      Returns True if the specified voice of the sample is currently paused.
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.isPaused: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Returning False.")
         return False
      return self._isPausedFlags[voice]

   def pause(self, voice=0):
      """
      Pauses sample playback (remembers current position for resume).
      If optional 'voice' is provided, the corresponding voice is paused
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.pause: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      player = self._players[voice]
      # RealtimeAudioPlayer.stop(immediate=False) initiates a fade-out and stops the stream,
      # preserving playbackPosition. This serves as our pause mechanism.
      if player.isPlaying: # only pause if it's actually playing
         # store current loops performed from the player *before* stopping it
         current_loops_performed_by_player = player.getLoopsPerformed()
         self._currentLoopSettings[voice]['loopsPerformedCurrent'] = current_loops_performed_by_player

         player.stop(immediate=False)
         self._isPausedFlags[voice] = True
      else:
         # if already stopped or paused, no action needed or print info
         if self._isPausedFlags[voice]:
            print(f"AudioSample.pause: Voice {voice} is already paused.")
         else:
            print(f"AudioSample.pause: Voice {voice} is not currently playing, cannot pause.")

   def resume(self, voice=0):
      """
      Resumes sample playback (from the paused position).
      If optional 'voice' is provided, the corresponding voice is resumed
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.resume: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      player = self._players[voice]
      loop_settings = self._currentLoopSettings[voice]

      if self._isPausedFlags[voice]:
         # this voice was explicitly paused by AudioSample.pause()
         if player.isPlaying:
            # This case should ideally not be hit if pause correctly stops the player.
            # if it is hit, it means player is playing despite being paused from AudioSample's view.
            print(f"AudioSample.resume: Voice {voice} was paused but player is already playing. Resuming anyway and clearing pause flag.")
         # else:
            # Expected path: paused and player is not playing, so resume.
            # print(f"AudioSample.resume: Resuming explicitly paused voice {voice}.")

         play_duration_for_resume = -1.0
         if not loop_settings['active']: # if it was a single play being resumed
            play_duration_for_resume = loop_settings.get('playDurationSourceFrames', -1.0)

         player.play(
             startAtBeginning=False, # resume from current player.playbackPosition
             loop=loop_settings['active'],
             playDurationSourceFrames=play_duration_for_resume,
             loopRegionStartFrame=loop_settings['loopRegionStartFrame'],
             loopRegionEndFrame=loop_settings['loopRegionEndFrame'],
             loopCountTarget=loop_settings['loopCountTarget'],
             initialLoopsPerformed=loop_settings['loopsPerformedCurrent'] # pass stored count
         )
         self._isPausedFlags[voice] = False
      else:
         # this voice was NOT explicitly paused by AudioSample.pause()
         if player.isPlaying:
            print(f"AudioSample.resume: Voice {voice} is already playing and was not paused!")
         else:
            print(f"AudioSample.resume: Voice {voice} was not paused via AudioSample.pause(). Call pause() first to use resume, or play() to start.")
            # do not change _isPausedFlags[voice] here, it's already False.
            # do not start playback.

   def setFrequency(self, freq, voice=0):
      """
      Sets the sample frequency (in Hz).
      If optional 'voice' is provided, the frequency of the corresponding voice is set
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.setFrequency: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      if not (isinstance(freq, (int, float)) and freq > 0):
         print(f"AudioSample.setFrequency: Warning - Invalid frequency value {freq}Hz. Must be a positive number. No change.")
         return

      player = self._players[voice]
      player.setFrequency(float(freq)) # RealtimeAudioPlayer handles rate adjustment

      self._currentFrequencies[voice] = float(freq)
      # when frequency is set, pitch also changes in the player
      self._currentPitches[voice] = player.getPitch()

   def getFrequency(self, voice=0):
      """
      Returns the current sample frequency.
      If optional 'voice' is provided, the frequency of the corresponding voice is returned
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.getFrequency: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Returning frequency of voice 0.")
         voice = 0
         if not self._currentFrequencies: # should only happen if maxVoices was 0 or less.
            print(f"AudioSample.getFrequency: Error - No voices available to get frequency from.")
            return self.actualFrequency # fallback to baseFrequency of the sample itself

      return self._currentFrequencies[voice]

   def setPitch(self, pitch, voice=0):
      """
      Sets the sample pitch (0-127) through pitch shifting from sample's base pitch.
      If optional 'voice' is provided, the pitch of the corresponding voice is set
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.setPitch: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      if not (isinstance(pitch, (int, float)) and 0 <= pitch <= 127):
         print(f"AudioSample.setPitch: Warning - Invalid pitch value {pitch}. Must be a number between 0 and 127. No change.")
         return

      player = self._players[voice]
      player.setPitch(float(pitch)) # RealtimeAudioPlayer handles rate adjustment based on its basePitch

      self._currentPitches[voice] = float(pitch)
      # when pitch is set, frequency also changes in the player
      self._currentFrequencies[voice] = player.getFrequency()

   def getPitch(self, voice=0):
      """
      Returns the sample's current pitch (it may be different from the default pitch).
      If optional 'voice' is provided, the pitch of the corresponding voice is returned
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.getPitch: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Returning pitch of voice 0.")
         voice = 0 # default to voice 0 if index is invalid
         # If maxVoices is 0 (should not happen with proper init), this could still fail.
         # However, __init__ should create at least one voice if voices >=1.
         # If voices was 0, _currentPitches would be empty. This case should be rare.
         if not self._currentPitches: # should only happen if maxVoices was 0 or less.
            print(f"AudioSample.getPitch: Error - No voices available to get pitch from.")
            return self.actualPitch # fallback to basePitch of the sample itself

      return self._currentPitches[voice]

   def getActualPitch(self):
      """
      Return sample's actual pitch.
      """
      return self.actualPitch


   def getActualFrequency(self):
      """
      Return sample's actual frequency.
      """
      return self.actualFrequency

   def setPanning(self, panning, voice=0):
      """
      Sets the panning of the sample (panning ranges from 0 – 127).
      0 is full left, 64 is center, 127 is full right.
      If optional 'voice' is provided, the panning of the corresponding voice is set
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.setPanning: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      if not (isinstance(panning, int) and 0 <= panning <= 127):
         print(f"AudioSample.setPanning: Warning - Invalid panning value {panning}. Must be an integer between 0 and 127. No change.")
         return

      player = self._players[voice]
      # convert API pan (0-127, 64=center) to player factor (-1.0 to 1.0)
      # (api_pan - 63.5) / 63.5 ensures that 64 -> ~0.0, 0 -> -1.0, 127 -> 1.0
      panFactor = (panning - 63.5) / 63.5
      player.setPanFactor(panFactor)

      self._currentPannings[voice] = panning

   def getPanning(self, voice=0):
      """
      Returns the current panning of the sample (panning ranges from 0 – 127).
      If optional 'voice' is provided, the panning of the corresponding voice is returned
      (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.getPanning: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Returning panning of voice 0.")
         voice = 0
         if not self._currentPannings: # should only happen if maxVoices was 0 or less.
            print(f"AudioSample.getPanning: Error - No voices available to get panning from.")
            return 64 # default center panning

      return self._currentPannings[voice]

   def setVolume(self, volume, delay=2, voice=0):
      """
      Sets the volume (amplitude) of the sample (volume ranges from 0 – 127).
      Optional delay indicates speed with which to adjust volume (in milliseconds – default is 2).
      If voice is provided, the volume of the corresponding voice is set (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.setVolume: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Using voice 0.")
         voice = 0

      if not (isinstance(volume, int) and 0 <= volume <= 127):
         print(f"AudioSample.setVolume: Warning - Invalid volume value {volume}. Must be an integer between 0 and 127. No change.")
         return

      if not (isinstance(delay, (int, float)) and delay >= 0):
         print(f"AudioSample.setVolume: Warning - Invalid delay value {delay}ms. Must be non-negative. Using default behavior (near immediate change).")
         delay = 2

      player = self._players[voice]
      targetVolumeFactor = volume / 127.0

      # define a callback for the ramp to update the player's volume factor
      def rampCallback(currentVolumeFactor):
         player.setVolumeFactor(currentVolumeFactor)
         # we update _currentVolumes with the target API volume, not the intermediate factors.

      if delay > 0: # arbitrary threshold, e.g. > 5ms for a noticeable ramp
         currentApiVolume = self._currentVolumes[voice]
         currentVolumeFactor = currentApiVolume / 127.0

         volumeRamp = LinearRamp(
            delayMs=float(delay),
            startValue=currentVolumeFactor,
            endValue=targetVolumeFactor,
            function=rampCallback,
            stepMs=10 # default step for the ramp, can be adjusted
         )
         volumeRamp.start()   # start volume ramp
         # Note: _currentVolumes[voice] is updated at the end of the ramp by ramp_callback(endValue)
         # or immediately if no ramp.
      else:
         # print(f"AudioSample.setVolume: Setting volume for voice {voice} to {volume} ({target_volume_factor:.2f}) immediately.")
         player.setVolumeFactor(targetVolumeFactor)

      self._currentVolumes[voice] = volume # store the target API volume

   def getVolume(self, voice=0):
      """
      Returns the current volume (amplitude) of the sample (volume ranges from 0 – 127).
      If optional voice is provided, the volume of the corresponding voice is returned (default is 0).
      """
      if not (isinstance(voice, int) and 0 <= voice < self.maxVoices):
         print(f"AudioSample.getVolume: Warning - Invalid voice index {voice}. Must be 0-{self.maxVoices-1}. Returning volume of voice 0.")
         voice = 0
         if not self._currentVolumes: # should only happen if maxVoices was 0 or less.
            print(f"AudioSample.getVolume: Error - No voices available to get volume from.")
            # In __init__, initialVolume is set. If maxVoices=0, _currentVolumes is empty.
            # return initialVolume of the sample if possible, or a default like 127 or 0.
            return self.initialVolume if hasattr(self, 'initialVolume') else 127

      return self._currentVolumes[voice]

   def allocateVoiceForPitch(self, pitch):
      """
      Returns the next available free voice, and allocates it as associated with this pitch.
      Returns None, if all voices / players are occupied.
      """
      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # yes, so convert pitch from MIDI number (int) to Hertz (float)
         pitch = noteToFreq(pitch)
      elif type(pitch) != float:                                   # if pitch a frequency (a float, in Hz)?
         raise TypeError("Pitch (" + str(pitch) + ") should be an int (range 0 and 127) or float (such as 440.0).")

      # now, assume pitch contains a frequency (float)

      # get next free voice (if any)
      voiceForThisPitch = self.getNextFreeVoice()

      if voiceForThisPitch != None:   # if a free voice exists...
         # associate it with this pitch
         if not self.voicesAllocatedToPitch.has_key(pitch):   # new pitch (not sounding already)?
            self.voicesAllocatedToPitch[pitch] = [voiceForThisPitch]         # remember that this voice is playing this pitch
         else:   # there is at least one other voice playing this pitch, so...
            self.voicesAllocatedToPitch[pitch].append( voiceForThisPitch )   # append this voice (mimicking MIDI standard for polyphony of same pitches!!!)

         # now, self.pitchSounding remembers that this voice is associated with this pitch

      # now, return new voice for this pitch (it could be None, if no free voices exist!)
      return voiceForThisPitch

   def getNextFreeVoice(self):
      """
      Returns the next available voice, i.e., a player that is not currently playing.
      Returns None, if all voices / players are occupied.
      """
      if len(self.freeVoices) > 0:   # are there some free voices?
         freeVoice = self.freeVoices.pop(0)   # get the first available one
      else:   # all voices are being used
         freeVoice = None

      return freeVoice

   def getVoiceForPitch(self, pitch):
      """
      Returns the first voice (if any) associated with this pitch (there may be more than one - as we allow polyphony for the same pitch).
      Returns None, if no voices are associated with this pitch.
      """

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # yes, so convert pitch from MIDI number (int) to Hertz (float)
         pitch = noteToFreq(pitch)

      elif type(pitch) != float:   # if pitch a frequency (a float, in Hz)
         raise TypeError("Pitch (" + str(pitch) + ") should be an int (range 0 and 127) or float (such as 440.0).")

      # now, assume pitch contains a frequency (float)

      voice = None   # initialize

      if self.voicesAllocatedToPitch.has_key(pitch) and len( self.voicesAllocatedToPitch[pitch] ) > 0:   # does this pitch have voices allocated to it?
         voice = self.voicesAllocatedToPitch[pitch][0]   # first voice used for this pitch
      else:   # pitch is not currently sounding, so...
         raise ValueError("Pitch (" + str(pitch) + ") is not currently playing!!!")

      # now, let them know which voice was freed (if any)
      return voice

   def deallocateVoiceForPitch(self, pitch):
      """
      Finds the first available voice (if any) associated with this pitch (there may be more than one - as we allow polyphony for the same pitch),
      and puts it back in the pool of free voices - deallocates it.
      """
      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # yes, so convert pitch from MIDI number (int) to Hertz (float)
         pitch = noteToFreq(pitch)

      elif type(pitch) != float:   # if pitch a frequency (a float, in Hz)

         raise TypeError("Pitch (" + str(pitch) + ") should be an int (range 0 and 127) or float (such as 440.0).")

      # now, assume pitch contains a frequency (float)
      if self.voicesAllocatedToPitch.has_key(pitch) and len( self.voicesAllocatedToPitch[pitch] ) > 0:   # does this pitch have voices allocated to it?
         freedVoice = self.voicesAllocatedToPitch[pitch].pop(0)   # deallocate first voice used for this pitch
         self.freeVoices.append( freedVoice )                     # and return it back to the pool of free voices

      else:   # pitch is not currently sounding, so...
         raise ValueError("Pitch (" + str(pitch) + ") is not currently playing!!!")

      # done!!!

   def getFrameRate(self):
      """
      Returns the sample's recording rate (e.g., 44100.0 Hz).
      """
      if not self._players:
         print("AudioSample.getFrameRate: Warning - No audio players initialized for this sample.")
         return None

      # all players share the same frame rate as they are from the same file
      return self._players[0].getFrameRate()

   def __del__(self):
      """
      Destructor for AudioSample. Cleans up the sample's player(s).
      """
      # ensure close is idempotent and handles being called multiple times
      if not hasattr(self, '_players') or not self._players: # check if already closed or not initialized
         return

      for i, player in enumerate(self._players):
         if player: # check if player instance exists
            try:
               player.close()
            except Exception as e:
               print(f"AudioSample.close: Error closing player {i} for '{self.filename}': {e}")
      self._players = [] # clear the list to help with garbage collection and prevent reuse

      # remove from global list if present
      if self in _activeAudioSamples:
         try:
            _activeAudioSamples.remove(self)
         except ValueError:
            # this can happen if close() is called multiple times.
            pass

def _cleanupAudioSamples():
   """Stops and closes all active AudioSample players registered with atexit."""
   # iterate over a copy because sample.__del__() will modify _activeAudioSamples
   activeSamplesCopy = list(_activeAudioSamples)
   for sample in activeSamplesCopy:
      try:
         sample.__del__()
      except Exception as e:
         filename = getattr(sample, 'filename', 'UnknownSample')
         print(f"atexit: Error closing sample {filename}: {e}")

   # After attempting to close all, _activeAudioSamples should ideally be empty
   # if AudioSample.__del__() correctly removes items.
   if _activeAudioSamples:
      # this might indicate an issue if samples couldn't be removed or __del__ wasn't effective.
      _activeAudioSamples.clear() # final attempt to clear the list.

# register cleanup function to be called at Python interpreter exit
atexit.register(_cleanupAudioSamples)

# Note on cleanup: sounddevice itself has an atexit handler that terminates PortAudio.
# Our cleanupAudioSamples function is a best-effort attempt to explicitly close all
# AudioSample instances and their underlying RealtimeAudioPlayer streams before that.
# The RealtimeAudioPlayer.close() method is designed to be robust and will not error
# if PortAudio has already been terminated by sounddevice's cleanup, preventing crashes
# if our atexit handler runs after sounddevice's.


########## tests ##############

if __name__ == '__main__':
   a = AudioSample("Vundabar - Smell Smoke - 03 Tar Tongue.wav")
   a.loop()
