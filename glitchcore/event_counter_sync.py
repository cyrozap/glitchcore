from amaranth import *


class EventCounterSync(Elaboratable):
    def __init__(self, width=32):
        # In, from host.
        self.arm_in = Signal()
        self.polarity_in = Signal()
        self.threshold_in = Signal(width)

        # Out, to host.
        self.count_out = Signal(width)
        self.trigger_out = Signal()

        # In, from async counter.
        self.count_in = Signal(width)
        self.trigger_in = Signal()

        # Out, to async counter.
        self.rst_out = Signal()
        self.enable_out = Signal()
        self.polarity_out = Signal()
        self.threshold_out = Signal(width)

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            self.polarity_out.eq(self.polarity_in),
            self.threshold_out.eq(self.threshold_in),
        ]

        m.d.sync += [
            self.count_out.eq(self.count_in),
            self.trigger_out.eq(self.trigger_in),
        ]

        with m.FSM() as fsm:
            with m.State("RESET"):
                m.d.comb += self.rst_out.eq(1),
                m.d.comb += self.enable_out.eq(0),
                with m.If((self.arm_in).bool()):
                    m.next = "ARMED"
                    m.d.comb += self.rst_out.eq(0),
                    m.d.comb += self.enable_out.eq(1),
            with m.State("ARMED"):
                m.d.comb += self.rst_out.eq(0),
                m.d.comb += self.enable_out.eq(1),
                with m.If((self.trigger_in).bool()):
                    m.next = "DISARMED"
                    m.d.comb += self.enable_out.eq(0),
            with m.State("DISARMED"):
                with m.If(~(self.arm_in).bool()):
                    m.next = "RESET"

        return m


if __name__ == "__main__":
    from amaranth.sim import Simulator

    dut = EventCounterSync()
    def bench():
        for _ in range(30):
            yield
            assert not (yield dut.trigger_out)

        yield dut.trigger_in.eq(1)
        yield
        yield
        assert (yield dut.trigger_out)
        yield dut.trigger_in.eq(0)

        for _ in range(30):
            yield
            assert (yield dut.rst_out)
            assert not (yield dut.enable_out)

        yield dut.arm_in.eq(1)
        assert (yield dut.rst_out)
        assert not (yield dut.enable_out)
        for _ in range(30):
            yield
            assert not (yield dut.rst_out)
            assert (yield dut.enable_out)

        yield dut.trigger_in.eq(1)
        for _ in range(30):
            yield
            assert not (yield dut.rst_out)
            assert not (yield dut.enable_out)

        yield dut.arm_in.eq(0)
        yield
        yield
        assert (yield dut.rst_out)
        assert not (yield dut.enable_out)

    sim = Simulator(dut)
    sim.add_clock(1e-6) # 1 MHz
    sim.add_sync_process(bench)
    with sim.write_vcd("event_counter_sync.vcd"):
        sim.run()
