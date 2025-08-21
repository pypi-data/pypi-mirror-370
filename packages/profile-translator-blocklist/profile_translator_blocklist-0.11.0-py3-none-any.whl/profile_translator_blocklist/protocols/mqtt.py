from .Custom import Custom

class mqtt(Custom):

    # Class variables
    layer = 7              # Protocol OSI layer
    protocol_name = "mqtt" # Protocol name

    supported_keys = [
        "packet-type",
        "topic-name",
        "payload-length"
    ]

    def parse(self, is_backward: bool = False, initiator: str = "src") -> dict:
        """
        Parse the MQTT protocol.

        :param is_backward (optional): Whether the protocol must be parsed for a backward rule.
                                       Optional, default is `False`.
        :param initiator (optional): Connection initiator (src or dst).
                                     Optional, default is "src".
        :return: Dictionary containing the (forward and backward) nftables and nfqueue rules for this policy.
        """
        # Handle MQTT packet type
        packet_type = self.protocol_data.get("packet-type", None)
        if packet_type is not None:
            rule = {"forward": "mqtt_message.packet_type == {}"}
            self.add_field("packet-type", rule, is_backward)

        # Handle MQTT client ID
        client_id = self.protocol_data.get("client-id", None)
        if client_id is not None:
            rule = {"forward": 'strcmp(mqtt_message.client_id, "{}") == 0'}
            self.add_field("client-id", rule, is_backward)

        # Handle MQTT client ID length
        client_id_length = self.protocol_data.get("client-id-length", None)
        if client_id_length is not None:
            rule = {"forward": "mqtt_message.client_id_length == {}"}
            self.add_field("client-id-length", rule, is_backward)

        # Handle MQTT clean session flag
        clean_session = self.protocol_data.get("clean-session", None)
        if clean_session is not None:
            rule = {"forward": "mqtt_message.connect_flags.clean_session == {}"}
            self.add_field("clean-session", rule, is_backward)
        
        # Handle MQTT Keep Alive
        keep_alive = self.protocol_data.get("keep-alive", None)
        if keep_alive is not None:
            rule = {"forward": "mqtt_message.keep_alive == {}"}
            self.add_field("keep-alive", rule, is_backward)

        # Handle MQTT topic name
        topic_name = self.protocol_data.get("topic-name", None)
        if topic_name is not None:
            string = 'strcmp(mqtt_message.topic_name, "{}") == 0'

            if topic_name == "temperature":
                string += "\n \t \t&& \n \t \tcheck_payload_regex(mqtt_message.payload, strlen((char *)mqtt_message.payload),\
\"-?[0-9]?[0-9]\\\\.[0-9]°[CF]\") == 1" # floating point number with 1 decimal place and °C
            elif topic_name == "humidity":
                string += "\n \t \t&& \n \t \tcheck_payload_regex(mqtt_message.payload, strlen((char *)mqtt_message.payload),\
\"[0-9]?[0-9]\\\\.[0-9]%\") == 1" # positive floating point number with 1 decimal place and %

            rule = {"forward": string}
            self.add_field("topic-name", rule, is_backward)
        
        # Handle MQTT payload regex
        payload_regex = self.protocol_data.get("payload-regex", None)
        if payload_regex is not None:
            rule = {"forward": 'check_payload_regex(mqtt_message.payload, strlen((char *)mqtt_message.payload), "{}") == 1'}
            self.add_field("payload-regex", rule, is_backward)

        # Handle MQTT payload length
        payload_length = self.protocol_data.get("payload-length", None)
        if payload_length is not None:
            payload_length = str(payload_length)
            if '-' in payload_length:
                min_length, max_length = payload_length.split('-')
                rule = {"forward": "mqtt_message.payload_length >= {} && mqtt_message.payload_length <= {}".format(min_length, max_length)}
            else:
                rule = {"forward": "mqtt_message.payload_length == {}"}
            self.add_field("payload-length", rule, is_backward)

        return self.rules
