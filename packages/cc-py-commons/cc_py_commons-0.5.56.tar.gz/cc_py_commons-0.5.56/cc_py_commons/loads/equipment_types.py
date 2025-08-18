import uuid

"""
EQUIPMENT_TYPES maps equipment class names from the mercury pricing db to equipment.id values in freight-hub.
"""
EQUIPMENT_TYPES = {
  "VAN": "b738a0d4-a03d-4302-8f57-2aa1f3eb2f9b",
  "REEFER": "836284b0-f1ae-4f78-83e6-93f81b4c22c9",
  "FLATBED": "59693058-3268-4827-b5cc-4eac370c8188",
  "CURTAIN_VAN": "a4cf30aa-9a29-48e7-8d70-5ccd118446a3",
  "DOUBLE_DROP": "02d36318-37fb-4967-85cf-d49b65758bc8",
  "POWER_ONLY": "e9ced401-93d9-4bc9-9342-d020481133dc",
  "STEP_DECK": "09090c04-c19d-4ef2-8cae-605d69105494",
  "TANKER": "689e53ba-f44f-4702-8db4-9f706018fc56",
  "RGN": "86bdf40d-539f-4e70-90a2-c5471f2604c3",
  "CONTAINER": "42a8e1cf-c85b-4357-b229-a09c163b72f7",
  "HIGH_CUBE_CONTAINER": "42a8e1cf-c85b-4357-b229-a09c163b72f7",
  "POWER ONLY": "e9ced401-93d9-4bc9-9342-d020481133dc",
  "BOX": "f5d9ac97-c088-473f-9ed1-f77548f6aeb1",
  "SPRINTER": "31d9c357-54a7-4df7-8bc6-d197c6e938a4",
  "STRAIGHT": "d1c3d5b2-48a9-420e-8c79-64e5a78383ec"
}
