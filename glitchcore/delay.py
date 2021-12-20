from amaranth import *


class TriggerDelay(Elaboratable):
    def __init__(self, width=32):
        # In, from external.
        self.trigger_in = Signal()

        # In, from host.
        self.arm = Signal()
        self.threshold = Signal(width)

        # Out, to host.
        self.value = Signal(width)
        self.trigger_delayed = Signal()

    def elaborate(self, platform):
        m = Module()

        with m.FSM() as fsm:
            with m.State("START"):
                m.d.comb += self.trigger_delayed.eq(0)
                with m.If((self.arm).bool() & (self.trigger_in).bool()):
                    m.next = "TRIGGERED"
                    m.d.sync += self.value.eq(self.value + 1)
            with m.State("TRIGGERED"):
                m.d.sync += self.value.eq(self.value + 1)
                with m.If(self.value >= self.threshold):
                    m.next = "STOP"
                    m.d.comb += self.trigger_delayed.eq(1)
            with m.State("STOP"):
                m.d.comb += self.trigger_delayed.eq(1)
                with m.If(~(self.arm).bool()):
                    m.next = "START"
                    m.d.sync += self.value.eq(0)

        return m


if __name__ == "__main__":
    from amaranth.sim import Simulator

    dut = TriggerDelay()
    def bench():
        for _ in range(30):
            yield
            assert not (yield dut.trigger_delayed)

        yield dut.trigger_in.eq(1)
        for _ in range(30):
            yield
            assert not (yield dut.trigger_delayed)

        yield dut.trigger_in.eq(0)
        yield dut.threshold.eq(0x10)
        yield dut.arm.eq(1)
        for _ in range(30):
            yield
            assert not (yield dut.trigger_delayed)

        yield dut.trigger_in.eq(1)
        for _ in range(0x10):
            yield
            assert not (yield dut.trigger_delayed)

        yield
        assert (yield dut.trigger_delayed)

        for _ in range(30):
            yield
            assert (yield dut.trigger_delayed)

        yield dut.arm.eq(0)
        yield
        yield
        assert not (yield dut.trigger_delayed)
        assert not (yield dut.value)

    sim = Simulator(dut)
    sim.add_clock(1e-6) # 1 MHz
    sim.add_sync_process(bench)
    with sim.write_vcd("delay.vcd"):
        sim.run()
