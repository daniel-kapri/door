from machine import Pin, SPI
import struct
from nrf24l01 import NRF24L01
import utime
from mfrc522 import MFRC522

reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=22)

led = Pin(25, Pin.OUT)
csn = Pin(15, mode=Pin.OUT, value=1)
ce  = Pin(14, mode=Pin.OUT, value=0)

pipes = (b"\x10\x10\x10\x10\x10", b"\x20\x20\x20\x20\x20")

def setup():
    print("Initializing NRF24L01 on Transmitter")
    spi = SPI(0, baudrate=4000000)  # Set SPI speed to 1 MHz
    nrf = NRF24L01(spi, csn, ce, payload_size=4)
    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()
    led.value(0)
    print("Setup complete on Transmitter")
    return nrf

def demo(nrf):
    state = 0
    while True:
        reader.init()
        (stat, tag_type) = reader.request(reader.REQIDL)
        if stat == reader.OK:
            (stat, uid) = reader.SelectTagSN()
            if stat == reader.OK:
                card = int.from_bytes(bytes(uid),"little",False)
                if card == 202407745:
                    print("Card ID: "+ str(card)+" PASS: Green Light Activated")
                    state = 1
                    nrf.stop_listening()
                    try:
                        nrf.send(struct.pack("i", state))
                        print("Sent:", state)
                        utime.sleep(2)
                        state = 0
                        nrf.send(struct.pack("i", state))
                        print("Sent:", state)
                    except OSError:
                        print('Message lost')
                    nrf.start_listening()
                utime.sleep(0.1)
            else:
                print("Card ID: "+ str(card)+" UNKNOWN CARD! Red Light Activated")

nrf = setup()
demo(nrf)
 
