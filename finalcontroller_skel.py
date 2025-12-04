from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class Final (object):
  """
  A Firewall object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages
    self.connection = connection
    # This binds PacketIn event listener
    connection.addListeners(self)

  def do_final (self, packet, packet_in, port_on_switch, switch_id):
    find_icmp = packet.find("icmp")
    find_ipv4 = packet.find("ipv4")

    if find_ipv4 is not None:
      src_ip = str(find_ipv4.srcip)
      dst_ip = str(find_ipv4.dstip)
      server_ip = "128.114.3.178"
      trusted_ip = "192.47.38.109"
      untrusted_ip = "108.35.24.113"
      floor_one_a = ["128.114.1.101", "128.114.1.102", "128.114.1.103", "128.114.1.104"]
      floor_two_b = ["128.114.2.201", "128.114.2.202", "128.114.2.203", "128.114.2.204"]

      #blocks traffic from untrusted server to server
      if src_ip == untrusted_ip and dst_ip == server_ip:
        self.drop(packet, packet_in)
        return
      
      #does not allow untrusted ICMP packets to any hosts
      if src_ip == untrusted_ip and find_icmp is not None:
        self.drop(packet, packet_in)
        return
      
      if src_ip == trusted_ip and dst_ip == server_ip:
        self.drop(packet, packet_in)
        return

      if src_ip == trusted_ip and dst_ip in floor_two_b and find_icmp is not None:
        self.drop(packet, packet_in)
        return

      #blocks ICMP packets from dept a and b
      if (src_ip in floor_one_a and dst_ip in floor_two_b) or (src_ip in floor_two_b and dst_ip in floor_one_a):
        if find_icmp is not None:
          self.drop(packet, packet_in)
          return

      output_port = None
      if switch_id == 5:
      # main switch 
        if dst_ip in floor_one_a:
          output_port = 1 #dept a port 1
        elif dst_ip in floor_two_b:
          output_port = 2 # dept b port 2
        elif dst_ip == server_ip:
          output_port = 6 # server port 6
        elif dst_ip == trusted_ip:
          output_port = 5 # trusted server port 5
        elif dst_ip == untrusted_ip:
          output_port = 7 # Untrusted server/host on port 7
      elif switch_id == 1:
        if dst_ip == "128.114.1.101":
          output_port = 8
        elif dst_ip == "128.114.1.102":
          output_port = 9
        else:
          output_port = 3
      elif switch_id == 2:
        if dst_ip == "128.114.1.103":
          output_port = 8
        elif dst_ip == "128.114.1.104":
          output_port = 9
        else:
          output_port = 3
      elif switch_id == 3:
        if dst_ip == "128.114.2.201":
          output_port = 8
        elif dst_ip == "128.114.2.202":
          output_port = 9
        else:
          output_port = 3

      elif switch_id == 4:
        if dst_ip == "128.114.2.203":
          output_port = 8
        elif dst_ip == "128.114.2.204":
          output_port = 9
        else:
          output_port = 3
      elif switch_id == 6:
        if dst_ip == server_ip:
          output_port = 8
        else:
          output_port = 2
        #accepts packets to predetermined output port
      if output_port is not None:
        self.accept(packet, packet_in, output_port)
      else:
        self.drop(packet, packet_in)
    else:
      self.accept(packet, packet_in, of.OFPP_FLOOD)

      
  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """
    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.
    self.do_final(packet, packet_in, event.port, event.dpid)

  # flow entries for allowed traffic
  def accept(self, packet, packet_in, output_port):
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet)
    msg.idle_timeout = 30
    msg.hard_timeout = 30
    msg.buffer_id = packet_in.buffer_id
    msg.actions.append(of.ofp_action_output(port = output_port))
    msg.data = packet_in
    self.connection.send(msg)

  # dropped packets 
  def drop(self, packet, packet_in):
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match.from_packet(packet)
    msg.idle_timeout = 30
    msg.hard_timeout = 30
    msg.buffer_id = packet_in.buffer_id
    self.connection.send(msg)


def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Final(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
