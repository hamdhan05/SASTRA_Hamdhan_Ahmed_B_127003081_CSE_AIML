import os
import pymupdf

def generate_pdf():
    os.makedirs("data", exist_ok=True)
    pdf_path = os.path.abspath("data/AUTOSAR_Adaptive_Powertrain_HLD.pdf")
    
    doc = pymupdf.open()
    
    # Page 1: Architecture Overview & Components
    p1 = doc.new_page()
    text_p1 = """AUTOSAR ADAPTIVE PLATFORM SPECIFICATION
Document ID: HLD-AUTOSAR-PWR-2026 | Version: 2.4 | Classification: Technical High-Level Design

1. SYSTEM ARCHITECTURE OVERVIEW
The Adaptive Powertrain Management System is architected in accordance with AUTOSAR Classic and Adaptive standards for high-performance electric vehicles. The supervisory control layer delegates real-time torque calculation, battery management, and thermal throttling across dedicated automotive software components.

2. SOFTWARE COMPONENTS (SWC)
- PowertrainManager_SWC:
  The master supervisory controller executing vehicle operating mode management (Park, Drive, Neutral, Reverse, Regeneration). It coordinates torque commands with the inverter stage and enforces regenerative braking limits.
  
- TorqueArbitration_SWC:
  The core arbitration unit responsible for merging torque demands from the accelerator pedal, ADAS Adaptive Cruise Control (ACC), and Traction Control System (TCS). It ensures smooth transition between positive acceleration and regenerative braking.
  
- BatterySafety_SWC:
  High-voltage battery supervisor monitoring pack voltage, cell temperature gradients, and contactor weld detection. In the event of an over-temperature condition (>65°C), it commands emergency power derating.

- InverterActuator_SWC:
  Low-level hardware abstraction component interfacing with the dual motor inverter bridges via high-speed CAN-FD.
"""
    p1.insert_text((50, 60), text_p1, fontsize=11, fontname="helv")
    
    # Page 2: Runnables, Timing & Interfaces
    p2 = doc.new_page()
    text_p2 = """3. RUNNABLES AND TASK SCHEDULING
The software architecture defines deterministic periodic and event-driven execution entities:

- Runnable_ArbitrateTorque:
  Periodic runnable scheduled every 10ms with priority 5. It executes the core PID arbitration algorithm, evaluates driver demand versus traction limits, and computes the net torque request.
  
- Runnable_CalculateThermals:
  Periodic runnable scheduled every 50ms with priority 3. It calculates stator and rotor thermal models to predict overheating before hardware thermal cutoffs trigger.
  
- Runnable_EmergencyCutoff:
  Event-triggered runnable executed immediately upon receiving high-voltage interlock loop (HVIL) fault signals or pyrofuse trigger requests. Latency must not exceed 2ms.

4. AUTOSAR INTERFACES & PORTS
Communication across components is strictly governed by AUTOSAR Port Interfaces:

- TorqueRequest_IF:
  Client-Server interface providing operations GetDriverDemand() and SetArbitratedTorque(). Allowed torque limits range from -500 Nm (maximum regeneration) to +1200 Nm (peak acceleration).
  
- BatteryStatus_IF:
  Sender-Receiver interface broadcasting state-of-charge (SoC: 0.0% to 100.0%), bus voltage, and isolation resistance metrics.
  
- ContactorCommand_IF:
  Dedicated secure interface triggering pyrofuse detachment and main DC contactor disconnect during unrecoverable faults.
"""
    p2.insert_text((50, 60), text_p2, fontsize=11, fontname="helv")

    # Page 3: Constraints, Compliance & Bounds
    p3 = doc.new_page()
    text_p3 = """5. SAFETY INTEGRITY & ENTERPRISE CONSTRAINTS
- ISO 26262 ASIL Rating:
  The complete Powertrain management subsystem is classified as ASIL D. The Fault Tolerant Time Interval (FTTI) is defined as 50 milliseconds.
  
- Memory & Buffer Boundaries:
  All arrays must be statically bounded in compliance with MISRA C:2012 Rule 17.2 and AUTOSAR Memory Mapping. The telemetry array torque_history_buffer[256] is allocated with a strict upper bound of 256 samples. Dynamic buffer allocation is prohibited.

- Inter-Process Communication (IPC) Rules:
  All data exchanges between PowertrainManager_SWC and TorqueArbitration_SWC must pass through the AUTOSAR Runtime Environment (RTE) ports. Direct memory access, raw pointers, or shared unmanaged memory are forbidden to preserve ASIL D safety isolation.
"""
    p3.insert_text((50, 60), text_p3, fontsize=11, fontname="helv")
    
    doc.save(pdf_path)
    doc.close()
    print(f"Generated sample PDF at: {pdf_path}")

if __name__ == "__main__":
    generate_pdf()
