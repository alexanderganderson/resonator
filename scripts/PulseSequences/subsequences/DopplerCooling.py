from lattice.scripts.PulseSequences.PulseSequence import PulseSequence

class doppler_cooling(PulseSequence):
    
    def configuration(self):
        
        config = [
                'doppler_cooling_frequency_397', 
                'doppler_cooling_amplitude_397', 
                'doppler_cooling_frequency_866', 
                'doppler_cooling_amplitude_866', 
                'doppler_cooling_duration',
                'doppler_cooling_repump_additional'
                ]
        return config
    
    def sequence(self):
        
        pulses = self.ttl_pulses
        repump_duration = self.p.doppler_cooling_duration + self.p.doppler_cooling_repump_additional
        pulses.append( ('866DP',self.start, repump_duration) )
        self.end = self.start + repump_duration
