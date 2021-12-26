from amaranth import *
from amaranth.back import verilog

from glitchcore import GlitchCore


class GlitchCoreWb(Elaboratable):
    def __init__(self):
        # In, from external.
        self.event_in = Signal()

        # Out, to external.
        self.glitch_out = Signal()

        # Wishbone I/O
        self.wb_adr_i = Signal(32)
        self.wb_dat_i = Signal(32)
        self.wb_dat_o = Signal(32)
        self.wb_we_i = Signal()
        self.wb_sel_i = Signal(4)
        self.wb_stb_i = Signal()
        self.wb_ack_o = Signal()
        self.wb_cyc_i = Signal()

    def elaborate(self, platform):
        m = Module()

        gc = GlitchCore()
        m.submodules += gc

        reg00 = Signal(32)

        reg10 = Signal(32)
        reg14 = Signal(32)
        reg18 = Signal(32)

        reg20 = Signal(32)
        reg24 = Signal(32)
        reg28 = Signal(32)

        reg30 = Signal(32)
        reg34 = Signal(32)
        reg38 = Signal(32)

        m.d.comb += [
            # In, from external.
            gc.event_in.eq(self.event_in),

            # Out, to external.
            self.glitch_out.eq(gc.glitch_out),

            reg00[0].eq(gc.event_polarity_in),
            reg00[1].eq(gc.trigger_sel_in),
            reg00[2:2+2].eq(gc.delay_sel_in),
            reg00[4].eq(gc.pulse_sel_in),
            reg00[5:].eq(0),

            reg10[0].eq(gc.event_counter_arm_in),
            reg10[1].eq(gc.event_trigger_out),
            reg10[2:].eq(0),
            gc.event_counter_threshold_in.eq(reg14),
            reg18.eq(gc.event_count_out),

            reg20[0].eq(gc.delay_arm),
            reg20[1].eq(gc.delay_trigger_delayed),
            reg20[2:].eq(0),
            gc.delay_threshold.eq(reg24),
            reg28.eq(gc.delay_count),

            reg30[0].eq(gc.pulse_arm),
            reg30[1].eq(gc.pulse_pulse),
            reg30[2].eq(gc.pulse_fired),
            reg30[3:].eq(0),
            gc.pulse_threshold.eq(reg34),
            reg38.eq(gc.pulse_count),
        ]

        with m.If(self.wb_stb_i & self.wb_we_i):
            with m.Switch(self.wb_adr_i[:8]):
                with m.Case(0x00):
                    m.d.sync += Cat(gc.event_polarity_in, gc.trigger_sel_in, gc.delay_sel_in, gc.pulse_sel_in).eq(self.wb_dat_i)
                with m.Case(0x10):
                    m.d.sync += gc.event_counter_arm_in.eq(self.wb_dat_i)
                with m.Case(0x14):
                    m.d.sync += reg14.eq(self.wb_dat_i)
                with m.Case(0x20):
                    m.d.sync += gc.delay_arm.eq(self.wb_dat_i)
                with m.Case(0x24):
                    m.d.sync += reg24.eq(self.wb_dat_i)
                with m.Case(0x30):
                    m.d.sync += gc.pulse_arm.eq(self.wb_dat_i)
                with m.Case(0x34):
                    m.d.sync += reg34.eq(self.wb_dat_i)

        with m.Switch(self.wb_adr_i[:8]):
            with m.Case(0x00):
                m.d.sync += self.wb_dat_o.eq(reg00)
            with m.Case(0x10):
                m.d.sync += self.wb_dat_o.eq(reg10)
            with m.Case(0x14):
                m.d.sync += self.wb_dat_o.eq(reg14)
            with m.Case(0x18):
                m.d.sync += self.wb_dat_o.eq(reg18)
            with m.Case(0x20):
                m.d.sync += self.wb_dat_o.eq(reg20)
            with m.Case(0x24):
                m.d.sync += self.wb_dat_o.eq(reg24)
            with m.Case(0x28):
                m.d.sync += self.wb_dat_o.eq(reg28)
            with m.Case(0x30):
                m.d.sync += self.wb_dat_o.eq(reg30)
            with m.Case(0x34):
                m.d.sync += self.wb_dat_o.eq(reg34)
            with m.Case(0x38):
                m.d.sync += self.wb_dat_o.eq(reg38)
            with m.Default():
                m.d.sync += self.wb_dat_o.eq(0)

        m.d.sync += self.wb_ack_o.eq(self.wb_stb_i)

        return m


if __name__ == "__main__":
    from amaranth.sim import Simulator

    dut = GlitchCoreWb()
    def bench():
        yield dut.wb_adr_i.eq(0x14)
        yield dut.wb_dat_i.eq(0x08)
        yield dut.wb_stb_i.eq(1)
        yield dut.wb_we_i.eq(1)
        yield
        yield dut.wb_we_i.eq(0)
        yield dut.wb_stb_i.eq(0)
        yield

        yield dut.wb_adr_i.eq(0x24)
        yield dut.wb_dat_i.eq(0x10)
        yield dut.wb_stb_i.eq(1)
        yield dut.wb_we_i.eq(1)
        yield
        yield dut.wb_we_i.eq(0)
        yield dut.wb_stb_i.eq(0)
        yield

        yield dut.wb_adr_i.eq(0x34)
        yield dut.wb_dat_i.eq(0x02)
        yield dut.wb_stb_i.eq(1)
        yield dut.wb_we_i.eq(1)
        yield
        yield dut.wb_we_i.eq(0)
        yield dut.wb_stb_i.eq(0)
        yield

        yield dut.wb_adr_i.eq(0x30)
        yield dut.wb_dat_i.eq(0x01)
        yield dut.wb_stb_i.eq(1)
        yield dut.wb_we_i.eq(1)
        yield
        yield dut.wb_we_i.eq(0)
        yield dut.wb_stb_i.eq(0)
        yield

        yield dut.wb_adr_i.eq(0x20)
        yield dut.wb_dat_i.eq(0x01)
        yield dut.wb_stb_i.eq(1)
        yield dut.wb_we_i.eq(1)
        yield
        yield dut.wb_we_i.eq(0)
        yield dut.wb_stb_i.eq(0)
        yield

        yield dut.wb_adr_i.eq(0x10)
        yield dut.wb_dat_i.eq(0x01)
        yield dut.wb_stb_i.eq(1)
        yield dut.wb_we_i.eq(1)
        yield
        yield dut.wb_we_i.eq(0)
        yield dut.wb_stb_i.eq(0)
        yield

        for _ in range(4):
            yield

        for _ in range(8):
            yield dut.event_in.eq(1)
            yield
            yield dut.event_in.eq(0)
            yield

        for _ in range(0x100):
            yield

    sim = Simulator(dut)
    sim.add_clock(1e-6) # 1 MHz
    sim.add_sync_process(bench)
    with sim.write_vcd("glitchcore_wb.vcd"):
        sim.run()
    with open("glitchcore_wb.v", "w") as f:
        top = GlitchCoreWb()
        f.write(verilog.convert(top, name="glitchcore_wb", ports=[
            # In, from external.
            top.event_in,

            # Out, to external.
            top.glitch_out,

            # Wishbone I/O
            top.wb_adr_i,
            top.wb_dat_i,
            top.wb_dat_o,
            top.wb_we_i,
            top.wb_sel_i,
            top.wb_stb_i,
            top.wb_ack_o,
            top.wb_cyc_i,
        ]))
