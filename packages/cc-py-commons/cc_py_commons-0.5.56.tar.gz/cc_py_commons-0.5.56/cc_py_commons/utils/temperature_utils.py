
def to_celsius(temp_in_fahrenheit):
	temp_in_celsius = None
	if temp_in_fahrenheit:
		temp_in_celsius = round(((temp_in_fahrenheit - 32) * 5) / 9, 2)
	return temp_in_celsius

def to_fahrenheit(temp_in_celsius):
	temp_in_fahrenheit = None
	if temp_in_celsius:
		temp_in_fahrenheit = round(((temp_in_celsius * 9) / 5) + 32, 2)
	return temp_in_fahrenheit
