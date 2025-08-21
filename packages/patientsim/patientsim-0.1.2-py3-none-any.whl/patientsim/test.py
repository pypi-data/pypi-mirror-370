from patientsim import DoctorAgent, PatientAgent
from patientsim.environment import EDSimulation



doctor_agent = DoctorAgent('gemini-2.5-flash')
patient_agent = PatientAgent('gpt-4o', 
                              visit_type='emergency_department',
                              confusion_level='normal',
                              personality='plain',
                              recall_level='no_history',
                              lang_proficiency_level='C'
                            )
    
simulation_env = EDSimulation(patient_agent, doctor_agent)

simulation_env.simulate()