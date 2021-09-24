from threading import Thread, Lock
import time

class SimpleStateMachine:

    def __init__(self) -> None:
        self.state = "idle"
        self.prev_state = ""
        self.ended_task = False
        self.mutex = Lock()
        self.action = ""
        self.stop_action = False

        self.machine_up = False
        self.t_thread = None

    def start(self):        
        self.machine_up = True
        self.t_thread = Thread(target=self.loop)
        self.t_thread.start()

    def stop(self):                
        self.machine_up = False
        if self.t_thread != None:
            self.t_thread.join()

    def start_dummy_task(self, duration):
        dummy_task_thread = Thread(target=self.dummy_task, args=(duration,))
        dummy_task_thread.start()

    def dummy_task(self, duration):
        start_time = time.time()
        self.ended_task = False        
        while(time.time() - start_time < duration):         
            if self.stop_action:                
                self.stop_action = False
                self.ended_task = True
                return            
            time.sleep(0.5)        
        self.ended_task = True

    def transition_logic(self):        
        self.prev_state = self.state
        # Transition logic for state idle
        if self.state == "idle":
            if self.action == "perform action 1":
                self.state = "action 1"
                self.start_dummy_task(5)
            if self.action == "perform action 2":
                self.state = "action 2"
                self.start_dummy_task(10)
        # Transition logic for action 1
        elif self.state == "action 1":
            if self.action == "stop":
                self.state = "stop"
            if self.ended_task:
                self.state = "idle"
        # Transition logic for action 2
        elif self.state == "action 2":
            if self.action == "stop":
                self.state = "stop"
            if self.ended_task:
                self.state = "idle"
        # Transition logic for stop
        elif self.state == "stop":
            self.state = "idle"

        # 'Consume' action
        self.action = ""
        if self.state != self.prev_state:
            if (self.prev_state == "action 1" or self.prev_state == "action 2") and self.state != "stop":
                print("Done!")
            print(f"\nChanged from state '{self.prev_state}' to '{self.state}'\n")
            if self.state == "action 1" or self.state == "action 2":
                print("Running task", end="", flush=True)

    def state_logic(self):
        # State logic        
        if self.state == "idle":
            pass
        elif self.state == "action 1":
            print(".", end="", flush=True)
        elif self.state == "action 2":
            print(".", end="", flush=True)            
        elif self.state == "stop":
            print(" Stopped!")
            self.stop_action = True            

    def loop(self):
        while self.machine_up:
            with self.mutex:                
                self.transition_logic()                
                self.state_logic()
                time.sleep(0.05)

    def perform_action(self, action):
        # print(f"Performing action: {action}")
        self.action = action

def main():
    s_machine = SimpleStateMachine()
    s_machine.start()
    while True:
        cmd = input(">")        
        if cmd in ["quit", "q", "exit"]:            
            break
        if cmd != "":
            s_machine.perform_action(cmd)
    s_machine.stop()

if __name__ == '__main__':
    main()