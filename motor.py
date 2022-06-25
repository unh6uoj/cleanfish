import wiringpi

def motor_delay(delay_time):
    wiringpi.delay(delay_time)
    
class Motor:
    def __init__(self, pwm_pin, pin1, pin2):
        self.pwm_pin = pwm_pin # pwm pin
        self.pin1 = pin1 # pin1
        self.pin2 = pin2 # pin2

        wiringpi.wiringPiSetup()
        self.set_pin_config()
    
    def set_pin(self, pwm_pin, pin1, pin2):
        self.pwm_pin = pwm_pin
        self.pin1 = pin1
        self.pin2 = pin2

    def set_pin_config(self):
        wiringpi.pinMode(self.pwm_pin, 1)
        wiringpi.pinMode(self.pin1, 1)
        wiringpi.pinMode(self.pin2, 1)
        wiringpi.softPwmCreate(self.pwm_pin, 0, 255)
    
    def go(self, speed): # 앞으로
        wiringpi.softPwmWrite(self.pwm_pin, speed)

        wiringpi.digitalWrite(self.pin1, 0)
        wiringpi.digitalWrite(self.pin2, 1)

    def back(self, speed): # 뒤로
        wiringpi.softPwmWrite(self.pwm_pin, speed)

        wiringpi.digitalWrite(self.pin1, 1)
        wiringpi.digitalWrite(self.pin2, 0)
    
    def motor_stop(self): # 모터 정지
        wiringpi.digitalWrite(self.pin1, 0)
        wiringpi.digitalWrite(self.pin2, 0)
