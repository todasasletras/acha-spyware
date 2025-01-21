class Device:
    def __init__(self, id, name):
        self.id = id
        self.name = name
    
    @staticmethod
    def list_connected_devices():
        import subprocess
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = []
        for line in result.stdout.splintlines()[1:]:
            if line.strip():
                parts = line.split()
                devices. append(Device(id=parts[0], name="Unknown"))
        return devices