# SDN Firewall and Multi Floor Network
## Mininet Topology (`final_skel.py`)
Creates a full emulated network including:
- Dept A hosts (h101–h104) — `128.114.1.x`
- Dept B hosts (h201–h204) — `128.114.2.x`
- Trusted host — `192.47.38.109`
- Untrusted host — `108.35.24.113`
- Server — `128.114.3.178`
- 6 switches (s1–s6)
- Core switch acting as aggregation point

Mininet runs with a remote POX controller.

## POX Controller (`finalcontroller_skel.py`)
Implements:
- **Firewall rules**
  - Block untrusted → server traffic
  - Block all ICMP from untrusted host
  - Block trusted → server
  - Block trusted ICMP → Dept B
  - Block ICMP between Dept A and Dept B
- **Routing logic**
  - Chooses output ports based on switch ID (dpid)
  - Installs flow rules for accepted traffic
  - Drops packets by omitting output actions
 
## Starting Controller
- ```bash
- cd pox
- ./pox.oy log.level --DEBUG finalcontroller_skel

- sudo python final_skel.py
