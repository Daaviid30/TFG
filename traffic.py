
# -------------------------------- PALETA DE COLORES ----------------------------------------
greenColour = "\033[0;32m\033[1m" 
endColour = "\033[0m\033[0m" 
redColour = "\033[0;31m\033[1m" 
blueColour = "\033[0;34m\033[1m" 
yellowColour = "\033[0;33m\033[1m" 
purpleColour = "\033[0;35m\033[1m" 
turquoiseColour = "\033[0;36m\033[1m" 
grayColour = "\033[0;37m\033[1m"
# -------------------------------------------------------------------------------------------

class Traffic:
    
    def __init__(self, request_ID: str, target_ID: str, origin: str, initiator, timestamp: int):
        """
        - request_ID: The ID of the request. It is the primary key of the node.
        - target_ID: The ID of the target where the request was made. It is referred to as the FrameID in CDP.
        - origin: The URL of the target that responded to the request.
        - initiator: The ID of the event that started the request.
        - timestamp: The timestamp of the request, measured in milliseconds.
        """
        self.request_ID = request_ID
        self.target_ID = target_ID
        self.origin = origin
        self.initiator = initiator
        self.timestamp = timestamp

    def __str__(self):
        return (
            f"{blueColour}-- Traffic --{endColour}\n"
            f"[-] request ID: {self.request_ID}\n"
            f"[-] target ID: {self.target_ID}\n"
            f"[-] origin: {self.origin}\n"
            f"[-] initiator: {self.initiator}\n"
            f"[-] timestamp: {self.timestamp}\n")
    
    def to_dict(self):
        return{
            "request_ID": self.request_ID,
            "target_ID": self.target_ID,
            "origin": self.origin,
            "initiator": self.initiator,
            "timestamp": self.timestamp
        }