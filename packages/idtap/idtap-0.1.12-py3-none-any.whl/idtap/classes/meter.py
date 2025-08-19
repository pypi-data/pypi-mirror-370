from __future__ import annotations
from typing import List, Dict, Optional
from uuid import uuid4

# Tempo validation constants
MIN_TEMPO_BPM = 20  # Very slow musical pieces (e.g., some alap sections)
MAX_TEMPO_BPM = 300  # Very fast musical pieces


def find_closest_idxs(trials: List[float], items: List[float]) -> List[int]:
    """Return indexes of items closest to each trial (greedy)."""
    used: set[int] = set()
    out: List[int] = []
    for trial in trials:
        diffs = [(abs(trial - item), idx) for idx, item in enumerate(items)
                 if idx not in used]
        diffs.sort(key=lambda x: x[0])
        if not diffs:
            raise ValueError("not enough items to match trials")
        used.add(diffs[0][1])
        out.append(diffs[0][1])
    return out


class Pulse:
    def __init__(self, real_time: float = 0.0, unique_id: Optional[str] = None,
                 affiliations: Optional[List[Dict]] = None,
                 meter_id: Optional[str] = None,
                 corporeal: bool = True) -> None:
        # Parameter validation
        self._validate_parameters({'real_time': real_time, 'unique_id': unique_id, 
                                  'affiliations': affiliations, 'meter_id': meter_id, 'corporeal': corporeal})
        self.real_time = real_time
        self.unique_id = unique_id or str(uuid4())
        self.affiliations: List[Dict] = affiliations or []
        self.meter_id = meter_id
        self.corporeal = corporeal

    def _validate_parameters(self, opts: Dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if not isinstance(opts.get('real_time', 0.0), (int, float)):
            raise TypeError(f"Parameter 'real_time' must be a number, got {type(opts['real_time']).__name__}")
        
        if opts.get('real_time', 0.0) < 0:
            raise ValueError(f"Parameter 'real_time' must be non-negative, got {opts['real_time']}")
        
        if 'unique_id' in opts and opts['unique_id'] is not None and not isinstance(opts['unique_id'], str):
            raise TypeError(f"Parameter 'unique_id' must be a string, got {type(opts['unique_id']).__name__}")
        
        if 'affiliations' in opts and opts['affiliations'] is not None:
            if not isinstance(opts['affiliations'], list):
                raise TypeError(f"Parameter 'affiliations' must be a list, got {type(opts['affiliations']).__name__}")
            if not all(isinstance(item, dict) for item in opts['affiliations']):
                raise TypeError("All items in 'affiliations' must be dictionaries")
        
        if 'meter_id' in opts and opts['meter_id'] is not None and not isinstance(opts['meter_id'], str):
            raise TypeError(f"Parameter 'meter_id' must be a string, got {type(opts['meter_id']).__name__}")
        
        if not isinstance(opts.get('corporeal', True), bool):
            raise TypeError(f"Parameter 'corporeal' must be a boolean, got {type(opts['corporeal']).__name__}")

    @staticmethod
    def from_json(obj: Dict) -> 'Pulse':
        return Pulse(
            real_time=obj.get('realTime', 0.0),
            unique_id=obj.get('uniqueId'),
            affiliations=obj.get('affiliations'),
            meter_id=obj.get('meterId'),
            corporeal=obj.get('corporeal', True),
        )

    def to_json(self) -> Dict:
        return {
            'realTime': self.real_time,
            'uniqueId': self.unique_id,
            'affiliations': self.affiliations,
            'meterId': self.meter_id,
            'corporeal': self.corporeal,
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Pulse) and self.to_json() == other.to_json()


class PulseStructure:
    def __init__(self, tempo: float = 60.0, size: int = 4,
                 start_time: float = 0.0, unique_id: Optional[str] = None,
                 front_weighted: bool = True, layer: Optional[int] = None,
                 parent_pulse_id: Optional[str] = None,
                 primary: bool = True, segmented_meter_idx: int = 0,
                 meter_id: Optional[str] = None,
                 pulses: Optional[List[Pulse | Dict]] = None) -> None:
        # Parameter validation
        self._validate_parameters({
            'tempo': tempo, 'size': size, 'start_time': start_time, 'unique_id': unique_id,
            'front_weighted': front_weighted, 'layer': layer, 'parent_pulse_id': parent_pulse_id,
            'primary': primary, 'segmented_meter_idx': segmented_meter_idx, 'meter_id': meter_id,
            'pulses': pulses
        })
        self.tempo = tempo
        self.pulse_dur = 60.0 / tempo
        self.size = size
        self.start_time = start_time
        self.unique_id = unique_id or str(uuid4())
        self.front_weighted = front_weighted
        self.layer = layer
        self.parent_pulse_id = parent_pulse_id
        self.primary = primary
        self.segmented_meter_idx = segmented_meter_idx
        self.meter_id = meter_id

        if pulses is not None:
            self.pulses = [p if isinstance(p, Pulse) else Pulse.from_json(p)
                           for p in pulses]
        else:
            self.pulses = [
                Pulse(
                    real_time=start_time + i * self.pulse_dur,
                    affiliations=[{
                        'psId': self.unique_id,
                        'idx': i,
                        'layer': self.layer,
                        'segmentedMeterIdx': self.segmented_meter_idx,
                        'strong': (i == 0) if front_weighted else (i == size - 1),
                    }],
                    meter_id=meter_id
                ) for i in range(size)
            ]

    def _validate_parameters(self, opts: Dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if not isinstance(opts.get('tempo', 60.0), (int, float)):
            raise TypeError(f"Parameter 'tempo' must be a number, got {type(opts['tempo']).__name__}")
        
        if opts.get('tempo', 60.0) <= 0:
            raise ValueError(f"Parameter 'tempo' must be positive, got {opts['tempo']}")
        
        if opts.get('tempo', 60.0) < MIN_TEMPO_BPM or opts.get('tempo', 60.0) > MAX_TEMPO_BPM:
            import warnings
            warnings.warn(f"Tempo {opts['tempo']} BPM is outside typical range ({MIN_TEMPO_BPM}-{MAX_TEMPO_BPM} BPM)", UserWarning)
        
        if not isinstance(opts.get('size', 4), int):
            raise TypeError(f"Parameter 'size' must be an integer, got {type(opts['size']).__name__}")
        
        if opts.get('size', 4) <= 0:
            raise ValueError(f"Parameter 'size' must be positive, got {opts['size']}")
        
        if not isinstance(opts.get('start_time', 0.0), (int, float)):
            raise TypeError(f"Parameter 'start_time' must be a number, got {type(opts['start_time']).__name__}")
        
        if opts.get('start_time', 0.0) < 0:
            raise ValueError(f"Parameter 'start_time' must be non-negative, got {opts['start_time']}")
        
        if 'unique_id' in opts and opts['unique_id'] is not None and not isinstance(opts['unique_id'], str):
            raise TypeError(f"Parameter 'unique_id' must be a string, got {type(opts['unique_id']).__name__}")
        
        if not isinstance(opts.get('front_weighted', True), bool):
            raise TypeError(f"Parameter 'front_weighted' must be a boolean, got {type(opts['front_weighted']).__name__}")
        
        if 'layer' in opts and opts['layer'] is not None:
            if not isinstance(opts['layer'], int):
                raise TypeError(f"Parameter 'layer' must be an integer, got {type(opts['layer']).__name__}")
            if opts['layer'] < 0:
                raise ValueError(f"Parameter 'layer' must be non-negative, got {opts['layer']}")
        
        if 'parent_pulse_id' in opts and opts['parent_pulse_id'] is not None and not isinstance(opts['parent_pulse_id'], str):
            raise TypeError(f"Parameter 'parent_pulse_id' must be a string, got {type(opts['parent_pulse_id']).__name__}")
        
        if not isinstance(opts.get('primary', True), bool):
            raise TypeError(f"Parameter 'primary' must be a boolean, got {type(opts['primary']).__name__}")
        
        if not isinstance(opts.get('segmented_meter_idx', 0), int):
            raise TypeError(f"Parameter 'segmented_meter_idx' must be an integer, got {type(opts['segmented_meter_idx']).__name__}")
        
        if opts.get('segmented_meter_idx', 0) < 0:
            raise ValueError(f"Parameter 'segmented_meter_idx' must be non-negative, got {opts['segmented_meter_idx']}")
        
        if 'meter_id' in opts and opts['meter_id'] is not None and not isinstance(opts['meter_id'], str):
            raise TypeError(f"Parameter 'meter_id' must be a string, got {type(opts['meter_id']).__name__}")
        
        if 'pulses' in opts and opts['pulses'] is not None:
            if not isinstance(opts['pulses'], list):
                raise TypeError(f"Parameter 'pulses' must be a list, got {type(opts['pulses']).__name__}")

    @property
    def dur_tot(self) -> float:
        return self.size * self.pulse_dur

    def set_tempo(self, new_tempo: float) -> None:
        self.tempo = new_tempo
        self.pulse_dur = 60.0 / new_tempo
        for i, pulse in enumerate(self.pulses):
            pulse.real_time = self.start_time + i * self.pulse_dur

    def set_start_time(self, new_start: float) -> None:
        diff = new_start - self.start_time
        self.start_time = new_start
        for pulse in self.pulses:
            pulse.real_time += diff

    @staticmethod
    def from_pulse(pulse: Pulse, duration: float, size: int,
                   front_weighted: bool = True, layer: int = 0) -> 'PulseStructure':
        tempo = 60 * size / duration
        ps = PulseStructure(tempo=tempo, size=size, start_time=pulse.real_time,
                            front_weighted=front_weighted, layer=layer,
                            parent_pulse_id=pulse.unique_id, meter_id=pulse.meter_id)
        idx = 0 if front_weighted else ps.size - 1
        pulse.affiliations.append({
            'psId': ps.unique_id,
            'idx': idx,
            'layer': layer,
            'segmentedMeterIdx': 0,
            'strong': True,
        })
        ps.pulses[idx] = pulse
        return ps

    def to_json(self) -> Dict:
        return {
            'pulses': [p.to_json() for p in self.pulses],
            'tempo': self.tempo,
            'pulseDur': self.pulse_dur,
            'size': self.size,
            'startTime': self.start_time,
            'uniqueId': self.unique_id,
            'frontWeighted': self.front_weighted,
            'layer': self.layer,
            'parentPulseID': self.parent_pulse_id,
            'primary': self.primary,
            'segmentedMeterIdx': self.segmented_meter_idx,
            'meterId': self.meter_id,
            'offsets': [0.0] * self.size,
        }

    @staticmethod
    def from_json(obj: Dict) -> 'PulseStructure':
        return PulseStructure(
            tempo=obj.get('tempo', 60.0),
            size=obj.get('size', 4),
            start_time=obj.get('startTime', 0.0),
            unique_id=obj.get('uniqueId'),
            front_weighted=obj.get('frontWeighted', True),
            layer=obj.get('layer'),
            parent_pulse_id=obj.get('parentPulseID'),
            primary=obj.get('primary', True),
            segmented_meter_idx=obj.get('segmentedMeterIdx', 0),
            meter_id=obj.get('meterId'),
            pulses=[Pulse.from_json(p) for p in obj.get('pulses', [])]
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PulseStructure) and self.to_json() == other.to_json()


class Meter:
    def __init__(self, hierarchy: Optional[List[int | List[int]]] = None,
                 start_time: float = 0.0, tempo: float = 60.0,
                 unique_id: Optional[str] = None, repetitions: int = 1) -> None:
        # Parameter validation
        self._validate_parameters({
            'hierarchy': hierarchy, 'start_time': start_time, 'tempo': tempo,
            'unique_id': unique_id, 'repetitions': repetitions
        })
        self.hierarchy = hierarchy or [4, 4]
        self.start_time = start_time
        self.tempo = tempo
        self.unique_id = unique_id or str(uuid4())
        self.repetitions = repetitions
        self.pulse_structures: List[List[PulseStructure]] = []
        self._generate_pulse_structures()

    def _validate_parameters(self, opts: Dict) -> None:
        """Validate constructor parameters and provide helpful error messages."""
        if 'hierarchy' in opts and opts['hierarchy'] is not None:
            if not isinstance(opts['hierarchy'], list):
                raise TypeError(f"Parameter 'hierarchy' must be a list, got {type(opts['hierarchy']).__name__}")
            
            if len(opts['hierarchy']) == 0:
                raise ValueError("Parameter 'hierarchy' cannot be empty")
            
            for i, level in enumerate(opts['hierarchy']):
                if isinstance(level, list):
                    if not all(isinstance(item, int) for item in level):
                        raise TypeError(f"All items in hierarchy[{i}] must be integers")
                    if any(item <= 0 for item in level):
                        raise ValueError(f"All items in hierarchy[{i}] must be positive")
                elif isinstance(level, int):
                    if level <= 0:
                        raise ValueError(f"hierarchy[{i}] must be positive, got {level}")
                else:
                    raise TypeError(f"hierarchy[{i}] must be an integer or list of integers, got {type(level).__name__}")
        
        if not isinstance(opts.get('start_time', 0.0), (int, float)):
            raise TypeError(f"Parameter 'start_time' must be a number, got {type(opts['start_time']).__name__}")
        
        if opts.get('start_time', 0.0) < 0:
            raise ValueError(f"Parameter 'start_time' must be non-negative, got {opts['start_time']}")
        
        if not isinstance(opts.get('tempo', 60.0), (int, float)):
            raise TypeError(f"Parameter 'tempo' must be a number, got {type(opts['tempo']).__name__}")
        
        if opts.get('tempo', 60.0) <= 0:
            raise ValueError(f"Parameter 'tempo' must be positive, got {opts['tempo']}")
        
        if opts.get('tempo', 60.0) < MIN_TEMPO_BPM or opts.get('tempo', 60.0) > MAX_TEMPO_BPM:
            import warnings
            warnings.warn(f"Tempo {opts['tempo']} BPM is outside typical range ({MIN_TEMPO_BPM}-{MAX_TEMPO_BPM} BPM)", UserWarning)
        
        if 'unique_id' in opts and opts['unique_id'] is not None and not isinstance(opts['unique_id'], str):
            raise TypeError(f"Parameter 'unique_id' must be a string, got {type(opts['unique_id']).__name__}")
        
        if not isinstance(opts.get('repetitions', 1), int):
            raise TypeError(f"Parameter 'repetitions' must be an integer, got {type(opts['repetitions']).__name__}")
        
        if opts.get('repetitions', 1) <= 0:
            raise ValueError(f"Parameter 'repetitions' must be positive, got {opts['repetitions']}")

    # helper values
    @property
    def _top_size(self) -> int:
        h0 = self.hierarchy[0]
        return sum(h0) if isinstance(h0, list) else int(h0)

    @property
    def _bottom_mult(self) -> int:
        mult = 1
        for h in self.hierarchy[1:]:
            mult *= int(h)
        return mult

    @property
    def _pulses_per_cycle(self) -> int:
        return self._top_size * self._bottom_mult

    @property
    def _pulse_dur(self) -> float:
        return 60.0 / self.tempo / self._bottom_mult

    @property
    def cycle_dur(self) -> float:
        return self._pulse_dur * self._pulses_per_cycle

    def _generate_pulse_structures(self) -> None:
        self.pulse_structures = [[]]
        # single layer of pulses for simplified implementation
        pulses: List[Pulse] = []
        for rep in range(self.repetitions):
            start = self.start_time + rep * self.cycle_dur
            for i in range(self._pulses_per_cycle):
                pulses.append(Pulse(real_time=start + i * self._pulse_dur,
                                    meter_id=self.unique_id))
        self.pulse_structures[0] = [PulseStructure(
            tempo=self.tempo,
            size=self._pulses_per_cycle,
            start_time=self.start_time,
            meter_id=self.unique_id,
            pulses=pulses,
        )]

    @property
    def all_pulses(self) -> List[Pulse]:
        return self.pulse_structures[-1][0].pulses

    @property
    def real_times(self) -> List[float]:
        return [p.real_time for p in self.all_pulses]

    def offset_pulse(self, pulse: Pulse, offset: float) -> None:
        pulse.real_time += offset

    def reset_tempo(self) -> None:
        base = self.all_pulses[:self._pulses_per_cycle]
        diff = base[-1].real_time - base[0].real_time
        if len(base) > 1:
            bit = diff / (len(base) - 1)
            if bit > 0:
                self.tempo = 60.0 / (bit * self._bottom_mult)
        # pulse duration will be derived from tempo

    def grow_cycle(self) -> None:
        self.reset_tempo()
        start = self.start_time + self.repetitions * self.cycle_dur
        for i in range(self._pulses_per_cycle):
            new_pulse = Pulse(real_time=start + i * self._pulse_dur,
                              meter_id=self.unique_id)
            self.pulse_structures[0][0].pulses.append(new_pulse)
        self.repetitions += 1

    def add_time_points(self, time_points: List[float], layer: int = 1) -> None:
        time_points = sorted(time_points)
        for tp in time_points:
            self.pulse_structures[0][0].pulses.append(Pulse(real_time=tp,
                                                            meter_id=self.unique_id))
        self.pulse_structures[0][0].pulses.sort(key=lambda p: p.real_time)

    @staticmethod
    def from_json(obj: Dict) -> 'Meter':
        m = Meter(hierarchy=obj.get('hierarchy'),
                  start_time=obj.get('startTime', 0.0),
                  tempo=obj.get('tempo', 60.0),
                  unique_id=obj.get('uniqueId'),
                  repetitions=obj.get('repetitions', 1))
        m.pulse_structures = [
            [PulseStructure.from_json(ps) for ps in layer]
            for layer in obj.get('pulseStructures', [])
        ]
        return m

    def to_json(self) -> Dict:
        return {
            'uniqueId': self.unique_id,
            'hierarchy': self.hierarchy,
            'startTime': self.start_time,
            'tempo': self.tempo,
            'repetitions': self.repetitions,
            'pulseStructures': [[ps.to_json() for ps in layer]
                                for layer in self.pulse_structures]
        }

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Meter) and self.to_json() == other.to_json()
