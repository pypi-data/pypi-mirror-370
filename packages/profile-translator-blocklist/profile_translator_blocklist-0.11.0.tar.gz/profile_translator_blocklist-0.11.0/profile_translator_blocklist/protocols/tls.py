from .Custom import Custom

class tls(Custom):

    # Class variables
    layer = 5               # Protocol OSI layer (arbitrary)
    protocol_name = "tls"   # Protocol name

    supported_keys = [
        "content-type",
        "handshake-type",
        "tls-version",
        "session-id"
    ]

    def parse(self, is_backward: bool = False, initiator: str = "src") -> dict:
        """
        Parse the TLS protocol.

        :param is_backward (optional): Whether the protocol must be parsed for a backward rule.
                                       Optional, default is `False`.
        :param initiator (optional): Connection initiator (src or dst).
                                     Optional, default is "src".
        :return: Dictionary containing the (forward and backward) nftables and nfqueue rules for this policy.
        """
        # Handle TLS content type
        content_type = self.protocol_data.get("content-type", None)
        if content_type is not None:
            rule = {"forward": "tls_packet->messages->message.content_type == {}"}
            self.add_field("content-type", rule, is_backward)
        
        # Handle TLS handshake type
        handshake_type = self.protocol_data.get("handshake-type", None)
        if handshake_type is not None:
            if not ',' in str(handshake_type):
                rule = {"forward": "tls_packet != NULL && tls_packet->messages != NULL && tls_packet->messages->message.handshake_type == {}"}
            else:
                if '[' in str(handshake_type): # in case format in profile is '[ {n°}, {n°}, ... ]'
                    handshake_type = handshake_type.replace('[', '').replace(']', '')
                lst = [int(x.strip(), 16 if x.strip().startswith('0x') else 10) for x in handshake_type.split(',')]
                conditions = ["tls_packet != NULL"]
                current_chain = "tls_packet->messages"
                conditions.append(f"{current_chain} != NULL")
                
                for i, value in enumerate(lst):
                    if i > 0:
                        current_chain = f"{current_chain}->next"
                        conditions.append(f"{current_chain} != NULL")
                    
                    if value == 20:  # change cipher spec message or much less likely finished handshake encryted message
                        conditions.append(f"( {current_chain}->message.content_type == {value} || {current_chain}->message.handshake_type == {value} )")
                    else:
                        conditions.append(f"{current_chain}->message.handshake_type == {value}")
                        
                string = " && ".join(conditions)
                rule = {"forward": string}
            self.add_field("handshake-type", rule, is_backward)
        
        # Handle TLS version
        tls_version = self.protocol_data.get("tls-version", None)
        if tls_version is not None:
            if '"' in str(tls_version): # in case written in profile as string, is float otherwise
                tls_version = tls_version.replace('"', '')
            rule = {"forward": "tls_packet->messages->message.tls_version == {}"}
            func = lambda tls_version: str(769 + int(str(tls_version)[-1])) # 769 = 0x0301
            self.add_field("tls-version", rule, is_backward, func)
        
        # Handle TLS session ID
        session_id = self.protocol_data.get("session-id", None)
        if session_id is not None:
            rule = {"forward": "tls_packet->messages->message.session_id_present == {}"}
            self.add_field("session-id", rule, is_backward)
        
        return self.rules
