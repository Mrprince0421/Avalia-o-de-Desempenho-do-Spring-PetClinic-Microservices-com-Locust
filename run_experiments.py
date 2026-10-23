#!/usr/bin/env python3
import subprocess
import time
import os
import json

TARGET_HOST = os.getenv("TARGET_HOST", "http://localhost:8080")
RESULTS_DIR = "results"
RAW_DIR = os.path.join(RESULTS_DIR, "raw")

os.makedirs(RAW_DIR, exist_ok=True)

SCENARIOS = {
    "A": {"users": 30, "spawn_rate": 5, "duration": 420, "warmup": 60},
    "B": {"users": 80, "spawn_rate": 10, "duration": 420, "warmup": 60},
    "C": {"users": 150, "spawn_rate": 15, "duration": 420, "warmup": 60}
}

PROFILES = ["ReadProfile", "WriteProfile"]
REPETITIONS = 10

def get_container_cpu():
    try:
        cmd = "docker stats --no-stream --format '{{.Name}},{{.CPUPerc}}'"
        output = subprocess.check_output(cmd, shell=True, text=True)
        cpu_data = {}
        for line in output.strip().split('\n'):
            if line:
                parts = line.split(',')
                if len(parts) == 2:
                    name, cpu = parts[0], parts[1].replace('%', '')
                    cpu_data[name] = float(cpu) if cpu != 'N/A' else 0.0
        return cpu_data
    except Exception:
        return {}

def run_single_experiment(profile, scenario_key, rep):
    scen = SCENARIOS[scenario_key]
    prefix = f"{profile}_{scenario_key}_rep{rep}"
    csv_prefix = os.path.join(RAW_DIR, prefix)
    
    print(f"\n[>>>] Executando Perfil: {profile} | Cenário {scenario_key} ({scen['users']} users) | Repetição {rep}/10")
    
    cmd = [
        "locust", "-f", "locustfile.py", "--headless",
        "-u", str(scen["users"]), "-r", str(scen["spawn_rate"]),
        "--run-time", f"{scen['duration']}s", "--host", TARGET_HOST,
        "--csv", csv_prefix, "--only-summary", profile
    ]
    
    proc = subprocess.Popen(cmd)
    time.sleep(scen["warmup"])
    
    cpu_samples_customer = []
    cpu_samples_vets = []
    sample_interval = 10
    remaining_time = scen["duration"] - scen["warmup"]
    
    for _ in range(int(remaining_time / sample_interval)):
        time.sleep(sample_interval)
        cpu_data = get_container_cpu()
        for cname, cpu_val in cpu_data.items():
            if "customer" in cname.lower():
                cpu_samples_customer.append(cpu_val)
            elif "vet" in cname.lower():
                cpu_samples_vets.append(cpu_val)
                
    proc.wait()
    
    avg_cpu_customer = sum(cpu_samples_customer)/len(cpu_samples_customer) if cpu_samples_customer else 0.0
    avg_cpu_vets = sum(cpu_samples_vets)/len(cpu_samples_vets) if cpu_samples_vets else 0.0
    
    with open(f"{csv_prefix}_cpu.json", "w") as f:
        json.dump({
            "customers_service_cpu_avg": avg_cpu_customer,
            "vets_service_cpu_avg": avg_cpu_vets
        }, f, indent=2)

def main():
    print("==========================================================")
    print(" INICIANDO BATERIA DE EXPERIMENTOS DE DESEMPENHO (LOCUST) ")
    print("==========================================================")
    for profile in PROFILES:
        for scen_key in ["A", "B", "C"]:
            for rep in range(1, REPETITIONS + 1):
                run_single_experiment(profile, scen_key, rep)
                time.sleep(5)

    print("\n[SUCCESS] Experimentos concluídos!")
    subprocess.run(["python3", "process_results.py"])

if __name__ == "__main__":
    main()
