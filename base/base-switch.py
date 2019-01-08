from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER 
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types

class Base365(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
	
	def __init__(self, *args, **kwargs):
		super(Base365, self).__init__(*args, **kwargs)

	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def _switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
				ofproto.OFPCML_NO_BUFFER)]
		print("joined datapath 0x%09x"%(datapath.id))
		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
				actions)]
		mod = parser.OFPFlowMod(datapath=datapath, priority=0,
					match=match, instructions=inst)
		datapath.send_msg(mod)
 
	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		"Handle Incoming Packets"
		msg = ev.msg

		#Get Datapath Info
		dpid = msg.datapath.id
		ofproto = msg.datapath.ofproto
		self.logger.info("PACKET IN | dpid: %s", dpid)		

		#Get Packet
		pkt = packet.Packet(msg.data)
		
		#Set to Flood
		output_port = ofproto.OFPP_FLOOD
		output_actions = [msg.datapath.ofproto_parser.OFPActionOutput(output_port)]
		
		data = None
		if msg.buffer_id == ofproto.OFP_NO_BUFFER:
			data = msg.data
 
		#Output Message
		output_msg = msg.datapath.ofproto_parser.OFPPacketOut(
			datapath=msg.datapath, actions=output_actions, 
			data=data, in_port=msg.match['in_port'], buffer_id=msg.buffer_id)

		#Send
		msg.datapath.send_msg(output_msg)

	
	@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
	def _port_status_change_hander(self, ev):
		"Log Port Events"
		msg = ev.msg
		port_no = msg.desc.port_no
		change = msg.reason
		ofproto = msg.datapath.ofproto
		dpid = msg.datapath.id
		log_ext = ""

		if change == ofproto.OFPPR_ADD:
			log_ext = "ADDED" 
		elif change == ofproto.OFPPR_DELETE:
			log_ext = "REMOVED"
		elif change == ofproto.OFPPR_MODIFY:
			log_ext = "MODIFIED"
		else:
			log_ext = "INVALID STATE"

		self.logger.info("PORT %s | dpid: %s | port: %s", log_ext, dpid, port_no)
