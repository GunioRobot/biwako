from biwako import bit, byte, common


class Sample(byte.Structure):
    title = byte.String(size=13, encoding='ascii')
    size = byte.Integer(size=4)
    loop_start = byte.Integer(size=4, default=0)
    loop_end = byte.Integer(size=4, default=0xFFFFF)
    
    @property
    def data(self):
        index = self.get_parent().samples.index(self)
        return self.get_parent().sample_data[index]
    
    def __unicode__(self):
        return self.title


class Note(bit.Structure):
    pitch = bit.Integer(size=6)
    sample = bit.Integer(size=6)
    volume = bit.Integer(size=4)
    command = bit.Integer(size=4)
    command_value = bit.Integer(size=4)
    
    @sample.getter
    def sample(self, index):
        return self.get_parent().samples[index]

    @sample.setter
    def sample(self, sample):
        return self.get_parent().samples.index(sample)


class Row(byte.Structure):
    notes = common.List(Note, size=8)
    
    def __iter__(self):
        return iter(self.notes)


class Pattern(byte.Structure):
    rows = common.List(Row, size=64)
    
    def __iter__(self):
        return iter(self.rows)


class _669(byte.Structure, endianness=byte.LittleEndian):
    marker = byte.FixedString('if')
    message = common.List(byte.String(size=36, encoding='ascii', padding=' '), size=3)
    sample_count = byte.Integer(size=1, max_value=64)
    pattern_count = byte.Integer(size=1, max_value=128)
    restart_position = byte.Integer(size=1)
    pattern_order = byte.List(byte.Integer(size=1, max_value=128), size=128)
    pattern_tempos = byte.List(byte.Integer(size=1), size=128)
    pattern_breaks = byte.List(byte.Integer(size=1), size=128)
    samples = common.List(Sample, size=sample_count)
    patterns = common.List(Pattern, size=pattern_count)
    sample_data = byte.ByteString(size=byte.REMAINDER)
    
    @sample_data.getter
    def sample_data(self, data):
        offset = 0
        output = []
        for info in self.samples:
            output.append(data[offset:offset + info.size])
            offset += info.size
        return output
    
    @sample_data.setter
    def sample_data(self, data_list):
        return ''.join(data_list)
    
    def __iter__(self):
        for index in self.pattern_order:
            yield self.patterns[index]
    
    def __unicode__(self):
        return self.message[0]
    

if __name__ == '__main__':
    track = _669(open(sys.argv[1], 'rb'))
    for line in track.message:
        print(line)
