

class Car:
    # STEP 1: Python builds the raw function first
    def raw_honk(self):
        return "Beep!"
        
    print(f"1. Raw Function lives at: {hex(id(raw_honk))}")

    # STEP 2 & 3 & 4: Python builds the property and swaps the pointer
    honk = property(raw_honk)
    print(f"2. Property Wrapper lives at: {hex(id(honk))}")

print("\n--- Let's look inside the Class Dictionary ---")
print(Car.__dict__['honk'])