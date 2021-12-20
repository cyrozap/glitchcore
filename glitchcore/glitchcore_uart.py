import struct

from amaranth import *
from amaranth.back import verilog

from uart import UART
from glitchcore_wb import GlitchCoreWb


class GlitchCoreUart(Elaboratable):
    def __init__(self):
        # In, from external.
        self.event_in = Signal()
        self.uart_rx = Signal()

        # Out, to external.
        self.glitch_out = Signal()
        self.uart_tx = Signal()

        self.D1 = Signal()
        self.D2 = Signal()
        self.D3 = Signal()
        self.D4 = Signal()
        self.D5 = Signal()

    def elaborate(self, platform):
        m = Module()

        gc = GlitchCoreWb()
        m.submodules += gc

        uart = UART(int(12e6/115200))
        m.submodules += uart

        wbm_adr_o = Signal(32)
        wbm_dat_o = Signal(32)
        wbm_dat_i = Signal(32)
        wbm_we_o = Signal()
        wbm_sel_o = Signal(4)
        wbm_stb_o = Signal()
        wbm_ack_i = Signal()
        wbm_cyc_o = Signal()

        tx_data = Signal(8)
        tx_rdy  = Signal()
        tx_ack  = Signal()

        rx_data = Signal(8)
        rx_err  = Signal()
        rx_ovf  = Signal()
        rx_rdy  = Signal()
        rx_ack  = Signal()

        m.d.comb += [
            # In, from external.
            gc.event_in.eq(self.event_in),
            uart.rx_i.eq(self.uart_rx),

            # Out, to external.
            self.glitch_out.eq(gc.glitch_out),
            self.uart_tx.eq(uart.tx_o),
            self.D1.eq(~self.uart_rx),
            self.D2.eq(0),
            self.D3.eq(~self.uart_tx),
            self.D4.eq(0),
            self.D5.eq(1),

            gc.wb_adr_i.eq(wbm_adr_o),
            gc.wb_dat_i.eq(wbm_dat_o),
            wbm_dat_i.eq(gc.wb_dat_o),
            gc.wb_we_i.eq(wbm_we_o),
            gc.wb_sel_i.eq(wbm_sel_o),
            gc.wb_stb_i.eq(wbm_stb_o),
            wbm_ack_i.eq(gc.wb_ack_o),
            gc.wb_cyc_i.eq(wbm_cyc_o),

            uart.tx_data.eq(tx_data),
            uart.tx_rdy.eq(tx_rdy),
            tx_ack.eq(uart.tx_ack),

            rx_data.eq(uart.rx_data),
            rx_err.eq(uart.rx_err),
            rx_ovf.eq(uart.rx_ovf),
            rx_rdy.eq(uart.rx_rdy),
            uart.rx_ack.eq(rx_ack),
        ]

        command = Signal(8)
        data = Signal(32)
        dword_byte_idx = Signal(range(4))

        with m.FSM() as fsm:
            with m.State("IDLE"):
                m.d.sync += rx_ack.eq(0)
                m.d.sync += wbm_we_o.eq(0)
                m.d.sync += wbm_sel_o.eq(0)
                m.d.sync += wbm_stb_o.eq(0)
                m.d.sync += wbm_cyc_o.eq(0)
                m.d.sync += dword_byte_idx.eq(0)
                with m.If(rx_rdy):
                    m.d.sync += rx_ack.eq(1)
                    m.d.sync += command.eq(rx_data)
                    m.next = "COMMAND"

            with m.State("COMMAND"):
                with m.Switch(command):
                    with m.Case(ord('\r')):
                        m.d.sync += data.eq(struct.unpack('<I', b"OK\r\n")[0])
                        m.next = "TX_DWORD"
                    with m.Case(ord('R')):
                        m.next = "READ_ADDR"
                    with m.Case(ord('W')):
                        m.next = "WRITE_ADDR"
                    with m.Default():
                        m.next = "IDLE"

            with m.State("READ_ADDR"):
                with m.If(rx_rdy):
                    m.d.sync += rx_ack.eq(1)
                    m.d.sync += wbm_adr_o.eq(rx_data)
                    m.d.sync += wbm_sel_o.eq(0xf)
                    m.d.sync += wbm_stb_o.eq(1)
                    m.d.sync += wbm_cyc_o.eq(1)
                    m.next = "READ_DATA"
            with m.State("READ_DATA"):
                with m.If(wbm_ack_i):
                    m.d.sync += data.eq(wbm_dat_i)
                    m.d.sync += wbm_sel_o.eq(0)
                    m.d.sync += wbm_stb_o.eq(0)
                    m.d.sync += wbm_cyc_o.eq(0)
                    m.next = "TX_DWORD"
            with m.State("TX_DWORD"):
                with m.Switch(dword_byte_idx):
                    for i in range(4):
                        with m.Case(i):
                            m.d.sync += tx_data.eq(data[8*i:8*i+8])
                m.d.sync += tx_rdy.eq(1)
                m.next = "TX_DWORD_BYTE"
            with m.State("TX_DWORD_BYTE"):
                m.d.sync += tx_rdy.eq(0)
                with m.If((tx_rdy == 0) & (tx_ack == 1)):
                    m.d.sync += dword_byte_idx.eq(dword_byte_idx + 1)
                    with m.If(dword_byte_idx == 3):
                        m.next = "IDLE"
                    with m.Else():
                        m.next = "TX_DWORD"

            with m.State("WRITE_ADDR"):
                with m.If(rx_rdy):
                    m.d.sync += rx_ack.eq(1)
                    m.d.sync += wbm_adr_o.eq(rx_data)
                    m.d.sync += wbm_sel_o.eq(0xf)
                    m.next = "RX_DWORD"
            with m.State("RX_DWORD"):
                with m.If(rx_rdy):
                    m.d.sync += rx_ack.eq(1)
                    with m.Switch(dword_byte_idx):
                        for i in range(4):
                            with m.Case(i):
                                m.d.sync += data[8*i:8*i+8].eq(rx_data)
                    m.d.sync += dword_byte_idx.eq(dword_byte_idx + 1)
                    with m.If(dword_byte_idx == 3):
                        m.next = "WRITE_DATA"
            with m.State("WRITE_DATA"):
                m.d.sync += wbm_dat_o.eq(data)
                m.d.sync += wbm_we_o.eq(1)
                m.d.sync += wbm_stb_o.eq(1)
                m.d.sync += wbm_cyc_o.eq(1)
                m.next = "IDLE"

        return m


if __name__ == "__main__":
    with open("glitchcore_uart.v", "w") as f:
        top = GlitchCoreUart()
        f.write(verilog.convert(top, name="glitchcore_uart", ports=[
            # In, from external.
            top.event_in,
            top.uart_rx,

            # Out, to external.
            top.glitch_out,
            top.uart_tx,
            top.D1,
            top.D2,
            top.D3,
            top.D4,
            top.D5,
        ]))
