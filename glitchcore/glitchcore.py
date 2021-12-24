from amaranth import *
from amaranth.back import verilog

from delay import TriggerDelay
from event_counter_sync import EventCounterSync
from pulse import TriggerPulse


class GlitchCore(Elaboratable):
    def __init__(self, width=32):
        self.width = width

        # In, from external.
        self.event_in = Signal()

        # Out, to external.
        self.glitch_out = Signal()

        # In, from host.
        self.event_counter_arm_in = Signal()
        self.event_counter_threshold_in = Signal(width)

        # Out, to host.
        self.event_count_out = Signal(width)
        self.event_trigger_out = Signal()

        # In, from host.
        self.delay_arm = Signal()
        self.delay_threshold = Signal(width)

        # Out, to host.
        self.delay_count = Signal(width)
        self.delay_trigger_delayed = Signal()

        # In, from host.
        self.pulse_arm = Signal()
        self.pulse_threshold = Signal(width)

        # Out, to host.
        self.pulse_count = Signal(width)
        self.pulse_pulse = Signal()

        # In, from host.
        self.event_polarity_in = Signal()
        self.trigger_sel_in = Signal()
        self.delay_sel_in = Signal(2)
        self.pulse_sel_in = Signal()

    def elaborate(self, platform):
        m = Module()

        event_internal = Signal()

        event_counter_sync = EventCounterSync(self.width)
        trigger_delay = TriggerDelay(self.width)
        trigger_pulse = TriggerPulse(self.width)

        event_counter_async_trigger = Signal()
        event_counter_async = Instance("event_counter_async",
            p_WIDTH = self.width,
            i_rst_i = event_counter_sync.rst_out,
            i_event_i = event_internal,
            i_enable_i = event_counter_sync.enable_out,
            i_threshold_i = event_counter_sync.threshold_out,
            o_count_o = event_counter_sync.count_in,
            o_trigger_o = event_counter_async_trigger,
        )

        m.submodules += [
            event_counter_async,
            event_counter_sync,
            trigger_delay,
            trigger_pulse,
        ]

        m.d.comb += [
            event_counter_sync.arm_in.eq(self.event_counter_arm_in),
            event_counter_sync.threshold_in.eq(self.event_counter_threshold_in),
            self.event_count_out.eq(event_counter_sync.count_out),
            self.event_trigger_out.eq(event_counter_sync.trigger_out),
            event_counter_sync.trigger_in.eq(event_counter_async_trigger),

            trigger_delay.arm.eq(self.delay_arm),
            trigger_delay.threshold.eq(self.delay_threshold),
            self.delay_count.eq(trigger_delay.value),
            self.delay_trigger_delayed.eq(trigger_delay.trigger_delayed),

            trigger_pulse.arm.eq(self.pulse_arm),
            trigger_pulse.threshold.eq(self.pulse_threshold),
            self.pulse_count.eq(trigger_pulse.value),
            self.pulse_pulse.eq(trigger_pulse.pulse),
        ]


        with m.If(self.event_polarity_in == 0):
            m.d.comb += event_internal.eq(self.event_in)
        with m.Else():
            m.d.comb += event_internal.eq(~self.event_in)

        with m.If(self.trigger_sel_in == 0):
            m.d.comb += trigger_delay.trigger_in.eq(event_counter_async_trigger)
        with m.Else():
            m.d.comb += trigger_delay.trigger_in.eq(event_internal)

        with m.If(self.delay_sel_in == 0):
            m.d.comb += trigger_pulse.trigger_in.eq(trigger_delay.trigger_delayed)
        with m.Elif(self.delay_sel_in == 1):
            m.d.comb += trigger_pulse.trigger_in.eq(event_counter_async_trigger)
        with m.Elif(self.delay_sel_in == 2):
            m.d.comb += trigger_pulse.trigger_in.eq(event_internal)

        with m.If(self.pulse_sel_in == 0):
            m.d.comb += self.glitch_out.eq(trigger_pulse.pulse)
        with m.Else():
            m.d.comb += self.glitch_out.eq(trigger_pulse.trigger_in)

        return m


if __name__ == "__main__":
    from amaranth.sim import Simulator

    dut = GlitchCore()
    def bench():
        yield

    sim = Simulator(dut)
    sim.add_clock(1e-6) # 1 MHz
    sim.add_sync_process(bench)
    with sim.write_vcd("glitchcore.vcd"):
        sim.run()
    with open("glitchcore.v", "w") as f:
        top = GlitchCore()
        f.write(verilog.convert(top, name="glitchcore", ports=[
            # In, from external.
            top.event_in,

            # Out, to external.
            top.glitch_out,

            # In, from host.
            top.event_counter_arm_in,
            top.event_counter_threshold_in,

            # Out, to host.
            top.event_count_out,
            top.event_trigger_out,

            # In, from host.
            top.delay_arm,
            top.delay_threshold,

            # Out, to host.
            top.delay_count,
            top.delay_trigger_delayed,

            # In, from host.
            top.pulse_arm,
            top.pulse_threshold,

            # Out, to host.
            top.pulse_count,
            top.pulse_pulse,

            # In, from host.
            top.event_polarity_in,
            top.trigger_sel_in,
            top.delay_sel_in,
            top.pulse_sel_in,
        ]))
