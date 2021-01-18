import json

class Config:
  def __init__(self):
    with open('DeviceSpecific/config.json') as f:
      self.Parameters = json.load(f)

  def Save(self):
    #print("Saving Config...")

    with open('DeviceSpecific/config.json', 'w') as f:
        f.write(json.dumps(self.Parameters))


    #print("Saved:",json.dumps(self.Parameters))
